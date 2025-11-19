# Jira MCP Agent

> [!NOTE]
> **About This Document**  
> This document was created by following the well-documented steps at https://github.com/redhat-community-ai-tools/jira-mcp for creating a Jira MCP agent.
>
> The steps below document the process of building a simple Jira MCP agent based on that repository. For comprehensive documentation, advanced features, and the complete implementation, please refer to the original: https://github.com/redhat-community-ai-tools/jira-mcp

## Overview

A containerized Python MCP server for Cursor that provides access to Jira issues, projects, boards, and sprints.

> [!IMPORTANT]
> This project is experimental and was initially created as a learning exercise.

## Files

- [`server.py`](server.py) - Main MCP server implementation
- `Containerfile` - Container image definition  
- `Makefile` - Build and deployment automation
- `requirements.txt` - Python dependencies
- `example.env` - Environment variables template
- `example.mcp.json` - MCP configuration template
- `LICENSE` - MIT License

---

## Set Up the Environment

### Prerequisites

- **podman** - Install with `sudo dnf install podman` (Fedora/RHEL) or `brew install podman` (macOS)
- **make** - Usually pre-installed on most systems

### Build the Container Image

Navigate to the `jira-agent` directory and build the image (remember to replace `<your-mymcp-cloned-repo-path>`):

```bash
cd <your-mymcp-cloned-repo-path>/jira-agent
make build
```

This creates a container image named `jira-agent:latest` with all required dependencies.

## Configure Jira Authentication

The Jira agent requires an API token to access your Jira instance.

### Create a Jira API Token

1. Go to your Jira instance's API token page (e.g., https://id.atlassian.com/manage-profile/security/api-tokens for Atlassian Cloud)
2. Click **"Create API token"**
3. Give it a descriptive label: `Cursor Jira MCP Agent`
4. **Copy the token** (you won't be able to see it again!)

### Set Up the Environment File

Create a `.rh-jira-agent.env` file in your home directory:

```bash
cp <your-mymcp-cloned-repo-path>/jira-agent/example.env ~/.rh-jira-agent.env
```

Edit the `~/.rh-jira-agent.env` file and replace the placeholder values:

```bash
JIRA_URL=https://issues.redhat.com
JIRA_API_TOKEN=your-actual-jira-token-here
```

> [!WARNING]
> **Security Note**  
> Keep the `.rh-jira-agent.env` file in your home directory (outside the repository) to protect your credentials. The file contains your personal API token.

> [!IMPORTANT]
> **Environment Variable Names**  
> The environment variable MUST be named `JIRA_API_TOKEN` (not `JIRA_TOKEN`). The server code expects this exact variable name.

## MCP Server Implementation

The server implementation uses FastMCP and the Jira Python library to provide tools for interacting with Jira.

**See the complete implementation:** [`server.py`](server.py)

**Key Components:**
- **FastMCP Framework**: Provides the MCP protocol implementation
- **Jira Client**: Connects to Jira REST API using credentials from environment
- **20+ Tools**: Implements various Jira operations as MCP tools

**Container Setup:**
- **Base Image**: Python 3.11-slim
- **Dependencies**: Defined in [`requirements.txt`](requirements.txt)
- **Build**: Automated via [`Makefile`](Makefile)
- **Configuration**: Uses Podman with environment file for credentials

**Container definition:** [`Containerfile`](Containerfile)

## Configure Cursor

Add the Jira agent to Cursor's MCP configuration.

### Step 1: Open Cursor Settings

Open Cursor's settings (**Cmd/Ctrl + Comma** or **File -> Settings**).

### Step 2: Navigate to MCP Servers

Search for **MCP Servers** or go to **Features -> MCP Servers**.

### Step 3: Add New Global MCP Server

Click **+ Add new global MCP server** and paste this JSON configuration.

> [!IMPORTANT]
> **Path Placeholder Note:**  
> Replace `<your-home-directory>` with your actual home directory path (e.g., `/home/username` on Linux or `/Users/username` on Mac).  
> **Do NOT use the tilde (`~`) character** as it will not expand correctly in the Podman context.

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
        "<your-home-directory>/.rh-jira-agent.env",
        "jira-agent:latest"
      ],
      "description": "Provides access to Jira issues, projects, boards, and sprints."
    }
  }
}
```

### Step 4: Save and Reload Cursor

**Save your new mcp.json configuration**  
Go to **File → Save** and then restart Cursor (**Ctrl+Shift+P** → "Developer: Reload Window")

> **Note**: Alternatively, you can fully exit Cursor (**Ctrl+Q**) and restart it, which will also reload the new settings.

## What This Agent Does

This agent provides 20+ tools that enable Cursor's AI to interact with Jira, such as:
- ✅ Get details for Jira issues
- ✅ Search issues using JQL (Jira Query Language)
- ✅ List projects and boards
- ✅ Query sprint information
- ✅ Search and manage users
- ✅ Access project components, versions, and roles
- ✅ Get assignable users for projects and issues
- ✅ Retrieve issue types and permission schemes

## Next Steps

- Try querying different Jira issues and projects in your workspace
- Use JQL search to find specific issues (e.g., bugs, features, by assignee)
- Explore sprint and board information for agile project management
- Combine with other MCP agents to correlate Jira issues with code changes
- Use for automated status updates and project tracking insights

## Security Notes

- ✅ Environment file stored outside repository (`~/.rh-jira-agent.env`)
- ✅ Credentials never committed to Git
- ✅ Uses containerized deployment for isolation
- ✅ API token with read-only recommended scopes
- ✅ Jira authentication through official API token mechanism

## Testing the Agent

### Test from Terminal

Test the container directly before using it in Cursor:

```bash
cd <your-mymcp-cloned-repo-path>/jira-agent
podman run --rm -i --env-file ~/.rh-jira-agent.env jira-agent:latest <<< '{"jsonrpc": "2.0", "method": "tools/list"}'
```

Expected output should list available Jira tools.

### Test in Cursor

After configuring the agent in Cursor, test it with these prompts:

**Get issue details:**
```
@jiraMcp Get details for issue OSPRH-13100
```

**Search issues:**
```
@jiraMcp Search for issues in project OSPRH
```

**List projects:**
```
@jiraMcp List all projects I have access to
```

## Available Tools

The MCP server provides these tools for interacting with Jira:

### Issue Search
- `get_jira` - Get details for a specific Jira issue by key
- `search_issues` - Search issues using JQL

### Project Management
- `list_projects` - List all projects
- `get_project` - Get project details by key
- `get_project_components` - Get components for a project
- `get_project_versions` - Get versions for a project
- `get_project_roles` - Get roles for a project
- `get_project_permission_scheme` - Get permission scheme for a project
- `get_project_issue_types` - Get issue types for a project

### User Management
- `search_users` - Search users by query
- `get_user` - Get user details by account ID
- `get_current_user` - Get current user info
- `get_assignable_users_for_project` - Get assignable users for a project
- `get_assignable_users_for_issue` - Get assignable users for an issue

### Board & Sprint Management
- `list_boards` - List all boards
- `get_board` - Get board details by ID
- `list_sprints` - List sprints for a board
- `get_sprint` - Get sprint details by ID
- `get_issues_for_board` - Get issues for a board
- `get_issues_for_sprint` - Get issues for a sprint in a board

## Troubleshooting

For solutions to common issues, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## Development Commands

If you want to modify or extend the agent:

- `make build` - Build the container image
- `make run` - Run the container locally for testing
- `make clean` - Clean up the built image

## License

This project is licensed under the MIT License. See the LICENSE file for details.
