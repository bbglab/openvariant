build:
	PYO3_PYTHON=$$(uv python find) cargo build

lint:
	PYO3_PYTHON=$$(uv python find) cargo clippy

format:
	PYO3_PYTHON=$$(uv python find) cargo fmt --check

check: lint format