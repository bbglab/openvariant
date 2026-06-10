build:
	PYO3_PYTHON=$$(uv python find) cargo build

release:
	PYO3_PYTHON=$$(uv python find) cargo build --release

test:
	PYO3_PYTHON=$$(uv python find) cargo test

lint:
	PYO3_PYTHON=$$(uv python find) cargo clippy

format:
	PYO3_PYTHON=$$(uv python find) cargo fmt --check

check: lint format