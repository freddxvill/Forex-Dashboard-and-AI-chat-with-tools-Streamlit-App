# Use a minimal Python 3.12 image
FROM python:3.12-slim-bookworm

# Configure environment variables
# - PYTHONUNBUFFERED: Forces stdout/stderr to be flushed immediately
# - UV_COMPILE_BYTECODE: Compiles python files for faster startup
ENV PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1

# Install uv (The underlying base image for uv is usually minimal, so we copy the binary)
# This is the recommended way to install uv in Docker for production
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files first to leverage cache
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
# --frozen: assert that the lockfile is up-to-date
# --no-dev: do not install development dependencies
RUN uv sync --frozen --no-dev

# Copy the application code
COPY app.py .
COPY utils/ ./utils/
# Copy metadata/config files if any (e.g. .streamlit config, though usually generated)

# Expose the standard Streamlit port
EXPOSE 8501

# Healthcheck to ensure the app is running
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Command to run the application
# We use `uv run` to ensure we use the virtual environment created by `uv sync`
CMD ["uv", "run", "streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
