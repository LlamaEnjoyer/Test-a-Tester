#!/bin/bash
# Format and lint all code

echo "========================================"
echo "  Format and Lint All Code"
echo "========================================"
echo ""

./format.sh
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Formatting failed"
    exit 1
fi

echo ""
echo "========================================"
echo ""

./lint.sh

echo ""
echo "========================================"
echo "  All Done!"
echo "========================================"
