pub mod config;

pub use config::{
    AnnotationConfig,
    AnnotationDelimiter,
    AnnotationEntry,
    AnnotationFormat,
    AnnotationType,
    ExcludeEntry,
    Severity,
    ValidationError,
    parse_and_validate,
    validate_config,
};