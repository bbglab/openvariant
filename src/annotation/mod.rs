pub mod config;
pub mod validator;

pub use config::{
    AnnotationConfig, AnnotationDelimiter, AnnotationEntry, AnnotationFormat, AnnotationType,
    ExcludeEntry,
};
pub use validator::{Severity, ValidationError, parse_and_validate, validate_config};
