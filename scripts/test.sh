#!/bin/bash
# Run all tests

echo "========================================"
echo "  Running All Tests"
echo "========================================"
echo ""

# Track failures
FAILED=0

# Run each test file
for test_file in tests/test_*.py; do
    if [ -f "$test_file" ]; then
        echo "Running $(basename "$test_file")..."
        python "$test_file"
        if [ $? -ne 0 ]; then
            FAILED=1
            echo "❌ $(basename "$test_file") failed!"
        fi
        echo ""
    fi
done

echo "========================================"
if [ $FAILED -eq 0 ]; then
    echo "✅ All tests passed!"
else
    echo "❌ Some tests failed!"
    exit 1
fi
echo "========================================"
