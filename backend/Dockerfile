FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production
ENV GUNICORN_CMD_ARGS="--workers=2 --threads=4 --worker-class=gthread --worker-tmp-dir=/dev/shm --timeout=30 --max-requests=1000 --max-requests-jitter=50 --log-level=debug --capture-output --enable-stdio-inheritance --access-logfile=- --error-logfile=- --graceful-timeout=30"

# Create log directory
RUN mkdir -p /var/log/gunicorn && \
    touch /var/log/gunicorn/error.log && \
    touch /var/log/gunicorn/access.log && \
    touch /var/log/gunicorn/app.log && \
    chmod -R 777 /var/log/gunicorn

# Create startup script
RUN echo '#!/bin/sh\n\
if [ "$ENVIRONMENT" = "production" ]; then\n\
    echo "Starting Gunicorn in production mode..."\n\
    exec gunicorn \\\n\
        --bind=0.0.0.0:$PORT \\\n\
        --error-logfile=- \\\n\
        --access-logfile=- \\\n\
        --log-level=debug \\\n\
        --capture-output \\\n\
        --preload \\\n\
        app:app\n\
else\n\
    echo "Starting Flask development server..."\n\
    exec python app.py\n\
fi' > /app/start.sh && chmod +x /app/start.sh

# Expose the port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8080}/health || exit 1

# Use the startup script
CMD ["/app/start.sh"] 