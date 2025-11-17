#!/bin/bash
# Simple test runner script for Push2Controller

echo "Running Push2Controller Tests..."
echo "================================="

cd "$(dirname "$0")"

# Check if pytest is available
if command -v pytest &> /dev/null; then
    echo "Using pytest..."
    pytest tests/ -v
else
    echo "Using unittest..."
    python tests/run_tests.py
fi

echo ""
echo "Test run complete!"