#!/bin/bash
# Format code with isort and black

echo "Running isort..."
python -m isort .
if [ $? -ne 0 ]; then
    echo "ERROR: isort failed"
    exit 1
fi

echo ""
echo "Running black..."
python -m black .
if [ $? -ne 0 ]; then
    echo "ERROR: black failed"
    exit 1
fi

echo ""
echo "✅ Code formatting complete!"
