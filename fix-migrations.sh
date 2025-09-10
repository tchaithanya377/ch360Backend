#!/bin/bash

# Script to fix pending migrations
set -e

echo "🔧 Fixing pending migrations..."

# Run makemigrations for the apps that need it
docker compose -f docker-compose.production.yml run --rm web bash -lc '
    python manage.py makemigrations academics
    python manage.py makemigrations students
    python manage.py migrate --noinput
'

echo "✅ Migrations fixed successfully!"
