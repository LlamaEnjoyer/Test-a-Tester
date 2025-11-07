#!/bin/bash
# validate-data.sh
# Validation script for CI/CD pipelines

set -e

echo "=================================="
echo "Data Validation Check"
echo "=================================="
echo ""

# Run validation
python validate_questions.py

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Data validation passed!"
    exit 0
else
    echo ""
    echo "✗ Data validation failed!"
    exit 1
fi
