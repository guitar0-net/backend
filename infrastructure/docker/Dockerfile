# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# Stage 1: Builder
FROM python:3.12-slim AS builder

WORKDIR /app

# Install PDM
RUN pip install --no-cache-dir pdm

# Copy dependency files
COPY pyproject.toml pdm.lock ./

# Export dependencies to requirements.txt (production only, no dev/test)
RUN pdm export --no-hashes -o requirements.txt --prod

# Stage 2: Production
FROM python:3.12-slim AS production

# Build arguments for versioning
ARG VERSION=unknown
ARG GIT_SHA=unknown
ARG BUILD_DATETIME=unknown

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    VERSION=${VERSION} \
    GIT_SHA=${GIT_SHA} \
    BUILD_DATETIME=${BUILD_DATETIME}

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd --gid 1001 appuser \
    && useradd --uid 1001 --gid 1001 --shell /bin/bash --create-home appuser

# Copy requirements from builder
COPY --from=builder /app/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=appuser:appuser manage.py ./
COPY --chown=appuser:appuser config/ ./config/
COPY --chown=appuser:appuser apps/ ./apps/

# Create directories for static files and logs
RUN mkdir -p /app/staticfiles /app/logs \
    && chown -R appuser:appuser /app/staticfiles /app/logs

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/metrics/ || exit 1

CMD ["gunicorn", "--config", "config/gunicorn.py", "config.wsgi:application"]
