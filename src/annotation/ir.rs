//! Compiled intermediate representation (IR) for OpenVariant annotations.
//!
//! # Design
//!
//! An annotation YAML file is parsed and compiled **once**
//! into a [`CompiledAnnotation`], which:
//!
//! - Stores one [`FieldOp`] per output column like a builder class.
//!
//! - Use of [`CompiledLambda`] to annotate native Rhai closure expressions (e.g. `"|x| x.to_upper()"`).
//!   The closure is compiled once via the [`rhai`] engine,
//!   there is no Python fallback and no PyO3 bridge involved.

use regex::Regex;
use rhai::{AST, Dynamic, Engine, FnPtr};
use std::collections::HashMap;
use std::path::PathBuf;
use std::sync::OnceLock;
use thiserror::Error;

use crate::annotation::config::AnnotationFormat;

/// Error returned when a `function` string is not a valid Rhai closure.
#[derive(Debug, Error)]
#[error("invalid closure {expression:?}: {reason}")]
pub struct LambdaCompileError {
    /// The closure source that failed to compile.
    expression: String,
    /// Underlying Rhai parse/eval error message.
    reason: String,
}

/// Error returned when a compiled closure fails to execute against a given input.
#[derive(Debug, Error)]
#[error("closure {expression:?} failed on input {input:?}: {reason}")]
pub struct LambdaApplyError {
    /// The closure source that failed to execute.
    expression: String,
    /// The input value the closure was applied to.
    input: String,
    /// Underlying Rhai runtime error message.
    reason: String,
}


/// A single compiled field-annotation rule.
///
/// Each variant mirrors one `type:` value supported in the annotation.
#[derive(Debug, Clone)]
pub enum FieldOp {
    /// Assign a fixed literal value to every output record.
    ///
    Static {
        value: String,
    },

    /// Copy the value from another column already present in the same record.
    ///
    Internal {
        /// Candidate source column names.
        sources: Vec<String>,
        /// Text to represent multiple sources parameters
        value: Option<String>,
        /// Fallback literal value used when no source column is found.
        default: Option<String>,
        /// Transformation applied to the extracted value.
        func: CompiledLambda,
    },

    /// Derive the value from the directory name of the file being processed.
    ///
    Dirname {
        /// Transformation applied to the raw directory name before `regex`.
        func: CompiledLambda,
        /// Regex whose first capture group extracts the final value.
        regex: Regex,
    },

    /// Derive the value from the file name of the file being processed.
    ///
    Filename {
        /// Transformation applied to the raw file name before `regex`.
        func: CompiledLambda,
        /// Regex whose first capture group extracts the final value.
        regex: Regex,
    },

    /// Look up the value in an external delimited mapping file, keyed by
    /// one of several candidate source columns.
    ///
    Mapping {
        /// Candidate source column names, tried in order.
        sources: Vec<String>,
        /// Pre-loaded lookup table: mapping-file key -> mapping-file value.
        table: HashMap<String, String>,
    },

    /// Delegate value computation to an external (Python) plugin.
    ///
    Plugin {
        /// Dotted plugin identifier (as written in the YAML `plugin` key).
        plugin: String,
    },
}

/// A native Rhai closure compiled from the annotation.
///
/// Author writes a closure expression, e.g.:
///
/// ```text
/// |x| x.to_upper()
/// |x| x.replace("old", "new");
/// |x| x.split("_")[1]
/// ```
///
/// `CompiledLambda::compile` parses that expression **once** into a Rhai
/// [`AST`] plus a [`FnPtr`] pointing at the resulting closure. `apply`
/// then re-executes the already-compiled closure for every row, without
/// re-parsing the source or invoking any external interpreter. Because the
/// closure is genuinely executed by the Rhai engine (a safe, sandboxed
/// scripting language embedded in Rust), any arbitrary transformation
/// expressible in Rhai is supported
#[derive(Clone)]
pub struct CompiledLambda {
    /// Original closure source, exactly as written in the annotation.
    source: String,
    /// Compiled AST backing `func`.
    ast: AST,
    /// Pointer to the (possibly anonymous) closure defined by `ast`.
    func: FnPtr,
}

impl std::fmt::Debug for CompiledLambda {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("CompiledLambda")
            .field("source", &self.source)
            .finish()
    }
}

/// The process-wide Rhai engine used to compile and evaluate every
/// [`CompiledLambda`].
///
/// A single shared `Engine` is reused because construction has non-trivial
/// cost and engines carry no per-annotation state; the `sync` feature makes
/// `Engine`, `AST`, and `FnPtr` all `Send + Sync` so this can be shared
/// safely across threads.
fn engine() -> &'static Engine {
    static ENGINE: OnceLock<Engine> = OnceLock::new();
    ENGINE.get_or_init(Engine::new)
}

impl CompiledLambda {
    /// Compile a Rhai closure expression such as `"|x| x.to_upper()"`.
    ///
    /// # Errors
    ///
    /// Returns [`LambdaCompileError`] if `source` fails to parse, or does
    /// not evaluate to a function pointer (closure).
    pub fn compile(source: impl Into<String>) -> Result<Self, LambdaCompileError> {
        let source = source.into();
        let engine = engine();

        let ast = engine
            .compile_expression(&source)
            .map_err(|e| LambdaCompileError {
                expression: source.clone(),
                reason: e.to_string(),
            })?;

        let func: FnPtr = engine
            .eval_ast(&ast)
            .map_err(|e| LambdaCompileError {
                expression: source.clone(),
                reason: e.to_string(),
            })?;

        Ok(Self { source, ast, func })
    }

    /// The original closure source text, as written in the annotation YAML.
    pub fn source(&self) -> &str {
        &self.source
    }

    /// Apply this closure to a single string input.
    ///
    /// # Errors
    ///
    /// Returns [`LambdaApplyError`] if the closure fails to execute (e.g.
    /// wrong arity or a runtime error raised by the Rhai script).
    pub fn apply(&self, input: &str) -> Result<String, LambdaApplyError> {
        let engine = engine();

        self.func
            .call::<Dynamic>(engine, &self.ast, [Dynamic::from(input.to_owned())])
            .map(|result| result.to_string())
            .map_err(|e| LambdaApplyError {
                expression: self.source.clone(),
                input: input.to_owned(),
                reason: e.to_string(),
            })
    }
}


/// The compiled form of an annotation file.
///
/// A `CompiledAnnotation` holds everything needed to match, read, and annotate
/// the files described by the annotation file, pre-compiled so that no YAML parsing,
/// regex compilation, or lambda-string evaluation happens again on the hot path.
///
/// Instances are meant to be built once and shared behind an `Arc`
/// across every file and every row that uses this annotation.
#[derive(Debug, Clone)]
pub struct CompiledAnnotation {
    /// Filesystem path of the annotation YAML this was compiled from.
    pub path: PathBuf,

    /// Glob patterns used to match input files
    pub patterns: Vec<String>,

    /// Whether matching recurses into sub-directories.
    pub recursive: bool,

    /// Output format (`TSV`/`CSV`).
    pub format: AnnotationFormat,

    /// Field delimiter used to read input files.
    pub delimiter: Option<char>,

    /// Ordered list of output column names.
    pub columns: Vec<String>,

    /// Compiled field rules, in declaration order, keyed by output column
    /// name (`field:` in the YAML). Declaration order is preserved via the
    /// paired `Vec` rather than a hash map so annotated output columns are
    /// emitted deterministically.
    pub fields: Vec<(String, FieldOp)>,

    /// Row-exclusion predicates: output column name -> values that, if
    /// matched, cause the row to be dropped.
    pub excludes: HashMap<String, Vec<String>>,
}

impl CompiledAnnotation {
    /// Look up the compiled [`FieldOp`] for a given output column name.
    pub fn field(&self, name: &str) -> Option<&FieldOp> {
        self.fields
            .iter()
            .find(|(field_name, _)| field_name == name)
            .map(|(_, op)| op)
    }
}
