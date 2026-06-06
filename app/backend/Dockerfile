# ── Stage 1: builder ──────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

# Install dependencies in a separate layer for Docker cache efficiency
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2: runtime ──────────────────────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application source
COPY src/ ./src/

# Copy DB init script
COPY src/scripts/init_db.py ./src/scripts/init_db.py

# Model artefacts are mounted at runtime via docker-compose (../modeling/models → /app/models)
RUN mkdir -p /app/models

# Non-root user for security
RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Run DB init then start the API (--app-dir src puts core/, api/, etc. on PYTHONPATH)
CMD ["sh", "-c", "python src/scripts/init_db.py && uvicorn main:app --app-dir src --host 0.0.0.0 --port 8000"]
