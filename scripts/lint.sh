#!/bin/bash
# Run all linters

echo "Running flake8..."
python -m flake8 .
if [ $? -ne 0 ]; then
    echo "WARNING: flake8 found issues"
fi

echo ""
echo "Running mypy..."
python -m mypy app.py
if [ $? -ne 0 ]; then
    echo "WARNING: mypy found type issues"
fi

echo ""
echo "✅ Linting complete!"
