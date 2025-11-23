# Activity Tracker Troubleshooting Guide

Common issues and their solutions for the activity-tracker MCP agent.

---

## Issue 1: "Virtual environment not found"

### Symptoms
```
Error: Virtual environment not found at /path/to/activity-tracker-agent/venv
Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
```

### Cause
The Python virtual environment hasn't been created yet.

### Solution
```bash
cd <mymcp-repo-path>/activity-tracker-agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Verification
```bash
source venv/bin/activate
python --version  # Should show Python 3.x
pip list | grep fastmcp  # Should show fastmcp installed
```

---

## Issue 2: "GITHUB_TOKEN not configured"

### Symptoms
When calling `get_github_activity()` or `generate_status_report()`, you get:
```json
{
  "error": "GITHUB_TOKEN not configured",
  "username": "omcgonag",
  "period": {"start": "...", "end": "..."}
}
```

### Cause
The `GITHUB_TOKEN` environment variable is not set.

### Solution

**Option A**: Copy from existing github-agent configuration

```bash
cd <mymcp-repo-path>/activity-tracker-agent

# If you have github-agent configured:
grep GITHUB_TOKEN ../github-agent/.env >> .env
```

**Option B**: Create GitHub Personal Access Token

1. Go to: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Select scopes:
   - `repo` (Full control of private repositories)
   - `read:user` (Read user profile data)
4. Copy the token
5. Add to `.env`:
   ```bash
   echo "GITHUB_TOKEN=ghp_your_token_here" >> .env
   ```

### Verification
```bash
grep GITHUB_TOKEN .env
# Should show: GITHUB_TOKEN=ghp_...
```

---

## Issue 3: "MCP agent not connected in Cursor"

### Symptoms
- In Cursor, when you type `@activity-tracker`, it doesn't appear
- MCP server shows as "disconnected" or "error"

### Cause
Either the MCP configuration is incorrect, or Cursor hasn't reloaded the configuration.

### Solution

**Step 1**: Verify MCP configuration

```bash
cat ~/.cursor/mcp.json | jq '.mcpServers."activity-tracker"'
```

Should show:
```json
{
  "command": "<mymcp-repo-path>/activity-tracker-agent/server.sh",
  "args": ["stdio"],
  "env": {}
}
```

**Step 2**: Fix if incorrect

```bash
# Backup existing config
cp ~/.cursor/mcp.json ~/.cursor/mcp.json.backup

# Edit manually
nano ~/.cursor/mcp.json
```

Add the activity-tracker entry to the `mcpServers` object.

**Step 3**: Restart Cursor

Fully quit Cursor (Ctrl+Q) and restart. Wait 10 seconds for MCP agents to initialize.

### Verification

In Cursor:
1. Ctrl+Shift+P → "MCP: Manage Servers"
2. Look for "activity-tracker" - should show "✔ connected"

---

## Issue 4: "Permission denied: ./server.sh"

### Symptoms
```
bash: ./server.sh: Permission denied
```

### Cause
The startup script is not executable.

### Solution
```bash
cd <mymcp-repo-path>/activity-tracker-agent
chmod +x server.sh
```

### Verification
```bash
ls -l server.sh
# Should show: -rwxr-xr-x ... server.sh (note the 'x' for executable)
```

---

## Issue 5: "GitHub API rate limit exceeded"

### Symptoms
Error in tool response:
```
GitHub API error: 403 Client Error: rate limit exceeded
```

### Cause
You've made too many requests to GitHub API within the rate limit window.

### Details
- **Unauthenticated**: 60 requests/hour
- **Authenticated**: 5,000 requests/hour
- **Search API**: 30 requests/minute

### Solution

**Immediate**: Use cached data
```bash
# Check cache age
ls -lh ~/Work/mymcp/workspace/iproject/activity/

# If cache exists and is recent (< 24 hours), it will be used automatically
```

**Long-term**: Verify authentication
```bash
# Make sure GITHUB_TOKEN is set in .env
grep GITHUB_TOKEN <mymcp-repo-path>/activity-tracker-agent/.env
```

**Wait it out**: Rate limits reset after 1 hour.

---

## Issue 6: "Workspace project directory not found"

### Symptoms
Error when generating reports:
```
FileNotFoundError: [Errno 2] No such file or directory: '/path/to/workspace/iproject/activity'
```

### Cause
The workspace project directory doesn't exist or `WORKSPACE_PROJECT` is misconfigured.

### Solution

**Step 1**: Check configuration
```bash
grep WORKSPACE_PROJECT <mymcp-repo-path>/activity-tracker-agent/.env
```

**Step 2**: Verify directory exists
```bash
ls -la ~/Work/mymcp/workspace/iproject
```

**Step 3**: Create if missing
```bash
mkdir -p ~/Work/mymcp/workspace/iproject/activity
```

**Step 4**: Update .env if wrong path
```bash
nano <mymcp-repo-path>/activity-tracker-agent/.env
# Set: WORKSPACE_PROJECT=<mymcp-repo-path>/workspace/iproject
```

---

## Issue 7: "OpenDev API connection timeout"

### Symptoms
```
OpenDev API error: HTTPSConnectionPool(host='review.opendev.org', port=443): Read timed out
```

### Cause
Network issues or review.opendev.org is temporarily unavailable.

### Solution

**Immediate**: Retry after a few minutes
```
@activity-tracker generate_status_report("last week")
```

**Check network**:
```bash
ping review.opendev.org
curl -I https://review.opendev.org
```

**Use cached data**: If you've successfully fetched data before, cached data (< 24 hours old) will be used automatically.

---

## Issue 8: "JSON decode error from OpenDev API"

### Symptoms
```
OpenDev API JSON parse error: Expecting value: line 1 column 1 (char 0)
```

### Cause
Gerrit API returns responses with XSSI protection prefix `)]}'` that wasn't stripped correctly.

### Solution
This should be handled automatically by the code. If you see this error, it's likely a bug.

**Workaround**: Generate an issue report
1. Note the exact error message
2. Note which tool you were calling
3. Check if a newer version of activity-tracker-agent is available

**Debug**:
```bash
cd <mymcp-repo-path>/activity-tracker-agent
python server.py  # Test standalone
```

---

## Issue 9: "Cache is stale but not refreshing"

### Symptoms
You know there's new activity, but the report shows old data.

### Cause
Cache file exists and is being used, but you want to force a refresh.

### Solution

**Option A**: Delete specific cache file
```bash
# Find the week number you want to refresh
ls ~/Work/mymcp/workspace/iproject/activity/

# Delete it
rm ~/Work/mymcp/workspace/iproject/activity/2025-W47.json

# Re-run the report
@activity-tracker generate_status_report("last week")
```

**Option B**: Delete all cache files (nuclear option)
```bash
rm ~/Work/mymcp/workspace/iproject/activity/*.json
```

**Option C**: Adjust cache age threshold
```bash
# Edit .env
nano <mymcp-repo-path>/activity-tracker-agent/.env

# Change to 1 hour instead of 24
CACHE_MAX_AGE_HOURS=1
```

---

## Issue 10: "No activity showing up in report"

### Symptoms
Report generates successfully but shows 0 activity for all categories.

### Possible Causes & Solutions

### Cause A: Wrong username

**Check**:
```bash
grep -E "GITHUB_USERNAME|OPENDEV_USERNAME" <mymcp-repo-path>/activity-tracker-agent/.env
```

**Fix**:
```bash
# Edit .env
nano <mymcp-repo-path>/activity-tracker-agent/.env

# Set correct usernames
GITHUB_USERNAME=your_actual_github_username
OPENDEV_USERNAME=your_actual_opendev_username
```

### Cause B: Wrong date range

**Check**: You actually had activity in the date range you specified.

**Fix**: Try a broader range:
```
@activity-tracker generate_status_report("2025-11-01 to 2025-11-30")
```

### Cause C: Private repos (GitHub)

GitHub API won't return activity from private repos unless your token has the correct scopes.

**Fix**: Regenerate token with `repo` scope (see Issue 2).

---

## Issue 11: "ModuleNotFoundError: No module named 'fastmcp'"

### Symptoms
```
Traceback (most recent call last):
  File "server.py", line 10, in <module>
    from mcp.server.fastmcp import FastMCP
ModuleNotFoundError: No module named 'fastmcp'
```

### Cause
Dependencies not installed in virtual environment.

### Solution
```bash
cd <mymcp-repo-path>/activity-tracker-agent
source venv/bin/activate
pip install -r requirements.txt
```

### Verification
```bash
pip list | grep fastmcp
# Should show: fastmcp    0.x.x
```

---

## Debug Mode

For advanced troubleshooting, you can run the server in standalone mode to see detailed output:

```bash
cd <mymcp-repo-path>/activity-tracker-agent
source venv/bin/activate

# Test mode (generates report for "last week")
python server.py

# MCP server mode (with debug output)
python server.py stdio
```

The standalone test mode will print the full report to stdout and show any errors directly.

---

## Getting Help

If none of these solutions work:

1. **Check logs**: Look at Cursor's MCP server logs (if accessible)
2. **Test components individually**:
   ```bash
   # Test GitHub API directly
   curl -H "Authorization: Bearer YOUR_TOKEN" \
     "https://api.github.com/users/omcgonag/events?per_page=10"
   
   # Test OpenDev API directly
   curl "https://review.opendev.org/changes/?q=owner:omcgonag&n=5"
   ```
3. **Create an issue**: Document the error, steps to reproduce, and your environment
4. **Review implementation WIP**: Check `workspace/iproject/analysis/activity_tracker_implementation_wip.md` for known issues

---

**Last Updated**: 2025-11-22  
**Version**: 1.0



