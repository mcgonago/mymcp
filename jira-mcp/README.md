# Jira MCP Agent

A containerized Python MCP server for Cursor to provide access to Jira.

> [!IMPORTANT]
> This project is experimental and was initially created as a learning exercise.

## Prerequisites

- **podman** - Install with `sudo dnf install podman` (Fedora/RHEL) or `brew install podman` (macOS)
- **make** - Usually pre-installed on most systems

## Quick Start

1. **Build the image:**
   ```bash
   make build
   ```

2. **Configure Cursor:**
   
   Copy `example.mcp.json` and modify it for your setup:
   ```json
   {
     "mcpServers": {
       "jiraMcp": {
         "command": "podman",
         "args": [
           "run",
           "--rm",
           "-i",
           "--env-file",
           "/path/to/.rh-jira-mcp.env",
           "jira-mcp:latest"
         ]
       }
     }
   }
   ```

3. **Prepare a Jira token:**
   - Create a personal access token in your Jira instance
   - Copy `example.env` to `~/.rh-jira-mcp.env` and add your token

## Available Tools

This MCP server provides 20+ tools including:

### Issue Search
- `get_jira` - Get details for a specific Jira issue
- `search_issues` - Search issues using JQL

### Project Management
- `list_projects` - List all projects
- `get_project` - Get project details
- `get_project_components` - Get components for a project
- And more...

### Board & Sprint Management
- `list_boards` - List all boards
- `get_board` - Get board details
- `list_sprints` - List sprints for a board
- And more...

### User Management
- `search_users` - Search users by query
- `get_user` - Get user details
- `get_current_user` - Get current user info
- And more...

## Files

- `server.py` - Main MCP server implementation
- `Containerfile` - Container image definition
- `Makefile` - Build and deployment automation
- `requirements.txt` - Python dependencies
- `example.env` - Environment variables template
- `example.mcp.json` - MCP configuration template
- `LICENSE` - MIT License

## Development Commands

- `make build` - Build the container image
- `make run` - Run the container locally
- `make clean` - Clean up the built image

## License

This project is licensed under the MIT License. See the LICENSE file for details.


