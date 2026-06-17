FROM python:3.12-slim

# Avoid writing .pyc files and buffer logs to see them immediately
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# 1. Install uv efficiently without using pip
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 2. Copy dependency files first to maximize Docker layer caching
COPY pyproject.toml uv.lock ./

# 3. Mount cache during sync to speed up subsequent builds
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project

# Copy application code
COPY . .

# 4. Final sync to include the project package itself
RUN uv sync --frozen

EXPOSE 8000

# Use array syntax for the default command
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
