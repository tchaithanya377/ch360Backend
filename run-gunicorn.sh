#!/usr/bin/env sh
set -eu

# Wait for database to be ready (up to 60s)
DB_HOST="${POSTGRES_HOST:-localhost}"
DB_PORT="${POSTGRES_PORT:-5432}"
ATTEMPTS=60
i=1
while [ "$i" -le "$ATTEMPTS" ]; do
  python - "$DB_HOST" "$DB_PORT" <<'PY'
import socket, sys
host, port = sys.argv[1], int(sys.argv[2])
s = socket.socket()
s.settimeout(1)
try:
    s.connect((host, port))
    sys.exit(0)
except Exception:
    sys.exit(1)
finally:
    s.close()
PY
  if [ "$?" -eq 0 ]; then
    echo "Database is available at ${DB_HOST}:${DB_PORT}"
    break
  fi
  echo "Waiting for database at ${DB_HOST}:${DB_PORT} (${i}/${ATTEMPTS})"
  i=$((i+1))
  sleep 1
done

# Collect static files (safe to run each start)
python manage.py collectstatic --noinput --verbosity 0

# Apply database migrations
python manage.py migrate --noinput

# Start gunicorn with configured settings module
exec gunicorn campshub360.wsgi:application \
  --config gunicorn.conf.py

#!/usr/bin/env bash
set -euo pipefail

export PYTHONUNBUFFERED=1
export DJANGO_SETTINGS_MODULE=campshub360.settings

# Default envs if not provided
: "${GUNICORN_BIND:=0.0.0.0:8000}"
: "${GUNICORN_WORKERS:=4}"
: "${GUNICORN_WORKER_CLASS:=gevent}"
: "${GUNICORN_WORKER_CONNECTIONS:=1000}"
: "${GUNICORN_TIMEOUT:=60}"
: "${GUNICORN_KEEPALIVE:=10}"

python manage.py collectstatic --noinput
python manage.py migrate --noinput

exec gunicorn \
  --config gunicorn.conf.py \
  --bind "$GUNICORN_BIND" \
  --workers "$GUNICORN_WORKERS" \
  --worker-class "$GUNICORN_WORKER_CLASS" \
  --worker-connections "$GUNICORN_WORKER_CONNECTIONS" \
  --timeout "$GUNICORN_TIMEOUT" \
  --keep-alive "$GUNICORN_KEEPALIVE" \
  campshub360.wsgi:application
