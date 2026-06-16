#!/bin/bash
# Molnify App Development - Python Environment Setup
# This script creates a virtual environment with dependencies for working with Excel files

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

echo "Setting up Molnify app development environment..."

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not found."
    echo "Please install Python 3 and try again."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
else
    echo "Virtual environment already exists."
fi

# Activate and install dependencies
echo "Installing dependencies..."
source "$VENV_DIR/bin/activate"

if ! pip install --upgrade pip; then
    echo "Error: Failed to upgrade pip."
    exit 1
fi

if ! pip install -r "$SCRIPT_DIR/requirements.txt"; then
    echo "Error: Failed to install dependencies from requirements.txt."
    exit 1
fi

echo ""
echo "Setup complete!"
echo ""
echo "To activate the environment, run:"
echo "  source $VENV_DIR/bin/activate"
echo ""
echo "Or use this one-liner from any directory:"
echo "  source \"$VENV_DIR/bin/activate\""
