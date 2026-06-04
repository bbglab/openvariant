use thiserror::Error;

// Define a custom error type for the OpenVariant project
// IO
// BadAnnotation
// BadRegex
// PluginNotCompiled

#[derive(Error, Debug)]
pub enum OVError {
    #[error("I/O error: {0}")]
    Io(#[from] std::io::Error),

    #[error("configuration error: {0}")]
    Config(String),

    #[error("invalid input: {0}")]
    InvalidInput(String),

    #[error("resource not found: {0}")]
    NotFound(String),

    #[error("operation failed: {0}")]
    Other(String),
}
