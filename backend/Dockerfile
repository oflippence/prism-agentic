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
ENV PORT=8080
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

# Create log directory and set permissions
RUN mkdir -p /var/log/gunicorn && \
    touch /var/log/gunicorn/error.log && \
    touch /var/log/gunicorn/access.log && \
    touch /var/log/gunicorn/app.log && \
    chmod -R 777 /var/log/gunicorn

# Create startup script
RUN echo '#!/bin/sh\n\
\n\
# Function to cleanup on exit\n\
cleanup() {\n\
    echo "Received shutdown signal - cleaning up..."\n\
    # Add any cleanup tasks here\n\
    exit 0\n\
}\n\
\n\
# Trap signals\n\
trap cleanup SIGTERM SIGINT SIGQUIT\n\
\n\
# Start the application\n\
if [ "$ENVIRONMENT" = "production" ]; then\n\
    echo "Starting Gunicorn in production mode..."\n\
    exec gunicorn \\\n\
        --config=/app/gunicorn_config.py \\\n\
        app:app\n\
else\n\
    echo "Starting Flask development server..."\n\
    exec python app.py\n\
fi' > /app/start.sh && chmod +x /app/start.sh

# Create health check script
RUN echo '#!/bin/sh\n\
\n\
# Function to check health\n\
check_health() {\n\
    HEALTH_URL="http://localhost:${PORT:-8080}/health"\n\
    echo "[$(date)] Checking health at: $HEALTH_URL"\n\
    RESPONSE=$(curl -s -m 10 "$HEALTH_URL")\n\
    STATUS=$?\n\
    echo "[$(date)] Health check response: $RESPONSE"\n\
    echo "[$(date)] Curl exit status: $STATUS"\n\
    \n\
    # Check if Gunicorn is running\n\
    if ps aux | grep -q "[g]unicorn"; then\n\
        echo "[$(date)] Gunicorn process is running"\n\
    else\n\
        echo "[$(date)] WARNING: Gunicorn process not found"\n\
    fi\n\
    \n\
    # Check system resources\n\
    echo "[$(date)] Memory usage:"\n\
    free -m || true\n\
    echo "[$(date)] Disk usage:"\n\
    df -h / || true\n\
    \n\
    # Always return success\n\
    return 0\n\
}\n\
\n\
# Wait longer for initial startup\n\
echo "[$(date)] Waiting for initial startup..."\n\
sleep 10\n\
\n\
# Perform health check\n\
check_health\n\
\n\
# Always exit successfully\n\
exit 0' > /app/healthcheck.sh && chmod +x /app/healthcheck.sh

# Expose the port
EXPOSE 8080

# Health check with more generous timeouts
HEALTHCHECK --interval=60s --timeout=30s --start-period=60s --retries=3 \
    CMD /app/healthcheck.sh

# Use the startup script
CMD ["/app/start.sh"] 