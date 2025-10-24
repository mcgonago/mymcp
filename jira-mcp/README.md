# Building a Jira MCP Agent

I wanted to build an agent for Cursor that provides access to Jira issues, projects, boards, and sprints. Here's the step-by-step process.

## Background

Many development teams use Jira for issue tracking and project management. Building a specialized agent for Jira allows us to query issues, search projects, and manage sprints directly from Cursor's AI interface. This agent uses a containerized approach with Podman for easy deployment and isolation, and leverages Jira's REST API for comprehensive access to Jira resources.

This agent provides 20+ tools that the LLM can use to answer prompts like: **"Get details for Jira issue OSPRH-13100"** or **"Search for issues assigned to me"**

> [!IMPORTANT]
> This project is experimental and was initially created as a learning exercise.

## Set Up the Environment

First, ensure you have the prerequisites installed and build the container image:

### Prerequisites

- **podman** - Install with `sudo dnf install podman` (Fedora/RHEL) or `brew install podman` (macOS)
- **make** - Usually pre-installed on most systems

### Build the Container Image

Navigate to the `jira-mcp` directory and build the image:

```bash
cd <your-mymcp-cloned-repo-path>/jira-mcp
make build
```

This will create a container image named `jira-mcp:latest` with all required dependencies.

## Configure Jira Authentication

The Jira agent requires an API token to access your Jira instance.

### Create a Jira API Token

1. Go to your Jira instance's API token page (e.g., https://id.atlassian.com/manage-profile/security/api-tokens for Atlassian Cloud)
2. Click **"Create API token"**
3. Give it a descriptive label: `Cursor Jira MCP Agent`
4. **Copy the token** (you won't be able to see it again!)

### Set Up the Environment File

Create a `.rh-jira-mcp.env` file in your home directory:

```bash
cp <your-mymcp-cloned-repo-path>/jira-mcp/example.env ~/.rh-jira-mcp.env
```

Edit the `~/.rh-jira-mcp.env` file and replace the placeholder values:

```bash
JIRA_URL=https://issues.redhat.com
JIRA_API_TOKEN=your-actual-jira-token-here
```

> [!WARNING]
> **Never commit this file to Git!** It contains your personal API token.  
> Keep it in your home directory (`~/.rh-jira-mcp.env`) outside the repository.

## Define the MCP Server Script

This agent uses a containerized approach with Podman. The main server is implemented in `server.py` and packaged into a container image.

**See the complete implementation:** [`jira-mcp/server.py`](server.py)

**Key Features:**
- **20+ Jira Tools**: Comprehensive access to issues, projects, boards, sprints, and users
- **Containerized Deployment**: Isolated environment with all dependencies
- **JQL Support**: Search issues using Jira Query Language
- **Authentication**: Secure token-based authentication

### Available Tools

The MCP server provides these tool categories:

#### Issue Management
- `get_jira` - Get details for a specific Jira issue
- `search_issues` - Search issues using JQL
- `create_issue` - Create a new issue
- `update_issue` - Update an existing issue
- And more...

#### Project Management
- `list_projects` - List all projects
- `get_project` - Get project details
- `get_project_components` - Get components for a project
- `get_project_versions` - Get versions for a project

#### Board & Sprint Management
- `list_boards` - List all boards
- `get_board` - Get board details
- `list_sprints` - List sprints for a board
- `get_sprint_issues` - Get issues in a sprint

#### User Management
- `search_users` - Search users by query
- `get_user` - Get user details
- `get_current_user` - Get current user info

## Create the Container Image

The agent is packaged using a `Containerfile` (Podman/Docker format) for easy deployment.

**Container definition:** [`jira-mcp/Containerfile`](Containerfile)

The container image is built with the `make build` command (see "Set Up the Environment" above).

## Configure Cursor

Now, tell Cursor where to find and how to run your Jira agent.

### Step 1: Open Cursor Settings

Open Cursor's settings (**Cmd/Ctrl + Comma** or **File -> Settings**).

### Step 2: Search for MCP Servers

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
        "<your-home-directory>/.rh-jira-mcp.env",
        "jira-mcp:latest"
      ],
      "description": "Provides access to Jira issues, projects, boards, and sprints."
    }
  }
}
```

**Example with actual path:**
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
        "/home/omcgonag/.rh-jira-mcp.env",
        "jira-mcp:latest"
      ],
      "description": "Provides access to Jira issues, projects, boards, and sprints."
    }
  }
}
```

### Step 4: Save and Reload Cursor

**Save your new mcp.json configuration**  
Go to **File → Save** and then restart Cursor (**Ctrl+Shift+P** → "Developer: Reload Window")

## Testing the Agent

### Test from Terminal

You can test the container directly before using it in Cursor:

```bash
cd <your-mymcp-cloned-repo-path>/jira-mcp
make run
```

This will start the container interactively and show you the MCP server banner with available tools.

**To exit**: Press `Ctrl+D`

### Test from Cursor

Once Cursor is restarted, test the agent by entering commands at the Cursor prompt:

```
@jiraMcp Get details for issue OSPRH-13100
```

or

```
@jiraMcp Search for issues assigned to me in the current sprint
```

or

```
@jiraMcp List all projects I have access to
```

The agent will query your Jira instance and return the requested information.

---

## Development Commands

If you want to modify or extend the agent:

- `make build` - Build the container image
- `make run` - Run the container locally for testing
- `make clean` - Clean up the built image

## Files

- `server.py` - Main MCP server implementation
- `Containerfile` - Container image definition  
- `Makefile` - Build and deployment automation
- `requirements.txt` - Python dependencies
- `example.env` - Environment variables template
- `example.mcp.json` - MCP configuration template
- `LICENSE` - MIT License

## License

This project is licensed under the MIT License. See the LICENSE file for details.


