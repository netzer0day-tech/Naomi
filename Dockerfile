# ─── Naomi's Blog — Dockerfile ──────────────────────────
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create data directory
RUN mkdir -p data

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s \
  CMD curl -f http://localhost:5000/api/settings || exit 1

# Run with gunicorn (2 workers for lightweight VPS)
CMD ["gunicorn", "app:app", "--workers", "2", "--bind", "0.0.0.0:5000", "--access-logfile", "-"]
