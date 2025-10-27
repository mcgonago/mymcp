# GitHub Review Agent - Troubleshooting Guide

This document provides solutions to common issues you may encounter when setting up and using the GitHub Review Agent MCP server for Cursor.

---

## Issue: "ModuleNotFoundError: No module named 'github'"

**Problem**: The virtual environment is missing required Python packages or has broken internal paths.

**Solution 1 - Install dependencies**:
```bash
cd github-agent
./venv/bin/pip install -r requirements.txt
```

**Solution 2 - Recreate virtual environment** (if paths are broken):
```bash
cd github-agent
rm -rf venv
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```

> **Tip**: Using `./venv/bin/pip` installs packages directly into the virtual environment without needing to activate it first. This prevents installation issues when the venv has broken paths.

---

## Issue: "GITHUB_TOKEN environment variable not set"

**Solution**: 
1. Ensure you've created the `.env` file in `github-agent/`
2. Verify the token is in the correct format: `GITHUB_TOKEN=ghp_...`
3. Fully quit and restart Cursor (Ctrl+Q)

---

## Issue: "Authentication failed" (401 error)

**Possible causes:**
- Token is invalid or expired
- Token doesn't have required scopes (`public_repo` or `repo`)

**Solution**:
1. Go to https://github.com/settings/tokens
2. Verify your token has the required scopes
3. If needed, create a new token with proper scopes
4. Update your `.env` file with the new token

---

## Additional Help

If you continue to experience issues:

1. Verify the `command` path in `~/.cursor/mcp.json` is correct and absolute
2. Check that `server.sh` is executable: `chmod +x server.sh`
3. Ensure virtual environment has all dependencies: `./venv/bin/pip list`
4. Restart Cursor after any configuration changes (Ctrl+Q to fully quit)
5. Check Cursor's console for any error messages

For more information, see [README.md](README.md) for setup instructions.

