use crate::annotation::{AnnotationConfig, AnnotationDelimiter, AnnotationEntry, AnnotationFormat};

use serde::Serialize;
use std::fmt;

/// Deserialise from YAML, re-serialise, then deserialise again.
/// Asserts the three values are equal and returns the first parsed value.
fn round_trip<T>(yaml: &str) -> T
where
    T: serde::de::DeserializeOwned + Serialize + PartialEq + fmt::Debug,
{
    let first: T = yaml_serde::from_str(yaml).expect("initial parse failed");
    let reserialized = yaml_serde::to_string(&first).expect("serialise failed");
    let second: T = yaml_serde::from_str(&reserialized).expect("re-parse failed");
    assert_eq!(
        first, second,
        "round-trip mismatch:\noriginal = {first:?}\nre-parsed = {second:?}"
    );
    first
}

///ENUMS

// AnnotationEntry Display tests
#[test]
fn entry_display_static() {
    let entry: AnnotationEntry =
        yaml_serde::from_str("type: static\nfield: GENOME\nvalue: GRCh38\n").unwrap();
    assert_eq!(entry.to_string(), "static(field=GENOME, value=GRCh38)");
 }

 #[test]
fn entry_display_dirname_minimal() {
    let entry: AnnotationEntry = yaml_serde::from_str("type: dirname\nfield: DIR\n").unwrap();
    assert_eq!(entry.to_string(), "dirname(field=DIR)");
}

 #[test]
fn entry_display_plugin() {
    let entry: AnnotationEntry =
        yaml_serde::from_str("type: plugin\nfield: SCORE\nplugin: scoring.module\n").unwrap();
     assert_eq!(
        entry.to_string(),
        "plugin(field=SCORE, plugin=scoring.module)"
     );
 }

// AnnotationDelimiter, round-trip tests
#[test]
fn delimiter_t_round_trip() {
    let d = round_trip::<AnnotationDelimiter>("T");
    assert_eq!(d, AnnotationDelimiter::T);
    assert_eq!(d.as_char(), '\t');
}

#[test]
fn delimiter_c_round_trip() {
    let d = round_trip::<AnnotationDelimiter>("C");
    assert_eq!(d, AnnotationDelimiter::C);
    assert_eq!(d.as_char(), ',');
}

#[test]
fn delimiter_unknown_variant_is_error() {
    assert!(yaml_serde::from_str::<AnnotationDelimiter>("X").is_err());
}

// AnnotationFormat, round-trip tests
#[test]
fn format_tsv_round_trip() {
    let f = round_trip::<AnnotationFormat>("TSV");
    assert_eq!(f, AnnotationFormat::Tsv);
    assert_eq!(f.separator(), '\t');
    assert_eq!(f.to_string(), "TSV");
}

#[test]
fn format_csv_round_trip() {
    let f = round_trip::<AnnotationFormat>("CSV");
    assert_eq!(f, AnnotationFormat::Csv);
    assert_eq!(f.separator(), ',');
    assert_eq!(f.to_string(), "CSV");
}

#[test]
fn format_lowercase_is_rejected() {
    // YAML keys for format are uppercase; lowercase must be rejected.
    assert!(yaml_serde::from_str::<AnnotationFormat>("tsv").is_err());
}

// Annotation Defaults
#[test]
fn config_defaults_are_applied_when_absent() {
    let yaml = "pattern:\n  - \"**/*.vcf.gz\"\nannotation:\n  - type: dirname\n    field: DIR\n";
    let cfg: AnnotationConfig = yaml_serde::from_str(yaml).unwrap();
    print!("{cfg:?}");
    assert_eq!(cfg.format, AnnotationFormat::Tsv);
    // `delimiter` is optional — omitting it yields `None`, not a default.
    assert_eq!(cfg.delimiter, None);
    assert!(!cfg.recursive);
    assert!(cfg.columns.is_empty());
    assert!(cfg.exclude.is_empty());
    assert!(!cfg.pattern.is_empty());
}

// `delimiter` is optional — omitting it must parse fine and yield `None`.
#[test]
fn config_missing_delimiter_is_none() {
    let yaml = "pattern:\n  - \"**/*.vcf.gz\"\nannotation:\n  - type: dirname\n    field: DIR\n";
    let cfg: AnnotationConfig = yaml_serde::from_str(yaml).unwrap();
    assert_eq!(cfg.delimiter, None);
}

// Full config round-trip test
#[test]
fn full_config_round_trip() {
    let yaml = r#"
pattern:
  - "**/*.vcf.gz"
recursive: true
format: CSV
delimiter: C
columns:
  - CHROM
  - POS
  - REF
  - ALT
annotation:
  - type: static
    field: GENOME
    value: GRCh38
  - type: internal
    field: ALLELE
    fieldSource: ALT
  - type: dirname
    field: STUDY_DIR
  - type: filename
    field: SAMPLE_FILE
  - type: plugin
    field: SCORE
    plugin: scoring.module
  - type: mapping
    field: GENE
    fieldSource: ENSEMBL_ID
    fileMapping: /data/genes.tsv
    fieldMapping: ENSEMBL
    fieldValue: SYMBOL
exclude:
  - field: FILTER
    value: FAIL
"#;
    let cfg = round_trip::<AnnotationConfig>(yaml);
    assert_eq!(cfg.pattern.len(), 1);
    assert_eq!(cfg.pattern[0], "**/*.vcf.gz");
    assert_eq!(cfg.annotation.len(), 6);
    assert_eq!(cfg.format, AnnotationFormat::Csv);
    assert_eq!(cfg.delimiter, Some(AnnotationDelimiter::C));
    assert_eq!(cfg.columns, vec!["CHROM", "POS", "REF", "ALT"]);
    assert!(cfg.recursive);
    assert_eq!(cfg.exclude.len(), 1);
}
