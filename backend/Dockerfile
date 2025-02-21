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

# Expose the port
EXPOSE 8080

# Use Gunicorn in production, Flask in development
CMD ["sh", "-c", "if [ \"$ENVIRONMENT\" = \"production\" ]; then gunicorn --config gunicorn_config.py app:app; else python app.py; fi"] 