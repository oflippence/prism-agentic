FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production
ENV PORT=8080
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app
ENV GUNICORN_CMD_ARGS="--log-file=- --access-logfile=- --error-logfile=- --capture-output"

# Create a non-root user and set up directories
RUN useradd -m -U app && \
    mkdir -p /var/log/gunicorn && \
    chown -R app:app /app /var/log/gunicorn

# Switch to non-root user
USER app

# Simple health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Expose the port
EXPOSE 8080

# Start Gunicorn with explicit log configuration
CMD ["gunicorn", "--config=/app/gunicorn_config.py", "--log-file=-", "--access-logfile=-", "--error-logfile=-", "app:app"] 