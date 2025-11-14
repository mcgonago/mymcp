# OpenDev Review Agent

An MCP (Model Context Protocol) agent for Cursor that analyzes OpenDev Gerrit code reviews for OpenStack projects.

> **Note**: The steps below can be executed from within the repository where the `server.sh` and `server.py` files are located.

> **Try This Yourself**: You can also try this on your own by asking the same question I asked Gemini:  
> *"Please give me the step-by-step instructions for building an MCP agent that analyzes review.opendev.org reviews"*

## Background

The OpenDev review system uses Gerrit, which is different from GitHub's pull request model. Building a specialized agent for OpenDev reviews allows us to analyze OpenStack code changes using Cursor's AI capabilities. This agent leverages Gerrit's REST API to fetch review metadata, file changes, and comments.

This agent will be a tool that the LLM uses to answer the prompt: **"Review this change: &lt;OpenDev URL&gt;"**

## Files

- [`server.py`](server.py) - Main MCP server implementation
- [`server.sh`](server.sh) - Launch script
- `requirements.txt` - Python dependencies

---

## Set Up the Environment

First, set up a minimal Python environment for your MCP server, you can do this from directory `opendev-review-agent` of your repo:

```bash
cd opendev-review-agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Alternatively, install packages directly into the venv without activating it:

```bash
./venv/bin/pip install -r requirements.txt
```

## Define the MCP Server Script (server.py)

For your convenience, since you are working in your cloned repo of **mymcp**, the [`server.py`](server.py) script has already been created for you.
- also, the [`server.sh`](server.sh) script below has already been created.
- when you get to the point (below) of adding your **opendev-review-agent**, you just point to this **directory**, which will find the [`server.sh`](server.sh) script

The [`server.py`](server.py) script hosts the MCP server and defines the **gerrit_review_fetcher** tool.

**Tool Definition:**
- **Tool Name**: `gerrit_review_fetcher`
- **Tool Action**: Retrieve review metadata, file changes, and comments from Gerrit API.

**See the complete implementation:** [`server.py`](server.py)

**Key Features:**
- **Gerrit API Integration**: Fetches review details from OpenDev's Gerrit REST API
- **Security Prefix Handling**: Strips the `)]}'` prefix that Gerrit adds for security
- **Comprehensive Data**: Retrieves change metadata, file statistics, and comments
- **URL Parsing**: Extracts change numbers from standard OpenDev review URLs

## Create the Server Launcher

Create a file named [`server.sh`](server.sh). This simple bash script activates the Python environment and runs the server script.

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

**See the complete implementation:** [`server.sh`](server.sh)

## Configure Cursor

Now, tell Cursor where to find and how to run your new agent.

### Step 1: Open Cursor Settings

Open Cursor's settings (**Cmd/Ctrl + Comma** or **File -> Settings**).

![Cursor Settings](../images/howto_use_cursor_mcp_ageng_github_settings.png)

### Step 2: Search for MCP Servers

Search for **MCP Servers** or go to **Features -> MCP Servers**.

![Search for MCP Servers](../images/howto_use_cursor_mcp_ageng_github_search_for_mcp_servers.png)

### Step 3: Add New Global MCP Server

Click **+ Add new global MCP server** and paste this JSON configuration (remember to replace `<your-mymcp-cloned-repo-path>`):

```json
{
  "mcpServers": {
    "opendev-reviewer-agent": {
      "command": "<your-mymcp-cloned-repo-path>/opendev-review-agent/server.sh",
      "description": "Analyzes OpenDev Gerrit reviews to perform automated code review."
    }
  }
}
```

### Step 4: Save and Reload Cursor

**Save your new mcp.json configuration**  
Go to **File → Save** and then restart Cursor (**Ctrl+Shift+P** → "Developer: Reload Window")

> **Note**: Alternatively, you can fully exit Cursor (**Ctrl+Q**) and restart it, which will also reload the new settings.

## Testing the Agent

### Invoke the OpenDev Cursor Agent on Review 960204

I tested my OpenDev Cursor agent on [Review 960204: Validate token before revoking in keystone_client](https://review.opendev.org/c/openstack/horizon/+/960204)

At the Cursor prompt, enter:

```
@opendev-reviewer-agent Analyze the review at https://review.opendev.org/c/openstack/horizon/+/960204
```

![Review OpenDev 963261](../images/howto_use_cursor_mcp_ageng_github_add_new_global_mcp_server_review_opendev_963261.png)

## Verifying OpenDev Review Agent is Operational

To test if your OpenDev review agent is working correctly, run this command from your terminal:

```bash
cd <your-mymcp-cloned-repo-path>/opendev-review-agent
bash server.sh <<< '{"jsonrpc": "2.0", "method": "exit"}' 2>&1 | head -20
```

If working correctly, you should see output like:

```
╭────────────────────────────────────────────────────────────────────────────╮
│                                                                            │
│        _ __ ___  _____           __  __  _____________    ____    ____     │
│       _ __ ___ .'____/___ ______/ /_/  |/  / ____/ __ \  |___ \  / __ \    │
│      _ __ ___ / /_  / __ `/ ___/ __/ /|_/ / /   / /_/ /  ___/ / / / / /    │
│     _ __ ___ / __/ / /_/ (__  ) /_/ /  / / /___/ ____/  /  __/_/ /_/ /     │
│    _ __ ___ /_/    \____/____/\__/_/  /_/\____/_/      /_____(*)____/      │
│                                                                            │
│                                                                            │
│                                FastMCP  2.0                                │
│                                                                            │
│                                                                            │
│                 🖥️  Server name:     opendev-reviewer                       │
│                 📦 Transport:       STDIO                                  │
│                                                                            │
│                 🏎️  FastMCP version: 2.12.5                                 │
│                 🤝 MCP SDK version: 1.16.0                                 │
│                                                                            │
```

This confirms the MCP server starts successfully.

## What This Agent Can Do

✅ **Fetch Review Details**: Get comprehensive change information from OpenDev Gerrit  
✅ **Analyze File Changes**: Review all modified files with change statistics  
✅ **Access Review Comments**: Read reviewer comments and feedback  
✅ **Track Review State**: See change status (NEW, MERGED, ABANDONED, etc.)  
✅ **View Commit Messages**: Access detailed commit descriptions  
✅ **Support OpenStack Projects**: Works with all projects on review.opendev.org  
✅ **Gerrit API Integration**: Handles Gerrit's unique security prefix and JSON format  
✅ **URL Parsing**: Extracts change numbers from standard OpenDev review URLs

## Next Steps

- Try analyzing OpenStack reviews across different projects (horizon, nova, keystone, etc.)
- Use the agent to understand review feedback and technical discussions
- Analyze review history to learn from accepted and rejected changes
- Combine with other MCP agents to correlate code changes with issues/bugs
- Use for understanding OpenStack coding patterns and best practices

## Security Notes

- ✅ No authentication required for public OpenDev reviews
- ✅ Read-only access to Gerrit REST API
- ✅ No credentials or tokens needed
- ✅ Works with all publicly accessible OpenStack projects
- ✅ Safe to use without any security concerns

## Troubleshooting

For solutions to common issues, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## Related Documentation

- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Solutions to common setup issues
- [Main Repository README](../README.md) - Overview of all MCP agents
