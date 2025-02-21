FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production
ENV GUNICORN_CMD_ARGS="--workers=2 --threads=4 --worker-class=gthread --worker-tmp-dir=/dev/shm --timeout=30 --max-requests=1000 --max-requests-jitter=50"

# Expose the port
EXPOSE 8080

# Use Gunicorn in production with explicit parameters
CMD ["sh", "-c", "if [ \"$ENVIRONMENT\" = \"production\" ]; then gunicorn --bind=0.0.0.0:$PORT app:app; else python app.py; fi"] 