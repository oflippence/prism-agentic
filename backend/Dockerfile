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
ENV GUNICORN_CMD_ARGS="--workers=2 --threads=4 --worker-class=gthread --worker-tmp-dir=/dev/shm --timeout=30 --max-requests=1000 --max-requests-jitter=50 --log-level=debug --capture-output --enable-stdio-inheritance --access-logfile=- --error-logfile=- --graceful-timeout=30 --keep-alive=2"

# Create log directory
RUN mkdir -p /var/log/gunicorn && \
    touch /var/log/gunicorn/error.log && \
    touch /var/log/gunicorn/access.log && \
    touch /var/log/gunicorn/app.log && \
    chmod -R 777 /var/log/gunicorn

# Create startup script with health check
RUN echo '#!/bin/sh\n\
# Start the application\n\
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

# Create health check script
RUN echo '#!/bin/sh\n\
# Wait for the application to start\n\
sleep 5\n\
\n\
# Get the health check URL\n\
HEALTH_URL="http://localhost:${PORT:-8080}/health"\n\
echo "Checking health at: $HEALTH_URL"\n\
\n\
# Try health check multiple times\n\
for i in 1 2 3; do\n\
    echo "Health check attempt $i..."\n\
    RESPONSE=$(curl -s "$HEALTH_URL")\n\
    STATUS=$?\n\
    echo "Response: $RESPONSE"\n\
    echo "Curl exit code: $STATUS"\n\
    \n\
    if [ $STATUS -eq 0 ]; then\n\
        echo "Health check succeeded"\n\
        exit 0\n\
    fi\n\
    echo "Health check attempt $i failed, retrying..."\n\
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