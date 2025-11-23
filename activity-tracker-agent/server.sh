#!/bin/bash

# Activity Tracker MCP Server Startup Script
# This script activates the Python virtual environment and starts the FastMCP server

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the agent directory
cd "$SCRIPT_DIR" || exit 1

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Error: Virtual environment not found at $SCRIPT_DIR/venv" >&2
    echo "Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt" >&2
    exit 1
fi

# Load environment variables from .env if it exists
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Start the MCP server in stdio mode
exec python server.py stdio



