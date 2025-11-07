#!/bin/bash
# Format and lint all code

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "========================================"
echo "  Format and Lint All Code"
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

echo ""
echo "========================================"
echo "  All Done!"
echo "========================================"
