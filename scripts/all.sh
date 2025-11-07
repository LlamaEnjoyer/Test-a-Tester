#!/bin/bash
# Format and lint all code

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "========================================"
echo "  Format, Lint, and Test All Code"
echo "========================================"
echo ""

"$SCRIPT_DIR/format.sh"
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Formatting failed"
    exit 1
fi

echo ""
echo "========================================"
echo ""

"$SCRIPT_DIR/lint.sh"
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Linting failed"
    exit 1
fi

echo ""
echo "========================================"
echo ""

"$SCRIPT_DIR/test.sh"
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Tests failed"
    exit 1
fi

echo ""
echo "========================================"
echo "  All Done!"
echo "========================================"
