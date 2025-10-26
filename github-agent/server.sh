#!/bin/bash
# This script launches the MCP server

# Get the directory of this script
SCRIPT_DIR="$(dirname "$0")"

# Load .env file if it exists
if [ -f "$SCRIPT_DIR/.env" ]; then
    export $(cat "$SCRIPT_DIR/.env" | grep -v '^#' | xargs)
fi

# Activate virtual environment and run server
source "$SCRIPT_DIR/venv/bin/activate"
python "$SCRIPT_DIR/server.py"
