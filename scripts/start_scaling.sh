#!/bin/bash
# Script to start horizontal scaling setup

echo "🚀 Starting CampusHub360 Horizontal Scaling Setup"
echo "=================================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if required files exist
if [ ! -f "docker-compose.scaling.yml" ]; then
    echo "❌ docker-compose.scaling.yml not found"
    exit 1
fi

if [ ! -f "nginx.conf" ]; then
    echo "❌ nginx.conf not found"
    exit 1
fi

if [ ! -f "gunicorn.conf.py" ]; then
    echo "❌ gunicorn.conf.py not found"
    exit 1
fi

echo "✅ All required files found"

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.scaling.yml down

# Build and start services
echo "🔨 Building and starting services..."
docker-compose -f docker-compose.scaling.yml up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service health
echo "🏥 Checking service health..."

# Check Django instances
for port in 8000 8001 8002 8003; do
    if curl -f http://localhost:$port/health/ > /dev/null 2>&1; then
        echo "✅ Django instance on port $port is healthy"
    else
        echo "❌ Django instance on port $port is not responding"
    fi
done

# Check Redis
if docker exec campushub_redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis is healthy"
else
    echo "❌ Redis is not responding"
fi

# Check PostgreSQL
if docker exec campushub_postgres pg_isready -U campushub -d campushub360 > /dev/null 2>&1; then
    echo "✅ PostgreSQL is healthy"
else
    echo "❌ PostgreSQL is not responding"
fi

# Check NGINX
if curl -f http://localhost/health/ > /dev/null 2>&1; then
    echo "✅ NGINX load balancer is healthy"
else
    echo "❌ NGINX load balancer is not responding"
fi

echo ""
echo "🎉 Horizontal scaling setup complete!"
echo "=================================================="
echo "📊 Services running:"
echo "   • NGINX Load Balancer: http://localhost"
echo "   • Django Instance 1: http://localhost:8000"
echo "   • Django Instance 2: http://localhost:8001"
echo "   • Django Instance 3: http://localhost:8002"
echo "   • Django Instance 4: http://localhost:8003"
echo "   • Redis Cache: localhost:6379"
echo "   • PostgreSQL DB: localhost:5432"
echo "   • Redis Commander: http://localhost:8081"
echo ""
echo "🧪 Test the setup:"
echo "   curl http://localhost/health/"
echo "   curl http://localhost/api/health/"
echo ""
echo "📈 Expected performance:"
echo "   • 4x Django instances"
echo "   • Load balanced requests"
echo "   • Redis caching"
echo "   • Target: 5,000+ RPS"
echo ""
echo "🛑 To stop: docker-compose -f docker-compose.scaling.yml down"
