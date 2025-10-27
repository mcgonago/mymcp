# GitLab Review Agent

An MCP (Model Context Protocol) agent for Cursor that analyzes GitLab Issues, Merge Requests, and Commits from internal Red Hat GitLab (gitlab.cee.redhat.com).

> **Note**: The steps below can be executed from within the repository where the `server.sh` and `server.py` files are located.

> **Try This Yourself**: You can also try this on your own by asking the same question I asked Gemini:  
> *"Please give me the step-by-step instructions for building an MCP agent that analyzes gitlab.cee.redhat.com issues, merge requests, and commits"*

## Background

Building a specialized agent for your internal GitLab instance is an excellent way to integrate code review and issue-tracking directly into the Cursor LLM environment. Since GitLab is an internal service (gitlab.cee.redhat.com), this custom MCP server handles authentication and API calls to fetch issue, merge request, and commit data.

This agent will be a tool that the LLM uses to answer prompts like:
- **"Analyze this issue: group/project/issues/123"**
- **"Review this merge request: group/project/merge_requests/456"**
- **"Analyze this commit: https://gitlab.cee.redhat.com/group/project/-/commit/abc123"**

## Set Up the Environment

First, set up a minimal Python environment for your MCP server, you can do this from directory `gitlab-rh-agent` of your repo:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Alternatively, install packages directly into the venv without activating it:

```bash
./venv/bin/pip install -r requirements.txt
```

## Configure GitLab Authentication

The GitLab agent requires a personal access token to fetch data from the GitLab API.

### Create a GitLab Personal Access Token

1. Go to https://gitlab.cee.redhat.com/-/user_settings/personal_access_tokens
2. Click **"Add new token"**
3. Give it a descriptive name: `Cursor GitLab MCP Agent`
4. Select scopes:
   - ✅ `read_api` (required for fetching issues and merge requests)
5. Click **"Create personal access token"**
6. **Copy the token** (you won't be able to see it again!)

### Set Up the Environment File

Create a `.env` file in the `gitlab-rh-agent` directory:

```bash
cp example.env .env
```

Edit the `.env` file and replace `your_gitlab_token_here` with your actual token:

```bash
GITLAB_TOKEN=glpat-your_actual_token_here
```

> [!WARNING]
> **Never commit the `.env` file to Git!** It contains your personal access token.  
> The `.gitignore` file is already configured to exclude `.env`.

## Create the Server Script (server.py)

The `server.py` file is already provided in this directory. It defines the logic for the `gitlab_resource_fetcher` tool that:

- Accepts GitLab paths or full URLs (e.g., `group/project/issues/123` or `https://gitlab.cee.redhat.com/...`)
- Fetches data from the GitLab API at `https://gitlab.cee.redhat.com/api/v4`
- Returns structured data for the LLM to analyze

Key features:
- ✅ Supports Issues, Merge Requests, **and Commits**
- ✅ Accepts both path format and full URLs
- ✅ Handles URL encoding for project paths
- ✅ Provides detailed metadata (author, state, assignees, labels, stats)
- ✅ Fetches commit diffs and file change summaries
- ✅ Formats data for security analysis (CVE detection)

## Create the Server Launcher (server.sh)

The `server.sh` file is already provided in this directory. It:

- Loads environment variables from `.env`
- Activates the virtual environment
- Runs the Python server

Make the script executable:

```bash
chmod +x server.sh
```

## Configure Cursor MCP

### Step 1: Open Cursor Settings

Go to **Cursor Settings** → **Features** → **Model Context Protocol**

### Step 2: Edit Your MCP Configuration

Open your MCP configuration file (`~/.cursor/mcp.json`)

### Step 3: Add the GitLab Agent Configuration

Add this JSON configuration (remember to replace `<your-mymcp-cloned-repo-path>`):

```json
{
  "mcpServers": {
    "gitlab-cee-agent": {
      "command": "<your-mymcp-cloned-repo-path>/gitlab-rh-agent/server.sh",
      "description": "Agent to fetch and analyze issues/MRs from internal Red Hat GitLab."
    }
  }
}
```

### Step 4: Save and Reload Cursor

**Save your new mcp.json configuration**  
Go to **File → Save** and then restart Cursor (**Ctrl+Shift+P** → "Developer: Reload Window")

> **Note**: Alternatively, you can fully exit Cursor (**Ctrl+Q**) and restart it, which will also reload the new settings.

## Testing the Agent

### Invoke the GitLab Cursor Agent

In Cursor's chat box, you can now invoke your custom agent using the `@` symbol:

**Test with an Issue:**
```
@gitlab-cee-agent Analyze the state and description of issue openstack-konflux/osp-director-operator-17.1/issues/24
```

**Test with a Merge Request:**
```
@gitlab-cee-agent Review merge request openstack-konflux/osp-director-operator-17.1/merge_requests/5
```

**Test with a Commit (using full URL):**
```
@gitlab-cee-agent Analyze commit https://gitlab.cee.redhat.com/eng/openstack/python-django/-/commit/848fd870bb51ae6d8ea44512665dab8257f9c27a
```

**Test with a Commit (using path format):**
```
@gitlab-cee-agent Analyze commit eng/openstack/python-django/commit/848fd870bb51ae6d8ea44512665dab8257f9c27a
```

**Supported formats:**
- Issues: `group/project/issues/123`
- Merge Requests: `group/project/merge_requests/456`
- Commits: `group/project/commit/abc123` or full URLs

### Expected Output

**For Issues and Merge Requests**, the agent will fetch:
- **Title** and **State** (opened, closed, merged)
- **Description** (first 500 characters)
- **Author** and **Assignees**
- **Labels** and timestamps
- **Analysis prompt** for the LLM to provide insights

**For Commits**, the agent will fetch:
- **Commit title and full message**
- **Author and committer** information
- **Timestamps** (authored and committed dates)
- **Change statistics** (+additions, -deletions, total lines)
- **Files changed** (list of modified files)
- **Analysis prompt** with focus on security implications (CVEs) and technical changes

### Test from Terminal (Optional)

You can also test the server directly from the terminal:

```bash
cd gitlab-rh-agent
source venv/bin/activate
./server.sh
```

Then send JSON input for different resource types:

**Test an Issue:**
```bash
echo '{"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "gitlab_resource_fetcher", "arguments": {"resource_path": "openstack-konflux/osp-director-operator-17.1/issues/24"}}}' | ./server.sh
```

**Test a Commit (with full URL):**
```bash
echo '{"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "gitlab_resource_fetcher", "arguments": {"resource_path": "https://gitlab.cee.redhat.com/eng/openstack/python-django/-/commit/848fd870bb51ae6d8ea44512665dab8257f9c27a"}}}' | ./server.sh
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'requests'" or similar

**Problem**: The virtual environment is missing required Python packages or has broken internal paths.

**Solution 1 - Install dependencies**:
```bash
cd gitlab-rh-agent
./venv/bin/pip install -r requirements.txt
```

**Solution 2 - Recreate virtual environment** (if paths are broken):
```bash
cd gitlab-rh-agent
rm -rf venv
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```

> **Tip**: Using `./venv/bin/pip` installs packages directly into the virtual environment without needing to activate it first. This prevents installation issues when the venv has broken paths.

### Issue: "GITLAB_TOKEN environment variable not set"

**Solution**: 
1. Ensure you've created the `.env` file in `gitlab-rh-agent/`
2. Verify the token is in the correct format: `GITLAB_TOKEN=glpat-...`
3. Fully quit and restart Cursor (Ctrl+Q)

### Issue: "Authentication failed" (401 error)

**Possible causes:**
- Token is invalid or expired
- Token doesn't have `read_api` scope

**Solution**:
1. Go to https://gitlab.cee.redhat.com/-/user_settings/personal_access_tokens
2. Verify your token has the `read_api` scope
3. If needed, create a new token with proper scopes
4. Update your `.env` file with the new token

### Issue: "Resource not found" (404 error)

**Possible causes:**
- Incorrect path format
- You don't have access to the requested issue/MR
- The issue/MR doesn't exist

**Solution**:
1. Verify the path format: `group/project/issues/123`
2. Check that you have access to the project in GitLab
3. Confirm the issue/MR number is correct

### Issue: Server not responding

**Solution**:
1. Check that `server.sh` is executable: `chmod +x server.sh`
2. Verify virtual environment exists: `ls -la venv/`
3. Check that dependencies are installed:
   ```bash
   source venv/bin/activate
   pip list | grep -E "requests|fastmcp"
   ```

## Security Notes

- ✅ The `.env` file is excluded from Git via `.gitignore`
- ✅ Never commit your personal access token
- ✅ The token only has `read_api` scope (cannot modify data)
- ✅ This is for internal Red Hat GitLab only (gitlab.cee.redhat.com)

## Files

- `server.py` - Main MCP server implementation
- `server.sh` - Launch script that loads `.env` for GitLab token
- `example.env` - Template for environment variables
- `requirements.txt` - Python dependencies
- `.gitignore` - Ensures `.env` is not committed

## What This Agent Can Do

✅ **Fetch Issue Details**: Get full information about any GitLab issue you have access to  
✅ **Fetch Merge Request Details**: Analyze merge requests with all metadata  
✅ **Analyze Commits**: Review individual commits with diffs and file changes  
✅ **Security Analysis**: Identify CVEs and security-related changes in commits  
✅ **Analyze State**: Understand the current status and progress of issues/MRs  
✅ **Review Descriptions**: Get summaries of issues and MRs  
✅ **Track Assignments**: See who is working on what  
✅ **View Labels**: Understand categorization and tagging  
✅ **Full URL Support**: Paste GitLab URLs directly from your browser

## Next Steps

- Try analyzing various issues, merge requests, and commits from your projects
- Use the agent to review security fixes and CVE patches
- Analyze commit history for specific features or bug fixes
- Use the agent to get quick summaries during code reviews
- Combine with other MCP agents for comprehensive project analysis



