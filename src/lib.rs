use pyo3::prelude::*;

//mod annotation;
//mod filter;
//mod reader;
//mod walker;
//mod tasks;
//mod py_bindings;
pub mod error;

#[pyfunction]
fn hello() {
    println!("Hello, OpenVariant!");
}

#[pymodule]
fn _core(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(hello, m)?)?;
    //py_bindings::annotation::register(py, m)?;
    //py_bindings::variant::register(py, m)?;
    //py_bindings::tasks::register(py, m)?;
    //py_bindings::find_files::register(py, m)?;
    Ok(())
}
