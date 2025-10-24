# GitHub PR Review Agent

A simple MCP agent for Cursor that analyzes GitHub Pull Requests.

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
       "github-reviewer-agent": {
         "command": "/absolute/path/to/cursor-github-agent/server.sh",
         "description": "Analyzes GitHub pull requests to perform automated code review."
       }
     }
   }
   ```

## Usage

In Cursor, use the agent by mentioning it:

```
@github-reviewer-agent Review the PR at https://github.com/owner/repo/pull/123
```

## Files

- `server.py` - Main MCP server implementation
- `server.sh` - Launch script that activates venv and runs server
- `requirements.txt` - Python dependencies


