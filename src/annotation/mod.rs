pub mod config;
pub mod ir;
pub mod validator;

pub use config::{
    AnnotationConfig, AnnotationDelimiter, AnnotationEntry, AnnotationFormat, ExcludeEntry,
};
pub use ir::{CompiledAnnotation, CompiledLambda, FieldOp, LambdaApplyError, LambdaCompileError};
pub use validator::{Severity, ValidationError, parse_and_validate, validate_config};
