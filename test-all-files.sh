#!/bin/bash

# CampusHub360 Comprehensive File Testing Script
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results tracking
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

# Function to check file syntax
check_file_syntax() {
    local file="$1"
    local file_type="$2"
    
    case "$file_type" in
        "yaml")
            if command -v yamllint &> /dev/null; then
                yamllint "$file" > /dev/null 2>&1
            else
                # Basic YAML syntax check
                python3 -c "import yaml; yaml.safe_load(open('$file'))" > /dev/null 2>&1
            fi
            ;;
        "json")
            python3 -c "import json; json.load(open('$file'))" > /dev/null 2>&1
            ;;
        "bash")
            bash -n "$file" > /dev/null 2>&1
            ;;
        "nginx")
            nginx -t -c "$file" > /dev/null 2>&1
            ;;
    esac
}

# Function to check Docker Compose files
check_docker_compose() {
    local file="$1"
    docker compose -f "$file" config > /dev/null 2>&1
}

# Function to check if required tools are installed
check_dependencies() {
    print_header "Checking Dependencies"
    
    local deps=("docker" "docker-compose" "curl" "openssl" "python3")
    for dep in "${deps[@]}"; do
        if command -v "$dep" &> /dev/null; then
            print_status "$dep is installed"
        else
            print_error "$dep is not installed"
        fi
    done
}

# Function to test Docker Compose files
test_docker_compose_files() {
    print_header "Testing Docker Compose Files"
    
    local compose_files=(
        "docker-compose.production.yml"
        "docker-compose.loadbalancer.yml"
        "docker-compose.scaling.yml"
        "docker-compose.redis.yml"
    )
    
    for file in "${compose_files[@]}"; do
        if [ -f "$file" ]; then
            run_test "Docker Compose syntax: $file" "check_docker_compose '$file'"
        else
            print_warning "$file not found"
        fi
    done
}

# Function to test configuration files
test_config_files() {
    print_header "Testing Configuration Files"
    
    # Test nginx configurations
    if [ -f "nginx/nginx-lb.conf" ]; then
        run_test "Nginx load balancer config" "check_file_syntax 'nginx/nginx-lb.conf' 'nginx'"
    fi
    
    if [ -f "nginx/nginx-lb-https.conf" ]; then
        run_test "Nginx HTTPS config" "check_file_syntax 'nginx/nginx-lb-https.conf' 'nginx'"
    fi
    
    # Test gunicorn config
    if [ -f "gunicorn.conf.py" ]; then
        run_test "Gunicorn config" "python3 -c 'import gunicorn.conf'"
    fi
    
    # Test Django settings
    if [ -f "campshub360/settings.py" ]; then
        run_test "Django settings" "python3 -c 'import campushub360.settings'"
    fi
}

# Function to test shell scripts
test_shell_scripts() {
    print_header "Testing Shell Scripts"
    
    local scripts=(
        "run-gunicorn.sh"
        "deploy-production.sh"
        "deploy-loadbalancer.sh"
        "manage-loadbalancer.sh"
        "monitor-and-scale.sh"
        "setup-ssl.sh"
        "fix-migrations.sh"
        "cleanup-ports.sh"
    )
    
    for script in "${scripts[@]}"; do
        if [ -f "$script" ]; then
            run_test "Shell script syntax: $script" "check_file_syntax '$script' 'bash'"
            
            # Check if script is executable
            if [ -x "$script" ]; then
                print_status "$script is executable"
            else
                print_warning "$script is not executable"
            fi
        else
            print_warning "$script not found"
        fi
    done
}

# Function to test JSON files
test_json_files() {
    print_header "Testing JSON Files"
    
    local json_files=(
        "CampusHub360_Postman_Collection.json"
        "infra/ecs-autoscaling.json"
    )
    
    for file in "${json_files[@]}"; do
        if [ -f "$file" ]; then
            run_test "JSON syntax: $file" "check_file_syntax '$file' 'json'"
        else
            print_warning "$file not found"
        fi
    done
}

# Function to test file permissions
test_file_permissions() {
    print_header "Testing File Permissions"
    
    # Check if required directories exist
    local dirs=("nginx" "nginx/ssl" "static" "media")
    for dir in "${dirs[@]}"; do
        if [ -d "$dir" ]; then
            print_status "Directory exists: $dir"
        else
            print_warning "Directory missing: $dir"
        fi
    done
    
    # Check if static directory has content
    if [ -d "static" ] && [ "$(ls -A static 2>/dev/null)" ]; then
        print_status "Static directory has content"
    else
        print_warning "Static directory is empty"
    fi
}

# Function to test Docker images
test_docker_images() {
    print_header "Testing Docker Images"
    
    # Check if Docker is running
    if docker info > /dev/null 2>&1; then
        print_status "Docker is running"
        
        # Check if we can build the image
        if [ -f "Dockerfile" ]; then
            run_test "Dockerfile syntax" "docker build --dry-run ."
        fi
    else
        print_error "Docker is not running"
    fi
}

# Function to test network connectivity
test_network_connectivity() {
    print_header "Testing Network Connectivity"
    
    # Test external connectivity
    run_test "Internet connectivity" "curl -s --max-time 5 https://www.google.com"
    
    # Test if ports are available
    local ports=(80 443 8000 8001 8002 8003 8081 9113)
    for port in "${ports[@]}"; do
        if ! lsof -i :$port > /dev/null 2>&1; then
            print_status "Port $port is available"
        else
            print_warning "Port $port is in use"
        fi
    done
}

# Function to test environment variables
test_environment() {
    print_header "Testing Environment Variables"
    
    # Check if required environment variables are set
    local env_vars=("SECRET_KEY" "POSTGRES_HOST" "REDIS_URL")
    for var in "${env_vars[@]}"; do
        if [ -n "${!var}" ]; then
            print_status "Environment variable $var is set"
        else
            print_warning "Environment variable $var is not set"
        fi
    done
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
        echo -e "${GREEN}🎉 All tests passed! Your setup is ready for deployment.${NC}"
        return 0
    else
        echo -e "${RED}❌ Some tests failed. Please fix the issues before deployment.${NC}"
        return 1
    fi
}

# Main test execution
main() {
    echo "🧪 CampusHub360 Comprehensive File Testing"
    echo "=========================================="
    
    check_dependencies
    test_docker_compose_files
    test_config_files
    test_shell_scripts
    test_json_files
    test_file_permissions
    test_docker_images
    test_network_connectivity
    test_environment
    
    generate_report
}

# Run the tests
main "$@"
