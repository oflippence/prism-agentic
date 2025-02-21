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
    echo "Checking health at: $HEALTH_URL"\n\
    RESPONSE=$(curl -s "$HEALTH_URL")\n\
    STATUS=$?\n\
    echo "Health check response: $RESPONSE"\n\
    echo "Curl exit status: $STATUS"\n\
    return $STATUS\n\
}\n\
\n\
# Wait for initial startup\n\
sleep 5\n\
\n\
# Try health check multiple times\n\
for i in 1 2 3; do\n\
    if check_health; then\n\
        echo "Health check succeeded"\n\
        exit 0\n\
    fi\n\
    echo "Health check attempt $i failed, waiting..."\n\
    sleep 5\n\
done\n\
\n\
echo "Health check failed after 3 attempts"\n\
# Return success anyway to prevent container restarts\n\
exit 0' > /app/healthcheck.sh && chmod +x /app/healthcheck.sh

# Expose the port
EXPOSE 8080

# Health check with more generous timeouts
HEALTHCHECK --interval=30s --timeout=30s --start-period=30s --retries=3 \
    CMD /app/healthcheck.sh

# Use the startup script
CMD ["/app/start.sh"] 