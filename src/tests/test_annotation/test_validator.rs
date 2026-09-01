use crate::annotation::AnnotationConfig;
use crate::annotation::validator::{
    Severity, ValidationError, parse_and_validate, validate_config,
};
use std::path::Path;

/// Test helper — parse a YAML string and validate with the current directory
/// as `base_dir`. Uses `yaml_serde::from_str` + `validate_config` directly, so
/// tests can work with inline strings without writing temp files.
fn parse(yaml: &str) -> Result<AnnotationConfig, Vec<ValidationError>> {
    let config: AnnotationConfig = yaml_serde::from_str(yaml).map_err(|e| {
        vec![ValidationError {
            message: format!("YAML parse error — {e}"),
            path: "<document>".into(),
            severity: Severity::Error,
        }]
    })?;
    let diagnostics = validate_config(&config, Path::new("."));
    let has_errors = diagnostics.iter().any(|d| d.severity == Severity::Error);
    if has_errors {
        Err(diagnostics)
    } else {
        Ok(config)
    }
}

// Test parse_and_validate, non-error cases

#[test]
fn validate_static_entry_ok() {
    let yaml = "pattern:\n  - \"**/*.vcf.gz\"\nannotation:\n  - type: static\n    field: BUILD\n    value: GRCh38\n";
    assert!(parse(yaml).is_ok());
}

#[test]
fn validate_internal_entry_ok() {
    let yaml = "pattern:\n  - \"**/*.vcf.gz\"\nannotation:\n  - type: internal\n    field: COPY\n    fieldSource: REF\n";
    assert!(parse(yaml).is_ok());
}

#[test]
fn validate_dirname_entry_ok() {
    let yaml = "pattern:\n  - \"**/*.vcf.gz\"\nannotation:\n  - type: dirname\n    field: DIR\n";
    assert!(parse(yaml).is_ok());
}

#[test]
fn validate_filename_entry_ok() {
    let yaml = "pattern:\n  - \"**/*.vcf.gz\"\nannotation:\n  - type: filename\n    field: FILE\n";
    assert!(parse(yaml).is_ok());
}

#[test]
fn validate_plugin_entry_ok() {
    let yaml = "pattern:\n  - \"**/*.vcf.gz\"\nannotation:\n  - type: plugin\n    field: S\n    plugin: pkg.mod\n";
    assert!(parse(yaml).is_ok());
}

#[test]
fn validate_mapping_entry_ok() {
    // Create a temp file so the fileMapping check passes.
    let map_file = std::env::temp_dir().join("openvariant_test_mapping_ok.tsv");
    std::fs::write(&map_file, "KEY\tVALUE\n").unwrap();

    let yaml = format!(
        r#"
pattern:
  - "**/*.vcf.gz"
annotation:
  - type: mapping
    field: GENE
    fieldSource: ENSEMBL_ID
    fileMapping: {}
    fieldMapping: KEY
    fieldValue: VAL
"#,
        map_file.to_str().unwrap()
    );
    assert!(parse(&yaml).is_ok());

    std::fs::remove_file(&map_file).ok();
}

// Test parse_and_validate, error cases
#[test]
fn validate_empty_pattern_list_is_error() {
    let yaml = "pattern: []\nannotation: []\n";
    let errs = parse(yaml).unwrap_err();
    assert!(errs.iter().any(|e| e.severity == Severity::Error));
}

#[test]
fn validate_wrong_type_pattern_list_is_error() {
    let yaml = "pattern: \"*.vcf\"\nannotation: []\n";
    let errs = parse(yaml).unwrap_err();
    assert!(errs.iter().any(|e| e.severity == Severity::Error));
}

#[test]
fn validate_empty_annotation_list_is_error() {
    let yaml = "pattern:\n  - \"**/*.vcf.gz\"\nannotation: []\n";
    let errs = parse(yaml).unwrap_err();
    assert!(errs.iter().any(|e| e.severity == Severity::Error));
}

#[test]
fn validate_static_missing_value_is_error() {
    let yaml = "pattern:\n  - \"**/*.vcf.gz\"\nannotation:\n  - type: static\n    field: BUILD\n";
    let errs = parse(yaml).unwrap_err();
    // With the tagged enum, serde rejects missing `value` for Static.
    assert!(
        errs.iter()
            .any(|e| e.message.contains("YAML parse error") && e.message.contains("value"))
    );
}

#[test]
#[allow(non_snake_case)]
fn validate_internal_missing_fieldSource_is_error() {
    let yaml = "pattern:\n  - \"**/*.vcf.gz\"\nannotation:\n  - type: internal\n    field: X\n";
    let errs = parse(yaml).unwrap_err();
    assert!(
        errs.iter()
            .any(|e| e.message.contains("YAML parse error") && e.message.contains("fieldSource"))
    );
}

#[test]
fn validate_non_lambda_function_is_error() {
    // `function` is a lambda field for Internal (not Plugin). A non-lambda
    // value should be rejected.
    let yaml = "pattern:\n  - \"**/*.vcf.gz\"\nannotation:\n  - type: internal\n    field: S\n    fieldSource: REF\n    function: not_a_lambda\n";
    let errs = parse(yaml).unwrap_err();
     assert!(
        errs.iter().any(|e| e.message.contains("must be a lambda")),
        "expected a lambda error, got: {errs:?}"
     );
 }

#[test]
fn validate_lambda_function_in_internal_is_ok() {
    let yaml = "pattern:\n  - \"**/*.vcf.gz\"\nannotation:\n  - type: internal\n    field: COPY\n    fieldSource: REF\n    function: \"lambda c: c.upper().replace('CHR', '')\"\n";
    assert!(parse(yaml).is_ok());
}

#[test]
fn validate_lambda_function_in_filename_is_ok() {
    let yaml = "pattern:\n  - \"**/*.vcf.gz\"\nannotation:\n  - type: filename\n    field: FILE\n    function: 'lambda x: \"{}\".format(x.lower()[:-4])'\n";
    assert!(parse(yaml).is_ok());
}

 #[test]
 fn validate_mapping_missing_keys_are_errors() {
     let yaml = "pattern:\n  - \"**/*.vcf.gz\"\nannotation:\n  - type: mapping\n    field: G\n    fileMapping: /f.tsv\n";
    let errs = parse(yaml).unwrap_err();
    // serde reports the first missing field; we just check it's a parse error.
    assert!(errs.iter().any(|e| e.message.contains("YAML parse error")));
 }

#[test]
fn validate_blank_field_is_error() {
    let yaml = "pattern:\n  - \"**/*.vcf.gz\"\nannotation:\n  - type: dirname\n    field: ''\n";
     let errs = parse(yaml).unwrap_err();
    assert!(
        errs.iter()
            .any(|e| e.message.contains("`field` must not be blank"))
    );
}

#[test]
fn validate_duplicate_field_names_are_errors() {
    let yaml = r#"
pattern:
  - "**/*.vcf.gz"
annotation:
  - type: dirname
    field: DIR
  - type: filename
    field: DIR
"#;
    let errs = parse(yaml).unwrap_err();
    assert!(
        errs.iter()
            .any(|e| e.message.contains("duplicate `field` name"))
    );
}

#[test]
fn validate_syntax_error_returned_as_parse_error() {
    let yaml = "annotation:\n  - type: [\nbad yaml";
    let errs = parse(yaml).unwrap_err();
    assert!(errs[0].message.contains("YAML parse error"));
}

#[test]
fn validate_unused_fields_not_errors() {
    // `fieldSource` is irrelevant for `static` entries, but it should not make an
    // otherwise-valid config fail validation.
    let yaml = r#"
pattern:
  - "**/*.vcf.gz"
annotation:
  - type: static
    field: BUILD
    value: GRCh38
    fieldSource: SPURIOUS
"#;
    assert!(parse(yaml).is_ok());
}

#[test]
fn validate_formatting_errors_returned_as_parse_errors() {
    let yaml = r#"
    pattern:
  - "**/*.vcf.gz"
annotation:
  - type: dirname
    field: DIR
"#;
    let errs = parse(yaml).unwrap_err();
    assert!(errs[0].message.contains("YAML parse error"));
}

#[test]
fn validate_formatting_errors_returned_as_parse_errors_annotation_entry() {
    let yaml = r#"
pattern:
  - "**/*.vcf.gz"
annotation:
        - type: dirname
    field: DIR
"#;
    let errs = parse(yaml).unwrap_err();
    assert!(errs[0].message.contains("YAML parse error"));
}

// --- fileMapping existence (integrated into validate_config) ---

#[test]
fn validate_mapping_missing_file_is_error() {
    let yaml = r#"
pattern:
  - "**/*.vcf.gz"
annotation:
  - type: mapping
    field: GENE
    fieldSource: ENSEMBL_ID
    fileMapping: /nonexistent/path/map.tsv
    fieldMapping: KEY
    fieldValue: VAL
"#;
    let errs = parse(yaml).unwrap_err();
    assert!(
        errs.iter()
            .any(|e| e.message.contains("fileMapping") && e.message.contains("not found")),
        "expected a 'not found' error, got: {errs:?}"
    );
}

#[test]
fn validate_mapping_relative_path_resolved_against_base_dir() {
    let dir = std::env::temp_dir();
    let map_file = dir.join("openvariant_test_rel_mapping.tsv");
    std::fs::write(&map_file, "KEY\tVALUE\n").unwrap();

    let yaml = r#"
pattern:
  - "**/*.vcf.gz"
annotation:
  - type: mapping
    field: GENE
    fieldSource: ENSEMBL_ID
    fileMapping: openvariant_test_rel_mapping.tsv
    fieldMapping: KEY
    fieldValue: VAL
"#;

    // With the correct base_dir, the file is found → no errors.
    let config: AnnotationConfig = yaml_serde::from_str(yaml).unwrap();
    let diags = validate_config(&config, &dir);
    assert!(!diags.iter().any(|d| d.severity == Severity::Error));

    // With the wrong base_dir, the file is not found → error.
    let diags = validate_config(&config, Path::new("/nonexistent"));
    assert!(
        diags.iter().any(|e| e.message.contains("not found")),
        "expected a 'not found' error, got: {diags:?}"
    );

    std::fs::remove_file(&map_file).ok();
}

// --- parse_and_validate with a File reader ---

#[test]
fn parse_and_validate_from_file_resolves_relative_filemapping() {
    // The annotation YAML references `map.tsv` by relative path. `parse_and_validate`
    // derives `base_dir` from the YAML file's parent directory, so the mapping
    // file is found without the caller passing a base_dir.
    let dir = std::env::temp_dir().join("openvariant_test_pavf");
    std::fs::create_dir_all(&dir).unwrap();

    let map_file = dir.join("map.tsv");
    std::fs::write(&map_file, "KEY\tVALUE\n").unwrap();

    let yaml_file = dir.join("annotation.yaml");
    std::fs::write(
        &yaml_file,
        r#"
pattern:
  - "**/*.vcf.gz"
annotation:
  - type: mapping
    field: GENE
    fieldSource: ENSEMBL_ID
    fileMapping: map.tsv
    fieldMapping: KEY
    fieldValue: VAL
"#,
    )
    .unwrap();

    assert!(parse_and_validate(&yaml_file).is_ok());

    std::fs::remove_file(&map_file).ok();
    std::fs::remove_file(&yaml_file).ok();
    std::fs::remove_dir(&dir).ok();
}