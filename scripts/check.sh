#!/bin/bash
# Check formatting without making changes

echo "Checking isort..."
python -m isort --check-only .
if [ $? -ne 0 ]; then
    echo "ERROR: Imports need to be sorted. Run ./format.sh to fix."
    exit 1
fi

echo ""
echo "Checking black..."
python -m black --check .
if [ $? -ne 0 ]; then
    echo "ERROR: Code needs formatting. Run ./format.sh to fix."
    exit 1
fi

echo ""
echo "✅ Format check complete - no changes needed!"
