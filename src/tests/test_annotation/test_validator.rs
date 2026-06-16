use crate::annotation::validator::{parse_and_validate, Severity};

// Test parse_and_validate, non-error cases

#[test]
fn validate_static_entry_ok() {
    let yaml = "pattern:\n  - \"**/*.vcf.gz\"\nannotation:\n  - type: static\n    field: BUILD\n    value: GRCh38\n";
    assert!(parse_and_validate(yaml).is_ok());
}

#[test]
fn validate_internal_entry_ok() {
    let yaml = "pattern:\n  - \"**/*.vcf.gz\"\nannotation:\n  - type: internal\n    field: COPY\n    fieldSource: REF\n";
    assert!(parse_and_validate(yaml).is_ok());
}

#[test]
fn validate_dirname_entry_ok() {
    let yaml = "pattern:\n  - \"**/*.vcf.gz\"\nannotation:\n  - type: dirname\n    field: DIR\n";
    assert!(parse_and_validate(yaml).is_ok());
}

#[test]
fn validate_filename_entry_ok() {
    let yaml = "pattern:\n  - \"**/*.vcf.gz\"\nannotation:\n  - type: filename\n    field: FILE\n";
    assert!(parse_and_validate(yaml).is_ok());
}

#[test]
fn validate_plugin_entry_ok() {
    let yaml = "pattern:\n  - \"**/*.vcf.gz\"\nannotation:\n  - type: plugin\n    field: S\n    plugin: pkg.mod\n    function: fn_name\n";
    assert!(parse_and_validate(yaml).is_ok());
}

#[test]
fn validate_mapping_entry_ok() {
    let yaml = r#"
pattern:
  - "**/*.vcf.gz"
annotation:
  - type: mapping
    field: GENE
    fieldSource: ENSEMBL_ID
    fileMapping: /data/map.tsv
    fieldMapping: KEY
    fieldValue: VAL
"#;
    assert!(parse_and_validate(yaml).is_ok());
}


// Test parse_and_validate, error cases
#[test]
fn validate_empty_pattern_list_is_error() {
    let yaml = "pattern: []\nannotation: []\n";
    let errs = parse_and_validate(yaml).unwrap_err();
    assert!(errs.iter().any(|e| e.severity == Severity::Error));
}

#[test]
fn validate_wrong_type_pattern_list_is_error() {
    let yaml = "pattern: \"*.vcf\"\nannotation: []\n";
    let errs = parse_and_validate(yaml).unwrap_err();
    assert!(errs.iter().any(|e| e.severity == Severity::Error));
}

#[test]
fn validate_empty_annotation_list_is_error() {
    let yaml = "pattern:\n  - \"**/*.vcf.gz\"\nannotation: []\n";
    let errs = parse_and_validate(yaml).unwrap_err();
    assert!(errs.iter().any(|e| e.severity == Severity::Error));
}

#[test]
fn validate_static_missing_value_is_error() {
    let yaml = "pattern:\n  - \"**/*.vcf.gz\"\nannotation:\n  - type: static\n    field: BUILD\n";
    let errs = parse_and_validate(yaml).unwrap_err();
    assert!(errs.iter().any(|e| e.message.contains("`value` is required")));    }

#[test]
#[allow(non_snake_case)]
fn validate_internal_missing_fieldSource_is_error() {
    let yaml = "pattern:\n  - \"**/*.vcf.gz\"\nannotation:\n  - type: internal\n    field: X\n";
    let errs = parse_and_validate(yaml).unwrap_err();
    assert!(errs.iter().any(|e| e.message.contains("`fieldSource` is required")));
}

#[test]
fn validate_plugin_missing_function_is_error() {
    let yaml = "pattern:\n  - \"**/*.vcf.gz\"\nannotation:\n  - type: plugin\n    field: S\n    plugin: mod\n";
    let errs = parse_and_validate(yaml).unwrap_err();
    assert!(errs.iter().any(|e| e.message.contains("`function` is required")));
}

#[test]
fn validate_mapping_missing_keys_are_errors() {
    let yaml = "pattern:\n  - \"**/*.vcf.gz\"\nannotation:\n  - type: mapping\n    field: G\n    fileMapping: /f.tsv\n";
    let errs = parse_and_validate(yaml).unwrap_err();
    let messages: Vec<&str> = errs.iter().map(|e| e.message.as_str()).collect();
    assert!(messages.iter().any(|m| m.contains("fieldMapping")));
    assert!(messages.iter().any(|m| m.contains("fieldValue")));
}

#[test]
fn validate_blank_field_is_error() {
    let yaml = "pattern:\n  - \"**/*.vcf.gz\"\nannotation:\n  - type: dirname\n    field: ''\n";
    let errs = parse_and_validate(yaml).unwrap_err();
    assert!(errs.iter().any(|e| e.message.contains("`field` must not be blank")));
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
    let errs = parse_and_validate(yaml).unwrap_err();
    assert!(errs.iter().any(|e| e.message.contains("duplicate `field` name")));
}

#[test]
fn validate_syntax_error_returned_as_parse_error() {
    let yaml = "annotation:\n  - type: [\nbad yaml";
    let errs = parse_and_validate(yaml).unwrap_err();
    assert!(errs[0].message.contains("YAML parse error"));
}

#[test]
fn validate_unused_fields_not_errors() {
    // `fieldSource` is irrelevant for `static`
    // must not blo                //]));ck a config that is otherwise valid.
    let yaml = r#"
pattern:
  - "**/*.vcf.gz"
annotation:
  - type: static
    field: BUILD
    value: GRCh38
    fieldSource: SPURIOUS
"#;
    // The config has an error because warnings from unused fields come back.
    // Let's check severity explicitly.
    assert!(parse_and_validate(yaml).is_ok());
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
    let errs = parse_and_validate(yaml).unwrap_err();
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
    let errs = parse_and_validate(yaml).unwrap_err();
    assert!(errs[0].message.contains("YAML parse error"));
}