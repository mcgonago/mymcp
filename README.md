# My MCP Agents Collection

This repository demonstrates how to build custom MCP (Model Context Protocol) agents for Cursor. It contains three MCP agents that I built to analyze different types of code reviews.

> [!NOTE]
> **About the Jira Agent**  
> The `jira-agent` in this repository is based on the excellent work from [redhat-community-ai-tools/jira-mcp](https://github.com/redhat-community-ai-tools/jira-mcp). I followed their well-documented steps as part of my learning journey to build MCP agents.
>
> **Explore More MCP Agents**  
> The [redhat-community-ai-tools](https://github.com/redhat-community-ai-tools) organization maintains several high-quality MCP agents and tools. I highly recommend checking out their repositories to discover other useful agents and learn from their implementations. They provide excellent examples of professional MCP agent development.

## TL;DR

This document describes how I built my MCP agents for Cursor, including:
- **github-agent**: Analyzes GitHub Pull Requests
- **opendev-review-agent**: Analyzes OpenDev Gerrit reviews  
- **jira-agent**: Provides access to Jira issues from Cursor

## Table of Contents

- [OpenDev Review Agent](#opendev-review-agent)
- [GitHub Review Agent](#github-review-agent)
- [Jira Agent](#jira-agent)
- [Complete MCP Configuration](#complete-mcp-configuration)
- [Additional Resources](#additional-resources)

---

## OpenDev Review Agent

An agent for analyzing OpenDev Gerrit code reviews for OpenStack projects.

### Features

- **Gerrit API Integration**: Fetches review details from OpenDev's Gerrit REST API
- **Security Prefix Handling**: Strips the `)]}'` prefix that Gerrit adds for security
- **Comprehensive Data**: Retrieves change metadata, file statistics, and comments
- **URL Parsing**: Extracts change numbers from standard OpenDev review URLs

**For detailed setup instructions, see [opendev-review-agent/README.md](opendev-review-agent/README.md).**

---

## GitHub Review Agent

An agent for analyzing GitHub Pull Requests with real GitHub API integration.

### Features

- **GitHub API Integration**: Fetches real PR data using PyGithub
- **Authentication**: Uses personal access tokens for API access
- **Comprehensive Data**: Retrieves PR metadata, file changes, comments, and reviews
- **Security**: Environment file for token management (never committed to Git)

**For detailed setup instructions, see [github-agent/README.md](github-agent/README.md).**

---

## Jira Agent

An agent that provides access to Jira from Cursor with containerized deployment.

### Features

- Containerized deployment with Podman
- 20+ Jira tools (issue search, project management, board & sprint management, user management)
- Production-ready setup with proper authentication
- Secure credential management

**For detailed setup instructions, see [jira-agent/README.md](jira-agent/README.md).**

---

## Complete MCP Configuration

To configure all three agents in Cursor at once:

1. Open Cursor Settings (**Ctrl/Cmd + ,**)
2. Search for: **MCP Servers**
3. Paste this complete configuration (remember to replace `<your-mymcp-cloned-repo-path>`):

```json
{
  "mcpServers": {
    "opendev-reviewer-agent": {
      "command": "<your-mymcp-cloned-repo-path>/opendev-review-agent/server.sh",
      "description": "Analyzes OpenDev Gerrit reviews to perform automated code review."
    },
    "github-reviewer-agent": {
      "command": "<your-mymcp-cloned-repo-path>/github-agent/server.sh",
      "description": "Analyzes GitHub pull requests to perform automated code review."
    },
    "jiraMcp": {
      "command": "podman",
      "args": [
        "run",
        "--rm",
        "-i",
        "--env-file",
        "/home/username/.rh-jira-mcp.env",
        "jira-agent:latest"
      ],
      "description": "Provides access to Jira issues, projects, boards, and sprints."
    }
  }
}
```

4. **Save your new mcp.json configuration**  
   Go to **File → Save** and then restart Cursor (**Ctrl+Shift+P** → "Developer: Reload Window")
   
   > **Note**: Alternatively, you can fully exit Cursor (**Ctrl+Q**) and restart it, which will also reload the new settings.

### Testing Each Agent

After configuration, test each agent in Cursor:

**OpenDev Agent:**
```
@opendev-reviewer-agent Analyze https://review.opendev.org/c/openstack/horizon/+/960204
```

**GitHub Agent:**
```
@github-reviewer-agent Review https://github.com/openstack-k8s-operators/horizon-operator/pull/402
```

**Jira Agent:**
```
@jiraMcp Get details for issue OSPRH-13100
```

---

## Additional Resources

### Verification Script

Use `test-mcp-setup.sh` to verify all agents are properly configured:

```bash
./test-mcp-setup.sh
```

This script will:
- Test each agent's server startup
- Verify virtual environments and dependencies
- Check Cursor configuration
- Provide troubleshooting guidance

### Related Documentation

- [OpenDev MCP Agent Setup Guide](opendev-review-agent/opendev-mcp-agent-setup.org) - Detailed setup documentation in org-mode format

### Directory Structure

```
mymcp/
├── README.md                           # This file
├── github-agent/                       # GitHub PR review agent
│   ├── server.py                       # Main MCP server
│   ├── server.sh                       # Launch script
│   ├── README.md                       # Detailed setup guide
│   ├── SETUP.md                        # GitHub authentication guide
│   ├── example.env                     # Environment template
│   └── requirements.txt                # Python dependencies
├── opendev-review-agent/               # OpenDev Gerrit review agent
│   ├── server.py                       # Main MCP server
│   ├── server.sh                       # Launch script
│   ├── README.md                       # Detailed setup guide
│   └── requirements.txt                # Python dependencies
├── jira-agent/                         # Jira integration agent
│   ├── server.py                       # Main MCP server
│   ├── README.md                       # Detailed setup guide
│   ├── requirements.txt                # Python dependencies
│   ├── Containerfile                   # Container definition
│   ├── Makefile                        # Build and setup automation
│   ├── example.env                     # Environment variables template
│   ├── example.mcp.json                # MCP configuration template
│   └── LICENSE                         # MIT License
├── images/                             # Screenshots and documentation images
├── test-mcp-setup.sh                   # Verification script for all agents
├── docs/                               # Additional documentation
└── use-case/                           # Example use cases and reviews
```

### Troubleshooting

**If an agent doesn't respond:**
- Verify the `command` path is correct and absolute
- Check that `server.sh` is executable (`chmod +x server.sh`)
- Ensure virtual environment has all dependencies
- Restart Cursor after configuration changes

**For Jira agent specifically:**
- Verify container image is built: `podman images | grep jira-agent`
- Check `.env` file has `JIRA_URL` and `JIRA_API_TOKEN`
- Ensure `--env-file` path is absolute (no `~` tilde)

**If you see "Tool not found" errors:**
- This is often normal during initial connection
- The agent is connected, but specific tools may not be fully loaded
- Try the command again after a few seconds

### Key Differences Between Agents

**OpenDev & GitHub Agents:**
- Simple shell script execution
- Uses `venv` for Python dependencies
- Direct server.py execution

**Jira Agent:**
- Containerized deployment with Podman
- Uses `--env-file` for credentials
- Runs in isolated container environment
- More secure (credentials never in config file)
- 20+ tools for comprehensive Jira integration

### Contributing

This repository is primarily for educational purposes and demonstration. Feel free to fork and adapt for your own MCP agents!

### License

- `jira-agent` is licensed under the MIT License
- Other agents are provided as examples for educational purposes

---

## Questions?

If you have questions during the demonstration or while following along, please feel free to reach out or open an issue in this repository.

**Happy MCP building!** 🚀
