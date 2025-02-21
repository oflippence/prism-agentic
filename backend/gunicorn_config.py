import os
import multiprocessing

# Basic server configuration
bind = f"0.0.0.0:{os.getenv('PORT', '8080')}"
workers = 1
worker_class = "sync"
threads = 4

# Logging
errorlog = "-"
accesslog = "-"
loglevel = "info"

# Timeouts
timeout = 120
graceful_timeout = 30
keepalive = 5

# Process naming
proc_name = "prism_agentic_backend"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None

# Prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Disable preloading
preload_app = False


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
