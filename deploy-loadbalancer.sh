#!/bin/bash

# CampusHub360 Load Balancer Deployment Script
set -e

echo "🚀 Starting CampusHub360 Load Balancer Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

print_header() {
    echo -e "${BLUE}[HEADER]${NC} $1"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

print_header "=== CampusHub360 Load Balancer Deployment ==="

# Stop and remove existing containers
print_status "Stopping existing containers..."
docker compose -f docker-compose.loadbalancer.yml down --remove-orphans || true
docker compose -f docker-compose.production.yml down --remove-orphans || true

# Clean up any port conflicts
print_status "Cleaning up port conflicts..."
for port in 80 443 8000 8001 8002 8003 8081 9113; do
    if lsof -i :$port > /dev/null 2>&1; then
        print_warning "Port $port is in use. Attempting to free it..."
        sudo fuser -k $port/tcp 2>/dev/null || true
    fi
done
sleep 3

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p nginx/ssl
mkdir -p static media
mkdir -p /var/cache/nginx/static /var/cache/nginx/api

# Generate a strong SECRET_KEY
print_status "Generating secure SECRET_KEY..."
SECRET_KEY=$(openssl rand -base64 32 | tr -d '\n')
export SECRET_KEY="django-insecure-${SECRET_KEY}"

# Build the Docker images
print_status "Building Docker images..."
docker compose -f docker-compose.loadbalancer.yml build --no-cache

# Run database migrations and collect static files
print_status "Running database migrations and collecting static files..."
docker compose -f docker-compose.loadbalancer.yml run --rm web1 bash -lc '
    python manage.py collectstatic --noinput && 
    python manage.py migrate --noinput
'

# Create superuser (optional, will skip if already exists)
print_status "Creating superuser..."
docker compose -f docker-compose.loadbalancer.yml run --rm web1 bash -lc '
    DJANGO_SUPERUSER_USERNAME=admin 
    DJANGO_SUPERUSER_EMAIL=admin@example.com 
    DJANGO_SUPERUSER_PASSWORD=Admin@123 
    python manage.py createsuperuser --noinput || true
'

# Start the load balancer services
print_status "Starting load balancer services..."
docker compose -f docker-compose.loadbalancer.yml up -d

# Wait for services to be healthy
print_status "Waiting for services to be healthy..."
sleep 15

# Check service health
print_status "Checking service health..."
max_attempts=30
attempt=1

while [ $attempt -le $max_attempts ]; do
    if curl -fsS http://localhost/health/ > /dev/null 2>&1; then
        print_status "✅ Load balancer is healthy!"
        break
    else
        print_warning "Attempt $attempt/$max_attempts: Waiting for services to be ready..."
        sleep 5
        ((attempt++))
    fi
done

if [ $attempt -gt $max_attempts ]; then
    print_error "❌ Services failed to become healthy within expected time."
    print_error "Checking logs..."
    docker compose -f docker-compose.loadbalancer.yml logs --tail=50
    exit 1
fi

# Verify all services are running
print_status "Verifying all services are running..."
if docker compose -f docker-compose.loadbalancer.yml ps | grep -q "Up"; then
    print_status "✅ Load balancer deployment successful!"
    
    echo ""
    print_header "=== Deployment Summary ==="
    print_status "🌐 Load Balancer: http://13.232.220.214"
    print_status "🔍 Health Check: http://13.232.220.214/health/"
    print_status "👤 Admin Panel: http://13.232.220.214/admin/"
    print_status "📊 Redis Commander: http://13.232.220.214:8081"
    print_status "📈 Nginx Metrics: http://13.232.220.214:9113/metrics"
    print_status "🔑 Admin Login: admin / Admin@123"
    
    echo ""
    print_status "Running services:"
    docker compose -f docker-compose.loadbalancer.yml ps
    
    echo ""
    print_status "Load balancer configuration:"
    print_status "  - 4 Django application instances (web1-web4)"
    print_status "  - Nginx load balancer with least_conn algorithm"
    print_status "  - Redis caching layer"
    print_status "  - Health monitoring and metrics"
    print_status "  - Rate limiting and security headers"
    print_status "  - Static file caching and compression"
    
    echo ""
    print_status "🎉 CampusHub360 Load Balancer is now running!"
    print_status "💡 Use 'docker compose -f docker-compose.loadbalancer.yml logs -f' to view logs"
    print_status "💡 Use 'docker compose -f docker-compose.loadbalancer.yml scale web1=6' to scale instances"
    
else
    print_error "❌ Load balancer deployment failed. Check the logs:"
    docker compose -f docker-compose.loadbalancer.yml logs
    exit 1
fi
