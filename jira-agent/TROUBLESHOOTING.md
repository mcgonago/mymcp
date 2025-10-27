# Jira Agent - Troubleshooting Guide

This document provides solutions to common issues you may encounter when setting up and using the Jira Agent MCP server for Cursor.

---

## Verifying Jira MCP Agent is Operational

To test if the Jira MCP agent is working correctly, run this command from your terminal:

```bash
timeout 5 podman run --rm -i --env-file ~/.rh-jira-agent.env jira-agent:latest <<< '{"jsonrpc": "2.0", "method": "exit"}' 2>&1 | head -20
```

If working correctly, you should see output like:

```
[10/24/25 21:06:34] INFO     Starting MCP server 'Jira Context     server.py:797
                             Server' with transport 'stdio'
```

This confirms the MCP server starts successfully and can connect to your Jira instance.

---

## Common Issues

### Issue: "No such image"

**Problem**: The container image hasn't been built yet.

**Solution**: 
```bash
cd <your-mymcp-cloned-repo-path>/jira-agent
make build
```

---

### Issue: "Environment file not found"

**Problem**: The `.rh-jira-agent.env` file doesn't exist or is in the wrong location.

**Solution**: 
```bash
cp <your-mymcp-cloned-repo-path>/jira-agent/example.env ~/.rh-jira-agent.env
# Then edit the file to add your Jira URL and API token
```

---

### Issue: "Authentication failed" or "401 Unauthorized"

**Problem**: Jira API token is incorrect, expired, or credentials are misconfigured.

**Error Message**:
```
JiraError HTTP 401 url: https://issues.redhat.com/rest/api/2/project
Unauthorized (401)
os_authType was 'any' and an invalid cookie was sent.
```

**Root Causes**:
1. Invalid or expired `JIRA_API_TOKEN`
2. Incorrect `JIRA_EMAIL` (doesn't match your Jira account)
3. Wrong `JIRA_URL` (pointing to incorrect Jira instance)

**Solution Steps**:

1. **Verify your environment file**:
   ```bash
   cat ~/.rh-jira-agent.env
   ```
   
   Should contain:
   ```bash
   JIRA_URL=https://issues.redhat.com
   JIRA_EMAIL=your.email@redhat.com
   JIRA_API_TOKEN=your_actual_api_token_here
   ```

2. **Generate a new API token**:
   - Go to your Jira profile settings
   - Navigate to **Security** → **API Tokens**
   - Click **Create API Token**
   - Give it a descriptive name (e.g., "Cursor Jira MCP Agent")
   - Copy the generated token

3. **Update your environment file**:
   ```bash
   # Edit the file
   nano ~/.rh-jira-agent.env
   # Update JIRA_API_TOKEN with your new token
   ```

4. **Rebuild and restart**:
   ```bash
   cd <your-mymcp-cloned-repo-path>/jira-agent
   make build
   ```
   
5. **Fully quit and restart Cursor** (Ctrl+Q)

**Note**: API tokens can expire or become invalid due to security policies. If a query worked previously but now returns 401, regenerate your token.

---

### Issue: Agent not appearing in Cursor

**Problem**: Cursor hasn't loaded the agent yet or the configuration is incorrect.

**Solution**:
1. Verify your `~/.cursor/mcp.json` has the correct **absolute path** to the env file (no `~` tilde)
2. **Fully quit Cursor** (Ctrl+Q) and restart (don't just reload window)
3. Check for any error messages in Cursor's console

---

## Additional Help

If you continue to experience issues:

1. Verify the `command` in `~/.cursor/mcp.json` is set to `podman`
2. Check that the container image is built: `podman images | grep jira-agent`
3. Verify environment file path is absolute (no `~` tilde character)
4. Restart Cursor after any configuration changes (Ctrl+Q to fully quit)
5. Check Cursor's console for any error messages

For more information, see [README.md](README.md) for setup instructions.

