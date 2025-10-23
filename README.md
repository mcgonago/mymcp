# My MCP Agents Collection

This repository demonstrates how to build custom MCP (Model Context Protocol) agents for Cursor. It contains three MCP agents that I built to analyze different types of code reviews.

## TL;DR

This document describes how I built my MCP agents for Cursor, including:
- **cursor-github-agent**: Analyzes GitHub Pull Requests
- **cursor-opendev-review-agent**: Analyzes OpenDev Gerrit reviews  
- **jira-mcp**: Provides access to Jira issues from Cursor

## Table of Contents

- [Building a GitHub Review Agent](#building-a-github-review-agent)
  - [Set Up the Environment](#set-up-the-environment)
  - [Define the MCP Server Script](#define-the-mcp-server-script)
  - [Create the Server Launcher](#create-the-server-launcher)
  - [Configure Cursor](#configure-cursor)
  - [Testing the Agent](#testing-the-agent)
- [OpenDev Review Agent](#opendev-review-agent)
- [Jira MCP Agent](#jira-mcp-agent)
- [Additional Resources](#additional-resources)

---

## Building a GitHub Review Agent

I wanted to build an agent for Cursor that analyzes GitHub reviews (pull requests). Here's the step-by-step process.

### Background

That's a fantastic idea! Building a specialized agent for code review is one of the most powerful uses of a custom LLM environment like Cursor. While Cursor doesn't have a direct *Agent Builder UI*, you can achieve this by creating a **custom Model Context Protocol (MCP) server** that provides GitHub pull request data as a *Tool* to the AI.

This agent will be a tool that the LLM uses to answer the prompt: **"Review this PR: &lt;GitHub URL&gt;"**

### Set Up the Environment

First, set up a minimal Python environment for your MCP server:

```bash
mkdir cursor-github-agent
cd cursor-github-agent
python3 -m venv venv
source venv/bin/activate
pip install requests fastmcp
pip install PyGithub
```

### Define the MCP Server Script

Create a file named `server.py`. This script will host the MCP server and define the **github_pr_fetcher** tool.

**Tool Definition:**
- **Tool Name**: `github_pr_fetcher`
- **Tool Action**: Retrieve the PR summary, file list, and diff content.

```python
import os
import sys
import json
from fastmcp import FastMCP, stdio_transport

# --- MCP Tool Definition ---
def github_pr_fetcher(pr_url: str):
    """A placeholder function to retrieve PR data.
    In a real implementation, this would use the GitHub API
    to fetch the PR's title, description, and diff."""

    if "github.com" not in pr_url:
        return {"error": "Invalid GitHub URL provided."}

    # Simulate API call and return structured data
    # In a real script, you would parse the URL (e.g., owner/repo/pull/number)
    # and use the PyGithub library to get the data.
 
    return {
        "pr_number": 945310,
        "title": "Fix: Catch callback in network service doesn't throw",
        "author": "tobias.urdin@binero.com",
        "file_changes_summary": "1 file changed, 10 insertions(+), 5 deletions(-)",
        "core_diff_summary": "Modified openstack/horizon/_static/app/network/network.service.js to add explicit error handling.",
        "review_prompt": "Analyze the change in the network service file. Verify that the new error handling is compliant with OpenStack standards."
    }

# --- Main MCP Server Setup ---
def main():
    mcp = FastMCP(
        name="github-reviewer",
        description="An agent that analyzes and summarizes GitHub Pull Requests for code review.",
        tools=[github_pr_fetcher]
    )

    # Run the server using standard I/O (stdio) transport
    stdio_transport(mcp)

if __name__ == "__main__":
    main()
```

### Create the Server Launcher

Create a file named `server.sh`. This simple bash script activates the Python environment and runs the server script.

```bash
#!/bin/bash
# This script launches the MCP server

source "$(dirname "$0")/venv/bin/activate"
python "$(dirname "$0")/server.py"
```

Make it executable:

```bash
chmod +x server.sh
```

### Configure Cursor

Now, tell Cursor where to find and how to run your new agent.

#### Step 1: Open Cursor Settings

Open Cursor's settings (**Cmd/Ctrl + Comma** or **File -> Settings**).

![Cursor Settings](images/howto_use_cursor_mcp_ageng_github_settings.png)

#### Step 2: Search for MCP Servers

Search for **MCP Servers** or go to **Features -> MCP Servers**.

![Search for MCP Servers](images/howto_use_cursor_mcp_ageng_github_search_for_mcp_servers.png)

#### Step 3: Add New Global MCP Server

Click **+ Add new global MCP server** and paste this JSON configuration:

![Add new global MCP server](images/howto_use_cursor_mcp_ageng_github_add_new_global_mcp_server.png)

Paste the below JSON configuration (replace with your actual path):

![Template](images/howto_use_cursor_mcp_ageng_github_add_new_global_mcp_server_template.png)

**Crucial:** You must replace `/absolute/path/to/cursor-github-agent/server.sh` with the actual file path on your laptop (e.g., `/home/omcgonag/Work/cursor-github-agent/server.sh`).

```json
{
  "mcpServers": {
    "github-reviewer-agent": {
      "command": "/home/omcgonag/Work/cursor-github-agent/server.sh",
      "description": "Analyzes GitHub pull requests to perform automated code review."
    }
  }
}
```

### Testing the Agent

#### Invoke the GitHub Cursor Agent on PR-501

I tested my GitHub Cursor agent on [PR-510: Make httpd Timeout Configurable](https://github.com/openstack-k8s-operators/horizon-operator/pull/510)

At the Cursor prompt, enter:

```
@github-reviewer-agent describe the changes for https://github.com/openstack-k8s-operators/horizon-operator/pull/510
```

![Review PR-510](images/howto_use_cursor_mcp_ageng_github_add_new_global_mcp_server_review_github_pull_request_510.png)

### Environment Setup
Ensure you have an OpenShift cluster with OpenStack operators.

Clone and checkout the PR:

```bash
git clone https://github.com/openstack-k8s-operators/horizon-operator.git
cd horizon-operator
git fetch origin pull/510/head:pr-510
git checkout pr-510
```
## OpenDev Review Agent

The second agent I created analyzes OpenDev Gerrit reviews. See the [cursor-opendev-review-agent](cursor-opendev-review-agent/) directory for the implementation.

This agent was created following similar steps to the GitHub agent, but adapted for OpenDev's Gerrit review system.

Example usage: Analyze [review 960204: Remove all dependencies/connections of old integration test code](https://review.opendev.org/c/openstack/horizon/+/960204)

![Review OpenDev](images/howto_use_cursor_mcp_ageng_github_add_new_global_mcp_server_review_opendev_960204.png)

---

## Jira MCP Agent

The third agent provides access to Jira from Cursor. See the [jira-mcp](jira-mcp/) directory for the complete implementation with containerized deployment.

This is a more mature implementation that includes:
- Containerized deployment with Podman
- 20+ Jira tools (issue search, project management, board & sprint management, user management)
- Production-ready setup with proper authentication

For detailed setup instructions, see [jira-mcp/README.md](jira-mcp/README.md).

---

## Additional Resources

### Related Documentation

- [OpenDev MCP Agent Setup Guide](cursor-opendev-review-agent/opendev-mcp-agent-setup.org) - Detailed setup documentation in org-mode format

### Directory Structure

```
mymcp/
├── README.md                           # This file
├── cursor-github-agent/                # GitHub PR review agent
│   ├── server.py                       # Main MCP server
│   ├── server.sh                       # Launch script
│   └── requirements.txt                # Python dependencies
├── cursor-opendev-review-agent/        # OpenDev Gerrit review agent
│   ├── server.py                       # Main MCP server
│   ├── server.sh                       # Launch script
│   └── requirements.txt                # Python dependencies
├── jira-mcp/                           # Jira integration agent
│   ├── server.py                       # Main MCP server
│   ├── requirements.txt                # Python dependencies
│   ├── Containerfile                   # Container definition
│   ├── Makefile                        # Build and setup automation
│   ├── example.env                     # Environment variables template
│   ├── example.mcp.json                # MCP configuration template
│   └── LICENSE                         # MIT License
└── images/                             # Screenshots and documentation images
```

### Setup Instructions for Participants

If you're attending my demonstration and want to follow along:

1. **Clone this repository**:
   ```bash
   git clone https://github.com/mcgonago/mymcp.git
   cd mymcp
   ```

2. **Choose an agent to set up** (start with cursor-github-agent for simplest):
   ```bash
   cd cursor-github-agent
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   chmod +x server.sh
   ```

3. **Configure Cursor**:
   - Open Cursor Settings (Cmd/Ctrl + ,)
   - Navigate to Features → MCP Servers
   - Add your agent configuration (see examples above)

4. **Test your agent**:
   - Try asking Cursor to review a PR or issue
   - Use the `@agent-name` syntax in your prompts

### Contributing

This repository is primarily for educational purposes and demonstration. Feel free to fork and adapt for your own MCP agents!

### License

- `jira-mcp` is licensed under the MIT License
- Other agents are provided as examples for educational purposes

---

## Questions?

If you have questions during the demonstration or while following along, please feel free to reach out or open an issue in this repository.

**Happy MCP building!** 🚀

