#!/bin/bash

# Exit on any error
set -e

# Default values
GUNICORN_WORKER_CLASS=${GUNICORN_WORKER_CLASS:-sync}
GUNICORN_WORKER_CONNECTIONS=${GUNICORN_WORKER_CONNECTIONS:-1000}
GUNICORN_WORKERS=${GUNICORN_WORKERS:-4}
GUNICORN_TIMEOUT=${GUNICORN_TIMEOUT:-30}
GUNICORN_BIND=${GUNICORN_BIND:-0.0.0.0:8000}

echo "Starting Gunicorn with:"
echo "  Worker Class: $GUNICORN_WORKER_CLASS"
echo "  Worker Connections: $GUNICORN_WORKER_CONNECTIONS"
echo "  Workers: $GUNICORN_WORKERS"
echo "  Timeout: $GUNICORN_TIMEOUT"
echo "  Bind: $GUNICORN_BIND"

# Start Gunicorn
exec gunicorn \
    --worker-class="$GUNICORN_WORKER_CLASS" \
    --worker-connections="$GUNICORN_WORKER_CONNECTIONS" \
    --workers="$GUNICORN_WORKERS" \
    --timeout="$GUNICORN_TIMEOUT" \
    --bind="$GUNICORN_BIND" \
    --access-logfile=- \
    --error-logfile=- \
    --log-level=info \
    campushub360.wsgi:application
