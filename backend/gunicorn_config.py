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
workers = 1  # Reduced to 1 worker for stability
worker_class = "gthread"
threads = 4
worker_connections = 1000
timeout = 300  # Increased timeout
keepalive = 10  # Increased keepalive

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

# Prevent memory leaks
max_requests = 100  # Reduced to prevent memory buildup
max_requests_jitter = 10

# Preload app
preload_app = False  # Disabled preloading to prevent issues with forking

# Graceful timeout
graceful_timeout = 120  # Increased graceful timeout


def when_ready(server):
    """Log when server is ready"""
    server.log.info("=== Gunicorn server is ready ===")


def worker_int(worker):
    """Log when worker receives INT signal"""
    worker.log.info(f"=== Worker {worker.pid} received INT signal ===")


def worker_abort(worker):
    """Log when worker receives ABORT signal"""
    worker.log.warning(f"=== Worker {worker.pid} received ABORT signal ===")


def worker_exit(server, worker):
    """Log when worker exits"""
    server.log.info(f"=== Worker {worker.pid} exited ===")
    # Try to spawn a new worker
    server.spawn_worker()


def on_exit(server):
    """Log when server exits"""
    server.log.info("=== Gunicorn server is shutting down ===")


def post_worker_init(worker):
    """Called just after a worker has initialized"""
    worker.log.info(f"=== Worker {worker.pid} initialized ===")


def pre_request(worker, req):
    """Called just before a worker processes the request"""
    worker.log.debug(f"=== Processing request: {req.uri} ===")
    return None


def post_request(worker, req, environ, resp):
    """Called after a worker processes the request"""
    worker.log.debug(f"=== Completed request: {req.uri} ===")


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
