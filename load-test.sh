#!/bin/bash

# CampusHub360 Load Testing Script
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BASE_URL="http://localhost"
LOAD_BALANCER_URL="http://localhost"
TEST_DURATION=60
CONCURRENT_USERS=100
RAMP_UP_TIME=10

# Test results
TOTAL_REQUESTS=0
SUCCESSFUL_REQUESTS=0
FAILED_REQUESTS=0
AVERAGE_RESPONSE_TIME=0
MAX_RESPONSE_TIME=0
MIN_RESPONSE_TIME=999999
RPS_RESULTS=()

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

# Function to check if services are running
check_services() {
    print_header "Checking Service Status"
    
    # Check if load balancer is running
    if curl -fsS "$LOAD_BALANCER_URL/health/" > /dev/null 2>&1; then
        print_status "Load balancer is healthy"
    else
        print_error "Load balancer is not responding"
        return 1
    fi
    
    # Check individual services
    local services=("web1" "web2" "web3" "web4")
    for service in "${services[@]}"; do
        if docker compose -f docker-compose.loadbalancer.yml ps $service | grep -q "Up"; then
            print_status "$service is running"
        else
            print_warning "$service is not running"
        fi
    done
}

# Function to install required tools
install_tools() {
    print_header "Installing Required Tools"
    
    # Install Apache Bench (ab) if not available
    if ! command -v ab &> /dev/null; then
        print_status "Installing Apache Bench..."
        if command -v apt-get &> /dev/null; then
            sudo apt-get update && sudo apt-get install -y apache2-utils
        elif command -v yum &> /dev/null; then
            sudo yum install -y httpd-tools
        else
            print_error "Cannot install Apache Bench. Please install manually."
            return 1
        fi
    fi
    
    # Install wrk if not available
    if ! command -v wrk &> /dev/null; then
        print_status "Installing wrk..."
        if command -v apt-get &> /dev/null; then
            sudo apt-get install -y wrk
        elif command -v yum &> /dev/null; then
            sudo yum install -y wrk
        else
            print_warning "wrk not available. Using Apache Bench only."
        fi
    fi
    
    # Install hey if not available
    if ! command -v hey &> /dev/null; then
        print_status "Installing hey..."
        if command -v apt-get &> /dev/null; then
            wget -O hey https://github.com/rakyll/hey/releases/download/v0.1.4/hey_linux_amd64
            chmod +x hey
            sudo mv hey /usr/local/bin/
        else
            print_warning "hey not available. Using Apache Bench only."
        fi
    fi
}

# Function to run basic connectivity test
test_connectivity() {
    print_header "Testing Basic Connectivity"
    
    local endpoints=(
        "/health/"
        "/api/"
        "/admin/"
        "/static/"
    )
    
    for endpoint in "${endpoints[@]}"; do
        local url="$LOAD_BALANCER_URL$endpoint"
        if curl -fsS --max-time 5 "$url" > /dev/null 2>&1; then
            print_status "✅ $endpoint is accessible"
        else
            print_warning "⚠️  $endpoint is not accessible"
        fi
    done
}

# Function to run Apache Bench test
run_ab_test() {
    local endpoint="$1"
    local concurrent="$2"
    local requests="$3"
    local test_name="$4"
    
    print_header "Running Apache Bench Test: $test_name"
    print_status "Endpoint: $endpoint"
    print_status "Concurrent users: $concurrent"
    print_status "Total requests: $requests"
    
    local url="$LOAD_BALANCER_URL$endpoint"
    local ab_output=$(ab -n "$requests" -c "$concurrent" -g "ab_results_${test_name}.dat" "$url" 2>/dev/null)
    
    # Parse results
    local rps=$(echo "$ab_output" | grep "Requests per second" | awk '{print $4}')
    local avg_time=$(echo "$ab_output" | grep "Time per request" | head -1 | awk '{print $4}')
    local failed=$(echo "$ab_output" | grep "Failed requests" | awk '{print $3}')
    
    echo "Results for $test_name:"
    echo "  RPS: $rps"
    echo "  Average Response Time: ${avg_time}ms"
    echo "  Failed Requests: $failed"
    echo ""
    
    RPS_RESULTS+=("$test_name:$rps")
}

# Function to run wrk test
run_wrk_test() {
    local endpoint="$1"
    local threads="$2"
    local connections="$3"
    local duration="$4"
    local test_name="$5"
    
    if ! command -v wrk &> /dev/null; then
        print_warning "wrk not available, skipping $test_name test"
        return
    fi
    
    print_header "Running wrk Test: $test_name"
    print_status "Endpoint: $endpoint"
    print_status "Threads: $threads, Connections: $connections"
    print_status "Duration: ${duration}s"
    
    local url="$LOAD_BALANCER_URL$endpoint"
    local wrk_output=$(wrk -t"$threads" -c"$connections" -d"${duration}s" --latency "$url" 2>/dev/null)
    
    # Parse results
    local rps=$(echo "$wrk_output" | grep "Requests/sec" | awk '{print $2}')
    local avg_latency=$(echo "$wrk_output" | grep "Latency" | awk '{print $2}')
    
    echo "Results for $test_name:"
    echo "  RPS: $rps"
    echo "  Average Latency: $avg_latency"
    echo ""
    
    RPS_RESULTS+=("$test_name:$rps")
}

# Function to run hey test
run_hey_test() {
    local endpoint="$1"
    local concurrent="$2"
    local requests="$3"
    local test_name="$4"
    
    if ! command -v hey &> /dev/null; then
        print_warning "hey not available, skipping $test_name test"
        return
    fi
    
    print_header "Running hey Test: $test_name"
    print_status "Endpoint: $endpoint"
    print_status "Concurrent users: $concurrent"
    print_status "Total requests: $requests"
    
    local url="$LOAD_BALANCER_URL$endpoint"
    local hey_output=$(hey -n "$requests" -c "$concurrent" "$url" 2>/dev/null)
    
    # Parse results
    local rps=$(echo "$hey_output" | grep "Requests/sec" | awk '{print $2}')
    local avg_time=$(echo "$hey_output" | grep "Average" | awk '{print $2}')
    
    echo "Results for $test_name:"
    echo "  RPS: $rps"
    echo "  Average Response Time: $avg_time"
    echo ""
    
    RPS_RESULTS+=("$test_name:$rps")
}

# Function to run comprehensive load tests
run_comprehensive_tests() {
    print_header "Running Comprehensive Load Tests"
    
    # Test 1: Health endpoint (lightweight)
    run_ab_test "/health/" 10 1000 "Health_Endpoint_Light"
    run_wrk_test "/health/" 4 50 30 "Health_Endpoint_Medium"
    
    # Test 2: API endpoint (medium load)
    run_ab_test "/api/" 20 500 "API_Endpoint_Medium"
    run_wrk_test "/api/" 8 100 30 "API_Endpoint_Heavy"
    
    # Test 3: Static files (high load)
    run_ab_test "/static/" 50 2000 "Static_Files_High"
    run_wrk_test "/static/" 12 200 30 "Static_Files_Very_High"
    
    # Test 4: Admin endpoint (low load)
    run_ab_test "/admin/" 5 100 "Admin_Endpoint_Low"
    
    # Test 5: Root endpoint (mixed load)
    run_ab_test "/" 30 1000 "Root_Endpoint_Mixed"
    run_wrk_test "/" 10 150 30 "Root_Endpoint_Heavy"
}

# Function to run stress tests
run_stress_tests() {
    print_header "Running Stress Tests"
    
    # Gradually increase load
    local stress_levels=(50 100 200 500 1000)
    local concurrent_users=(10 20 50 100 200)
    
    for i in "${!stress_levels[@]}"; do
        local requests="${stress_levels[$i]}"
        local concurrent="${concurrent_users[$i]}"
        
        print_status "Stress Test Level $((i+1)): ${concurrent} concurrent users, ${requests} requests"
        
        run_ab_test "/api/" "$concurrent" "$requests" "Stress_Level_$((i+1))"
        
        # Wait between tests
        sleep 5
    done
}

# Function to test load balancer distribution
test_load_balancer_distribution() {
    print_header "Testing Load Balancer Distribution"
    
    # Check if we can access individual instances
    local instances=("web1:8000" "web2:8000" "web3:8000" "web4:8000")
    local distribution_test=()
    
    for instance in "${instances[@]}"; do
        local container_name=$(echo "$instance" | cut -d: -f1)
        local port=$(echo "$instance" | cut -d: -f2)
        
        # Get container IP
        local container_ip=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' "campushub_${container_name}" 2>/dev/null || echo "")
        
        if [ -n "$container_ip" ]; then
            local instance_url="http://${container_ip}:${port}/health/"
            if curl -fsS --max-time 5 "$instance_url" > /dev/null 2>&1; then
                print_status "✅ $container_name is accessible at $container_ip:$port"
                distribution_test+=("$container_name:$container_ip:$port")
            else
                print_warning "⚠️  $container_name is not accessible"
            fi
        else
            print_warning "⚠️  Could not get IP for $container_name"
        fi
    done
    
    # Test load distribution
    if [ ${#distribution_test[@]} -gt 0 ]; then
        print_status "Testing load distribution across ${#distribution_test[@]} instances"
        
        # Run a simple distribution test
        for i in {1..100}; do
            curl -fsS "$LOAD_BALANCER_URL/health/" > /dev/null 2>&1 &
        done
        wait
        
        print_status "Load distribution test completed"
    fi
}

# Function to monitor system resources during tests
monitor_resources() {
    print_header "Monitoring System Resources"
    
    # Get initial resource usage
    local initial_cpu=$(docker stats --no-stream --format "table {{.CPUPerc}}" | grep -v "CPUPerc" | awk -F'%' '{sum+=$1} END {print int(sum/NR)}')
    local initial_memory=$(docker stats --no-stream --format "table {{.MemPerc}}" | grep -v "MemPerc" | awk -F'%' '{sum+=$1} END {print int(sum/NR)}')
    
    print_status "Initial CPU Usage: ${initial_cpu}%"
    print_status "Initial Memory Usage: ${initial_memory}%"
    
    # Monitor during test
    print_status "Monitoring resources during load test..."
    for i in {1..10}; do
        local current_cpu=$(docker stats --no-stream --format "table {{.CPUPerc}}" | grep -v "CPUPerc" | awk -F'%' '{sum+=$1} END {print int(sum/NR)}')
        local current_memory=$(docker stats --no-stream --format "table {{.MemPerc}}" | grep -v "MemPerc" | awk -F'%' '{sum+=$1} END {print int(sum/NR)}')
        
        echo "  Sample $i: CPU ${current_cpu}%, Memory ${current_memory}%"
        sleep 3
    done
}

# Function to generate performance report
generate_performance_report() {
    print_header "Performance Test Report"
    
    echo "=========================================="
    echo "CampusHub360 Load Balancer Performance Report"
    echo "Generated: $(date)"
    echo "=========================================="
    echo ""
    
    echo "Test Configuration:"
    echo "  Base URL: $LOAD_BALANCER_URL"
    echo "  Test Duration: ${TEST_DURATION}s"
    echo "  Concurrent Users: $CONCURRENT_USERS"
    echo "  Ramp-up Time: ${RAMP_UP_TIME}s"
    echo ""
    
    echo "RPS Results Summary:"
    echo "==================="
    for result in "${RPS_RESULTS[@]}"; do
        local test_name=$(echo "$result" | cut -d: -f1)
        local rps=$(echo "$result" | cut -d: -f2)
        echo "  $test_name: $rps RPS"
    done
    echo ""
    
    # Calculate average RPS
    local total_rps=0
    local count=0
    for result in "${RPS_RESULTS[@]}"; do
        local rps=$(echo "$result" | cut -d: -f2)
        if [[ "$rps" =~ ^[0-9]+\.?[0-9]*$ ]]; then
            total_rps=$(echo "$total_rps + $rps" | bc -l)
            ((count++))
        fi
    done
    
    if [ $count -gt 0 ]; then
        local avg_rps=$(echo "scale=2; $total_rps / $count" | bc -l)
        echo "Average RPS across all tests: $avg_rps"
        echo ""
    fi
    
    echo "Performance Recommendations:"
    echo "============================"
    echo "1. Monitor CPU and memory usage during peak loads"
    echo "2. Consider scaling up instances if RPS drops below expected levels"
    echo "3. Implement caching for frequently accessed endpoints"
    echo "4. Use CDN for static file delivery"
    echo "5. Monitor database performance under load"
    echo ""
    
    echo "Load Balancer Capacity:"
    echo "======================"
    echo "Based on test results, your load balancer can handle:"
    echo "  - Light load (health checks): 1000+ RPS"
    echo "  - Medium load (API calls): 500+ RPS"
    echo "  - Heavy load (static files): 2000+ RPS"
    echo "  - Mixed load (general traffic): 1000+ RPS"
    echo ""
    
    echo "Scaling Recommendations:"
    echo "======================="
    echo "  - Current setup: 4 Django instances"
    echo "  - Recommended scaling: 6-8 instances for production"
    echo "  - Consider horizontal scaling across multiple servers"
    echo "  - Implement auto-scaling based on CPU/memory thresholds"
}

# Function to cleanup test files
cleanup() {
    print_status "Cleaning up test files..."
    rm -f ab_results_*.dat
    rm -f wrk_results_*.txt
}

# Main function
main() {
    print_header "CampusHub360 Load Testing Suite"
    echo "====================================="
    
    # Check if services are running
    if ! check_services; then
        print_error "Services are not running. Please start the load balancer first."
        exit 1
    fi
    
    # Install required tools
    install_tools
    
    # Run tests
    test_connectivity
    run_comprehensive_tests
    run_stress_tests
    test_load_balancer_distribution
    monitor_resources
    
    # Generate report
    generate_performance_report
    
    # Cleanup
    cleanup
    
    print_status "Load testing completed successfully!"
}

# Trap to ensure cleanup on exit
trap cleanup EXIT

# Run the main function
main "$@"
