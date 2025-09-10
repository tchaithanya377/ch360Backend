#!/bin/bash

# CampusHub360 Load Balancer Management Script
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

COMPOSE_FILE="docker-compose.loadbalancer.yml"

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

# Function to show usage
show_usage() {
    echo "CampusHub360 Load Balancer Management Script"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  start                 Start the load balancer"
    echo "  stop                  Stop the load balancer"
    echo "  restart               Restart the load balancer"
    echo "  status                Show status of all services"
    echo "  logs [service]        Show logs (optionally for specific service)"
    echo "  scale <instances>     Scale web instances (2-8)"
    echo "  health                Check health of all services"
    echo "  stats                 Show resource usage statistics"
    echo "  backup                Backup configuration and data"
    echo "  restore <backup_file> Restore from backup"
    echo "  update                Update and restart services"
    echo "  monitor               Start monitoring and auto-scaling"
    echo "  ssl <type>            Setup SSL certificates"
    echo ""
    echo "Examples:"
    echo "  $0 start"
    echo "  $0 scale 6"
    echo "  $0 logs nginx-lb"
    echo "  $0 ssl letsencrypt campushub360.xyz admin@example.com"
}

# Function to start services
start_services() {
    print_header "Starting CampusHub360 Load Balancer..."
    docker compose -f $COMPOSE_FILE up -d
    print_status "Load balancer started successfully!"
    show_status
}

# Function to stop services
stop_services() {
    print_header "Stopping CampusHub360 Load Balancer..."
    docker compose -f $COMPOSE_FILE down
    print_status "Load balancer stopped successfully!"
}

# Function to restart services
restart_services() {
    print_header "Restarting CampusHub360 Load Balancer..."
    docker compose -f $COMPOSE_FILE restart
    print_status "Load balancer restarted successfully!"
    show_status
}

# Function to show status
show_status() {
    print_header "CampusHub360 Load Balancer Status"
    echo ""
    docker compose -f $COMPOSE_FILE ps
    echo ""
    
    # Check health
    if curl -fsS http://localhost/health/ > /dev/null 2>&1; then
        print_status "✅ Load balancer is healthy"
    else
        print_error "❌ Load balancer health check failed"
    fi
    
    # Show resource usage
    echo ""
    print_status "Resource Usage:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
}

# Function to show logs
show_logs() {
    local service=$1
    if [ -n "$service" ]; then
        print_header "Showing logs for $service..."
        docker compose -f $COMPOSE_FILE logs -f $service
    else
        print_header "Showing logs for all services..."
        docker compose -f $COMPOSE_FILE logs -f
    fi
}

# Function to scale services
scale_services() {
    local instances=$1
    
    if [ -z "$instances" ] || ! [[ "$instances" =~ ^[0-9]+$ ]]; then
        print_error "Please provide a valid number of instances (2-8)"
        exit 1
    fi
    
    if [ $instances -lt 2 ] || [ $instances -gt 8 ]; then
        print_error "Number of instances must be between 2 and 8"
        exit 1
    fi
    
    print_header "Scaling to $instances instances..."
    docker compose -f $COMPOSE_FILE up -d --scale web1=$instances
    print_status "Scaled to $instances instances successfully!"
    show_status
}

# Function to check health
check_health() {
    print_header "Health Check Results"
    
    # Check load balancer
    if curl -fsS http://localhost/health/ > /dev/null 2>&1; then
        print_status "✅ Load Balancer: Healthy"
    else
        print_error "❌ Load Balancer: Unhealthy"
    fi
    
    # Check individual services
    services=("web1" "web2" "web3" "web4" "redis" "nginx-lb")
    for service in "${services[@]}"; do
        if docker compose -f $COMPOSE_FILE ps $service | grep -q "Up"; then
            print_status "✅ $service: Running"
        else
            print_error "❌ $service: Not running"
        fi
    done
    
    # Check resource usage
    echo ""
    print_status "Resource Usage:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
}

# Function to show statistics
show_stats() {
    print_header "Load Balancer Statistics"
    
    # Container stats
    echo ""
    print_status "Container Statistics:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
    
    # Network stats
    echo ""
    print_status "Network Statistics:"
    docker network ls
    docker network inspect campushub360_campushub_network 2>/dev/null || print_warning "Network not found"
    
    # Volume stats
    echo ""
    print_status "Volume Statistics:"
    docker volume ls
    docker system df
}

# Function to backup
backup_data() {
    local backup_dir="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p $backup_dir
    
    print_header "Creating backup in $backup_dir..."
    
    # Backup configuration files
    cp docker-compose.loadbalancer.yml $backup_dir/
    cp -r nginx/ $backup_dir/
    cp *.sh $backup_dir/
    
    # Backup volumes
    docker run --rm -v campushub360_redis_data:/data -v $(pwd)/$backup_dir:/backup alpine tar czf /backup/redis_data.tar.gz -C /data .
    
    print_status "Backup created successfully in $backup_dir"
}

# Function to restore
restore_data() {
    local backup_file=$1
    
    if [ -z "$backup_file" ] || [ ! -d "$backup_file" ]; then
        print_error "Please provide a valid backup directory"
        exit 1
    fi
    
    print_header "Restoring from $backup_file..."
    
    # Stop services
    docker compose -f $COMPOSE_FILE down
    
    # Restore configuration
    cp $backup_file/docker-compose.loadbalancer.yml ./
    cp -r $backup_file/nginx/ ./
    
    # Restore volumes
    if [ -f "$backup_file/redis_data.tar.gz" ]; then
        docker run --rm -v campushub360_redis_data:/data -v $(pwd)/$backup_file:/backup alpine tar xzf /backup/redis_data.tar.gz -C /data
    fi
    
    # Start services
    docker compose -f $COMPOSE_FILE up -d
    
    print_status "Restore completed successfully!"
}

# Function to update services
update_services() {
    print_header "Updating CampusHub360 Load Balancer..."
    
    # Pull latest images
    docker compose -f $COMPOSE_FILE pull
    
    # Rebuild and restart
    docker compose -f $COMPOSE_FILE up -d --build
    
    print_status "Update completed successfully!"
    show_status
}

# Function to start monitoring
start_monitoring() {
    print_header "Starting monitoring and auto-scaling..."
    
    if [ -f "monitor-and-scale.sh" ]; then
        chmod +x monitor-and-scale.sh
        ./monitor-and-scale.sh &
        print_status "Monitoring started in background"
        print_status "Use 'ps aux | grep monitor-and-scale' to check if running"
    else
        print_error "monitor-and-scale.sh not found"
        exit 1
    fi
}

# Function to setup SSL
setup_ssl() {
    local ssl_type=$1
    shift
    
    if [ -f "setup-ssl.sh" ]; then
        chmod +x setup-ssl.sh
        ./setup-ssl.sh $ssl_type "$@"
    else
        print_error "setup-ssl.sh not found"
        exit 1
    fi
}

# Main script logic
case "${1:-}" in
    "start")
        start_services
        ;;
    "stop")
        stop_services
        ;;
    "restart")
        restart_services
        ;;
    "status")
        show_status
        ;;
    "logs")
        show_logs "$2"
        ;;
    "scale")
        scale_services "$2"
        ;;
    "health")
        check_health
        ;;
    "stats")
        show_stats
        ;;
    "backup")
        backup_data
        ;;
    "restore")
        restore_data "$2"
        ;;
    "update")
        update_services
        ;;
    "monitor")
        start_monitoring
        ;;
    "ssl")
        setup_ssl "$2" "$3" "$4"
        ;;
    *)
        show_usage
        ;;
esac
