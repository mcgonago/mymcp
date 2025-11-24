# Jira Configuration Update - Using ~/.rh-jira-agent.env ✅

**Date**: 2025-11-24  
**Issue**: OSPRH-19705 not appearing in activity reports  
**Solution**: Updated activity-tracker-agent to use jira-agent's standard config file

---

## ✅ What Was Fixed

### Problem
The activity-tracker-agent was looking for Jira credentials in:
- ❌ `jira-agent/.env` (in the repo)

But your jira-agent is configured to use:
- ✅ `~/.rh-jira-agent.env` (in your home directory)

### Solution
Updated `activity-tracker-agent/server.py` to also load from `~/.rh-jira-agent.env`:

```python
# Load from jira-agent if exists (check both locations)
jira_env = load_env_from_file(os.path.join(MYMCP_REPO_PATH, 'jira-agent', '.env'))
# Also check ~/.rh-jira-agent.env (per jira-agent/README.md configuration)
rh_jira_env = load_env_from_file(os.path.expanduser('~/.rh-jira-agent.env'))
# Merge jira configs (~/.rh-jira-agent.env takes precedence)
jira_env = {**jira_env, **rh_jira_env}
```

---

## 📋 Current Status

**Configuration File**: `~/.rh-jira-agent.env`

**Current Contents**:
```bash
JIRA_URL=https://issues.redhat.com
JIRA_API_TOKEN=<your-api-token>

# For activity tracking - identifies your Jira tickets
JIRA_EMAIL=omcgona@redhat.com
```

**Status**:
- ✅ JIRA_URL: Configured correctly
- ✅ JIRA_EMAIL: Configured correctly (omcgona@redhat.com)
- ⚠️  JIRA_API_TOKEN: **Still needs your actual token**

---

## 🔐 Next Step: Add Your Jira API Token

### Step 1: Get Your Token

**For Red Hat Jira**:

1. Go to: https://issues.redhat.com
2. Click your profile icon (top right)
3. Select "Personal Access Tokens" or "API Tokens"
4. Click "Create token"
5. Name it: `mymcp-activity-tracker`
6. **Copy the token immediately** (you won't see it again!)

### Step 2: Update Configuration

Edit the file:
```bash
nano ~/.rh-jira-agent.env
```

Replace this line:
```bash
JIRA_API_TOKEN=<your-api-token>
```

With your actual token:
```bash
JIRA_API_TOKEN=YOUR_ACTUAL_TOKEN_HERE
```

**Example** (not a real token):
```bash
JIRA_API_TOKEN=YOUR_ACTUAL_JIRA_TOKEN_HERE_DO_NOT_COMMIT
```

### Step 3: Test It

Run this test command:
```bash
cd /home/omcgonag/Work/mymcp/activity-tracker-agent
python3 << 'EOF'
import server
import requests

headers = {
    'Authorization': f'Bearer {server.JIRA_API_TOKEN}',
    'Content-Type': 'application/json'
}

jql = f'assignee = "{server.JIRA_EMAIL}" AND status not in (Done, Closed, Resolved)'
response = requests.get(
    f'{server.JIRA_URL}/rest/api/3/search',
    headers=headers,
    params={'jql': jql, 'maxResults': 50, 'fields': 'key,summary,status'}
)

if response.status_code == 200:
    data = response.json()
    print(f"✅ Found {data.get('total', 0)} open ticket(s)")
    for issue in data.get('issues', []):
        key = issue['key']
        summary = issue['fields']['summary']
        icon = "🎯" if key == "OSPRH-19705" else "  "
        print(f"{icon} {key}: {summary}")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text[:500])
EOF
```

If you see `🎯 OSPRH-19705` in the output, it's working!

### Step 4: Generate Fresh Report

Clear the cache and regenerate:
```bash
cd /home/omcgonag/Work/mymcp/activity-tracker-agent
rm ~/Work/mymcp/workspace/iproject/activity/2025-W46.json
python3 -c "import server; print(server.generate_status_report('this week'))"
```

Check the report:
```bash
cat ~/Work/mymcp/workspace/iproject/activity/2025-W46_report.md
```

Look for the "📋 Jira: My Open Tickets" section - OSPRH-19705 should be there!

---

## 🎯 Expected Result

Once you add your token, the "Jira: My Open Tickets" section will show:

```markdown
### 📋 Jira: My Open Tickets

**X open ticket(s)**

| Ticket | Summary | Type | Status | Priority | Created | Last Updated | Days Idle | Link |
|--------|---------|------|--------|----------|---------|--------------|-----------|------|
| [OSPRH-19705](...) | <summary> | <type> | 🟢 Review | <priority> | YYYY-MM-DD | YYYY-MM-DD | X | [View](...) |
```

And if it's been idle for more than 7 days, it will also appear in:

```markdown
### 📋 Jira: Tickets Requiring Update

**1 ticket(s) need attention**

| Ticket | Summary | Type | Status | Priority | Created | Last Updated | Days Idle | Link |
|--------|---------|------|--------|----------|---------|--------------|-----------|------|
| [OSPRH-19705](...) | <summary> | <type> | 🔴 Review | <priority> | YYYY-MM-DD | YYYY-MM-DD | **X** | [View](...) |
```

---

## 🔄 Configuration Flow

```
┌──────────────────────────────────────────────────────────────┐
│  ~/.rh-jira-agent.env                                        │
│  ├─ JIRA_URL=https://issues.redhat.com                       │
│  ├─ JIRA_API_TOKEN=<your-token>                              │
│  └─ JIRA_EMAIL=omcgona@redhat.com                            │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       │ (loaded by)
                       ▼
┌──────────────────────────────────────────────────────────────┐
│  activity-tracker-agent/server.py                            │
│  ├─ load_env_from_file('~/.rh-jira-agent.env')               │
│  └─ Uses credentials to query Jira API                       │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│  Activity Report: 2025-W46_report.md                         │
│  └─ "📋 Jira: My Open Tickets" section                       │
│     └─ Shows OSPRH-19705 and all your open tickets           │
└──────────────────────────────────────────────────────────────┘
```

---

## 📚 References

- **Jira Agent Setup**: `jira-agent/README.md`
- **Activity Tracker**: `activity-tracker-agent/README.md`
- **Ownership Feature**: `activity-tracker-agent/OWNERSHIP_FEATURE_SUMMARY.md`
- **Red Hat Jira**: https://issues.redhat.com

---

## ✅ Summary

**Before**:
- ❌ Activity tracker couldn't find Jira credentials
- ❌ OSPRH-19705 not showing in reports

**After**:
- ✅ Activity tracker loads from `~/.rh-jira-agent.env`
- ✅ JIRA_EMAIL configured (omcgona@redhat.com)
- ⏳ **Waiting for**: Your JIRA_API_TOKEN

**Once you add your token**:
- ✅ OSPRH-19705 will appear in every activity report
- ✅ All your open Jira tickets will be tracked
- ✅ Stale tickets (>7 days idle) will be highlighted

---

*Configuration updated: 2025-11-24*  
*Next: Add your Jira API token to ~/.rh-jira-agent.env*

