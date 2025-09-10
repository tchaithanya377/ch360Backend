#!/bin/bash

# CampusHub360 Health Monitoring and Auto-Scaling Script
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.loadbalancer.yml"
HEALTH_CHECK_URL="http://localhost/health/"
MIN_INSTANCES=2
MAX_INSTANCES=8
SCALE_UP_THRESHOLD=80
SCALE_DOWN_THRESHOLD=30
CHECK_INTERVAL=30

# Function to print colored output
print_status() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] [INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] [WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] [HEADER]${NC} $1"
}

# Function to get current CPU usage
get_cpu_usage() {
    docker stats --no-stream --format "table {{.CPUPerc}}" | grep -v "CPUPerc" | awk -F'%' '{sum+=$1} END {print int(sum/NR)}'
}

# Function to get current memory usage
get_memory_usage() {
    docker stats --no-stream --format "table {{.MemPerc}}" | grep -v "MemPerc" | awk -F'%' '{sum+=$1} END {print int(sum/NR)}'
}

# Function to get current number of instances
get_current_instances() {
    docker compose -f $COMPOSE_FILE ps | grep "web" | grep "Up" | wc -l
}

# Function to check health
check_health() {
    if curl -fsS $HEALTH_CHECK_URL > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to scale services
scale_services() {
    local target_instances=$1
    local current_instances=$(get_current_instances)
    
    if [ $target_instances -gt $current_instances ]; then
        print_status "Scaling UP from $current_instances to $target_instances instances"
        docker compose -f $COMPOSE_FILE up -d --scale web1=$target_instances
    elif [ $target_instances -lt $current_instances ]; then
        print_status "Scaling DOWN from $current_instances to $target_instances instances"
        docker compose -f $COMPOSE_FILE up -d --scale web1=$target_instances
    fi
}

# Function to restart unhealthy services
restart_unhealthy_services() {
    print_warning "Restarting unhealthy services..."
    docker compose -f $COMPOSE_FILE restart
    sleep 10
}

# Function to send alert (customize as needed)
send_alert() {
    local message=$1
    print_error "ALERT: $message"
    # Add your alert mechanism here (email, Slack, etc.)
    # Example: curl -X POST -H 'Content-type: application/json' --data '{"text":"'$message'"}' YOUR_SLACK_WEBHOOK_URL
}

# Main monitoring loop
print_header "Starting CampusHub360 Health Monitoring and Auto-Scaling"
print_status "Configuration:"
print_status "  - Min instances: $MIN_INSTANCES"
print_status "  - Max instances: $MAX_INSTANCES"
print_status "  - Scale up threshold: $SCALE_UP_THRESHOLD%"
print_status "  - Scale down threshold: $SCALE_DOWN_THRESHOLD%"
print_status "  - Check interval: $CHECK_INTERVAL seconds"

while true; do
    print_status "=== Health Check Cycle ==="
    
    # Check overall health
    if ! check_health; then
        print_error "Health check failed!"
        restart_unhealthy_services
        
        # If still unhealthy after restart, send alert
        sleep 30
        if ! check_health; then
            send_alert "CampusHub360 is unhealthy after restart attempt"
        fi
        continue
    fi
    
    # Get current metrics
    cpu_usage=$(get_cpu_usage)
    memory_usage=$(get_memory_usage)
    current_instances=$(get_current_instances)
    
    print_status "Current metrics:"
    print_status "  - CPU Usage: ${cpu_usage}%"
    print_status "  - Memory Usage: ${memory_usage}%"
    print_status "  - Active Instances: $current_instances"
    
    # Determine if scaling is needed
    target_instances=$current_instances
    
    # Scale up logic
    if [ $cpu_usage -gt $SCALE_UP_THRESHOLD ] || [ $memory_usage -gt $SCALE_UP_THRESHOLD ]; then
        if [ $current_instances -lt $MAX_INSTANCES ]; then
            target_instances=$((current_instances + 1))
            print_warning "High resource usage detected. Scaling up to $target_instances instances"
        else
            print_warning "High resource usage but already at max instances ($MAX_INSTANCES)"
        fi
    fi
    
    # Scale down logic
    if [ $cpu_usage -lt $SCALE_DOWN_THRESHOLD ] && [ $memory_usage -lt $SCALE_DOWN_THRESHOLD ]; then
        if [ $current_instances -gt $MIN_INSTANCES ]; then
            target_instances=$((current_instances - 1))
            print_status "Low resource usage detected. Scaling down to $target_instances instances"
        fi
    fi
    
    # Apply scaling if needed
    if [ $target_instances -ne $current_instances ]; then
        scale_services $target_instances
        sleep 30  # Wait for scaling to complete
    else
        print_status "No scaling needed"
    fi
    
    # Show current status
    print_status "Current service status:"
    docker compose -f $COMPOSE_FILE ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
    
    print_status "Waiting $CHECK_INTERVAL seconds for next check..."
    sleep $CHECK_INTERVAL
done
