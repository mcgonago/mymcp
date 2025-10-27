# OpenDev Review Agent - Troubleshooting Guide

This document provides solutions to common issues you may encounter when setting up and using the OpenDev Review Agent MCP server for Cursor.

---

## Issue: "ModuleNotFoundError: No module named 'requests'" or similar

**Problem**: The virtual environment is missing required Python packages or has broken internal paths.

**Solution 1 - Install dependencies**:
```bash
cd opendev-review-agent
./venv/bin/pip install -r requirements.txt
```

**Solution 2 - Recreate virtual environment** (if paths are broken):
```bash
cd opendev-review-agent
rm -rf venv
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```

> **Tip**: Using `./venv/bin/pip` installs packages directly into the virtual environment without needing to activate it first. This prevents installation issues when the venv has broken paths.

---

## Issue: Server fails to start or times out

**Solution**:
1. Check that `server.sh` is executable: `chmod +x server.sh`
2. Verify virtual environment exists: `ls -la venv/`
3. Check that dependencies are installed:
   ```bash
   source venv/bin/activate
   pip list | grep -E "requests|fastmcp"
   ```
4. Test the server manually:
   ```bash
   cd opendev-review-agent
   bash server.sh <<< '{"jsonrpc": "2.0", "method": "exit"}' 2>&1 | head -20
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

