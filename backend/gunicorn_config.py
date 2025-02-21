import os
import multiprocessing
import logging
from gunicorn import glogging


# Logging
class CustomGunicornLogger(glogging.Logger):
    def setup(self, cfg):
        super().setup(cfg)

        # Add custom file handler
        error_handler = logging.FileHandler("/var/log/gunicorn/error.log")
        error_handler.setLevel(logging.INFO)
        self.error_log.addHandler(error_handler)


logger_class = CustomGunicornLogger

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', '8080')}"
backlog = 2048

# Worker processes
workers = 2  # Fixed number for Railway
worker_class = "gthread"
threads = 4
worker_connections = 1000
timeout = 120  # Increased timeout
keepalive = 5  # Increased keepalive

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "debug"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
capture_output = True
enable_stdio_inheritance = True

# Process naming
proc_name = "prism_agentic_backend"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL
keyfile = None
certfile = None


def on_starting(server):
    """Log when server is starting"""
    server.log.info("=== Gunicorn server is starting ===")


def on_reload(server):
    """Log when server is reloaded"""
    server.log.info("=== Gunicorn server is reloading ===")


def post_fork(server, worker):
    """Log when a worker is forked"""
    server.log.info(f"=== Worker {worker.pid} forked ===")


def pre_fork(server, worker):
    """Log before a worker is forked"""
    server.log.info(f"=== Preparing to fork worker {worker.pid} ===")


def pre_exec(server):
    """Log before exec-ing"""
    server.log.info("=== Gunicorn pre-exec ===")


def when_ready(server):
    """Log when server is ready"""
    server.log.info("=== Gunicorn server is ready ===")


def worker_int(worker):
    """Log when worker receives INT or QUIT signal"""
    worker.log.info(f"=== Worker {worker.pid} received INT or QUIT signal ===")


def worker_abort(worker):
    """Log when worker receives SIGABRT signal"""
    worker.log.warning(f"=== Worker {worker.pid} received SIGABRT signal ===")


def worker_exit(server, worker):
    """Log when worker exits"""
    server.log.info(f"=== Worker {worker.pid} exited ===")


def on_exit(server):
    """Log when server exits"""
    server.log.info("=== Gunicorn server is shutting down ===")


# Prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Preload app to save memory
preload_app = True

# Graceful timeout
graceful_timeout = 60  # Increased graceful timeout
