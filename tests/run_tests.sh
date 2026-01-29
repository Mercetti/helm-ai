#!/bin/bash

# Helm AI Test Runner
# This script runs different types of tests with appropriate configurations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
TEST_TYPE="all"
COVERAGE=true
PARALLEL=true
VERBOSE=false
REPORT_DIR="tests/reports"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--type)
            TEST_TYPE="$2"
            shift 2
            ;;
        -c|--coverage)
            COVERAGE="$2"
            shift 2
            ;;
        -p|--parallel)
            PARALLEL="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -r|--report-dir)
            REPORT_DIR="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  -t, --type TYPE     Test type: unit, integration, performance, all (default: all)"
            echo "  -c, --coverage BOOL Enable coverage (default: true)"
            echo "  -p, --parallel BOOL  Enable parallel execution (default: true)"
            echo "  -v, --verbose       Enable verbose output"
            echo "  -r, --report-dir DIR Report directory (default: tests/reports)"
            echo "  -h, --help          Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Create report directory
mkdir -p "$REPORT_DIR"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to run unit tests
run_unit_tests() {
    print_status "Running unit tests..."
    
    local pytest_args=(
        "tests/test_unit_*.py"
        "-m" "unit"
        "-v"
    )
    
    if [ "$COVERAGE" = "true" ]; then
        pytest_args+=(
            "--cov=src"
            "--cov-report=html:$REPORT_DIR/html/unit"
            "--cov-report=xml:$REPORT_DIR/coverage-unit.xml"
            "--cov-report=term-missing"
            "--cov-fail-under=80"
        )
    fi
    
    if [ "$PARALLEL" = "true" ]; then
        pytest_args+=("-n" "auto")
    fi
    
    if [ "$VERBOSE" = "true" ]; then
        pytest_args+=("-vv")
    fi
    
    pytest "${pytest_args[@]}"
    
    if [ $? -eq 0 ]; then
        print_success "Unit tests passed!"
    else
        print_error "Unit tests failed!"
        return 1
    fi
}

# Function to run integration tests
run_integration_tests() {
    print_status "Running integration tests..."
    
    local pytest_args=(
        "tests/test_integration_*.py"
        "-m" "integration"
        "-v"
    )
    
    if [ "$COVERAGE" = "true" ]; then
        pytest_args+=(
            "--cov=src"
            "--cov-report=html:$REPORT_DIR/html/integration"
            "--cov-report=xml:$REPORT_DIR/coverage-integration.xml"
            "--cov-append"
        )
    fi
    
    if [ "$VERBOSE" = "true" ]; then
        pytest_args+=("-vv")
    fi
    
    pytest "${pytest_args[@]}"
    
    if [ $? -eq 0 ]; then
        print_success "Integration tests passed!"
    else
        print_error "Integration tests failed!"
        return 1
    fi
}

# Function to run performance tests
run_performance_tests() {
    print_status "Running performance tests..."
    
    local pytest_args=(
        "tests/test_performance.py"
        "-m" "performance"
        "-v"
        "--benchmark-only"
        "--benchmark-sort=mean"
        "--benchmark-json=$REPORT_DIR/benchmark.json"
    )
    
    if [ "$VERBOSE" = "true" ]; then
        pytest_args+=("-vv")
    fi
    
    pytest "${pytest_args[@]}"
    
    if [ $? -eq 0 ]; then
        print_success "Performance tests passed!"
    else
        print_error "Performance tests failed!"
        return 1
    fi
}

# Function to run load tests
run_load_tests() {
    print_status "Running load tests..."
    
    # Check if Locust is available
    if ! command -v locust &> /dev/null; then
        print_warning "Locust not found. Install with: pip install locust"
        return 0
    fi
    
    # Run Locust load tests
    locust -f tests/load_test.py --headless --users 10 --spawn-rate 2 --run-time 60s --host http://localhost:5000 --html "$REPORT_DIR/locust_report.html"
    
    if [ $? -eq 0 ]; then
        print_success "Load tests completed!"
    else
        print_error "Load tests failed!"
        return 1
    fi
}

# Function to run security tests
run_security_tests() {
    print_status "Running security tests..."
    
    # Run Bandit security analysis
    if command -v bandit &> /dev/null; then
        print_status "Running Bandit security analysis..."
        bandit -r src/ -f json -o "$REPORT_DIR/bandit-report.json" || true
        bandit -r src/ -f html -o "$REPORT_DIR/bandit-report.html" || true
    else
        print_warning "Bandit not found. Install with: pip install bandit"
    fi
    
    # Run Safety dependency check
    if command -v safety &> /dev/null; then
        print_status "Running Safety dependency check..."
        safety check --json --output "$REPORT_DIR/safety-report.json" || true
        safety check --html --output "$REPORT_DIR/safety-report.html" || true
    else
        print_warning "Safety not found. Install with: pip install safety"
    fi
    
    print_success "Security tests completed!"
}

# Function to generate test report
generate_report() {
    print_status "Generating test report..."
    
    local report_file="$REPORT_DIR/test-summary.html"
    
    cat > "$report_file" << EOF
<!DOCTYPE html>
<html>
<head>
    <title>Helm AI Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #f0f0f0; padding: 20px; border-radius: 5px; }
        .section { margin: 20px 0; }
        .success { color: green; }
        .error { color: red; }
        .warning { color: orange; }
        .link { margin: 5px 0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Helm AI Test Report</h1>
        <p>Generated on: $(date)</p>
        <p>Test Type: $TEST_TYPE</p>
    </div>
    
    <div class="section">
        <h2>Test Results</h2>
        <div class="link">
            <a href="html/index.html">Coverage Report</a>
        </div>
        <div class="link">
            <a href="junit.xml">JUnit XML Report</a>
        </div>
        <div class="link">
            <a href="report.html">Pytest HTML Report</a>
        </div>
    </div>
    
    <div class="section">
        <h2>Security Reports</h2>
        <div class="link">
            <a href="bandit-report.html">Bandit Security Report</a>
        </div>
        <div class="link">
            <a href="safety-report.html">Safety Dependency Report</a>
        </div>
    </div>
    
    <div class="section">
        <h2>Performance Reports</h2>
        <div class="link">
            <a href="benchmark.json">Benchmark Results</a>
        </div>
        <div class="link">
            <a href="locust_report.html">Load Test Report</a>
        </div>
    </div>
</body>
</html>
EOF
    
    print_success "Test report generated: $report_file"
}

# Main execution
main() {
    print_status "Starting Helm AI test suite..."
    print_status "Test type: $TEST_TYPE"
    print_status "Coverage: $COVERAGE"
    print_status "Parallel: $PARALLEL"
    print_status "Report directory: $REPORT_DIR"
    
    # Set environment variables
    export ENVIRONMENT=test
    export TESTING=true
    export LOG_LEVEL=DEBUG
    
    # Run tests based on type
    case $TEST_TYPE in
        "unit")
            run_unit_tests
            ;;
        "integration")
            run_integration_tests
            ;;
        "performance")
            run_performance_tests
            ;;
        "load")
            run_load_tests
            ;;
        "security")
            run_security_tests
            ;;
        "all")
            run_unit_tests || exit 1
            run_integration_tests || exit 1
            run_performance_tests || exit 1
            run_security_tests
            ;;
        *)
            print_error "Unknown test type: $TEST_TYPE"
            exit 1
            ;;
    esac
    
    # Generate report
    generate_report
    
    print_success "All tests completed successfully!"
    print_status "View reports at: $REPORT_DIR"
}

# Run main function
main "$@"
