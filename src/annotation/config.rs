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


/// AnnotationDelimiter

#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum AnnotationDelimiter {
    /// Tab character (`\t`).
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

#[derive(Debug, Clone, PartialEq, Eq, Hash, Default, Serialize, Deserialize)]
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
/// A tagged enum: the YAML `type` key selects the variant, and each variant
/// carries only the fields relevant to that annotation strategy. Required
/// fields are enforced by serde at parse time — a missing required field
/// produces a deserialization error immediately.
#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(tag = "type", rename_all = "lowercase")]
pub enum AnnotationEntry {
    /// Assign a fixed literal value to every output record.
    ///
    /// ```yaml
    /// - type: static
    ///   field: GENOME_BUILD
    ///   value: GRCh38
    /// ```
    Static {
        /// Output column name that will receive the derived value.
        field: String,
        /// Literal value to assign (any YAML scalar or structure).
        value: yaml_serde::Value,
    },

    /// Copy the value from another column already present in the same record.
    ///
    /// ```yaml
    /// - type: internal
    ///   field: ALT_ALLELE
    ///   fieldSource: ALT
    /// ```
    Internal {
        field: String,
        #[serde(rename = "fieldSource")]
        field_source: String,
        #[serde(default, skip_serializing_if = "Option::is_none")]
        value: Option<yaml_serde::Value>,
        #[serde(default, skip_serializing_if = "Option::is_none")]
        function: Option<String>,
    },

    /// Set the field to the **directory name** of the source file being processed.
    ///
    /// ```yaml
    /// - type: dirname
    ///   field: STUDY_DIR
    /// ```
    Dirname {
        field: String,
        #[serde(default, skip_serializing_if = "Option::is_none")]
        function: Option<String>,
        #[serde(default, skip_serializing_if = "Option::is_none")]
        regex: Option<String>,
    },

    /// Set the field to the **filename** (no path) of the source file being processed.
    ///
    /// ```yaml
    /// - type: filename
    ///   field: SOURCE_FILE
    /// ```
    Filename {
        field: String,
        #[serde(default, skip_serializing_if = "Option::is_none")]
        function: Option<String>,
        #[serde(default, skip_serializing_if = "Option::is_none")]
        regex: Option<String>,
    },

    /// Delegate value computation to an external Python plugin function.
    ///
    /// ```yaml
    /// - type: plugin
    ///   field: COMPUTED_SCORE
    ///   plugin: my_package.scoring
    /// ```
    Plugin {
        field: String,
        /// Dotted Python module path of the plugin (e.g. `my_pkg.scoring`).
        plugin: String,
    },

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
    Mapping {
        field: String,
        #[serde(rename = "fieldSource")]
        field_source: String,
        #[serde(rename = "fileMapping")]
        file_mapping: String,
        #[serde(rename = "fieldMapping")]
        field_mapping: String,
        #[serde(rename = "fieldValue")]
        field_value: String,
    },
}

impl AnnotationEntry {
    /// Returns the output column name for this entry, regardless of variant.
    pub fn field(&self) -> &str {
        match self {
            AnnotationEntry::Static { field, .. }
            | AnnotationEntry::Internal { field, .. }
            | AnnotationEntry::Dirname { field, .. }
            | AnnotationEntry::Filename { field, .. }
            | AnnotationEntry::Plugin { field, .. }
            | AnnotationEntry::Mapping { field, .. } => field,
        }
    }

    /// Returns the annotation strategy name (e.g. `"static"`, `"mapping"`).
    pub fn type_name(&self) -> &'static str {
        match self {
            AnnotationEntry::Static { .. } => "static",
            AnnotationEntry::Internal { .. } => "internal",
            AnnotationEntry::Dirname { .. } => "dirname",
            AnnotationEntry::Filename { .. } => "filename",
            AnnotationEntry::Plugin { .. } => "plugin",
            AnnotationEntry::Mapping { .. } => "mapping",
        }
    }
}

impl fmt::Display for AnnotationEntry {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}(field={}", self.type_name(), self.field())?;
        match self {
            AnnotationEntry::Static { value, .. } => {
                let v = yaml_serde::to_string(value).unwrap_or_default();
                write!(f, ", value={})", v.trim())
            }
            AnnotationEntry::Internal {
                field_source,
                value,
                function,
                ..
            } => {
                write!(f, ", fieldSource={field_source}")?;
                if let Some(v) = value {
                    let s = yaml_serde::to_string(v).unwrap_or_default();
                    write!(f, ", value={}", s.trim())?;
                }
                if let Some(func) = function {
                    write!(f, ", function={func}")?;
                }
                write!(f, ")")
            }
            AnnotationEntry::Dirname {
                function, regex, ..
            }
            | AnnotationEntry::Filename {
                function, regex, ..
            } => {
                if let Some(func) = function {
                    write!(f, ", function={func}")?;
                }
                if let Some(r) = regex {
                    write!(f, ", regex={r}")?;
                }
                write!(f, ")")
            }
            AnnotationEntry::Plugin { plugin, .. } => {
                write!(f, ", plugin={plugin})")
            }
            AnnotationEntry::Mapping {
                field_source,
                file_mapping,
                field_mapping,
                field_value,
                ..
            } => {
                write!(
                    f,
                    ", fieldSource={field_source}, fileMapping={file_mapping}, fieldMapping={field_mapping}, fieldValue={field_value})"
                )
            }
        }
    }
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

    /// Field delimiter. Optional — when omitted in the YAML it is `None`.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub delimiter: Option<AnnotationDelimiter>,

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
