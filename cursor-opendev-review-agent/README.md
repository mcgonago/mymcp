# OpenDev Review Agent

An MCP agent for Cursor that analyzes OpenDev Gerrit reviews for OpenStack projects.

## Setup

1. **Create virtual environment and install dependencies:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Make the launch script executable:**
   ```bash
   chmod +x server.sh
   ```

3. **Configure Cursor:**
   
   Add this to your Cursor MCP settings (replace with your actual path):
   
   ```json
   {
     "mcpServers": {
       "opendev-reviewer-agent": {
         "command": "/absolute/path/to/cursor-opendev-review-agent/server.sh",
         "description": "Analyzes OpenDev Gerrit reviews to perform automated code review."
       }
     }
   }
   ```

## Usage

In Cursor, use the agent by mentioning it:

```
@opendev-reviewer-agent Analyze https://review.opendev.org/c/openstack/horizon/+/963261
```

## Features

- Fetches review metadata from Gerrit REST API
- Analyzes file changes with detailed statistics
- Provides comprehensive review prompts focusing on:
  - Code quality and OpenStack standards
  - Security implications
  - Performance impact
  - Backward compatibility
  - Test coverage and documentation

## Files

- `server.py` - Main MCP server with Gerrit API integration
- `server.sh` - Launch script that activates venv and runs server
- `requirements.txt` - Python dependencies


