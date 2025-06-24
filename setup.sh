#!/usr/bin/env bash

# Time MCP Server Setup Script

echo "Setting up Time MCP Server (Python)..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not installed. Please install Python 3.8 or later."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -e .

echo "Setup complete!"
echo ""
echo "To run the server:"
echo "  MCP Server: python -m time_mcp_server"
echo "  HTTP Server: python -m time_mcp_server --http"
echo "  Standalone: python -m time_mcp_server --standalone"
echo ""
echo "To run tests:"
echo "  pip install pytest"
echo "  pytest"
