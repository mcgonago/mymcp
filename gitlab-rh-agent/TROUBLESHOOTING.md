# GitLab Review Agent - Troubleshooting Guide

This document provides solutions to common issues you may encounter when setting up and using the GitLab Review Agent MCP server for Cursor.

---

## Issue: "ModuleNotFoundError: No module named 'requests'" or similar

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

---

## Issue: "GITLAB_TOKEN environment variable not set"

**Solution**: 
1. Ensure you've created the `.env` file in `gitlab-rh-agent/`
2. Verify the token is in the correct format: `GITLAB_TOKEN=glpat-...`
3. Fully quit and restart Cursor (Ctrl+Q)

---

## Issue: "Authentication failed" (401 error)

**Possible causes:**
- Token is invalid or expired
- Token doesn't have `read_api` scope

**Solution**:
1. Go to https://gitlab.cee.redhat.com/-/user_settings/personal_access_tokens
2. Verify your token has the `read_api` scope
3. If needed, create a new token with proper scopes
4. Update your `.env` file with the new token

---

## Issue: "Resource not found" (404 error)

**Possible causes:**
- Incorrect path format
- You don't have access to the requested issue/MR
- The issue/MR doesn't exist

**Solution**:
1. Verify the path format: `group/project/issues/123`
2. Check that you have access to the project in GitLab
3. Confirm the issue/MR number is correct

---

## Issue: Server not responding

**Solution**:
1. Check that `server.sh` is executable: `chmod +x server.sh`
2. Verify virtual environment exists: `ls -la venv/`
3. Check that dependencies are installed:
   ```bash
   source venv/bin/activate
   pip list | grep -E "requests|fastmcp"
   ```

---

## Additional Help

If you continue to experience issues:

1. Verify the `command` path in `~/.cursor/mcp.json` is correct and absolute
2. Check that `server.sh` is executable: `chmod +x server.sh`
3. Ensure virtual environment has all dependencies: `./venv/bin/pip list`
4. Restart Cursor after any configuration changes (Ctrl+Q to fully quit)
5. Check Cursor's console for any error messages

For more information, see [README.md](README.md) for setup instructions.

