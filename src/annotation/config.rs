//! Core configuration types for OpenVariant annotation.
//!
//! This file defines the core configuration types for OpenVariant annotation, including
//! `AnnotationType`, `AnnotationDelimiter`, `AnnotationFormat`, `AnnotationEntry`,
//! `ExcludeEntry`, and `AnnotationConfig`. These types are designed to be serde-compatible,
//! allowing for easy serialisation and deserialisation to and from YAML annotation definition files. The structures defined here mirror the
//! expected structure of the YAML files, enabling seamless integration with the OpenVariant annotation system.

use serde::{Deserialize, Serialize};
use std::fmt;

/// Constants
pub const ANNOTATION_EXTENSION: &str = "yaml";
pub const DEFAULT_COLUMNS: &[&str] = &[];
pub const DEFAULT_RECURSIVE: bool = false;

/// AnnotationType

#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum AnnotationType {
    /// Assign a fixed literal value to every output record.
    ///
    /// ```yaml
    /// - type: static
    ///   field: GENOME_BUILD
    ///   value: GRCh38
    /// ```
    Static,

    /// Copy the value from another column already present in the same record.
    ///
    /// ```yaml
    /// - type: internal
    ///   field: ALT_ALLELE
    ///   fieldSource: ALT
    /// ```
    Internal,

    /// Set the field to the **directory name** of the source file being processed.
    ///
    /// ```yaml
    /// - type: dirname
    ///   field: STUDY_DIR
    /// ```
    Dirname,

    /// Set the field to the **filename** (no path) of the source file being processed.
    ///
    /// ```yaml
    /// - type: filename
    ///   field: SOURCE_FILE
    /// ```
    Filename,

    /// Delegate value computation to an external Python plugin function.
    ///
    /// ```yaml
    /// - type: plugin
    ///   field: COMPUTED_SCORE
    ///   plugin: my_package.scoring
    ///   function: compute_score
    /// ```
    Plugin,

    /// Look up the value in an external delimited mapping file.
    ///
    /// ```yaml
    /// - type: mapping
    ///   field: GENE_NAME
    ///   fieldSource: ENSEMBL_ID
    ///   fileMapping: /data/gene_map.tsv
    ///   fieldMapping: ENSEMBL_ID
    ///   fieldValue: GENE_SYMBOL
    /// ```
    Mapping,
}

impl fmt::Display for AnnotationType {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let s = match self {
            AnnotationType::Static => "static",
            AnnotationType::Internal => "internal",
            AnnotationType::Dirname => "dirname",
            AnnotationType::Filename => "filename",
            AnnotationType::Plugin => "plugin",
            AnnotationType::Mapping => "mapping",
        };
        write!(f, "{s}")
    }
}

/// AnnotationDelimiter

#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize, Default)]
pub enum AnnotationDelimiter {
    /// Tab character (`\t`).
    #[default]
    T,
    /// Comma character (`,`).
    C,
}

impl AnnotationDelimiter {
    /// Returns the delimiter as a `char`.
    pub fn as_char(&self) -> char {
        match self {
            AnnotationDelimiter::T => '\t',
            AnnotationDelimiter::C => ',',
        }
    }
}

impl fmt::Display for AnnotationDelimiter {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let s = match self {
            AnnotationDelimiter::T => "T",
            AnnotationDelimiter::C => "C",
        };
        write!(f, "{s}")
    }
}

/// AnnotationFormat

#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize, Default)]
pub enum AnnotationFormat {
    /// Tab-Separated Values — field separator is `\t`.
    #[serde(rename = "TSV")]
    #[default]
    Tsv,
    /// Comma-Separated Values — field separator is `,`.
    #[serde(rename = "CSV")]
    Csv,
}

impl AnnotationFormat {
    /// Returns the field separator character for this format.
    pub fn separator(&self) -> char {
        match self {
            AnnotationFormat::Tsv => '\t',
            AnnotationFormat::Csv => ',',
        }
    }
}

impl fmt::Display for AnnotationFormat {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let s = match self {
            AnnotationFormat::Tsv => "TSV",
            AnnotationFormat::Csv => "CSV",
        };
        write!(f, "{s}")
    }
}

/// AnnotationEntry

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct AnnotationEntry {
    /// The annotation strategy to apply (required).
    #[serde(rename = "type")]
    pub annotation_type: AnnotationType,

    /// Output column name that will receive the derived value (required, non-blank).
    pub field: String,

    /// *(static, internal)* Literal value to assign. Accepts any YAML scalar or
    /// structure (`string`, `int`, `float`, `bool`, `null`).
    #[serde(skip_serializing_if = "Option::is_none")]
    pub value: Option<yaml_serde::Value>,

    /// *(internal, mapping)* Name of the source column to copy from.
    #[serde(rename = "fieldSource", skip_serializing_if = "Option::is_none")]
    pub field_source: Option<String>,

    /// *(internal, filename, dirname)* Dotted Python module path of the plugin (e.g. `my_pkg.scoring`).
    #[serde(skip_serializing_if = "Option::is_none")]
    pub plugin: Option<String>,

    /// *(plugin)* Lambda function that will be executed.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub function: Option<String>,

    /// Optional regular-expression applied to the derived value before storage.
    /// The first capture group is used when present.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub regex: Option<String>,

    /// *(mapping)* Path to the external lookup file.
    #[serde(rename = "fileMapping", skip_serializing_if = "Option::is_none")]
    pub file_mapping: Option<String>,

    /// *(mapping)* Column in the mapping file used as the lookup key.
    #[serde(rename = "fieldMapping", skip_serializing_if = "Option::is_none")]
    pub field_mapping: Option<String>,

    /// *(mapping)* Column in the mapping file whose value is returned.
    #[serde(rename = "fieldValue", skip_serializing_if = "Option::is_none")]
    pub field_value: Option<String>,
}

/// ExcludeEntry

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct ExcludeEntry {
    /// The column name to exclude values from.
    pub field: String,
    /// The value that triggers exclusion (any YAML scalar).
    pub value: yaml_serde::Value,
}

/// AnnotationConfig

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct AnnotationConfig {
    /// Glob pattern used to discover source files (e.g. `"**/*.vcf.gz"`).
    #[serde(default)]
    pub pattern: Vec<String>,

    /// Recurse into sub-directories when scanning for source files.
    /// Default: `false`.
    #[serde(default)]
    pub recursive: bool,

    /// Output file format. Default: `TSV`.
    #[serde(default)]
    pub format: AnnotationFormat,

    /// Field delimiter. Default: `T` (tab).
    #[serde(default)]
    pub delimiter: AnnotationDelimiter,

    /// Ordered list of columns to include in the output.
    /// Empty list means "all columns".
    #[serde(default)]
    pub columns: Vec<String>,

    /// The annotation rules to apply, in order.
    #[serde(default)]
    pub annotation: Vec<AnnotationEntry>,

    /// Records matching **any** exclude predicate are dropped.
    #[serde(default)]
    pub exclude: Vec<ExcludeEntry>,
}
