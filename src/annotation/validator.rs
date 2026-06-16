//! Annotation validators for OpenVariant annotation.
//!
//! This module provides validation logic for ensuring that annotation configurations are valid and consistent.
//! It includes functions to validate annotation types, delimiters, formats, and overall configuration structures.
//! The validators are designed to be used during the deserialization process of YAML annotation definition files,
//! providing immediate feedback on any issues with the configuration. This helps maintain the integrity of the annotation system and
//! prevents runtime errors due to misconfigurations.

use std::fmt;

use super::config::{AnnotationConfig, AnnotationType};

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

/// Parse YAML text and validate the resulting [`AnnotationConfig`].
///
/// Validation runs in three passes:
///
/// 1. **Syntax** — `serde_yaml` rejects malformed YAML and unknown enum
///    variants, reporting the exact line/column of the problem.
/// 2. **Structural** — missing or blank required fields (`field`, type-specific
///    keys) and an empty `annotation` list are flagged as errors.
/// 3. **Semantic** — keys that exist but are irrelevant for the chosen
///    annotation type are not reported, and don't cause and error.
///
/// # Returns
///
/// - `Ok(config)` — the config is structurally and semantically valid.
///   Warnings are *not* returned; use [`validate_config`] directly to
///   inspect them.
/// - `Err(errors)` — one or more `Severity::Error` diagnostics (warnings
///   included for context).
pub fn parse_and_validate(yaml: &str) -> Result<AnnotationConfig, Vec<ValidationError>> {
    // Pass 1 — syntax + structural (serde)
    let config: AnnotationConfig = yaml_serde::from_str(yaml).map_err(|e| {
        // serde_yaml errors include line/column information in their Display.
        vec![ValidationError {
            message: format!("YAML parse error — {e}"),
            path: "<document>".into(),
            severity: Severity::Error,
        }]
    })?;

    // Pass 2 + 3 — structural + semantic
    let diagnostics = validate_config(&config);
    let has_errors = diagnostics.iter().any(|d| d.severity == Severity::Error);

    if has_errors {
        Err(diagnostics)
    } else {
        Ok(config)
    }
}

/// Validate an already-deserialised [`AnnotationConfig`].
///
/// Returns *all* diagnostics (errors and warnings) found.
/// An empty `Vec<ValidationError>` means the configuration is fully valid, no errors found.
pub fn validate_config(config: &AnnotationConfig) -> Vec<ValidationError> {
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

    // Validate Annotation entries
    for (i, entry) in config.annotation.iter().enumerate() {
        let base = format!("annotation[{i}]");

        // `field` must always be present and non-blank (serde already
        // ensures it exists; we check for an accidental empty string).
        if entry.field.trim().is_empty() {
            diags.push(err(&base, "`field` must not be blank"));
        }

        match &entry.annotation_type {
            // Static
            AnnotationType::Static => {
                // Check that `value` is present (can be any YAML scalar or structure, so we don't require a specific type).
                if entry.value.is_none() {
                    diags.push(err(&base, "`value` is required but missing"));
                }
            }

            // Internal
            AnnotationType::Internal => {
                check_required_str(
                    &base,
                    "fieldSource",
                    entry.field_source.as_deref(),
                    &mut diags,
                );
            }

            // Dirname / Filenanme
            AnnotationType::Dirname | AnnotationType::Filename => {}

            // Plugin
            AnnotationType::Plugin => {
                check_required_str(&base, "plugin", entry.plugin.as_deref(), &mut diags);
                check_required_str(&base, "function", entry.function.as_deref(), &mut diags);
            }

            // Mapping
            AnnotationType::Mapping => {
                check_required_str(
                    &base,
                    "fieldSource",
                    entry.field_source.as_deref(),
                    &mut diags,
                );
                check_required_str(
                    &base,
                    "fileMapping",
                    entry.file_mapping.as_deref(),
                    &mut diags,
                );
                check_required_str(
                    &base,
                    "fieldMapping",
                    entry.field_mapping.as_deref(),
                    &mut diags,
                );
                check_required_str(
                    &base,
                    "fieldValue",
                    entry.field_value.as_deref(),
                    &mut diags,
                );
            }
        }
    }

    // Validate Exclude entries
    for (i, excl) in config.exclude.iter().enumerate() {
        if excl.field.trim().is_empty() {
            diags.push(err(&format!("exclude[{i}]"), "`field` must not be blank"));
        }
    }

    // Validate Column name uniqueness
    let mut seen_fields: std::collections::HashSet<&str> = std::collections::HashSet::new();
    for entry in &config.annotation {
        if !seen_fields.insert(entry.field.as_str()) {
            diags.push(ValidationError {
                message: format!(
                    "duplicate `field` name `{}` — each annotation field must be unique",
                    entry.field
                ),
                path: "<document>.annotation".into(),
                severity: Severity::Error,
            });
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

/// Emit an error if `value` is `None` or blank.
fn check_required_str(
    base: &str,
    key: &str,
    value: Option<&str>,
    diags: &mut Vec<ValidationError>,
) {
    match value {
        None => diags.push(err(base, &format!("`{key}` is required but missing"))),
        Some(v) if v.trim().is_empty() => {
            diags.push(err(base, &format!("`{key}` must not be blank")))
        }
        _ => {}
    }
}
