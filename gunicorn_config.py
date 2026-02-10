# Gunicorn configuration file for production deployment
# Usage: gunicorn -c gunicorn_config.py wsgi:app

import multiprocessing
import os
from datetime import datetime

# Server socket configuration
bind = "0.0.0.0:8000"  # Listen on port 8000 (will be behind nginx on port 80)
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
log_file = "/var/log/gunicorn/access.log"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
loglevel = "info"

# Application name for process monitoring
proc_name = "plataforma-on"

# Reload on code change (if in development - disable for production)
reload = False

# Max requests per worker (for memory leak mitigation)
max_requests = 1000
max_requests_jitter = 50

# Server mechanics
daemon = False
pidfile = "/tmp/gunicorn.pid"
umask = 0
user = None
group = None

# Headers
raw_env = ["FLASK_ENV=production"]

# SSL configuration (when using directly, not behind nginx)
# Uncomment if not using nginx reverse proxy
# keyfile = "/path/to/keyfile.key"
# certfile = "/path/to/certfile.crt"

print(f"✅ Gunicorn config loaded - {workers} workers, port 8000")
