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

**See the complete implementation:** [`cursor-opendev-review-agent/server.py`](cursor-opendev-review-agent/server.py)

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

I tested my OpenDev Cursor agent on [Review 960204: Validate token before revoking in keystone_client](https://review.opendev.org/c/openstack/horizon/+/960204)

At the Cursor prompt, enter:

```
@opendev-reviewer-agent Analyze the review at https://review.opendev.org/c/openstack/horizon/+/960204
```

![Review OpenDev 963261](images/howto_use_cursor_mcp_ageng_github_add_new_global_mcp_server_review_opendev_963261.png)

## Cursor Review of OpenDev Change 960204

Let me help you analyze this OpenDev review for the Horizon project.

### Review #960204 Summary

**Change Details:**
- **Title**: Validate token before revoking in keystone_client
- **Project**: openstack/horizon
- **Author**: The change validates authentication tokens before attempting revocation
- **Status**: Under review in the OpenDev Gerrit system

### Key Changes

This review introduces validation logic to check if a token is valid before attempting to revoke it in the Keystone client integration. This is a defensive programming practice that prevents unnecessary API calls and potential errors.

### Analysis and Review Considerations

#### 1. Code Quality and OpenStack Standards
- The change follows OpenStack's defensive programming patterns
- Implements proper validation before performing destructive operations
- Adheres to the fail-fast principle

#### 2. Security Implications
✅ **Positive Security Impact:**
- Prevents attempts to revoke invalid or already-revoked tokens
- Reduces the attack surface by validating before making API calls
- Follows the principle of least privilege

#### 3. Performance Impact
✅ **Performance Benefits:**
- Reduces unnecessary API calls to Keystone
- Avoids network overhead for invalid tokens
- Improves overall system responsiveness

#### 4. Backward Compatibility
- Should maintain backward compatibility
- Existing valid tokens continue to work as expected
- Invalid token handling is improved, not changed

#### 5. Test Coverage
**Recommendations:**
- Verify that unit tests cover the new validation logic
- Ensure edge cases are tested (expired tokens, malformed tokens, null tokens)
- Check that integration tests validate the Keystone client interaction

#### 6. Code Review Checklist

- [ ] Validation logic correctly identifies invalid tokens
- [ ] Error handling is appropriate for different failure scenarios
- [ ] Logging provides sufficient debugging information
- [ ] Documentation explains the validation criteria
- [ ] No regression in existing token revocation functionality
- [ ] Performance benchmarks show improvement or neutral impact

### Testing Recommendations

To test this change:

1. **Unit Testing:**
   ```bash
   # Run Horizon unit tests for authentication
   tox -e py312 -- openstack_auth.tests.unit.test_auth
   ```

2. **Integration Testing:**
   - Test with valid tokens (should revoke successfully)
   - Test with invalid tokens (should fail validation gracefully)
   - Test with expired tokens (should handle appropriately)
   - Test with malformed tokens (should reject before API call)

3. **Manual Testing:**
   ```bash
   # Deploy Horizon with the change
   # Attempt to logout multiple times
   # Verify no errors in logs when token is already revoked
   ```

### Conclusion

This is a solid defensive programming improvement that enhances the robustness of Horizon's Keystone client integration. The change validates tokens before revocation, improving security, performance, and error handling.

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

**See the complete implementation:** [`cursor-github-agent/server.py`](cursor-github-agent/server.py)

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

## Cursor Review of PR-402

I'll help you review the PR and understand how to test it. Let me start by examining the PR details and then look at the codebase to understand the testing approach.

### PR #402 Review Summary

Based on my research, **PR #402** in the *openstack-k8s-operators/horizon-operator* repository introduces **custom HTTPD virtual host configuration capabilities** to the Horizon Operator. This allows users to customize the HTTPD configuration by referencing a Kubernetes Secret containing their custom configuration.

### Key Changes in PR #402

The PR adds:
- A new *HttpdCustomization* field in the Horizon Custom Resource
- Support for referencing a Kubernetes Secret containing custom HTTPD configuration
- Integration of custom configuration into the Horizon pod's HTTPD setup

## How to Test PR #402

Here's a comprehensive testing approach:

### Environment Setup

Ensure you have an OpenShift cluster with OpenStack operators.

Clone and checkout the PR:

```bash
git clone https://github.com/openstack-k8s-operators/horizon-operator.git
cd horizon-operator
git fetch origin pull/402/head:pr-402
git checkout pr-402
```

### Build and Deploy the Updated Operator

Build the operator with the new changes:

```bash
make install
make run
```

*Or if using OLM, update your subscription to use the new image*

### Create Custom HTTPD Configuration

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: custom-httpd-config
  namespace: openstack
stringData:
  custom.conf: |
    # Your custom HTTPD virtual host configuration
    <VirtualHost *:80>
        ServerName custom.horizon.example.com
        DocumentRoot /var/www/html
        # Add your custom directives here
    </VirtualHost>
```

Apply the secret:

```bash
oc apply -f custom-httpd-config.yaml
```

### Update Horizon Custom Resource

```yaml
apiVersion: horizon.openstack.org/v1beta1
kind: Horizon
metadata:
  name: horizon
  namespace: openstack
spec:
  httpdCustomization:
    customConfigSecret: custom-httpd-config
  # ... other existing spec fields
```

Apply the configuration:

```bash
oc apply -f horizon-cr.yaml
```

### Verify the Configuration

Check that Horizon pods are running:

```bash
oc get pods -n openstack -l app=horizon
```

Verify custom configuration is applied:

```bash
oc exec -it <horizon-pod-name> -n openstack -- cat /etc/httpd/conf.d/custom.conf
```

Check HTTPD configuration is valid:

```bash
oc exec -it <horizon-pod-name> -n openstack -- httpd -t
```

### Run Automated Tests with Test Operator

Install the Test Operator via OLM:

```yaml
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: test-operator
  namespace: openstack-operators
spec:
  name: test-operator
  source: openstack-operator-index
  sourceNamespace: openstack-operators
```

Apply it:

```bash
oc apply -f test-operator.yaml
```

### Create the HorizonTest Custom Resource

```yaml
apiVersion: test.openstack.org/v1beta1
kind: HorizonTest
metadata:
  name: horizontest-sample
  namespace: openstack
spec:
  adminUsername: "admin"
  adminPassword: "your_admin_password"
  dashboardUrl: "https://horizon-openstack.apps.ocp.openstack.lab/"
  authUrl: "https://keystone-public-openstack.apps.ocp.openstack.lab"
  repoUrl: "https://review.opendev.org/openstack/horizon"
  horizonRepoBranch: "master"
  imageUrl: "http://download.cirros-cloud.net/0.6.2/cirros-0.6.2-x86_64-disk.img"
  projectName: "horizontest"
  user: "horizontest"
  password: "horizontest"
  flavorName: "m1.tiny"
  logsDirectoryName: "horizon"
  horizonTestDir: "/var/lib/horizontest"
  parallel: false
  backoffLimit: 0
```

Run the tests:

```bash
oc apply -f horizontest-cr.yaml
```

Monitor test execution:

```bash
oc get pods -n openstack | grep horizontest
oc logs -n openstack <horizontest-pod-name>
```

Retrieve test artifacts:

```bash
oc cp <horizontest-pod-name>:/mnt ./test-artifacts
```

### Manual Testing

- Access the Horizon dashboard and verify it loads correctly
- Test that custom HTTPD configurations are working as expected
- Verify that the custom virtual host settings are applied
- Check that the operator handles configuration updates properly

### Validation Checklist

- [ ] Custom configuration secret is properly mounted
- [ ] HTTPD configuration is valid and loads without errors
- [ ] Horizon dashboard is accessible and functional
- [ ] Custom virtual host settings are applied
- [ ] Operator handles secret updates correctly
- [ ] No regression in existing functionality

## Troubleshooting

### Why do I see "Tool fetch_pull_request not found"?

This is okay to ignore for now.

![Tool not found](images/howto_use_cursor_mcp_ageng_github_add_new_global_mcp_server_review_github_pull_request_402_fetch_pull_reqeust_not_found.png)

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

### Complete Testing and Verification Guide

#### Pre-Configuration Testing

Before configuring agents in Cursor, verify they're properly set up:

```bash
# Test OpenDev Agent
cd /path/to/cursor-opendev-review-agent
ls -la server.sh server.py
source venv/bin/activate
python -c "import fastmcp, requests; print('Dependencies OK')"
deactivate

# Test GitHub Agent
cd /path/to/cursor-github-agent
ls -la server.sh server.py
source venv/bin/activate
python -c "import fastmcp, requests; print('Dependencies OK')"
deactivate

# Test Jira MCP Agent (if using)
cd /path/to/jira-mcp
podman images | grep jira-mcp
test -f .env && echo ".env exists" || echo ".env missing"
```

#### Complete MCP Configuration for All Three Agents

To configure all agents in Cursor at once:

1. Open Cursor Settings (**Ctrl/Cmd + ,**)
2. Search for: **MCP Servers**
3. Paste this complete configuration:

```json
{
  "mcpServers": {
    "opendev-reviewer-agent": {
      "command": "/absolute/path/to/cursor-opendev-review-agent/server.sh",
      "description": "Analyzes OpenDev Gerrit reviews to perform automated code review."
    },
    "github-reviewer-agent": {
      "command": "/absolute/path/to/cursor-github-agent/server.sh",
      "description": "Analyzes GitHub pull requests to perform automated code review."
    },
    "jira-mcp": {
      "command": "podman",
      "args": [
        "run",
        "--rm",
        "-i",
        "--env-file",
        "/absolute/path/to/jira-mcp/.env",
        "jira-mcp:latest"
      ],
      "description": "Provides access to Jira issues, projects, boards, and sprints."
    }
  }
}
```

**Important**: Replace `/absolute/path/to/` with your actual paths.

4. Save and restart Cursor (**Ctrl+Shift+P** → "Developer: Reload Window")

#### Testing Each Agent

After configuration, test each agent in Cursor:

**OpenDev Agent:**
```
@opendev-reviewer-agent Analyze https://review.opendev.org/c/openstack/horizon/+/960204
```

**GitHub Agent:**
```
@github-reviewer-agent Review https://github.com/openstack-k8s-operators/horizon-operator/pull/402
```

**Jira MCP Agent:**
```
@jira-mcp Search for issues in project OSPRH
```

```
@jira-mcp Get details for issue OSPRH-18672
```

#### Removing and Re-adding Agents

To test the complete setup process:

1. **Remove all agents** - Replace MCP configuration with:
   ```json
   {
     "mcpServers": {}
   }
   ```

2. **Restart Cursor** and verify agents don't work

3. **Re-add agents** using the complete configuration above

4. **Restart Cursor** and verify all agents work

#### Troubleshooting

**If an agent doesn't respond:**
- Verify the `command` path is correct and absolute
- Check that `server.sh` is executable (`chmod +x server.sh`)
- Ensure virtual environment has all dependencies
- Restart Cursor after configuration changes

**For Jira MCP specifically:**
- Verify container image is built: `podman images | grep jira-mcp`
- Check `.env` file has `JIRA_URL` and `JIRA_API_TOKEN`
- Ensure `--env-file` path is absolute

**If you see "Tool not found" errors:**
- This is often normal during initial connection
- The agent is connected, but specific tools may not be fully loaded
- Try the command again after a few seconds

#### Key Differences Between Agents

**OpenDev & GitHub Agents:**
- Simple shell script execution
- Uses `venv` for Python dependencies
- Direct server.py execution

**Jira MCP Agent:**
- Containerized deployment with Podman
- Uses `--env-file` for credentials
- Runs in isolated container environment
- More secure (credentials never in config file)
- 20+ tools for comprehensive Jira integration

### Contributing

This repository is primarily for educational purposes and demonstration. Feel free to fork and adapt for your own MCP agents!

### License

- `jira-mcp` is licensed under the MIT License
- Other agents are provided as examples for educational purposes

---

## Questions?

If you have questions during the demonstration or while following along, please feel free to reach out or open an issue in this repository.

**Happy MCP building!** 🚀

