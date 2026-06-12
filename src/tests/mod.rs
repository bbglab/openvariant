mod tests {
    use crate::annotation::AnnotationType;
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
        assert_eq!(first, second, "round-trip mismatch:\noriginal = {first:?}\nre-parsed = {second:?}");
        first
    }

    // ── AnnotationType ────────────────────────────────────────────────────────

    #[test]
    fn annotation_type_static_round_trip() {
        assert_eq!(round_trip::<AnnotationType>("static"), AnnotationType::Static);
    }
}
