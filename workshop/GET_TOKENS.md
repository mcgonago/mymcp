# Get Authentication Tokens - Workshop Pre-Requisite

**⏰ Time Required:** 30-45 minutes  
**📋 Must Complete:** BEFORE attending the workshop  
**✅ Verification:** Run `./check_authentication_tokens.sh` successfully

---

## Overview

This document guides you through setting up authentication for all MCP agents. You'll need tokens/credentials for:

| Agent | Required? | Setup Time | Used For |
|-------|-----------|------------|----------|
| **OpenDev Review Agent** | ✅ Yes | 2 min | OpenStack Gerrit reviews (public, no auth needed) |
| **GitHub Agent** | ✅ Yes | 5 min | GitHub pull request analysis |
| **GitLab Agent** | ⚠️ Optional | 5 min | Internal GitLab (gitlab.cee.redhat.com) |
| **Jira Agent** | ⚠️ Optional | 10 min | Jira ticket analysis |

**Minimum for workshop:** OpenDev + GitHub agents (no tokens needed for OpenDev!)

---

## Prerequisites

Before you begin, ensure you have:

- [ ] **podman** installed (`sudo dnf install podman` on Fedora/RHEL)
- [ ] **Python 3.8+** installed (`python3 --version`)
- [ ] **Git** installed and configured
- [ ] **Text editor** (nano, vim, or your preference)
- [ ] **mymcp repository** cloned: `git clone <repo-url> ~/Work/mymcp`

---

## Agent 1: OpenDev Review Agent (Required)

**Good news:** No authentication required! OpenDev Gerrit reviews are public.

### Setup Steps

```bash
cd ~/Work/mymcp/opendev-review-agent

# Create virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Make server script executable
chmod +x server.sh

# Test it works
./server.sh <<< '{"jsonrpc": "2.0", "method": "exit"}' 2>&1 | head -20
```

**Expected Output:**
```
╭────────────────────────────────────────────────────────────────────────────╮
│                            FastMCP  2.0                                    │
│                 🖥️  Server name:     opendev-reviewer                      │
│                 📦 Transport:       STDIO                                  │
╰────────────────────────────────────────────────────────────────────────────╯
```

✅ **Done!** OpenDev agent is ready.

---

## Agent 2: GitHub Agent (Required)

GitHub requires a personal access token for API access.

### Step 1: Create GitHub Personal Access Token

1. Go to https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Give it a descriptive name: **`Cursor GitHub MCP Agent`**
4. Select scopes:
   - ✅ `public_repo` (for accessing public repositories)
   - ✅ `repo` (only if you need access to private repositories)
5. Click **"Generate token"**
6. **📋 Copy the token** (you won't be able to see it again!)

**Important:** Treat this token like a password! Anyone with it can access your GitHub on your behalf.

### Step 2: Set Up Environment File

```bash
cd ~/Work/mymcp/github-agent

# Create virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env file from example
cp example.env .env

# Edit the .env file and add your token
nano .env
```

**Contents of `.env`:**
```bash
GITHUB_TOKEN=ghp_your_actual_token_here
```

Save and exit (Ctrl+X, then Y, then Enter in nano)

### Step 3: Make Server Script Executable

```bash
chmod +x server.sh
```

### Step 4: Test the Agent

```bash
# Test the agent starts correctly
./server.sh <<< '{"jsonrpc": "2.0", "method": "exit"}' 2>&1 | head -20
```

**Expected Output:**
```
╭────────────────────────────────────────────────────────────────────────────╮
│                            FastMCP  2.0                                    │
│                 🖥️  Server name:     github-reviewer                       │
│                 📦 Transport:       STDIO                                  │
╰────────────────────────────────────────────────────────────────────────────╯
```

✅ **Done!** GitHub agent is ready.

---

## Agent 3: GitLab Agent (Optional - Red Hat Internal)

**Skip this if:** You don't have access to gitlab.cee.redhat.com

### Step 1: Create GitLab Personal Access Token

1. Go to https://gitlab.cee.redhat.com/-/user_settings/personal_access_tokens
2. Click **"Add new token"**
3. Give it a descriptive name: **`Cursor GitLab MCP Agent`**
4. Select scopes:
   - ✅ `read_api` (required for fetching issues and merge requests)
5. Click **"Create personal access token"**
6. **📋 Copy the token** (you won't be able to see it again!)

### Step 2: Set Up Environment File

```bash
cd ~/Work/mymcp/gitlab-rh-agent

# Create virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env file from example
cp example.env .env

# Edit the .env file and add your token
nano .env
```

**Contents of `.env`:**
```bash
GITLAB_TOKEN=glpat-your_actual_token_here
```

Save and exit (Ctrl+X, then Y, then Enter in nano)

### Step 3: Make Server Script Executable

```bash
chmod +x server.sh
```

### Step 4: Test the Agent

```bash
./server.sh <<< '{"jsonrpc": "2.0", "method": "exit"}' 2>&1 | head -20
```

**Expected Output:**
```
╭────────────────────────────────────────────────────────────────────────────╮
│                            FastMCP  2.0                                    │
│                 🖥️  Server name:     gitlab-cee                            │
│                 📦 Transport:       STDIO                                  │
╰────────────────────────────────────────────────────────────────────────────╯
```

✅ **Done!** GitLab agent is ready.

---

## Agent 4: Jira Agent (Optional)

**Skip this if:** You don't need Jira integration

### Step 1: Create Jira API Token

**For Atlassian Cloud Jira:**
1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click **"Create API token"**
3. Give it a label: **`Cursor Jira MCP Agent`**
4. **📋 Copy the token**

**For Red Hat Jira (issues.redhat.com):**
1. Go to your Jira profile → **Security** → **API Tokens**
2. Click **"Create API Token"**
3. Give it a descriptive name: **`Cursor Jira MCP Agent`**
4. **📋 Copy the token**

### Step 2: Set Up Environment File

```bash
cd ~/Work/mymcp/jira-agent

# Create environment file in your home directory
cp example.env ~/.rh-jira-agent.env

# Edit the file and add your credentials
nano ~/.rh-jira-agent.env
```

**Contents of `~/.rh-jira-agent.env`:**
```bash
JIRA_URL=https://issues.redhat.com
JIRA_API_TOKEN=your_actual_api_token_here
```

**⚠️ IMPORTANT:** The variable MUST be named `JIRA_API_TOKEN` (not `JIRA_TOKEN`)!

Save and exit (Ctrl+X, then Y, then Enter in nano)

### Step 3: Build the Container Image

```bash
cd ~/Work/mymcp/jira-agent
make build
```

**Expected Output:**
```
Building container image jira-agent:latest
STEP 1/5: FROM python:3.11-slim
...
Successfully tagged localhost/jira-agent:latest
```

### Step 4: Test the Agent

```bash
timeout 5 podman run --rm -i --env-file ~/.rh-jira-agent.env jira-agent:latest <<< '{"jsonrpc": "2.0", "method": "exit"}' 2>&1 | head -20
```

**Expected Output:**
```
[10/24/25 21:06:34] INFO     Starting MCP server 'Jira Context     server.py:797
                             Server' with transport 'stdio'
```

✅ **Done!** Jira agent is ready.

---

## Configure Cursor MCP Settings

After setting up all agents, you need to add them to Cursor's MCP configuration.

### Step 1: Open Cursor Settings

1. Open Cursor
2. Press **Cmd/Ctrl + Comma** (or **File** → **Settings**)
3. Search for **"MCP Servers"** or go to **Features** → **MCP Servers**
4. Click **"+ Add new global MCP server"**

### Step 2: Add Each Agent

**Important:** Replace `<your-home-directory>` with your actual home path (e.g., `/home/username`). Do NOT use the tilde (`~`) character.

#### OpenDev Review Agent

```json
{
  "mcpServers": {
    "opendev-reviewer-agent": {
      "command": "<your-home-directory>/Work/mymcp/opendev-review-agent/server.sh",
      "description": "Analyzes OpenDev Gerrit reviews to perform automated code review."
    }
  }
}
```

#### GitHub Agent

```json
{
  "mcpServers": {
    "github-reviewer-agent": {
      "command": "<your-home-directory>/Work/mymcp/github-agent/server.sh",
      "description": "Analyzes GitHub pull requests to perform automated code review."
    }
  }
}
```

#### GitLab Agent (Optional)

```json
{
  "mcpServers": {
    "gitlab-cee-agent": {
      "command": "<your-home-directory>/Work/mymcp/gitlab-rh-agent/server.sh",
      "description": "Agent to fetch and analyze issues/MRs from internal Red Hat GitLab."
    }
  }
}
```

#### Jira Agent (Optional)

```json
{
  "mcpServers": {
    "jiraMcp": {
      "command": "podman",
      "args": [
        "run",
        "--rm",
        "-i",
        "--env-file",
        "<your-home-directory>/.rh-jira-agent.env",
        "jira-agent:latest"
      ],
      "description": "Provides access to Jira issues, projects, boards, and sprints."
    }
  }
}
```

### Step 3: Save and Reload Cursor

1. **Save** your mcp.json configuration (File → Save)
2. **Reload** Cursor:
   - Option A: Press **Ctrl+Shift+P** → "Developer: Reload Window"
   - Option B: Fully quit Cursor (**Ctrl+Q**) and restart

---

## Verify Your Setup

Run the comprehensive verification script:

```bash
cd ~/Work/mymcp
./workshop/check_authentication_tokens.sh
```

**Expected Output:**
```
==================================================
  MCP Agents Authentication Verification
==================================================

✓ OpenDev Review Agent     - No auth required
✓ GitHub Agent             - Token configured
✓ GitLab Agent             - Token configured
✓ Jira Agent               - Token configured

All agents configured successfully! ✅
```

If you see any ❌ errors, see the Troubleshooting section below.

---

## Troubleshooting

### Common Issues and Solutions

#### Issue: "No such file or directory: server.sh"

**Problem:** Script isn't executable or doesn't exist.

**Solution:**
```bash
cd ~/Work/mymcp/<agent-name>
chmod +x server.sh
ls -la server.sh  # Verify it exists and is executable
```

---

#### Issue: "Virtual environment not found"

**Problem:** The `venv` directory wasn't created.

**Solution:**
```bash
cd ~/Work/mymcp/<agent-name>
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

#### Issue: GitHub "401 Unauthorized" or "Bad credentials"

**Problem:** GitHub token is invalid or has wrong scopes.

**Solution:**
1. Generate a new token at https://github.com/settings/tokens
2. Ensure you selected `public_repo` or `repo` scope
3. Update `~/Work/mymcp/github-agent/.env` with new token
4. Test: `cd ~/Work/mymcp/github-agent && ./server.sh <<< '{"jsonrpc": "2.0", "method": "exit"}'`

---

#### Issue: Jira "Missing JIRA_URL or JIRA_API_TOKEN environment variables"

**Problem:** Environment variable is named incorrectly.

**Solution:**
```bash
# Check your environment file
cat ~/.rh-jira-agent.env

# Ensure it says JIRA_API_TOKEN (not JIRA_TOKEN)
# WRONG ❌
JIRA_TOKEN=your_token_here

# CORRECT ✅
JIRA_API_TOKEN=your_token_here

# Edit the file to fix it
nano ~/.rh-jira-agent.env
```

---

#### Issue: Jira "401 Unauthorized" or "Authentication failed"

**Problem:** Jira API token is invalid or expired.

**Root Causes:**
1. Invalid or expired `JIRA_API_TOKEN`
2. Wrong `JIRA_URL` (pointing to incorrect Jira instance)

**Solution:**
1. Generate a new API token from your Jira profile
2. Update `~/.rh-jira-agent.env` with the new token
3. Rebuild the container: `cd ~/Work/mymcp/jira-agent && make build`
4. Test again

---

#### Issue: Jira container "No such image"

**Problem:** Container image hasn't been built yet.

**Solution:**
```bash
cd ~/Work/mymcp/jira-agent
make build
```

---

#### Issue: GitLab "401 Unauthorized"

**Problem:** GitLab token is invalid or has wrong scopes.

**Solution:**
1. Generate a new token at https://gitlab.cee.redhat.com/-/user_settings/personal_access_tokens
2. Ensure `read_api` scope is selected
3. Update `~/Work/mymcp/gitlab-rh-agent/.env` with new token
4. Test: `cd ~/Work/mymcp/gitlab-rh-agent && ./server.sh <<< '{"jsonrpc": "2.0", "method": "exit"}'`

---

#### Issue: Agent not appearing in Cursor

**Problem:** Cursor hasn't loaded the agent yet or configuration is incorrect.

**Solution:**
1. Verify your `~/.cursor/mcp.json` has the correct **absolute path** (no `~` tilde)
2. **Fully quit Cursor** (Ctrl+Q) and restart (don't just reload window)
3. Check for any error messages in Cursor's Developer Tools:
   - Press **Ctrl+Shift+I** to open Developer Tools
   - Look for errors in the Console tab

---

### Security Best Practices

✅ **DO:**
- Store tokens in files outside the repository (e.g., `~/.rh-jira-agent.env`)
- Use `.gitignore` to exclude token files
- Generate tokens with minimal required scopes
- Rotate tokens periodically
- Revoke tokens when no longer needed

❌ **DON'T:**
- Commit `.env` files to Git
- Share tokens with others
- Use tokens with excessive permissions
- Store tokens in code or scripts

---

## Quick Reference: File Locations

| Agent | Environment File | Virtual Env | Server Script |
|-------|------------------|-------------|---------------|
| OpenDev | None (no auth) | `~/Work/mymcp/opendev-review-agent/venv` | `~/Work/mymcp/opendev-review-agent/server.sh` |
| GitHub | `~/Work/mymcp/github-agent/.env` | `~/Work/mymcp/github-agent/venv` | `~/Work/mymcp/github-agent/server.sh` |
| GitLab | `~/Work/mymcp/gitlab-rh-agent/.env` | `~/Work/mymcp/gitlab-rh-agent/venv` | `~/Work/mymcp/gitlab-rh-agent/server.sh` |
| Jira | `~/.rh-jira-agent.env` | Container-based | `podman run ... jira-agent:latest` |

---

## Verification Checklist

Before attending the workshop, confirm:

- [ ] OpenDev agent starts successfully
- [ ] GitHub agent starts successfully (with your token)
- [ ] GitLab agent starts successfully (if applicable)
- [ ] Jira agent starts successfully (if applicable)
- [ ] All agents added to Cursor's MCP configuration
- [ ] Cursor restarted after configuration
- [ ] `./workshop/check_authentication_tokens.sh` passes all checks
- [ ] `./test-mcp-setup.sh` passes all checks

---

## Getting Help

If you're stuck:

1. **Check the troubleshooting section above**
2. **Review agent-specific documentation:**
   - [opendev-review-agent/README.md](../opendev-review-agent/README.md)
   - [github-agent/README.md](../github-agent/README.md)
   - [gitlab-rh-agent/README.md](../gitlab-rh-agent/README.md)
   - [jira-agent/README.md](../jira-agent/README.md)
3. **Run verification scripts:**
   ```bash
   cd ~/Work/mymcp
   ./workshop/check_authentication_tokens.sh
   ./test-mcp-setup.sh
   ```
4. **Ask for help during the workshop setup session**

---

## Ready for the Workshop?

If you've completed all steps and verification passes, you're ready!

✅ **Next:** Attend the workshop and follow [`workshop/README.md`](README.md)

---

**Document Version:** 1.0  
**Last Updated:** 2025-11-22  
**Feedback:** Report issues to the workshop facilitator

**Good luck with your setup! See you at the workshop! 🚀**

