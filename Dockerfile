# ──────────────────────────────────────────────────────────────────────────────
# Dockerfile — Gelateria Backend (Python + Flask + Gunicorn)
# ──────────────────────────────────────────────────────────────────────────────

FROM python:3.12-slim AS base

# Security: run as non-root user
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

WORKDIR /app

# Install dependencies first (Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY backend/ ./backend/
COPY database/ ./database/

RUN chown -R appuser:appgroup /app
USER appuser

# Expose port (Railway/Render use $PORT dynamically)
EXPOSE 5000

ENV FLASK_ENV=production

# Start Gunicorn
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 2 --timeout 120 backend.app:app"]
