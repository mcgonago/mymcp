# My MCP Agents Collection

This repository demonstrates how to build custom MCP (Model Context Protocol) agents for Cursor. It contains three MCP agents that I built to analyze different types of code reviews.

## TL;DR

This document describes how I built my MCP agents for Cursor, including:
- **cursor-github-agent**: Analyzes GitHub Pull Requests
- **cursor-opendev-review-agent**: Analyzes OpenDev Gerrit reviews  
- **jira-mcp**: Provides access to Jira issues from Cursor

## Table of Contents

- [Building an OpenDev Review Agent](#building-an-opendev-review-agent)
  - [Set Up the Environment](#set-up-the-environment)
  - [Define the MCP Server Script](#define-the-mcp-server-script-1)
  - [Create the Server Launcher](#create-the-server-launcher-1)
  - [Configure Cursor](#configure-cursor-1)
  - [Testing the Agent](#testing-the-agent-1)
- [Building a GitHub Review Agent](#building-a-github-review-agent)
  - [Set Up the Environment](#set-up-the-environment-1)
  - [Define the MCP Server Script](#define-the-mcp-server-script-2)
  - [Create the Server Launcher](#create-the-server-launcher-2)
  - [Configure Cursor](#configure-cursor-2)
  - [Testing the Agent](#testing-the-agent-2)
- [Jira MCP Agent](#jira-mcp-agent)
- [Additional Resources](#additional-resources)

---

## Building an OpenDev Review Agent

I wanted to build an agent for Cursor that analyzes OpenDev Gerrit reviews for OpenStack projects. Here's the step-by-step process.

### Background

The OpenDev review system uses Gerrit, which is different from GitHub's pull request model. Building a specialized agent for OpenDev reviews allows us to analyze OpenStack code changes using Cursor's AI capabilities. This agent leverages Gerrit's REST API to fetch review metadata, file changes, and comments.

This agent will be a tool that the LLM uses to answer the prompt: **"Review this change: &lt;OpenDev URL&gt;"**

### Set Up the Environment

First, set up a minimal Python environment for your MCP server:

```bash
mkdir cursor-opendev-review-agent
cd cursor-opendev-review-agent
python3 -m venv venv
source venv/bin/activate
pip install requests fastmcp
```

### Define the MCP Server Script

Create a file named `server.py`. This script will host the MCP server and define the **gerrit_review_fetcher** tool.

**Tool Definition:**
- **Tool Name**: `gerrit_review_fetcher`
- **Tool Action**: Retrieve review metadata, file changes, and comments from Gerrit API.

```python
#!/usr/bin/env python3
"""
OpenDev.Review MCP Agent
An MCP server that analyzes OpenDev Gerrit reviews for code review.
"""

import os
import sys
import json
import requests
import re
import asyncio
from datetime import datetime
from fastmcp import FastMCP

def extract_change_number(review_url):
    """Extract change number from OpenDev.Review URL."""
    # Pattern to match URLs like: https://review.opendev.org/c/openstack/horizon/+/963261
    pattern = r'review\.opendev\.org/c/[^/]+/[^/]+/\+/(\d+)'
    match = re.search(pattern, review_url)
    if match:
        return match.group(1)
    return None

def gerrit_review_fetcher(review_url: str):
    """
    Fetches review data from OpenDev's Gerrit system.
    
    Args:
        review_url: The full URL to the OpenDev.Review change (e.g., 
                   https://review.opendev.org/c/openstack/horizon/+/963261)
    
    Returns:
        Dictionary containing review metadata and analysis prompt
    """
    if "review.opendev.org" not in review_url:
        return {"error": "Invalid OpenDev Gerrit URL provided."}

    # Extract change number from the URL
    change_number = extract_change_number(review_url)
    if not change_number:
        return {"error": "Could not extract change number from URL. Expected format: https://review.opendev.org/c/project/repo/+/CHANGE_NUMBER"}

    # Gerrit REST API endpoints
    change_url = f"https://review.opendev.org/changes/{change_number}/detail"
    files_url = f"https://review.opendev.org/changes/{change_number}/revisions/current/files"
    comments_url = f"https://review.opendev.org/changes/{change_number}/comments"

    try:
        # Fetch the change details
        response = requests.get(change_url, timeout=10)
        response.raise_for_status()
        # Gerrit API responses start with a security prefix that needs to be stripped
        json_content = response.text
        if json_content.startswith(")]}'"):
            json_content = json_content[4:]
        change_data = json.loads(json_content)

        # Fetch the list of files changed
        files_response = requests.get(files_url, timeout=10)
        files_response.raise_for_status()
        files_json_content = files_response.text
        if files_json_content.startswith(")]}'"):
            files_json_content = files_json_content[4:]
        files_data = json.loads(files_json_content)

        # Fetch comments if available
        comments_response = requests.get(comments_url, timeout=10)
        if comments_response.status_code == 200:
            comments_json_content = comments_response.text
            if comments_json_content.startswith(")]}'"):
                comments_json_content = comments_json_content[4:]
            comments_data = json.loads(comments_json_content)
        else:
            comments_data = {}

        # Process the change data
        title = change_data.get('subject', 'No title available')
        author = change_data.get('owner', {}).get('name', 'Unknown author')
        author_email = change_data.get('owner', {}).get('email', '')
        project = change_data.get('project', 'Unknown project')
        branch = change_data.get('branch', 'Unknown branch')
        status = change_data.get('status', 'Unknown status')
        
        # Process files changed
        files_changed = []
        file_stats = []
        
        for file_path, file_info in files_data.items():
            if file_path == '/COMMIT_MSG':
                continue
                
            files_changed.append(file_path)
            
            # Extract file statistics
            lines_inserted = file_info.get('lines_inserted', 0)
            lines_deleted = file_info.get('lines_deleted', 0)
            file_stats.append({
                'file': file_path,
                'insertions': lines_inserted,
                'deletions': lines_deleted,
                'net_changes': lines_inserted - lines_deleted
            })

        # Calculate total changes
        total_insertions = sum(stat['insertions'] for stat in file_stats)
        total_deletions = sum(stat['deletions'] for stat in file_stats)
        total_files = len(files_changed)

        # Construct the review prompt
        review_prompt = f"""
Analyze the OpenDev.Review change for {project}:

**Change Summary:**
- Title: {title}
- Author: {author} ({author_email})
- Project: {project}
- Branch: {branch}
- Status: {status}
- Files Changed: {total_files}
- Lines: +{total_insertions}/-{total_deletions}

**Files Modified:**
{chr(10).join([f"- {file}" for file in files_changed[:10]])}
{f"... and {len(files_changed) - 10} more files" if len(files_changed) > 10 else ""}

**Review Focus Areas:**
1. Code quality and adherence to OpenStack standards
2. Security implications of the changes
3. Performance impact
4. Backward compatibility
5. Test coverage and documentation
6. Compliance with project coding guidelines

Please provide a comprehensive code review focusing on these areas.
"""

        return {
            "change_number": change_number,
            "title": title,
            "author": author,
            "project": project,
            "branch": branch,
            "status": status,
            "total_files": total_files,
            "total_insertions": total_insertions,
            "total_deletions": total_deletions,
            "files_changed": files_changed,
            "file_stats": file_stats,
            "review_prompt": review_prompt.strip()
        }

    except requests.RequestException as e:
        return {"error": f"Failed to fetch review data: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

async def main():
    """Main function to set up and run the MCP server."""
    mcp = FastMCP(
        name="opendev-reviewer",
        instructions="An agent that analyzes and summarizes OpenDev Gerrit reviews for code review.",
        tools=[gerrit_review_fetcher]
    )

    # Run the server using standard I/O (stdio) transport
    await mcp.run_stdio_async()

if __name__ == "__main__":
    asyncio.run(main())
```

**Key Features:**
- **Gerrit API Integration**: Fetches review details from OpenDev's Gerrit REST API
- **Security Prefix Handling**: Strips the `)]}'` prefix that Gerrit adds for security
- **Comprehensive Data**: Retrieves change metadata, file statistics, and comments
- **URL Parsing**: Extracts change numbers from standard OpenDev review URLs

### Create the Server Launcher

Create a file named `server.sh`. This simple bash script activates the Python environment and runs the server script.

```bash
#!/bin/bash
# This script launches the OpenDev.Review MCP server

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activate the virtual environment
source "$SCRIPT_DIR/venv/bin/activate"

# Run the server script
python "$SCRIPT_DIR/server.py"
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

**Crucial:** You must replace `/absolute/path/to/cursor-opendev-review-agent/server.sh` with the actual file path on your laptop (e.g., `/home/omcgonag/Work/cursor-opendev-review-agent/server.sh`).

```json
{
  "mcpServers": {
    "opendev-reviewer-agent": {
      "command": "/home/omcgonag/Work/cursor-opendev-review-agent/server.sh",
      "description": "Analyzes OpenDev Gerrit reviews to perform automated code review."
    }
  }
}
```

### Testing the Agent

#### Invoke the OpenDev Cursor Agent on Review 960204

I tested my OpenDev Cursor agent on [Review 960204: Remove all dependencies/connections of old integration test code](https://review.opendev.org/c/openstack/horizon/+/960204)

At the Cursor prompt, enter:

```
@opendev-reviewer-agent Analyze the review at https://review.opendev.org/c/openstack/horizon/+/960204
```

![Review OpenDev 963261](images/howto_use_cursor_mcp_ageng_github_add_new_global_mcp_server_review_opendev_963261.png)

See more details at use-case/opendev-reviewer-agent/960204


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

#### Invoke the GitHub Cursor Agent on PR-402

I tested my GitHub Cursor agent on [PR-402: Allow customize http vhost config using HttpdCustomization.CustomConfigSecret](https://github.com/openstack-k8s-operators/horizon-operator/pull/402)

At the Cursor prompt, enter:

```
@github-reviewer-agent Review the PR at https://github.com/openstack-k8s-operators/horizon-operator/pull/402 How do I test this?
```

![Review PR-402](images/howto_use_cursor_mcp_ageng_github_add_new_global_mcp_server_review_github_pull_request_402.png)

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

