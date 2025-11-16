#!/bin/bash

echo "Running All Shepherd Backend Tests"
echo "=================================="
echo

# Run simple tests
echo "1. Simple Tests (Core Logic)"
echo "----------------------------"
make -f simple_makefile test
SIMPLE_RESULT=$?
echo

# Run mock framework tests
echo "2. Mock Framework Tests"
echo "----------------------"
make -f mock_makefile test
MOCK_RESULT=$?
echo

# Run integration tests
echo "3. Integration Tests (Mock-based)"
echo "--------------------------------"
make -f integration_makefile test
INTEGRATION_RESULT=$?
echo

# Run backend component tests
echo "4. Backend Component Tests (Mock-based)"
echo "---------------------------------------"
make -f backend_component_makefile test
COMPONENT_RESULT=$?
echo

# Run minimal JUCE-like tests
echo "5. Minimal JUCE-like Tests (Proof of Concept)"
echo "----------------------------------------------"
make -f minimal_juce_makefile test
JUCE_RESULT=$?
echo

# Summary
echo "Test Summary"
echo "============"
if [ $SIMPLE_RESULT -eq 0 ]; then
    echo "✅ Simple Tests: PASSED"
else
    echo "❌ Simple Tests: FAILED"
fi

if [ $MOCK_RESULT -eq 0 ]; then
    echo "✅ Mock Framework Tests: PASSED"
else
    echo "❌ Mock Framework Tests: FAILED"
fi

if [ $INTEGRATION_RESULT -eq 0 ]; then
    echo "✅ Integration Tests: PASSED"
else
    echo "❌ Integration Tests: FAILED"
fi

if [ $COMPONENT_RESULT -eq 0 ]; then
    echo "✅ Backend Component Tests: PASSED"
else
    echo "❌ Backend Component Tests: FAILED"
fi

if [ $JUCE_RESULT -eq 0 ]; then
    echo "✅ Minimal JUCE-like Tests: PASSED"
else
    echo "❌ Minimal JUCE-like Tests: FAILED"
fi

# Overall result
TOTAL_FAILURES=$((SIMPLE_RESULT + MOCK_RESULT + INTEGRATION_RESULT + COMPONENT_RESULT + JUCE_RESULT))
if [ $TOTAL_FAILURES -eq 0 ]; then
    echo
    echo "🎉 All tests passed!"
    exit 0
else
    echo
    echo "💥 $TOTAL_FAILURES test suite(s) failed"
    exit 1
fi