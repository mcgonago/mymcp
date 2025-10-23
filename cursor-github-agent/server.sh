#!/bin/bash
# This script launches the MCP server

source "$(dirname "$0")/venv/bin/activate"
python "$(dirname "$0")/server.py"
