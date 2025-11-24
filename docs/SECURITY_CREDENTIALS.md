# Security & Credentials Management

## Overview

The mymcp repository uses `.mymcp-config` for storing sensitive credentials and configuration. This file is **gitignored** to prevent accidental credential exposure.

---

## 🔒 Critical Security Rules

### ❌ NEVER Commit These Files

- `.mymcp-config` - Contains your actual credentials (gitignored)
- `.env` files - Environment-specific secrets
- Any file with API tokens, passwords, or webhook URLs

### ✅ Safe to Commit

- `.mymcp-config.template` - Template with placeholders (tracked in git)
- Documentation files
- Scripts (that read from config, not hardcoded secrets)

---

## 📋 Initial Setup

### 1. Create Your Config File

```bash
cd /home/omcgonag/Work/mymcp

# Copy template to create your config
cp .mymcp-config.template .mymcp-config
```

### 2. Add Your Credentials

Edit `.mymcp-config` and uncomment/fill in the services you use:

```bash
vim .mymcp-config
```

**Example:**
```bash
# Slack Integration
SLACK_WEBHOOK_URL="https://hooks.slack.com/services/T027F3GAJ/B09V2L4SV5J/YOUR_ACTUAL_TOKEN"

# GitHub API
GITHUB_TOKEN="ghp_YOUR_GITHUB_TOKEN_HERE"

# OpenDev
OPENDEV_USERNAME="your_username"
```

### 3. Verify It's Gitignored

```bash
git status .mymcp-config
# Should show: nothing to commit (file is ignored)
```

---

## 🔑 Credentials by Service

### Slack Webhook URL

**What it is:** URL for posting messages to Slack  
**Get it from:** https://api.slack.com/messaging/webhooks  
**Format:** `https://hooks.slack.com/services/T.../B.../XXX`  
**Used by:** `scripts/send_to_slack.py`

**Add to `.mymcp-config`:**
```bash
SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

---

### GitHub Personal Access Token

**What it is:** Token for GitHub API access  
**Get it from:** https://github.com/settings/tokens  
**Permissions needed:** `repo`, `read:org`, `user`  
**Used by:** `activity-tracker-agent`, `github-reviewer-agent`

**Add to `.mymcp-config`:**
```bash
GITHUB_TOKEN="ghp_YOUR_TOKEN_HERE"
```

**Or create separate `.env` file:**
```bash
# In github-reviewer-agent/.env
GITHUB_TOKEN=ghp_YOUR_TOKEN_HERE
GITHUB_USERNAME=your_username
```

---

### OpenDev Username

**What it is:** Your OpenDev Gerrit username  
**Get it from:** https://review.opendev.org/#/settings/  
**Used by:** `activity-tracker-agent`, `opendev-reviewer-agent`

**Add to `.mymcp-config`:**
```bash
OPENDEV_USERNAME="your_username"
```

**Or create separate `.env` file:**
```bash
# In opendev-reviewer-agent/.env
OPENDEV_USERNAME=your_username
```

---

### GitLab API Token

**What it is:** Token for GitLab API access  
**Get it from:** https://gitlab.cee.redhat.com/-/profile/personal_access_tokens  
**Permissions needed:** `read_api`, `read_repository`  
**Used by:** `gitlab-cee-agent`, `activity-tracker-agent` (future)

**Add to `.mymcp-config`:**
```bash
GITLAB_TOKEN="your_gitlab_token"
GITLAB_URL="https://gitlab.cee.redhat.com"
```

**Or create separate `.env` file:**
```bash
# In gitlab-cee-agent/.env
GITLAB_TOKEN=your_gitlab_token
GITLAB_URL=https://gitlab.cee.redhat.com
```

---

### Jira API Credentials

**What it is:** Jira API token for issue access  
**Get it from:** https://id.atlassian.com/manage-profile/security/api-tokens  
**Used by:** `jira-agent`

**Add to `.mymcp-config`:**
```bash
JIRA_URL="https://your-company.atlassian.net"
JIRA_EMAIL="your.email@company.com"
JIRA_API_TOKEN="your_api_token"
```

**Or create separate `.env` file:**
```bash
# In jira-agent/.rh-jira-mcp.env
JIRA_URL=https://your-company.atlassian.net
JIRA_EMAIL=your.email@company.com
JIRA_API_TOKEN=your_api_token
```

---

## 🛡️ Security Best Practices

### 1. Rotate Credentials Regularly

- Regenerate tokens every 90 days
- Immediately revoke if compromised
- Use token expiration when available

### 2. Use Minimal Permissions

- Only grant necessary API scopes
- Use read-only tokens when possible
- Separate tokens for different purposes

### 3. Never Commit Secrets

```bash
# Before committing, always check:
git status
git diff --staged

# If you accidentally stage a secret:
git restore --staged .mymcp-config
```

### 4. Verify Gitignore

```bash
# Check that .mymcp-config is ignored:
git check-ignore -v .mymcp-config
# Should show: .gitignore:47:.mymcp-config	.mymcp-config
```

---

## 🚨 I Accidentally Committed a Secret!

### If You Haven't Pushed Yet

```bash
# Remove from last commit
git reset HEAD~1
git restore --staged .mymcp-config

# Or amend the commit
git reset HEAD .mymcp-config
git commit --amend --no-edit
```

### If You Already Pushed

1. **Revoke the credential immediately** (regenerate token/webhook)
2. Remove from git history:

```bash
# WARNING: This rewrites history!
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch .mymcp-config' \
  --prune-empty --tag-name-filter cat -- --all

# Force push (coordinate with team!)
git push origin --force --all
```

3. **Update `.gitignore`** (if not already there)
4. **Create new credentials**
5. **Notify your team** if it's a shared repository

---

## 📂 File Locations

| File | Purpose | Git Tracked? |
|------|---------|--------------|
| `.mymcp-config` | Your actual credentials | ❌ NO (gitignored) |
| `.mymcp-config.template` | Template with placeholders | ✅ YES |
| `.gitignore` | Ensures secrets not committed | ✅ YES |
| `*-agent/.env` | Agent-specific credentials | ❌ NO (gitignored) |
| `docs/SECURITY_CREDENTIALS.md` | This document | ✅ YES |

---

## 🔍 Checking for Exposed Secrets

### Manual Check

```bash
# Search for potential secrets in git history
git log --all --full-history -- .mymcp-config

# Search for webhook patterns
git log -S "hooks.slack.com" --all

# Search for token patterns
git log -S "ghp_" --all
```

### Automated Tools

```bash
# Install git-secrets (prevents committing secrets)
brew install git-secrets  # macOS
# or
sudo dnf install git-secrets  # Fedora

# Set up hooks
cd /home/omcgonag/Work/mymcp
git secrets --install
git secrets --register-aws
```

---

## 📚 Related Documentation

- [Slack Integration Guide](./SLACK_INTEGRATION.md)
- [Activity Tracker Setup](../activity-tracker-agent/README.md)
- [Central Configuration](./CENTRAL_CONFIGURATION.md)

---

## ❓ FAQ

**Q: Can I use environment variables instead of `.mymcp-config`?**  
A: Yes! Scripts check both. Environment variables take precedence.

**Q: Should I encrypt `.mymcp-config`?**  
A: Not necessary if it's properly gitignored. But you can use `git-crypt` if desired.

**Q: What if I need to share credentials with my team?**  
A: Use a password manager (1Password, LastPass) or secrets management tool (HashiCorp Vault). Never commit to git.

**Q: How do I back up my credentials?**  
A: Store in your password manager, not in git. The `.mymcp-config` file is intentionally excluded from git backups.

---

**Remember:** When in doubt, don't commit it! Regenerating credentials is easier than cleaning them from git history. 🔒

