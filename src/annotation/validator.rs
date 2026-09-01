//! Annotation validators for OpenVariant annotation.
//!
//! This module provides validation logic for ensuring that annotation configurations are valid and consistent.
//! It includes functions to validate annotation types, delimiters, formats, and overall configuration structures.
//! The validators are designed to be used during the deserialization process of YAML annotation definition files,
//! providing immediate feedback on any issues with the configuration. This helps maintain the integrity of the annotation system and
//! prevents runtime errors due to misconfigurations.

use regex::Regex;

use std::path::Path;
use std::fmt;
use super::config::{AnnotationConfig, AnnotationEntry};

#[derive(Debug, Clone, PartialEq)]
pub struct ValidationError {
    /// Human-readable problem description.
    pub message: String,
    /// The YAML path that contains the problem, e.g. `"annotation[2].fieldSource"`.
    pub path: String,
    /// Severity: `Error` = invalid config; `Warning` = suspicious but not fatal.
    pub severity: Severity,
}

/// Severity of a [`ValidationError`].
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Severity {
    /// The annotation file is invalid and cannot be used.
    Error,
    /// A field is present but will be silently ignored by the runtime.
    Warning,
}

impl fmt::Display for ValidationError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let tag = match self.severity {
            Severity::Error => "ERROR",
            Severity::Warning => "WARN ",
        };
        write!(f, "[{tag}] {}: {}", self.path, self.message)
    }
}

/// Read a YAML annotation file, parse, and validate the resulting [`AnnotationConfig`].
///
/// Opens the file at `path`, parses it directly via [`yaml_serde::from_reader`]
/// (no intermediate `String` allocated), and runs validation.
///
/// The `base_dir` used to resolve relative `fileMapping` paths is derived from
/// `path.parent()` — matching the Python OpenVariant behaviour where
/// `fileMapping` is resolved relative to the annotation file's location. If
/// `path` has no parent component (e.g. `"config.yaml"`), the current directory
/// (`.`) is used.
///
/// Validation runs in two passes:
///
/// 1. **Syntax + structural** — `yaml_serde` rejects malformed YAML, unknown
///    enum variants, and missing required fields. Because `AnnotationEntry`
///    is a tagged enum, required fields are enforced per-variant at parse
///    time — no separate validator check is needed for them.
/// 2. **Semantic + resource** — blank `field` names, empty `pattern`/`annotation`
///    lists, duplicate `field` names, and missing `fileMapping` files are
///    flagged as errors.
///
/// # Example
///
/// ```no_run
/// use openvariant::annotation::validator::parse_and_validate;
/// use std::path::Path;
///
/// let config = parse_and_validate(Path::new("annotation.yaml"))?;
/// # Ok::<(), Vec<openvariant::annotation::validator::ValidationError>>(())
/// ```
///
/// [`yaml_serde::from_reader`]: https://docs.rs/yaml_serde/latest/yaml_serde/fn.from_reader.html
pub fn parse_and_validate(path: &Path) -> Result<AnnotationConfig, Vec<ValidationError>> {
    let file = std::fs::File::open(path).map_err(|e| {
        vec![ValidationError {
            message: format!("Unable to open annotation file — {e}"),
            path: path.display().to_string(),
            severity: Severity::Error,
        }]
    })?;

    // Pass 1 — syntax + structural (serde)
    let config: AnnotationConfig = yaml_serde::from_reader(file).map_err(|e| {
        // yaml_serde errors include line/column information in their Display.
        vec![ValidationError {
            message: format!("YAML parse error — {e}"),
            path: "<document>".into(),
            severity: Severity::Error,
        }]
    })?;

    // Pass 2 — semantic + resource
    let base_dir = path.parent().unwrap_or(Path::new("."));
    let diagnostics = validate_config(&config, base_dir);

    let has_errors = diagnostics.iter().any(|d| d.severity == Severity::Error);

    if has_errors {
        Err(diagnostics)
    } else {
        Ok(config)
    }
}

/// Validate an already-deserialised [`AnnotationConfig`].
///
/// `base_dir` is used to resolve relative `fileMapping` paths in `Mapping` entries.
///
/// Returns *all* diagnostics (errors and warnings) found.
/// An empty `Vec<ValidationError>` means the configuration is fully valid, no errors found.
pub fn validate_config(config: &AnnotationConfig, base_dir: &Path) -> Vec<ValidationError> {
     let mut diags: Vec<ValidationError> = Vec::new();

     if config.pattern.is_empty() {
        diags.push(err(
            "<document>",
            "`pattern` is empty — at least one entry is required",
        ));
        // Remaining checks are per-entry; bail early.
        return diags;
    }

    // Empty file check — this is technically valid YAML but not a valid annotation config.
    if config.annotation.is_empty() {
        diags.push(err(
            "<document>",
            "`annotation` list is empty — at least one entry is required",
        ));
        // Remaining checks are per-entry; bail early.
        return diags;
    }

    // Validate annotation entries: blank `field` names, duplicates, and resource existence.
    // Per-variant required fields are already enforced by serde (tagged enum).
    let mut seen_fields: std::collections::HashSet<&str> = std::collections::HashSet::new();
    for (i, entry) in config.annotation.iter().enumerate() {
        let base = format!("annotation[{i}]");

        // `field` is required by serde; we check for an accidental empty string.
        if entry.field().trim().is_empty() {
             diags.push(err(&base, "`field` must not be blank"));
         }

        if !seen_fields.insert(entry.field()) {
            diags.push(ValidationError {
                message: format!(
                    "duplicate `field` name `{}` — each annotation field must be unique",
                    entry.field()
                ),
                path: "<document>.annotation".into(),
                severity: Severity::Error,
            });
        }

        if let AnnotationEntry::Filename { regex, .. }
        | AnnotationEntry::Dirname { regex, .. } = entry
        {
            if let Some(r) = regex.as_deref() {
                if !r.trim().is_empty() && Regex::new(r).is_err() {
                    diags.push(err(
                        &format!("{base}.regex"),
                        &format!(
                            "invalid `regex` for `{}` entry: {r}",
                            entry.type_name()
                        ),
                    ));
                }
            }
        }

        // Check that `fileMapping` files exist on disk.
        if let AnnotationEntry::Mapping { file_mapping, .. } = entry {
            if file_mapping.trim().is_empty() {
                diags.push(err(
                    &format!("{base}.fileMapping"),
                    "`fileMapping` must not be blank",
                ));
            } else if !base_dir.join(file_mapping).is_file() {
                diags.push(err(
                    &format!("{base}.fileMapping"),
                    &format!("`fileMapping` file not found: {file_mapping}"),
                ));
            }
        }

        // Check that `function` fields contain a lambda expression.
        let func: Option<&str> = match entry {
            AnnotationEntry::Internal { function, .. }
            | AnnotationEntry::Dirname { function, .. }
            | AnnotationEntry::Filename { function, .. } => function.as_deref(),
            AnnotationEntry::Static { .. }
            | AnnotationEntry::Plugin { .. }
            | AnnotationEntry::Mapping { .. } => None,
        };
        if let Some(f) = func {
            if !is_lambda(f) {
                diags.push(err(
                    &format!("{base}.function"),
                    "`function` must be a lambda expression (e.g. \"lambda x: x.upper()\")",
                ));
             }
         }
     }

    // Validate Exclude entries
    for (i, excl) in config.exclude.iter().enumerate() {
        if excl.field.trim().is_empty() {
            diags.push(err(&format!("exclude[{i}]"), "`field` must not be blank"));
        }
    }

    diags
}

fn err(path: &str, message: &str) -> ValidationError {
    ValidationError {
        message: message.into(),
        path: path.into(),
        severity: Severity::Error,
    }
}

/// Check that `s` looks like a Python lambda expression.
///
/// Accepts strings of the form `lambda <params>: <body>`, e.g.
/// `lambda x: x.upper()` or `lambda c, d: c + d`.
fn is_lambda(s: &str) -> bool {
    let s = s.trim();
    if !s.starts_with("lambda ") {
        return false;
    }
    let rest = &s[7..]; // after "lambda "
    let colon_pos = match rest.find(':') {
        Some(pos) => pos,
        None => return false,
    };
    !rest[..colon_pos].trim().is_empty() && !rest[colon_pos + 1..].trim().is_empty()
 }
