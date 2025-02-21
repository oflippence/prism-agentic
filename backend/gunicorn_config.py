import os

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', '8080')}"
backlog = 2048

# Worker processes - more conservative for Railway
workers = 4  # Fixed number of workers instead of CPU-based
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process naming
proc_name = "prism-agentic-backend"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Memory management
max_requests = 1000
max_requests_jitter = 50

# Prevent memory leaks
preload_app = True

# SSL
keyfile = None
certfile = None
