use thiserror::Error;

// Define a custom error type for the OpenVariant project

#[derive(Error, Debug)]
pub enum OVError {
    #[error("I/O error: {0}")]
    Io(#[from] std::io::Error),

    #[error("bad annotation: {0}")]
    BadAnnotation(String),

    #[error("bad regex: {0}")]
    BadRegex(String),

    #[error("plugin not compiled: {0}")]
    PluginNotCompiled(String),

    #[error("operation failed: {0}")]
    Other(String),
}
