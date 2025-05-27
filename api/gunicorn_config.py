import multiprocessing

# Number of worker processes
workers = multiprocessing.cpu_count() * 2 + 1

# Worker class
worker_class = 'sync'

# Maximum number of requests a worker will process before restarting
max_requests = 1000
max_requests_jitter = 50

# Timeout for worker processes
timeout = 120

# Maximum number of simultaneous clients
worker_connections = 1000

# Server socket
bind = "0.0.0.0:3001"

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process naming
proc_name = "nfl-simulation-api"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Memory management - increased to handle large simulation requests
max_worker_memory = 2048  # MB
worker_memory_limit = 2048  # MB 