import multiprocessing
import os

# Bind to all interfaces inside container; ALB/Nginx terminates TLS
bind = os.getenv('GUNICORN_BIND', '0.0.0.0:8000')

# Workers: (2 x CPU) + 1 heuristic; allow override via env
_cpu_count = multiprocessing.cpu_count()
workers = int(os.getenv('GUNICORN_WORKERS', str(max(2, _cpu_count * 2 + 1))))

# Worker class: use sync by default for compatibility
worker_class = os.getenv('GUNICORN_WORKER_CLASS', 'sync')
worker_connections = int(os.getenv('GUNICORN_WORKER_CONNECTIONS', '1000'))
threads = int(os.getenv('GUNICORN_THREADS', '1'))

# App performance
preload_app = True
max_requests = int(os.getenv('GUNICORN_MAX_REQUESTS', '2000'))
max_requests_jitter = int(os.getenv('GUNICORN_MAX_REQUESTS_JITTER', '200'))
keepalive = int(os.getenv('GUNICORN_KEEPALIVE', '10'))
backlog = int(os.getenv('GUNICORN_BACKLOG', '2048'))

# Timeouts
timeout = int(os.getenv('GUNICORN_TIMEOUT', '60'))
graceful_timeout = int(os.getenv('GUNICORN_GRACEFUL_TIMEOUT', '30'))

# Security hardening
limit_request_line = int(os.getenv('GUNICORN_LIMIT_REQUEST_LINE', '8190'))
limit_request_fields = int(os.getenv('GUNICORN_LIMIT_REQUEST_FIELDS', '100'))
limit_request_field_size = int(os.getenv('GUNICORN_LIMIT_REQUEST_FIELD_SIZE', '8190'))
proxy_protocol = os.getenv('GUNICORN_PROXY_PROTOCOL', 'false').lower() == 'true'
forwarded_allow_ips = os.getenv('GUNICORN_FORWARDED_ALLOW_IPS', '*')

# Logging
accesslog = os.getenv('GUNICORN_ACCESSLOG', '-')
errorlog = os.getenv('GUNICORN_ERRORLOG', '-')
loglevel = os.getenv('GUNICORN_LOGLEVEL', 'info')

# Health: adjust after fork (DB, etc.)
def post_fork(server, worker):
    # Reduce GC pressure for gevent workers
    try:
        import gevent.monkey  # noqa: F401
    except Exception:
        pass

# Lifecycle hooks for observability
def on_starting(server):
    server.log.info('Gunicorn starting with %s workers', workers)

def when_ready(server):
    server.log.info('Gunicorn is ready. PID: %s', server.pid)

def worker_exit(server, worker):
    server.log.info('Worker exited: %s', worker.pid)
