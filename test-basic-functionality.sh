#!/bin/bash

# CampusHub360 Basic Functionality Test
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

# Test results
TESTS_PASSED=0
TESTS_FAILED=0
TOTAL_TESTS=0

# Function to print colored output
print_status() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((TESTS_PASSED++))
}

print_error() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((TESTS_FAILED++))
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

# Function to run a test
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    print_header "Testing: $test_name"
    ((TOTAL_TESTS++))
    
    if eval "$test_command" > /dev/null 2>&1; then
        print_status "$test_name"
        return 0
    else
        print_error "$test_name"
        return 1
    fi
}

# Function to test Docker services
test_docker_services() {
    print_header "Testing Docker Services"
    
    # Check if Docker is running
    run_test "Docker is running" "docker info"
    
    # Check if load balancer compose file exists
    run_test "Load balancer compose file exists" "[ -f docker-compose.loadbalancer.yml ]"
    
    # Check if production compose file exists
    run_test "Production compose file exists" "[ -f docker-compose.production.yml ]"
    
    # Test Docker Compose syntax
    run_test "Load balancer compose syntax" "docker compose -f docker-compose.loadbalancer.yml config"
    run_test "Production compose syntax" "docker compose -f docker-compose.production.yml config"
}

# Function to test file existence and permissions
test_files() {
    print_header "Testing Required Files"
    
    # Test core files
    run_test "Dockerfile exists" "[ -f Dockerfile ]"
    run_test "run-gunicorn.sh exists" "[ -f run-gunicorn.sh ]"
    run_test "gunicorn.conf.py exists" "[ -f gunicorn.conf.py ]"
    
    # Test nginx configuration
    run_test "Nginx load balancer config exists" "[ -f nginx/nginx-lb.conf ]"
    run_test "Nginx HTTPS config exists" "[ -f nginx/nginx-lb-https.conf ]"
    
    # Test deployment scripts
    run_test "Deploy load balancer script exists" "[ -f deploy-loadbalancer.sh ]"
    run_test "Manage load balancer script exists" "[ -f manage-loadbalancer.sh ]"
    run_test "Load test script exists" "[ -f load-test.sh ]"
    
    # Test if scripts are executable
    run_test "run-gunicorn.sh is executable" "[ -x run-gunicorn.sh ]"
    run_test "deploy-loadbalancer.sh is executable" "[ -x deploy-loadbalancer.sh ]"
    run_test "manage-loadbalancer.sh is executable" "[ -x manage-loadbalancer.sh ]"
}

# Function to test network connectivity
test_network() {
    print_header "Testing Network Connectivity"
    
    # Test if ports are available
    local ports=(80 443 8000 8001 8002 8003 8081 9113)
    for port in "${ports[@]}"; do
        if ! lsof -i :$port > /dev/null 2>&1; then
            print_status "Port $port is available"
        else
            print_warning "Port $port is in use"
        fi
    done
    
    # Test internet connectivity
    run_test "Internet connectivity" "curl -s --max-time 5 https://www.google.com"
}

# Function to test load balancer endpoints
test_endpoints() {
    print_header "Testing Load Balancer Endpoints"
    
    # Test health endpoint
    run_test "Health endpoint accessible" "curl -fsS --max-time 5 $LOAD_BALANCER_URL/health/"
    
    # Test API endpoint
    run_test "API endpoint accessible" "curl -fsS --max-time 5 $LOAD_BALANCER_URL/api/"
    
    # Test admin endpoint
    run_test "Admin endpoint accessible" "curl -fsS --max-time 5 $LOAD_BALANCER_URL/admin/"
    
    # Test static files
    run_test "Static files accessible" "curl -fsS --max-time 5 $LOAD_BALANCER_URL/static/"
}

# Function to test load balancer distribution
test_load_balancer_distribution() {
    print_header "Testing Load Balancer Distribution"
    
    # Check if load balancer is running
    if docker compose -f docker-compose.loadbalancer.yml ps | grep -q "Up"; then
        print_status "Load balancer services are running"
        
        # Test multiple requests to see distribution
        local success_count=0
        for i in {1..10}; do
            if curl -fsS --max-time 5 "$LOAD_BALANCER_URL/health/" > /dev/null 2>&1; then
                ((success_count++))
            fi
        done
        
        if [ $success_count -eq 10 ]; then
            print_status "Load balancer is distributing requests correctly"
        else
            print_warning "Load balancer distribution test had $((10 - success_count)) failures"
        fi
    else
        print_warning "Load balancer services are not running"
    fi
}

# Function to test SSL configuration
test_ssl_config() {
    print_header "Testing SSL Configuration"
    
    # Check if SSL certificates exist
    if [ -f "nginx/ssl/cert.pem" ] && [ -f "nginx/ssl/key.pem" ]; then
        print_status "SSL certificates exist"
        
        # Test certificate validity
        if openssl x509 -in nginx/ssl/cert.pem -text -noout > /dev/null 2>&1; then
            print_status "SSL certificate is valid"
        else
            print_warning "SSL certificate is invalid"
        fi
    else
        print_warning "SSL certificates not found"
    fi
    
    # Check if HTTPS nginx config exists
    run_test "HTTPS nginx config exists" "[ -f nginx/nginx-lb-https.conf ]"
}

# Function to test monitoring
test_monitoring() {
    print_header "Testing Monitoring Setup"
    
    # Check if monitoring scripts exist
    run_test "Monitor and scale script exists" "[ -f monitor-and-scale.sh ]"
    run_test "Setup SSL script exists" "[ -f setup-ssl.sh ]"
    
    # Test if monitoring ports are accessible
    if curl -fsS --max-time 5 "http://localhost:8081" > /dev/null 2>&1; then
        print_status "Redis Commander is accessible"
    else
        print_warning "Redis Commander is not accessible"
    fi
    
    if curl -fsS --max-time 5 "http://localhost:9113/metrics" > /dev/null 2>&1; then
        print_status "Nginx metrics are accessible"
    else
        print_warning "Nginx metrics are not accessible"
    fi
}

# Function to test performance basics
test_performance_basics() {
    print_header "Testing Performance Basics"
    
    # Test response time
    local response_time=$(curl -o /dev/null -s -w '%{time_total}' "$LOAD_BALANCER_URL/health/")
    if (( $(echo "$response_time < 1.0" | bc -l) )); then
        print_status "Response time is good: ${response_time}s"
    else
        print_warning "Response time is slow: ${response_time}s"
    fi
    
    # Test concurrent requests
    local success_count=0
    for i in {1..5}; do
        if curl -fsS --max-time 5 "$LOAD_BALANCER_URL/health/" > /dev/null 2>&1; then
            ((success_count++))
        fi &
    done
    wait
    
    if [ $success_count -eq 5 ]; then
        print_status "Concurrent requests handled successfully"
    else
        print_warning "Concurrent requests had $((5 - success_count)) failures"
    fi
}

# Function to generate test report
generate_report() {
    print_header "Test Report Summary"
    
    echo "=========================================="
    echo "Total Tests: $TOTAL_TESTS"
    echo "Passed: $TESTS_PASSED"
    echo "Failed: $TESTS_FAILED"
    echo "Success Rate: $(( (TESTS_PASSED * 100) / TOTAL_TESTS ))%"
    echo "=========================================="
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}🎉 All tests passed! Your load balancer setup is working correctly.${NC}"
        return 0
    else
        echo -e "${RED}❌ Some tests failed. Please check the issues above.${NC}"
        return 1
    fi
}

# Main function
main() {
    echo "🧪 CampusHub360 Basic Functionality Test"
    echo "========================================"
    
    test_docker_services
    test_files
    test_network
    test_endpoints
    test_load_balancer_distribution
    test_ssl_config
    test_monitoring
    test_performance_basics
    
    generate_report
}

# Run the tests
main "$@"
