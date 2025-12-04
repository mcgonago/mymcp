# HOWTO: Building an MCP Agent for GitLab from Scratch

**Step-by-step instructions for building an MCP agent for gitlab.cee.redhat.com**

---

## TL;DR

This document contains the response from Cursor when asked to build the GitLab MCP server:

> Please give me the step-by-step instructions for building an MCP agent for https://gitlab.cee.redhat.com/

The steps below give the original response, which grew into the version at [gitlab MCP: README.md](https://github.com/mcgonago/mymcp/blob/main/gitlab-rh-agent/README.md)

---

## Improvements

As this was my 2nd MCP add, I learned a few things the first time, cleaned things up a bit and improved [README.md](https://github.com/mcgonago/mymcp/blob/main/gitlab-rh-agent/README.md):

- Added **Configure GitLab Authentication** to help cleanup how users of **mymcp** install their **Personal Access Token**
- I also added more context with [Configure Cursor](https://github.com/mcgonago/mymcp/blob/main/opendev-review-agent/README.md#configure-cursor)

### Improved version of server.py

The version of [server.py](https://github.com/mcgonago/mymcp/blob/main/opendev-review-agent/server.py) that we have **today** differs a bit from **what I show below** from my initial ask on creating this GitLab RH server.

As I improved, and expanded the scope of how we can use MCP, I created the script [fetch-review.sh](https://github.com/mcgonago/mymcp/blob/main/workspace/scripts/fetch-review.sh) which is described at [Use Case #1: Review Automation](https://github.com/mcgonago/mymcp/tree/main#1-review-automation)

This is a classic case where you can **start small**, get **baseline** feature/function, and then grow upon that.

---

## Ask Cursor

Go into the CLI and ask:

```
Please give me the step-by-step instructions for building an MCP agent for https://gitlab.cee.redhat.com/
```

---

## Cursor Response

This is a copy and paste directly from Cursor.

---

## High Level

Building a Model Context Protocol (MCP) agent for an internal service like GitLab involves:

- Creating a Python server that can authenticate with the GitLab API
- Retrieve data
- And expose that retrieval process as a **tool** to Cursor's LLM

Since your GitLab instance is internal (**gitlab.cee.redhat.com**), you will need a **Personal Access Token** to authenticate.

Here are the step-by-step instructions to create and configure the agent.

---

## Steps

This is raw verbatim response from my initial ask.

### Prerequisites and Setup ⚙️

You need Python 3.x, **pip**, and a GitLab Personal Access Token.

```bash
mkdir cursor-gitlab-agent
cd cursor-gitlab-agent
python3 -m venv venv
source venv/bin/activate
pip install requests fastmcp
```

### Define Authentication and Server Script (`server.py`) 🔑

Create a file named `server.py`. This script will handle the API interaction using the **requests** library and define your MCP tool.

```python
import os
import sys
import json
import requests
from fastmcp import FastMCP, stdio_transport

# --- Configuration ---
# NOTE: Set your GitLab URL and Token here or use environment variables
GITLAB_URL = "https://gitlab.cee.redhat.com/api/v4"
# IMPORTANT: Replace this with your actual GitLab Personal Access Token
GITLAB_TOKEN = os.getenv("GITLAB_TOKEN", "YOUR_GITLAB_ACCESS_TOKEN_HERE")

# --- MCP Tool Definition ---
def gitlab_issue_fetcher(issue_id: str):
    """Fetches details for a specific GitLab Issue or Merge Request.
    
    Example issue_id format: project_name/group_name/issues/123
    """
    try:
        # Split the input string to get project name and issue number
        # This assumes the user provides the full path (e.g., 'group/project/issues/123')
        parts = issue_id.split('/')

        # The project path is the first two parts joined, URL-encoded
        project_path = requests.utils.quote('/'.join(parts[:-2]), safe='')

        # The issue or merge request ID is the last part
        target_id = parts[-1]

        # Assume the endpoint for the issue is correct
        endpoint = f"{GITLAB_URL}/projects/{project_path}/issues/{target_id}"

        headers = {"Private-Token": GITLAB_TOKEN}

        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()  # Raise exception for 4xx or 5xx status codes

        data = response.json()

        # Extract key information to structure the answer for the LLM
        return {
            "id": data.get("id"),
            "title": data.get("title"),
            "state": data.get("state"),
            "description": data.get("description"),
            "web_url": data.get("web_url"),
            "assignee": data.get("assignee", {}).get("username"),
            "project": data.get("web_url", "").split('/-/', 1)[0].split('/')[-1]
        }

    except requests.exceptions.RequestException as e:
        return {"error": f"API Request Failed: {e}"}
    except IndexError:
        return {"error": "Invalid issue ID format. Use format like 'group/project/issues/ID'."}

# --- Main MCP Server Setup ---
def main():
    mcp = FastMCP(
        name="gitlab-cee-agent",
        description="An agent that retrieves issues and merge requests from internal Red Hat GitLab (cee.redhat.com).",
        tools=[gitlab_issue_fetcher]
    )

    # Run the server using standard I/O (stdio) transport
    stdio_transport(mcp)

if __name__ == "__main__":
    main()
```

### Create the Server Launcher (`server.sh`) 🚀

Create a file named `server.sh`. This script activates the Python environment and runs the server script.

```bash
#!/bin/bash
# This script launches the MCP server

# Activate the virtual environment
source "$(dirname "$0")/venv/bin/activate"

# Run the Python server script
python "$(dirname "$0")/server.py"
```

Make it executable:

```bash
chmod +x server.sh
```

### Configure Cursor (Linking the Agent) 🔗

1. Open Cursor's settings (**Cmd/Ctrl + Comma** or **File -> Settings**)
2. Search for **MCP Servers** or go to **Features -> MCP Servers**
3. Click **+ Add new global MCP server**
4. Paste this JSON configuration:

```json
{
  "mcpServers": {
    "gitlab-cee": {
      "command": "/absolute/path/to/cursor-gitlab-agent/server.sh",
      "description": "Agent to fetch and analyze issues/MRs from internal Red Hat GitLab."
    }
  }
}
```

> **Important:** Replace `/absolute/path/to/cursor-gitlab-agent/server.sh` with the actual, full path to your `server.sh` file.

### Test the Agent

In Cursor's chat box, you can now invoke your custom agent using the `@` symbol:

```
@gitlab-cee Analyze the state and description of issue <group/project/issues/ID>
```

---

*Converted from org-mode format on 2025-12-04*

