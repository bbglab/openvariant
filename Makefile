build:
	PYO3_PYTHON=$$(uv python find) cargo build

release:
	PYO3_PYTHON=$$(uv python find) cargo build --release

test:
	PYO3_PYTHON=$$(uv python find) cargo test

test-filter:
	PYO3_PYTHON=$$(uv python find) cargo test $(FILTER)

fmt:
	PYO3_PYTHON=$$(uv python find) cargo fmt

lint:
	PYO3_PYTHON=$$(uv python find) cargo clippy -- -D warnings

fix:
	PYO3_PYTHON=$$(uv python find) cargo clippy --fix --allow-dirty --allow-staged
	PYO3_PYTHON=$$(uv python find) cargo fmt

check:
	PYO3_PYTHON=$$(uv python find) cargo fmt --check
	PYO3_PYTHON=$$(uv python find) cargo clippy -- -D warnings