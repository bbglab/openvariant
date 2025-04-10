FROM ghcr.io/astral-sh/uv:0.5-python3.13-bookworm AS build-stage

# Set environment variables
ENV UV_COMPILE_BYTECODE=1

# Set the working directory to /openvariant
WORKDIR /openvariant

# Stage necessary files into the container
COPY uv.lock uv.lock
COPY pyproject.toml pyproject.toml
COPY openvariant openvariant
COPY LICENSE LICENSE
COPY README.md README.md

# Install dependencies and build the project
RUN mkdir -p /root/.cache/uv \
    && uv sync --frozen --no-dev \
    && uv build

# Second stage: Runtime image
FROM python:3.13-bookworm AS runtime-stage

# Copy openvariant from the build stage
COPY --from=build-stage /openvariant/dist /openvariant/dist
WORKDIR /openvariant

# Install openvariant
RUN pip install dist/*.tar.gz 

# Test the installation
RUN openvar --help