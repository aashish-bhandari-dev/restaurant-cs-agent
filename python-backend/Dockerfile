# Use an official Python runtime as the base image
FROM python:3.12-slim

# Set environment variables
ENV POETRY_VERSION=1.8.3 \
    POETRY_VIRTUALENVS_CREATE=false \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/root/.local/bin:$PATH"

# Install system dependencies required for Poetry
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    libc-dev \
    && pip install poetry==${POETRY_VERSION} \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Verify Poetry installation
RUN poetry --version

# Set working directory
WORKDIR /app

# Copy Poetry configuration files first for dependency caching
COPY pyproject.toml poetry.lock* /app/

# Install dependencies with Poetry (main group only)
RUN poetry install --no-root --only main --no-interaction --no-ansi

# Copy the rest of the application
COPY . /app

# Expose port for FastAPI
EXPOSE 8000

# Default command for FastAPI
CMD ["poetry", "run", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]