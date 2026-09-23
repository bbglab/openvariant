use crate::annotation::CompiledLambda;

#[test]
fn identity_closure_returns_input_unchanged() {
    let lambda = CompiledLambda::compile("|y| y").unwrap();
    assert_eq!(lambda.apply("hello").unwrap(), "hello");
    assert_eq!(lambda.apply("").unwrap(), "");
}

#[test]
fn split_closure_returns_selected_part() {
    let lambda = CompiledLambda::compile(r#"|y| y.split("_")[1]"#).unwrap();
    assert_eq!(lambda.apply("sample_specimen_donor").unwrap(), "specimen");
}


#[test]
fn upper_closure_uppercases_input() {
    let lambda = CompiledLambda::compile("|y| y.to_upper()").unwrap();

    assert_eq!(lambda.apply("chr1").unwrap(), "CHR1");
}

#[test]
fn replace_chr() {
    let lambda = CompiledLambda::compile(r#"|y| y.replace("CHR", "") ?? y"#).unwrap();
    assert_eq!(lambda.apply("CHR1").unwrap(), "1");
}

#[test]
fn upper_then_replace() {
    let lambda = CompiledLambda::compile(
        r#"|y| y.make_upper() ?? y.replace("CHR", "") ?? y"#,
    )
    .unwrap();
    assert_eq!(lambda.apply("chr1").unwrap(), "1");
}

#[test]
fn long_closure_example() {
    let lambda = CompiledLambda::compile(
        r#"|y| y.make_upper() ?? y.replace("CHR", "") ?? y.replace("23", "X") ?? y.replace("24", "Y") ?? y"#,
    )
    .unwrap();
    assert_eq!(lambda.apply("chr24").unwrap(), "Y");
}

#[test]
fn lower_closure_lowercases_input() {
    let lambda = CompiledLambda::compile("|c| c.to_lower()").unwrap();
    assert_eq!(lambda.apply("CHR1").unwrap(), "chr1");
}

#[test]
fn arbitrary_closure_is_actually_executed() {
    let lambda = CompiledLambda::compile(r#"|y| y + "_suffix""#).unwrap();
    assert_eq!(lambda.apply("value").unwrap(), "value_suffix");
}

#[test]
fn invalid_syntax_fails_to_compile() {
    assert!(CompiledLambda::compile("not a closure").is_err());
}

#[test]
fn call_errors_on_arity_mismatch() {
    let lambda = CompiledLambda::compile(r#"|x, y| x.replace("CHR", y)"#).unwrap();
    assert!(lambda.apply("value").is_err());
}

#[test]
fn source_returns_original_text() {
    let lambda = CompiledLambda::compile("|y| y.to_upper()").unwrap();
    assert_eq!(lambda.source(), "|y| y.to_upper()");
}

