#!/bin/bash

# MyCRM Test Runner Script
# This script provides easy commands to run different types of tests

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Navigate to backend directory
cd backend

print_header() {
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Function to run unit tests
run_unit_tests() {
    print_header "Running Unit Tests"
    python manage.py test --parallel --keepdb --verbosity=2
    if [ $? -eq 0 ]; then
        print_success "Unit tests passed!"
    else
        print_error "Unit tests failed!"
        exit 1
    fi
}

# Function to run tests with coverage
run_coverage() {
    print_header "Running Tests with Coverage"
    coverage run --source='.' manage.py test --keepdb
    coverage report
    coverage html
    print_success "Coverage report generated in htmlcov/index.html"
}

# Function to run performance tests
run_performance_tests() {
    print_header "Running Performance Tests"
    python manage.py test core.performance_tests --keepdb
    if [ $? -eq 0 ]; then
        print_success "Performance tests passed!"
    else
        print_error "Performance tests failed!"
    fi
}

# Function to run load tests
run_load_tests() {
    print_header "Running Load Tests"
    print_warning "Make sure the server is running!"
    python load_test.py
}

# Function to run specific app tests
run_app_tests() {
    print_header "Running Tests for $1"
    python manage.py test $1 --verbosity=2
}

# Function to run locust load tests
run_locust() {
    print_header "Starting Locust Load Testing"
    print_warning "Open http://localhost:8089 in your browser"
    locust -f locustfile.py --host=http://localhost:8000
}

# Function to check code quality
check_code_quality() {
    print_header "Checking Code Quality"
    
    # Check for migrations
    echo "Checking for pending migrations..."
    python manage.py makemigrations --check --dry-run
    
    # Check deployment readiness
    echo "Checking deployment configuration..."
    python manage.py check --deploy
    
    print_success "Code quality checks complete!"
}

# Function to run all tests
run_all_tests() {
    print_header "Running All Tests"
    
    echo "1. Unit Tests..."
    run_unit_tests
    
    echo ""
    echo "2. Performance Tests..."
    run_performance_tests
    
    echo ""
    echo "3. Code Quality Checks..."
    check_code_quality
    
    print_success "All tests completed successfully!"
}

# Function to setup test environment
setup_test_env() {
    print_header "Setting Up Test Environment"
    
    echo "Installing test dependencies..."
    pip install coverage locust django-debug-toolbar
    
    echo "Running migrations..."
    python manage.py migrate
    
    echo "Creating test data..."
    # You can add fixtures here if you have them
    
    print_success "Test environment ready!"
}

# Function to display help
show_help() {
    echo ""
    echo "MyCRM Test Runner"
    echo ""
    echo "Usage: ./run_tests.sh [command]"
    echo ""
    echo "Commands:"
    echo "  unit              - Run unit tests"
    echo "  coverage          - Run tests with coverage report"
    echo "  performance       - Run performance tests"
    echo "  load              - Run load tests (requires running server)"
    echo "  locust            - Start Locust for interactive load testing"
    echo "  app [name]        - Run tests for specific app"
    echo "  quality           - Check code quality"
    echo "  all               - Run all tests"
    echo "  setup             - Setup test environment"
    echo "  help              - Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./run_tests.sh unit"
    echo "  ./run_tests.sh app user_management"
    echo "  ./run_tests.sh coverage"
    echo "  ./run_tests.sh locust"
    echo ""
}

# Main script logic
case "${1:-help}" in
    unit)
        run_unit_tests
        ;;
    coverage)
        run_coverage
        ;;
    performance)
        run_performance_tests
        ;;
    load)
        run_load_tests
        ;;
    locust)
        run_locust
        ;;
    app)
        if [ -z "$2" ]; then
            print_error "Please specify an app name"
            echo "Example: ./run_tests.sh app user_management"
            exit 1
        fi
        run_app_tests "$2"
        ;;
    quality)
        check_code_quality
        ;;
    all)
        run_all_tests
        ;;
    setup)
        setup_test_env
        ;;
    help|*)
        show_help
        ;;
esac
