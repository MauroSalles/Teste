# ──────────────────────────────────────────────────────────────────────────────
# Dockerfile — Gelateria Backend (Python + Flask + Gunicorn)
# Multi-stage build for minimal production image
# ──────────────────────────────────────────────────────────────────────────────

# Stage 1: dependency builder
FROM python:3.12-slim AS builder

WORKDIR /install
COPY requirements.txt .
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# Stage 2: production image
FROM python:3.12-slim

# Security: run as non-root user
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

WORKDIR /app

# Copy pre-built dependencies from builder into a system-accessible location
COPY --from=builder /install/lib /usr/local/lib
COPY --from=builder /install/bin /usr/local/bin

# Copy application source
COPY backend/ ./backend/
COPY database/ ./database/

RUN chown -R appuser:appgroup /app
USER appuser

# Expose port (Render/Railway use $PORT dynamically)
EXPOSE 8000

ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT:-8000}/health')" || exit 1

# Start Gunicorn
CMD ["sh", "-c", "gunicorn backend.app:app --bind 0.0.0.0:${PORT:-8000} --workers 4 --timeout 120"]

