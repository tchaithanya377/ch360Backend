#!/bin/bash

# Production Deployment Script for CampusHub360
set -e

echo "🚀 Starting CampusHub360 Production Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Stop and remove existing containers to avoid port conflicts
print_status "Stopping existing containers..."
docker compose -f docker-compose.production.yml down --remove-orphans || true

# Remove any containers using port 8000
print_status "Checking for port 8000 conflicts..."
if lsof -i :8000 > /dev/null 2>&1; then
    print_warning "Port 8000 is in use. Attempting to free it..."
    # Kill processes using port 8000
    sudo fuser -k 8000/tcp || true
    sleep 2
fi

# Generate a strong SECRET_KEY
print_status "Generating secure SECRET_KEY..."
SECRET_KEY=$(openssl rand -base64 32 | tr -d '\n')
export SECRET_KEY="django-insecure-${SECRET_KEY}"

# Build the Docker image
print_status "Building Docker image..."
docker compose -f docker-compose.production.yml build --no-cache

# Run one-off tasks
print_status "Running database migrations and collecting static files..."
docker compose -f docker-compose.production.yml run --rm web bash -lc '
    python manage.py collectstatic --noinput && 
    python manage.py migrate --noinput
'

# Create superuser (optional, will skip if already exists)
print_status "Creating superuser..."
docker compose -f docker-compose.production.yml run --rm web bash -lc '
    DJANGO_SUPERUSER_USERNAME=admin 
    DJANGO_SUPERUSER_EMAIL=admin@example.com 
    DJANGO_SUPERUSER_PASSWORD=Admin@123 
    python manage.py createsuperuser --noinput || true
'

# Start the services
print_status "Starting production services..."
docker compose -f docker-compose.production.yml up -d

# Wait for services to be healthy
print_status "Waiting for services to be healthy..."
sleep 10

# Check if services are running
if docker compose -f docker-compose.production.yml ps | grep -q "Up"; then
    print_status "✅ Deployment successful!"
    print_status "🌐 Application is running at: http://13.232.220.214:8000"
    print_status "📊 Health check: http://13.232.220.214:8000/health/"
    print_status "👤 Admin login: admin / Admin@123"
    
    # Show running containers
    echo ""
    print_status "Running containers:"
    docker compose -f docker-compose.production.yml ps
else
    print_error "❌ Deployment failed. Check the logs:"
    docker compose -f docker-compose.production.yml logs
    exit 1
fi

echo ""
print_status "🎉 CampusHub360 is now running in production mode!"
