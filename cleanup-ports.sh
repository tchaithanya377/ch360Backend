#!/bin/bash

# Script to cleanup port conflicts
set -e

echo "🧹 Cleaning up port conflicts..."

# Stop all running containers
echo "Stopping all Docker containers..."
docker stop $(docker ps -q) 2>/dev/null || true

# Remove all containers
echo "Removing all Docker containers..."
docker rm $(docker ps -aq) 2>/dev/null || true

# Kill any processes using port 8000
echo "Checking for processes using port 8000..."
if lsof -i :8000 > /dev/null 2>&1; then
    echo "Killing processes using port 8000..."
    sudo fuser -k 8000/tcp 2>/dev/null || true
    sleep 2
fi

# Clean up Docker system
echo "Cleaning up Docker system..."
docker system prune -f

echo "✅ Port cleanup completed!"
