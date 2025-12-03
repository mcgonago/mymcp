# Activity Tracker MCP Agent

An MCP (Model Context Protocol) server that tracks GitHub, OpenDev, GitLab, and Jira activities for automated status report generation.

## What's New (v2.5)

- 🏆 **Success Stories**: Tracks completed items with accountability ratings (A+/A/B/F)
- ⏱️ **AI Timeline Estimates**: Priority scheduling with estimated completion dates
- 🌡️ **Jira Health Heatmap**: Visual ticket aging with health score (0-100)
- 📊 **Complexity Scoring**: Heuristic-based complexity for all platforms
- 🔔 **People Waiting**: Shows reviews/PRs/MRs awaiting your action
- 🔧 **Unplanned Work Tracking**: Track interrupts, firefights, ad-hoc tasks
- 📅 **First Seen / Days Tracked**: Timeline accountability for all items
- 📧 **Slack & Email Notifications**: Proactive reminders for stale reviews

## Purpose

This agent enables automated collection and reporting of development activities across multiple platforms:

- **GitHub Activity Tracking**: PRs created/reviewed, commits, issues
- **OpenDev Activity Tracking**: Reviews posted, comments, votes
- **GitLab Activity Tracking**: Merge requests, issues, comments
- **Jira Activity Tracking**: Issues created/resolved/assigned, watched tickets
- **Automated Report Generation**: Weekly reports + real-time In Progress dashboard
- **Smart Caching**: Avoids API rate limits with intelligent caching
- **Success Tracking**: Persistent quarterly stats with completion ratings
- **Workspace Integration**: Stores activity history in `workspace/iproject/activity/`

## Architecture

```
┌──────────────┐
│ Cursor/User  │
└──────┬───────┘
       │
       ▼
┌────────────────────────────────────┐
│  activity-tracker MCP Agent        │
│  ├─ get_github_activity()          │
│  ├─ get_opendev_activity()         │
│  ├─ get_gitlab_activity()          │
│  ├─ get_jira_activity()            │
│  └─ generate_status_report()       │
└──────┬────┬────┬────┬──────────────┘
       │    │    │    │
       ▼    ▼    ▼    ▼
  ┌────────┬──────┬────────┬──────────┐
  │GitHub  │Gerrit│GitLab  │Jira API  │
  │API     │API   │API     │          │
  └────────┴──────┴────────┴──────────┘
```

For detailed architecture, see [`design/Design_MCP_Standup.md`](../design/Design_MCP_Standup.md).

## Installation

### 1. Create Virtual Environment

```bash
cd <mymcp-repo-path>/activity-tracker-agent
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit .env with your settings
nano .env
```

#### Incremental Platform Support

**You don't need all platforms configured!** The activity tracker works with any subset:

| Platform | Required Config | Without Config |
|----------|-----------------|----------------|
| **OpenDev** | `OPENDEV_USERNAME` | Skipped (no token needed) |
| **GitHub** | `GITHUB_USERNAME` + `GITHUB_TOKEN` | Skipped |
| **GitLab** | `GITLAB_USERNAME` + `GITLAB_TOKEN` | Skipped |
| **Jira** | `JIRA_EMAIL` + `JIRA_API_TOKEN` + `JIRA_URL` | Skipped |

**Start with one platform, add more later:**
```bash
# Start with just Jira
JIRA_EMAIL=you@company.com
JIRA_API_TOKEN=xxx
JIRA_URL=https://issues.redhat.com

# Later, add GitHub
GITHUB_USERNAME=yourusername
GITHUB_TOKEN=ghp_xxx

# And so on...
```

Reports automatically include only configured platforms. Unconfigured platforms show "not configured" and are excluded from tracking.

#### Required Configuration

These environment variables must be set for the agent to function:

**`WORKSPACE_PROJECT`**
- **Purpose**: Root directory for storing activity reports and cached data
- **Default**: `<mymcp-repo-path>/workspace/iproject`
- **Usage**: The agent creates an `activity/` subdirectory here to store:
  - Cached API responses (`YYYY-Www.json`)
  - Generated reports (`YYYY-Www_report.md`)
- **Example**: `<mymcp-repo-path>/workspace/iproject`

**`GITHUB_USERNAME`**
- **Purpose**: Your GitHub username for filtering activity
- **Usage**: Used in GitHub API queries to find:
  - PRs you created (`author:username`)
  - PRs you reviewed (`reviewed-by:username`)
  - Commits you authored (`author:username`)
  - Issues you created or commented on
- **Example**: `yourusername`
- **Where to find**: Your GitHub profile URL: `https://github.com/USERNAME`

**`OPENDEV_USERNAME`**
- **Purpose**: Your OpenDev/Gerrit username for filtering activity
- **Usage**: Used in Gerrit API queries to find:
  - Reviews you posted (`owner:username`)
  - Comments you made
  - Votes you gave (Code-Review, Workflow)
- **Example**: `yourusername`
- **Where to find**: Your OpenDev profile: `https://review.opendev.org/q/owner:USERNAME`

**`GITHUB_TOKEN`**
- **Purpose**: Authenticates GitHub API requests
- **Usage**: 
  - Enables access to private repositories
  - Increases API rate limit from 60/hour (unauthenticated) to 5,000/hour
  - Required for fetching PR reviews and detailed commit data
- **Example**: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
- **Where to get**: 
  - GitHub Settings → Developer settings → Personal access tokens
  - https://github.com/settings/tokens
- **Required scopes**: `repo`, `read:org`, `read:user`
- **Reuse existing**: If you have `../github-agent/.env` configured, this will be automatically sourced from `.mymcp-config`

**`GITLAB_USERNAME`** (Optional)
- **Purpose**: Your GitLab username for filtering activity
- **Usage**: Used in GitLab API queries to find:
  - Merge requests you created
  - Merge requests you reviewed/commented on
  - Issues you created or commented on
- **Example**: `yourusername`
- **Where to find**: Your GitLab profile URL: `https://gitlab.cee.redhat.com/USERNAME`
- **Reuse existing**: If you have `gitlab-rh-agent` configured, this will be automatically sourced from `.mymcp-config`

**`GITLAB_TOKEN`** (Optional)
- **Purpose**: Authenticates GitLab API requests
- **Usage**: Required for accessing GitLab activity data
- **Example**: `glpat-xxxxxxxxxxxxxxxxxxxx`
- **Where to get**: 
  - GitLab → User Settings → Access Tokens
  - https://gitlab.cee.redhat.com/-/profile/personal_access_tokens
- **Required scopes**: `read_api`, `read_repository`
- **Reuse existing**: If you have `../gitlab-rh-agent/.env` configured, this will be automatically sourced from `.mymcp-config`

**`GITLAB_URL`** (Optional)
- **Purpose**: GitLab instance URL
- **Default**: `https://gitlab.cee.redhat.com`
- **Usage**: Set if using a different GitLab instance
- **Example**: `https://gitlab.com` or `https://gitlab.yourcompany.com`

**`JIRA_EMAIL`** (Optional)
- **Purpose**: Your Jira account email for filtering activity
- **Usage**: Used in Jira JQL queries to find issues you created/resolved
- **Example**: `your.email@company.com`
- **Where to find**: Your Jira profile settings
- **Reuse existing**: If you have `../jira-agent/.env` configured, this will be automatically sourced from `.mymcp-config`

**`JIRA_API_TOKEN`** (Optional)
- **Purpose**: Authenticates Jira API requests
- **Usage**: Required for accessing Jira activity data
- **Example**: `YOUR_JIRA_API_TOKEN_HERE`
- **Where to get**:
  - Jira → Account settings → Security → API tokens
  - https://id.atlassian.com/manage-profile/security/api-tokens
- **Reuse existing**: If you have `../jira-agent/.env` configured, this will be automatically sourced from `.mymcp-config`

**`JIRA_URL`** (Optional)
- **Purpose**: Your Jira instance URL
- **Usage**: Base URL for your Jira instance
- **Example**: `https://your-company.atlassian.net` or `https://jira.yourcompany.com`
- **Reuse existing**: If you have `../jira-agent/.env` configured, this will be automatically sourced from `.mymcp-config`

#### Optional Configuration

These variables have sensible defaults but can be customized:

**`CACHE_MAX_AGE_HOURS`**
- **Purpose**: Controls how long cached activity data remains valid
- **Default**: `24` (hours)
- **Usage**: 
  - If cached data is older than this, the agent refetches from APIs
  - Prevents hitting API rate limits on repeated queries
  - Set to `0` to disable caching (always fetch fresh data)
- **Example**: `48` (for 2-day cache), `168` (for 1-week cache)

**`ACTIVITY_DIR`**
- **Purpose**: Custom location for activity reports and cache
- **Default**: `${WORKSPACE_PROJECT}/activity`
- **Usage**: Override if you want to store reports elsewhere
- **Example**: `~/my_reports/activity`
- **Note**: The directory will be created automatically if it doesn't exist

#### Configuration Example

Here's a complete `.env` file example:

```bash
# Required: Your workspace project root
WORKSPACE_PROJECT=<mymcp-repo-path>/workspace/iproject

# Required: Your GitHub username (find at https://github.com/USERNAME)
GITHUB_USERNAME=yourusername

# Required: Your OpenDev username (find at https://review.opendev.org/q/owner:USERNAME)
OPENDEV_USERNAME=yourusername

# Optional: GitLab tracking
# If you have gitlab-rh-agent configured, these will be auto-sourced from ../gitlab-rh-agent/.env
# Otherwise, set them here:
# GITLAB_USERNAME=yourusername
# GITLAB_TOKEN=glpat-xxxxxxxxxxxxxxxxxxxx
# GITLAB_URL=https://gitlab.cee.redhat.com

# Optional: Jira tracking
# If you have jira-agent configured, these will be auto-sourced from ../jira-agent/.env
# Otherwise, set them here:
# JIRA_EMAIL=your.email@company.com
# JIRA_API_TOKEN=YOUR_JIRA_API_TOKEN_HERE
# JIRA_URL=https://your-company.atlassian.net

# Required: GitHub personal access token
# If you have github-agent configured, this will be auto-sourced from ../github-agent/.env
# Otherwise, set it here:
# Get from: https://github.com/settings/tokens
# Scopes needed: repo, read:org, read:user
# GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Optional: Cache validity period (default: 24 hours)
CACHE_MAX_AGE_HOURS=24

# Optional: Custom activity directory (default: ${WORKSPACE_PROJECT}/activity)
# ACTIVITY_DIR=~/custom_activity_reports
```

**Quick Setup Tip:**

If you already have `github-agent` configured, you can copy the token:

```bash
grep GITHUB_TOKEN ../github-agent/.env >> .env
```

### 4. Configure MCP Client

Add to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "activity-tracker": {
      "command": "<mymcp-repo-path>/activity-tracker-agent/server.sh",
      "args": ["stdio"],
      "env": {}
    }
  }
}
```

### 5. Restart Cursor

Fully quit Cursor (Ctrl+Q) and restart to load the new MCP agent.

### How Configuration Variables Are Used

Here's the complete data flow showing where each configuration variable is used:

```
User Request: @activity-tracker generate_status_report("last week")
       ↓
┌──────────────────────────────────────────────────────────────┐
│ 1. Parse Time Range                                          │
│    "last week" → 2025-11-15 to 2025-11-22                    │
└──────────────────────────────────────────────────────────────┘
       ↓
┌──────────────────────────────────────────────────────────────┐
│ 2. Check Cache (uses WORKSPACE_PROJECT + ACTIVITY_DIR)       │
│    Location: ${WORKSPACE_PROJECT}/activity/2025-W46.json     │
│    Cache age check: CACHE_MAX_AGE_HOURS                      │
│                                                              │
│    If cache valid (< 24 hours old) → Skip API calls          │
│    If cache stale (> 24 hours old) → Fetch from APIs         │
└──────────────────────────────────────────────────────────────┘
       ↓
┌──────────────────────────────────────────────────────────────┐
│ 3. Fetch GitHub Activity (if needed)                         │
│    Uses: GITHUB_USERNAME, GITHUB_TOKEN                       │
│                                                              │
│    API Queries:                                              │
│    - PRs created:  author:${GITHUB_USERNAME}                 │
│    - PRs reviewed: reviewed-by:${GITHUB_USERNAME}            │
│    - Commits:      author:${GITHUB_USERNAME}                 │
│    - Issues:       author:${GITHUB_USERNAME}                 │
│                                                              │
│    Authentication: GITHUB_TOKEN in request headers           │
└──────────────────────────────────────────────────────────────┘
       ↓
┌──────────────────────────────────────────────────────────────┐
│ 4. Fetch OpenDev Activity (if needed)                        │
│    Uses: OPENDEV_USERNAME                                    │
│                                                              │
│    Gerrit API Queries:                                       │
│    - Reviews posted: owner:${OPENDEV_USERNAME}               │
│    - Comments made:  commenter:${OPENDEV_USERNAME}           │
│    - Votes given:    reviewer:${OPENDEV_USERNAME}            │
│                                                              │
│    Note: No authentication needed (public API)               │
└──────────────────────────────────────────────────────────────┘
       ↓
┌──────────────────────────────────────────────────────────────┐
│ 5. Save Cache (uses WORKSPACE_PROJECT + ACTIVITY_DIR)        │
│    Save to: ${WORKSPACE_PROJECT}/activity/2025-W46.json      │
│    Contains: Raw GitHub + OpenDev activity data              │
└──────────────────────────────────────────────────────────────┘
       ↓
┌──────────────────────────────────────────────────────────────┐
│ 6. Generate Report (uses WORKSPACE_PROJECT + ACTIVITY_DIR)   │
│    Save to: ${WORKSPACE_PROJECT}/activity/2025-W46_report.md │
│    Format: Markdown with activity summaries                  │
└──────────────────────────────────────────────────────────────┘
       ↓
   Return report to user in Cursor
```

**Example File Structure After Running:**

```
<mymcp-repo-path>/workspace/iproject/      ← WORKSPACE_PROJECT
└── activity/                               ← ACTIVITY_DIR
    ├── 2025-W45.json                       ← Cached data (week 45)
    ├── 2025-W45_report.md                  ← Generated report (week 45)
    ├── 2025-W46.json                       ← Cached data (week 46)
    └── 2025-W46_report.md                  ← Generated report (week 46)
```

## Usage

### From Cursor

#### Get GitHub Activity

```
@activity-tracker get_github_activity("2025-11-15", "2025-11-22", "yourusername")
```

Returns JSON with:
- PRs created
- PRs reviewed  
- Commits
- Issues created

#### Get OpenDev Activity

```
@activity-tracker get_opendev_activity("2025-11-15", "2025-11-22", "yourusername")
```

Returns JSON with:
- Reviews posted
- Comments
- Votes (Code-Review, Workflow)

#### Generate Status Report

```
@activity-tracker generate_status_report("last week")
```

Supported time ranges:
- `"this week"` - Current week (Monday to today)
- `"last week"` - Previous week (Monday to Sunday)
- `"yesterday"` - Single day
- `"2025-11-15 to 2025-11-22"` - Custom range

Supported formats:
- `"markdown"` (default) - Human-readable report
- `"json"` - Raw data

**Examples**:

```
@activity-tracker generate_status_report("this week")
@activity-tracker generate_status_report("last week", "markdown")
@activity-tracker generate_status_report("2025-11-01 to 2025-11-30")
```

#### Generate In Progress Report

Generate a comprehensive "In Progress" dashboard showing all open items across platforms:

```
@activity-tracker generate_in_progress_report()
```

**Report Sections:**
- 🔔 **People Waiting for Your Review**: Reviews/PRs/MRs awaiting your action
- 🟠 **OpenDev**: Your active reviews with complexity scores
- 🔵 **GitHub**: Your open PRs with complexity scores
- 🦊 **GitLab**: Your open MRs with complexity scores
- 🏆 **Success Stories**: Completed items with ratings (persistent quarterly)
- ⏱️ **AI Timeline Estimates**: Priority-ranked work schedule
- 🌡️ **Jira Health Heatmap**: Visual ticket aging (0-100 health score)
- 📋 **Jira**: Open tickets, tickets needing update, watched tickets
- 🔧 **Unplanned Work**: Active interrupts/firefights being tracked

**Key features**:
- ✅ Always fetches fresh data (no caching)
- ✅ Compares against previous run for Success Stories
- ✅ Tracks "First Seen" and "Days Tracked" for accountability
- ✅ Calculates complexity scores based on comments/reviewers/patchsets

### From Command Line

#### Quick Method (Recommended)

Use the convenience wrapper scripts:

**Daily Standup Prep** (recommended):
```bash
<mymcp-repo-path>/standup-prep.sh
```

**Weekly Activity Reports**:
```bash
cd <mymcp-repo-path>/activity-tracker-agent
./generate_report.sh "this week"
./generate_report.sh "last week"
./generate_report.sh  # defaults to "last week"
```

**In Progress Report** (current ownership status):
```bash
cd <mymcp-repo-path>/activity-tracker-agent
./generate_in_progress.sh
```

**Unplanned Work Tracking**:
```bash
# Add unplanned work as it happens
<mymcp-repo-path>/unplanned-add.sh INTERRUPT "Helped debug issue" 1.5
<mymcp-repo-path>/unplanned-add.sh FIREFIGHT "CI investigation" 2.0

# Mark as complete with outcome
<mymcp-repo-path>/unplanned-done.sh "Helped debug issue" 2.0 "Fixed, PR merged"
```

This generates reports and saves them to `workspace/iproject/activity/`.

#### Direct Python Invocation

```bash
cd <mymcp-repo-path>/activity-tracker-agent
source venv/bin/activate
python server.py
```

This will generate a test report for "last week" and print to stdout.

## Output

### Report Location

Generated reports are saved to:
```
workspace/iproject/activity/
├── 2025-W46.json              # Cached activity data (weekly)
├── 2025-W46_report.md         # Generated markdown report (weekly)
├── in_progress.md             # Current ownership dashboard
├── in_progress.json           # Current state (for diff comparison)
├── in_progress_previous.json  # Previous state (for Success Stories)
├── tracking_history.json      # Persistent first_seen dates + quarterly stats
├── unplanned.txt              # Active unplanned work items
├── unplanned_done.txt         # Completed unplanned work
└── ...
```

### Report Structure

```markdown
# Status Report: Week 2025-W47

**Period**: 2025-11-15 to 2025-11-22
**Generated**: 2025-11-22 16:30:00

---

## Summary
- **GitHub**: 2 PRs created, 5 PRs reviewed, 12 commits, 0 issues
- **OpenDev**: 1 reviews posted, 3 comments, 2 votes

---

## GitHub Activity

### Pull Requests Created (2)
[Detailed list]

### Pull Requests Reviewed (5)
[Detailed list]

### Commits (12)
[Detailed list]

---

## OpenDev Activity

### Reviews Posted (1)
[Detailed list]

### Comments & Votes (3 comments, 2 votes)
[Detailed list]

---

## Key Themes
_To be filled by AI analysis_

## Blockers
_None or user-provided_

---

_Generated by mymcp activity-tracker on 2025-11-22 16:30:00_
_Data cached at: `workspace/iproject/activity/2025-W47.json`_
```

## Caching

### How It Works

1. **First request**: Fetches data from GitHub and OpenDev APIs, caches to `YYYY-Www.json`
2. **Subsequent requests** (within 24 hours): Uses cached data, no API calls
3. **Stale cache** (> 24 hours): Refetches data, updates cache

### Cache Management

```bash
# View cached data
ls -lh <mymcp-repo-path>/workspace/iproject/activity/

# Clear cache (force fresh fetch)
rm <mymcp-repo-path>/workspace/iproject/activity/*.json

# View cached JSON
cat <mymcp-repo-path>/workspace/iproject/activity/2025-W47.json | jq
```

### Why Caching?

- **API Rate Limits**: GitHub (5,000/hour), Gerrit (no official limit but can be throttled)
- **Performance**: Instant results for repeated queries
- **Historical Data**: Enables trend analysis over time

## Testing

### 1. Verify Virtual Environment

```bash
cd <mymcp-repo-path>/activity-tracker-agent
source venv/bin/activate
python --version  # Should be Python 3.x
pip list | grep fastmcp  # Should show fastmcp installed
```

### 2. Test Server Startup

```bash
./server.sh &
sleep 2
ps aux | grep "server.py stdio"  # Should show process running
kill %1  # Stop the test server
```

### 3. Test MCP Connection

In Cursor, check MCP servers:
- Ctrl+Shift+P → "MCP: Manage Servers"
- Verify "activity-tracker" shows as "connected"

### 4. Test Tools

```
@activity-tracker generate_status_report("yesterday")
```

Should return a report with your actual activity from yesterday.

## Troubleshooting

See [`TROUBLESHOOTING.md`](./TROUBLESHOOTING.md) for common issues and solutions.

## Integration with mymcp Workflow

### askme Framework (Future)

Once integrated with the askme framework, you'll be able to use natural language:

```
status report last week
status report this week
status report 2025-11-01 to 2025-11-30
```

See [`askme/README.md`](../askme/README.md) for the askme framework details.

### Workshop

This agent will be included in Workshop Session #5: "Automated Status Reports".

See [`workshop/README.md`](../workshop/README.md) for the full workshop agenda.

## Workspace Project Setup

The activity tracker stores reports in `workspace/<your-project>/activity/`. You have options:

| Option | Description | Best For |
|--------|-------------|----------|
| **Default** | Auto-creates `workspace/iproject/` | Quick start, temporary use |
| **Custom Dir** | Use `--myworkspace <name>` | Custom organization |
| **Git Repo** | Clone your repo to `workspace/` | Version control, sharing |

**Minimum structure needed:**
```
workspace/<your-project>/
├── activity/          # Reports, tracking (auto-created)
├── results/           # Review assessments
└── analysis/          # Feature analysis, spikes
```

**If you don't configure a workspace project:**
- A temporary `workspace/iproject/` is created automatically
- Works fine for getting started
- Consider a git repo for persistent tracking

**To use your own repository:**
```bash
cd <mymcp-repo-path>/workspace
git clone https://gitlab.example.com/you/your-project.git
# Then set WORKSPACE_PROJECT in activity-tracker-agent/.env
```

**Full documentation:** [`docs/WORKSPACE_PROJECT.md`](../docs/WORKSPACE_PROJECT.md)

## Resources

- **Design Document**: [`design/Design_MCP_Standup.md`](../design/Design_MCP_Standup.md)
- **Workspace Setup**: [`docs/WORKSPACE_PROJECT.md`](../docs/WORKSPACE_PROJECT.md)
- **FastMCP**: https://github.com/pydantic/fastmcp
- **GitHub API**: https://docs.github.com/en/rest
- **Gerrit API**: https://gerrit-review.googlesource.com/Documentation/rest-api.html

## License

Part of the mymcp project. See main repository README for license information.

---

**Version**: 2.5  
**Created**: 2025-11-22  
**Updated**: 2025-12-03  
**Status**: Production - Full Feature Set



