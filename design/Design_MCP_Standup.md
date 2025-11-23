# Design: Activity Tracking & Status Reports for mymcp

## Executive Summary

This design document details the integration of automated activity tracking and status report generation into the mymcp framework, **inspired by the excellent work of Francesco Pantano** in [`standup_mcp`](https://gitlab.cee.redhat.com/fpantano/standup_mcp). Francesco's innovative approach to automating standup reports using MCP and the `did` tool served as the catalyst for this implementation. While his project focuses on Slack integration using the `did` tool, our implementation adapts his core concepts for OpenStack Horizon development workflows:

- Track **GitHub activities** (commits, PRs, reviews, comments)
- Track **OpenDev review activities** (comments, votes, review submissions)
- Leverage **existing mymcp MCP agents** (GitHub, OpenDev)
- Generate **flexible status reports** (daily, weekly, custom ranges)
- Store **activity history** in workspace for trend analysis
- Provide **workshop-ready examples** for team adoption

**Goal:** Before Christmas break, enable automated weekly status report generation for OpenStack Horizon development activities.

---

## Analysis of standup_mcp

> **Credit**: The `standup_mcp` project by **Francesco Pantano** is an outstanding example of practical MCP server implementation. His clean architecture, thoughtful caching design, and production-ready approach to solving real-world workflow automation challenges demonstrates deep understanding of both the MCP protocol and enterprise development needs. This analysis studies his work to understand what makes it successful and how we can adapt his patterns for our specific use case.

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     standup_mcp Architecture                    │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐
│ User/Claude  │
└──────┬───────┘
       │
       │ MCP Protocol (stdio)
       ▼
┌────────────────────────────────────────────────┐
│          FastMCP Server (server.py)            │
│  ┌──────────────────────────────────────────┐  │
│  │  @mcp.tool()                             │  │
│  │  def standup(arguments, cached=True):    │  │
│  │    - Parse time range (last week, etc.)  │  │
│  │    - Check cache (avoid rate limits)     │  │
│  │    - Call did tool                       │  │
│  │    - Format plugin outputs               │  │
│  │    - Return report                       │  │
│  └──────────────────────────────────────────┘  │
└──────────────────┬─────────────────────────────┘
                   │
                   │ Subprocess call
                   ▼
┌────────────────────────────────────────────────┐
│           "did" Tool (Python CLI)              │
│  ┌──────────────────────────────────────────┐  │
│  │  Plugin Architecture:                    │  │
│  │  - Git plugin (local repos)              │  │
│  │  - Jira plugin (API)                     │  │
│  │  - Bugzilla plugin (API)                 │  │
│  │  - GitHub plugin (API)                   │  │
│  │  - GitLab plugin (API)                   │  │
│  │  - Gerrit plugin (API)                   │  │
│  └──────────────────────────────────────────┘  │
└──────────────────┬─────────────────────────────┘
                   │
                   │ API calls (multiple services)
                   ▼
┌────────────────────────────────────────────────┐
│         External Services                      │
│  - github.com (REST API)                       │
│  - jira.atlassian.com (REST API)               │
│  - bugzilla.redhat.com (XML-RPC)               │
│  - gitlab.cee.redhat.com (REST API)            │
│  - review.opendev.org (Gerrit REST API)        │
└────────────────────────────────────────────────┘
```

### Key Components

#### 1. **FastMCP Server** (`server.py`)
   - Implements MCP protocol using `fastmcp` library
   - Exposes `standup(arguments, cached)` tool
   - Handles caching to avoid API rate limits
   - Formats output from `did` tool

#### 2. **"did" Tool Integration**
   - External Python CLI tool (`pip install did[all]`)
   - Plugin-based architecture for various services
   - Configured via `~/.did/config` (INI format)
   - Gathers statistics for specified time ranges

#### 3. **Caching Mechanism**
   - Uses `STANDUP_PATH` environment variable
   - Appends results to cache file
   - Returns cached data first (if available)
   - Mitigates API rate limiting issues

#### 4. **Prompt Template**
   - Located in `prompts/standup_prompt.md`
   - Guides Claude to format output for Slack
   - Three-question structure (What/Unplanned/Blockers)
   - Copy-pastable format with specific formatting rules

### Strengths

Francesco's `standup_mcp` demonstrates several architectural strengths that make it a reference implementation:

✅ **Comprehensive Data Collection**: Supports 20+ services via plugins - showing excellent understanding of enterprise development ecosystems  
✅ **Rate Limit Mitigation**: Built-in caching prevents API exhaustion - a critical production concern handled elegantly  
✅ **Flexible Time Ranges**: "last week", "yesterday", custom dates - intuitive UX that respects how developers think  
✅ **MCP Integration**: Seamlessly works with Claude/Cursor - clean FastMCP implementation that "just works"  
✅ **Proven in Production**: Used by Red Hat teams - real-world validation of the design  
✅ **Minimal Dependencies**: Leverages existing `did` tool - smart reuse rather than reimplementation  
✅ **Clear Separation of Concerns**: MCP server focuses on orchestration, `did` handles data collection - excellent architecture

### Limitations (for our use case)

❌ **Heavy Dependency**: Requires external `did` tool + all plugins  
❌ **Generic Output**: Not optimized for OpenStack/Horizon workflows  
❌ **Slack-Focused**: Formatting assumes Slack as target  
❌ **No Gerrit/OpenDev Optimization**: Generic Gerrit plugin, not OpenDev-specific  
❌ **No Historical Analysis**: Cache is append-only, no trend tracking  
❌ **Configuration Complexity**: Requires `~/.did/config` setup

---

## Proposed mymcp Integration

### Design Philosophy

**Build on Existing Infrastructure**: Leverage mymcp's existing MCP agents (GitHub, OpenDev) rather than introducing the `did` tool dependency.

**mymcp-Specific Features**: Optimize for OpenStack Horizon development workflows (reviews, patchsets, de-angularization features).

**Workspace Integration**: Store activity history in `workspace/iproject/activity/` for long-term tracking and trend analysis.

**Simple Configuration**: Use existing `.env` files and `workspace/.workspace-config`.

### Proposed Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                mymcp Activity Tracking Architecture             │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐
│ User/Cursor  │
└──────┬───────┘
       │
       │ Ask: "Generate my weekly status report"
       ▼
┌────────────────────────────────────────────────┐
│      Cursor AI (with askme framework)          │
│  - Parses request                              │
│  - Queries activity-tracker MCP agent          │
│  - Formats report using prompt template        │
└──────────────────┬─────────────────────────────┘
                   │
                   │ MCP Protocol (stdio)
                   ▼
┌────────────────────────────────────────────────┐
│    activity-tracker MCP Agent (NEW)            │
│  ┌──────────────────────────────────────────┐  │
│  │  @mcp.tool()                             │  │
│  │  def get_github_activity(start, end):    │  │
│  │    - Query GitHub MCP agent              │  │
│  │    - Filter by user                      │  │
│  │    - Return structured data              │  │
│  │                                          │  │
│  │  @mcp.tool()                             │  │
│  │  def get_opendev_activity(start, end):   │  │
│  │    - Query OpenDev MCP agent             │  │
│  │    - Filter reviews by user              │  │
│  │    - Return structured data              │  │
│  │                                          │  │
│  │  @mcp.tool()                             │  │
│  │  def generate_status_report(range):      │  │
│  │    - Call get_github_activity()          │  │
│  │    - Call get_opendev_activity()         │  │
│  │    - Merge data                          │  │
│  │    - Cache to workspace/iproject/activity│  │
│  │    - Return formatted report             │  │
│  └──────────────────────────────────────────┘  │
└──────────────────┬───────────┬─────────────────┘
                   │           │
       ┌───────────┘           └───────────┐
       │                                   │
       ▼                                   ▼
┌────────────────────┐          ┌────────────────────┐
│  GitHub MCP Agent  │          │ OpenDev MCP Agent  │
│  (EXISTING)        │          │  (EXISTING)        │
│  - Fetch user PRs  │          │  - Fetch reviews   │
│  - Fetch commits   │          │  - Fetch comments  │
│  - Fetch reviews   │          │  - Fetch votes     │
└────────┬───────────┘          └────────┬───────────┘
         │                               │
         │ GitHub API                    │ Gerrit API
         ▼                               ▼
┌────────────────────┐          ┌────────────────────┐
│  github.com        │          │ review.opendev.org │
└────────────────────┘          └────────────────────┘

                   │
                   │ Persisted to workspace
                   ▼
┌────────────────────────────────────────────────┐
│  workspace/iproject/activity/                  │
│  ├── 2025-W46.json  (week 46 activities)       │
│  ├── 2025-W47.json  (week 47 activities)       │
│  └── 2025-W48.json  (current week)             │
└────────────────────────────────────────────────┘
```

### Data Flow

```
[1] User Request
    ↓
[2] Cursor parses → askme framework
    ↓
[3] activity-tracker MCP called with time range
    ↓
[4] activity-tracker queries existing agents:
    ├─→ github-agent.get_user_activity(start, end)
    └─→ opendev-agent.get_user_activity(start, end)
    ↓
[5] activity-tracker merges results
    ↓
[6] activity-tracker caches to workspace/iproject/activity/YYYY-Www.json
    ↓
[7] Returns structured data to Cursor
    ↓
[8] Cursor formats using prompt template
    ↓
[9] User receives report
```

---

## Implementation Plan

### Phase 1: Core Activity Tracking (Week 1)

**Goal**: Basic MCP agent that can query GitHub and OpenDev for user activities.

#### Deliverables

1. **`activity-tracker-agent/` directory structure**
   ```
   activity-tracker-agent/
   ├── server.py                 # FastMCP server
   ├── server.sh                 # Startup script
   ├── venv/                     # Python virtual environment
   ├── requirements.txt          # Dependencies (fastmcp)
   ├── .env.example              # Example configuration
   ├── README.md                 # Setup instructions
   └── TROUBLESHOOTING.md        # Common issues
   ```

2. **MCP Tools Implemented**
   - `get_github_activity(start_date, end_date, username)`
   - `get_opendev_activity(start_date, end_date, username)`

3. **Data Structures**
   ```python
   # GitHub Activity
   {
     "username": "omcgonag",
     "period": {"start": "2025-11-15", "end": "2025-11-22"},
     "commits": [
       {"repo": "horizon-operator", "sha": "abc123", "message": "...", "date": "..."}
     ],
     "prs_created": [
       {"repo": "horizon-operator", "number": 402, "title": "...", "state": "open"}
     ],
     "prs_reviewed": [
       {"repo": "horizon", "number": 510, "comments": 3, "approved": true}
     ],
     "issues_created": [],
     "issues_commented": []
   }

   # OpenDev Activity
   {
     "username": "omcgonag",
     "period": {"start": "2025-11-15", "end": "2025-11-22"},
     "reviews_posted": [
       {"number": 967269, "project": "horizon", "subject": "...", "patchsets": 2}
     ],
     "comments_posted": [
       {"review": 966349, "patchset": 3, "message": "...", "date": "..."}
     ],
     "votes_given": [
       {"review": 967269, "type": "Code-Review", "value": "+1", "date": "..."}
     ],
     "reviews_received": []
   }
   ```

4. **Update `~/.cursor/mcp.json`**
   ```json
   {
     "mcpServers": {
       ...
       "activity-tracker": {
         "command": "/home/omcgonag/Work/mymcp/activity-tracker-agent/server.sh",
         "args": ["stdio"],
         "env": {}
       }
     }
   }
   ```

#### Testing
```bash
# Test the activity-tracker agent
cd /home/omcgonag/Work/mymcp
./test-mcp-setup.sh  # Should include activity-tracker checks

# Test in Cursor
@activity-tracker get_github_activity("2025-11-15", "2025-11-22", "omcgonag")
@activity-tracker get_opendev_activity("2025-11-15", "2025-11-22", "omcgonag")
```

---

### Phase 2: Report Generation (Week 2)

**Goal**: Implement the main `generate_status_report()` tool and cache mechanism.

#### Deliverables

1. **New MCP Tool**
   - `generate_status_report(time_range, format="markdown")`
     - `time_range`: "this week", "last week", "2025-11-15 to 2025-11-22"
     - `format`: "markdown", "json", "slack" (for future)

2. **Workspace Integration**
   ```
   workspace/iproject/activity/
   ├── 2025-W46.json          # Raw activity data (cached)
   ├── 2025-W46_report.md     # Generated markdown report
   ├── 2025-W47.json
   ├── 2025-W47_report.md
   └── README.md              # Explains activity tracking
   ```

3. **Caching Logic**
   - Check if `YYYY-Www.json` exists for requested week
   - If exists + fresh (< 24 hours old), use cached data
   - If stale or missing, query APIs and cache
   - Always regenerate report (cheap operation)

4. **Report Template** (`results/status_report_template.md`)
   ```markdown
   # Status Report: Week {WEEK_NUMBER} ({START_DATE} to {END_DATE})

   ## Summary
   - **GitHub**: {PR_COUNT} PRs created, {REVIEW_COUNT} PRs reviewed, {COMMIT_COUNT} commits
   - **OpenDev**: {REVIEW_COUNT} reviews posted, {COMMENT_COUNT} comments, {VOTE_COUNT} votes

   ## GitHub Activity

   ### Pull Requests Created ({PR_COUNT})
   {FOR EACH PR}
   - **{REPO}#{NUMBER}**: {TITLE} ({STATE})
     - Created: {DATE}
     - {DESCRIPTION}
   {END FOR}

   ### Pull Requests Reviewed ({REVIEW_COUNT})
   {FOR EACH REVIEWED_PR}
   - **{REPO}#{NUMBER}**: {TITLE}
     - {COMMENT_COUNT} comments, {APPROVED ? "✅ Approved" : "💬 Commented"}
   {END FOR}

   ### Commits ({COMMIT_COUNT})
   {FOR EACH COMMIT}
   - **{REPO}** `{SHORT_SHA}`: {MESSAGE}
   {END FOR}

   ## OpenDev Activity

   ### Reviews Posted ({REVIEW_COUNT})
   {FOR EACH REVIEW}
   - **Review {NUMBER}**: {SUBJECT}
     - Project: {PROJECT}
     - Patchsets: {PATCHSET_COUNT}
     - Status: {STATUS}
   {END FOR}

   ### Comments & Votes ({COMMENT_COUNT} comments, {VOTE_COUNT} votes)
   {FOR EACH COMMENT}
   - **Review {REVIEW_NUMBER}** (Patchset {PATCHSET}): {VOTE} | {MESSAGE_PREVIEW}
   {END FOR}

   ## Key Themes
   {AI-GENERATED SUMMARY OF WORK THEMES}

   ## Blockers
   {USER_PROVIDED OR "None"}

   ---
   Generated by mymcp activity-tracker on {GENERATION_DATE}
   ```

#### Testing
```bash
# Test report generation
cd /home/omcgonag/Work/mymcp/workspace

# In Cursor:
@activity-tracker generate_status_report("last week")
@activity-tracker generate_status_report("this week")
@activity-tracker generate_status_report("2025-11-01 to 2025-11-30")
```

---

### Phase 3: Askme Integration (Week 3)

**Goal**: Create askme keys for common status report requests.

#### Deliverables

1. **`askme/keys/status_report_weekly.yaml`**
   ```yaml
   type: status_report
   action: generate_weekly_report
   config:
     time_range: "last week"
     format: "markdown"
     output_location: "workspace/iproject/activity/"
     include_themes: true
     include_blockers: true
   sources:
     - github
     - opendev
   prompt_template: "results/status_report_template.md"
   ```

2. **`askme/keys/status_report_this_week.yaml`**
   ```yaml
   type: status_report
   action: generate_weekly_report
   config:
     time_range: "this week"
     format: "markdown"
     output_location: "workspace/iproject/activity/"
     include_themes: true
     include_blockers: false
   sources:
     - github
     - opendev
   prompt_template: "results/status_report_template.md"
   ```

3. **`askme/keys/status_report_custom.yaml`**
   ```yaml
   type: status_report
   action: generate_custom_report
   config:
     time_range: "{user_provided}"  # e.g., "2025-11-01 to 2025-11-30"
     format: "markdown"
     output_location: "workspace/iproject/activity/"
     include_themes: true
     include_blockers: true
   sources:
     - github
     - opendev
   prompt_template: "results/status_report_template.md"
   ```

4. **Usage Documentation** (`askme/STATUS_REPORTS.md`)
   ```markdown
   # Status Reports with askme Framework

   ## Quick Commands

   ### Weekly Status Report (Last Week)
   ```
   status report last week
   ```
   This triggers `askme/keys/status_report_weekly.yaml`.

   ### Current Week Status
   ```
   status report this week
   ```
   This triggers `askme/keys/status_report_this_week.yaml`.

   ### Custom Date Range
   ```
   status report 2025-11-01 to 2025-11-30
   ```
   This triggers `askme/keys/status_report_custom.yaml`.

   ## What Happens

   1. AI queries activity-tracker MCP agent
   2. activity-tracker fetches GitHub + OpenDev data
   3. Data cached to `workspace/iproject/activity/YYYY-Www.json`
   4. Report generated using `results/status_report_template.md`
   5. AI analyzes and extracts key themes
   6. Final report saved to `workspace/iproject/activity/YYYY-Www_report.md`
   7. Summary displayed to user

   ## Customization

   Edit `results/status_report_template.md` to change report structure.
   ```

#### Testing
```bash
# Test askme integration in Cursor
status report last week
status report this week
status report 2025-11-01 to 2025-11-30
```

---

### Phase 4: Workshop Integration (Week 4)

**Goal**: Add status reporting to the mymcp workshop.

#### Deliverables

1. **Update `workshop/README.md`**
   - Add new session: "Session #5: Automated Status Reports"
   - Include example walkthrough
   - Link to `askme/STATUS_REPORTS.md`

2. **New Workshop Session**
   ```markdown
   ## Session #5: Automated Status Reports (30 minutes)

   ### Learning Objectives
   - Understand activity tracking architecture
   - Generate your first weekly status report
   - Customize report templates
   - Integrate into team workflows

   ### Hands-On Exercise

   1. **Verify activity-tracker setup**
      ```bash
      ./test-mcp-setup.sh
      # Should show: ✓ Activity Tracker Agent is working
      ```

   2. **Generate your first report**
      In Cursor, type:
      ```
      status report last week
      ```

   3. **Review the output**
      - Check `workspace/iproject/activity/2025-W4x_report.md`
      - Verify GitHub activity is captured
      - Verify OpenDev reviews are listed

   4. **Customize the template**
      - Edit `results/status_report_template.md`
      - Add a new section: "## Meetings & Discussions"
      - Regenerate report to see changes

   5. **Export for team standup**
      - Copy key themes to your team's Slack/email
      - Discuss blockers with your manager
      - Archive report in your workspace

   ### Discussion
   - How could this integrate with your existing workflows?
   - What other activities would you like tracked?
   - How could we use this for quarterly reviews?
   ```

3. **Update `workshop/GET_TOKENS.md`**
   - Add section: "Activity Tracker (Optional)"
   - Note: Reuses existing GitHub + OpenDev tokens

4. **Update `workshop/check_authentication_tokens.sh`**
   - Add check for activity-tracker agent
   - Verify it can communicate with github-agent and opendev-agent

#### Testing
```bash
# Dry run the workshop session
cd /home/omcgonag/Work/mymcp
./workshop/check_authentication_tokens.sh
# Follow Session #5 steps
```

---

## Technical Specifications

### MCP Agent Implementation

#### Server Structure (`activity-tracker-agent/server.py`)

```python
#!/usr/bin/env python
"""
Activity Tracker MCP Server for mymcp

Aggregates GitHub and OpenDev activities for status report generation.
"""

from mcp.server.fastmcp import FastMCP
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
import os
import subprocess

mcp = FastMCP("Activity Tracker")

# Configuration
WORKSPACE_PROJECT = os.environ.get(
    'WORKSPACE_PROJECT',
    '/home/omcgonag/Work/mymcp/workspace/iproject'
)
ACTIVITY_DIR = os.path.join(WORKSPACE_PROJECT, 'activity')

# Ensure activity directory exists
os.makedirs(ACTIVITY_DIR, exist_ok=True)


def parse_date_range(time_range: str) -> tuple[str, str]:
    """
    Parse time range string into start/end dates.
    
    Supported formats:
    - "this week"
    - "last week"
    - "yesterday"
    - "YYYY-MM-DD to YYYY-MM-DD"
    
    Returns:
        (start_date, end_date) in YYYY-MM-DD format
    """
    today = datetime.now()
    
    if time_range == "this week":
        start = today - timedelta(days=today.weekday())
        end = today
    elif time_range == "last week":
        start = today - timedelta(days=today.weekday() + 7)
        end = start + timedelta(days=6)
    elif time_range == "yesterday":
        start = end = today - timedelta(days=1)
    elif " to " in time_range:
        start_str, end_str = time_range.split(" to ")
        start = datetime.strptime(start_str.strip(), "%Y-%m-%d")
        end = datetime.strptime(end_str.strip(), "%Y-%m-%d")
    else:
        raise ValueError(f"Invalid time range: {time_range}")
    
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


def get_week_number(date_str: str) -> str:
    """Get ISO week number (YYYY-Www) for a date."""
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return dt.strftime("%Y-W%U")


def get_cached_activity(week_number: str) -> Optional[Dict]:
    """Retrieve cached activity data for a week."""
    cache_file = os.path.join(ACTIVITY_DIR, f"{week_number}.json")
    if os.path.exists(cache_file):
        # Check if cache is fresh (< 24 hours old)
        age_hours = (datetime.now() - datetime.fromtimestamp(
            os.path.getmtime(cache_file)
        )).total_seconds() / 3600
        
        if age_hours < 24:
            with open(cache_file, 'r') as f:
                return json.load(f)
    return None


def cache_activity(week_number: str, data: Dict) -> None:
    """Cache activity data for a week."""
    cache_file = os.path.join(ACTIVITY_DIR, f"{week_number}.json")
    with open(cache_file, 'w') as f:
        json.dump(data, f, indent=2)


@mcp.tool()
def get_github_activity(
    start_date: str,
    end_date: str,
    username: str = "omcgonag"
) -> Dict:
    """
    Fetch GitHub activity for a user in the given date range.
    
    Queries:
    - PRs created
    - PRs reviewed
    - Commits pushed
    - Issues created
    - Issue comments
    
    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        username: GitHub username
    
    Returns:
        Dict with GitHub activities
    """
    # TODO: Implement actual GitHub API calls via github-agent
    # For now, return mock data structure
    return {
        "username": username,
        "period": {"start": start_date, "end": end_date},
        "commits": [],
        "prs_created": [],
        "prs_reviewed": [],
        "issues_created": [],
        "issues_commented": []
    }


@mcp.tool()
def get_opendev_activity(
    start_date: str,
    end_date: str,
    username: str = "omcgonag"
) -> Dict:
    """
    Fetch OpenDev review activity for a user in the given date range.
    
    Queries:
    - Reviews posted
    - Comments posted
    - Votes given (Code-Review, Workflow)
    - Reviews received
    
    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        username: OpenDev username
    
    Returns:
        Dict with OpenDev activities
    """
    # TODO: Implement actual Gerrit API calls via opendev-agent
    # For now, return mock data structure
    return {
        "username": username,
        "period": {"start": start_date, "end": end_date},
        "reviews_posted": [],
        "comments_posted": [],
        "votes_given": [],
        "reviews_received": []
    }


@mcp.tool()
def generate_status_report(
    time_range: str = "last week",
    format: str = "markdown"
) -> str:
    """
    Generate a status report for the given time range.
    
    Combines GitHub and OpenDev activities, caches data,
    and formats according to the template.
    
    Args:
        time_range: "this week", "last week", or "YYYY-MM-DD to YYYY-MM-DD"
        format: "markdown" or "json"
    
    Returns:
        Formatted status report
    """
    # Parse date range
    start_date, end_date = parse_date_range(time_range)
    week_number = get_week_number(start_date)
    
    # Check cache
    cached_data = get_cached_activity(week_number)
    
    if cached_data:
        github_data = cached_data['github']
        opendev_data = cached_data['opendev']
    else:
        # Fetch fresh data
        github_data = get_github_activity(start_date, end_date)
        opendev_data = get_opendev_activity(start_date, end_date)
        
        # Cache it
        cache_activity(week_number, {
            'github': github_data,
            'opendev': opendev_data,
            'generated_at': datetime.now().isoformat()
        })
    
    # Format report
    if format == "json":
        return json.dumps({
            'github': github_data,
            'opendev': opendev_data
        }, indent=2)
    else:
        # Generate markdown report
        report = f"# Status Report: Week {week_number}\n\n"
        report += f"**Period**: {start_date} to {end_date}\n\n"
        report += "## GitHub Activity\n\n"
        report += f"- PRs Created: {len(github_data['prs_created'])}\n"
        report += f"- PRs Reviewed: {len(github_data['prs_reviewed'])}\n"
        report += f"- Commits: {len(github_data['commits'])}\n\n"
        report += "## OpenDev Activity\n\n"
        report += f"- Reviews Posted: {len(opendev_data['reviews_posted'])}\n"
        report += f"- Comments: {len(opendev_data['comments_posted'])}\n"
        report += f"- Votes: {len(opendev_data['votes_given'])}\n\n"
        
        # Save report to workspace
        report_file = os.path.join(ACTIVITY_DIR, f"{week_number}_report.md")
        with open(report_file, 'w') as f:
            f.write(report)
        
        return report


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "stdio":
        mcp.run()
    else:
        # CLI mode for testing
        print(generate_status_report("last week"))
```

---

## Comparison: standup_mcp vs mymcp Implementation

| Aspect | standup_mcp | mymcp Implementation |
|--------|-------------|----------------------|
| **Dependencies** | `did` tool + 20+ plugins | FastMCP + existing mymcp agents |
| **Configuration** | `~/.did/config` (complex INI) | Reuses existing `.env` files |
| **Data Sources** | Git, Jira, Bugzilla, GitHub, GitLab, Gerrit, etc. | GitHub, OpenDev (focused) |
| **Output Target** | Slack (formatted for copy-paste) | Markdown (workspace files) |
| **Caching** | Single append-only file (`$STANDUP_PATH`) | Per-week JSON files + reports |
| **Historical Tracking** | No (cache is transient) | Yes (`workspace/iproject/activity/`) |
| **Integration** | Standalone MCP server | Integrated with askme framework |
| **Workshop Ready** | No documentation for workshops | Designed for workshop Session #5 |
| **OpenDev Optimization** | Generic Gerrit plugin | Custom OpenDev-specific queries |
| **Trend Analysis** | Not supported | Enabled via cached weekly files |
| **Setup Complexity** | High (external tool + plugins) | Low (reuses existing infrastructure) |

---

## Benefits of mymcp Approach

### 1. **Leverages Existing Infrastructure**
   - No new external dependencies (`did` tool)
   - Reuses GitHub and OpenDev MCP agents already in place
   - Consistent authentication (existing `.env` files)

### 2. **OpenStack Horizon Optimized**
   - Designed for de-angularization workflow tracking
   - Captures OpenDev patchset iterations
   - Tracks review comments specific to Horizon development

### 3. **Workspace Integration**
   - Activity history stored in `workspace/iproject/activity/`
   - Can be committed to personal iproject repo
   - Supports long-term trend analysis
   - Can generate quarterly/annual reports from accumulated data

### 4. **askme Framework Ready**
   - Natural language commands: `status report last week`
   - Consistent with existing review/feature workflows
   - Workshop-friendly for team adoption

### 5. **Extensible**
   - Easy to add Jira tracking (already have `@jiraMcp` agent)
   - Can add GitLab CEE tracking (already have `@gitlab-cee-agent`)
   - Template-based reports allow custom formats

---

## Risks & Mitigations

### Risk 1: API Rate Limiting

**Issue**: GitHub and Gerrit APIs have rate limits that could be exceeded with frequent status report generation.

**Mitigation**:
- Implement 24-hour cache freshness (reuse data if < 24 hours old)
- Batch API calls (fetch all data in single query per service)
- Use authenticated API calls (higher rate limits)
- Store activity incrementally (daily jobs could pre-populate cache)

### Risk 2: Missing GitHub/OpenDev Agent Features

**Issue**: Current `github-agent` and `opendev-agent` may not expose user activity queries.

**Mitigation**:
- **Option A**: Extend existing agents with new tools:
  - `github-agent`: Add `get_user_activity(username, start_date, end_date)`
  - `opendev-agent`: Add `get_user_reviews(username, start_date, end_date)`
- **Option B**: activity-tracker makes direct API calls (bypasses agents)
- **Option C**: Start with Option B, migrate to Option A in Phase 2

**Recommendation**: Start with Option B for speed, refactor to Option A for cleaner architecture.

### Risk 3: Incomplete Activity Capture

**Issue**: Not all activities may be tracked (e.g., emails, meetings, documentation).

**Mitigation**:
- Phase 1 focuses on code-related activities (PRs, reviews, commits)
- Template includes "## Other Activities" section for manual additions
- Future phases can add Jira, email, calendar integrations

### Risk 4: Time Before Christmas

**Issue**: Only ~4 weeks until Christmas break, may not complete all phases.

**Mitigation**:
- **Priority**: Phase 1 + Phase 2 (core tracking + basic reports)
- **Nice to have**: Phase 3 (askme integration)
- **Defer**: Phase 4 (workshop) to January 2026

---

## Success Criteria

### Minimum Viable Product (MVP) - Before Christmas

✅ **Functional activity-tracker MCP agent**
   - Can query GitHub for user PRs, commits, reviews
   - Can query OpenDev for user reviews, comments, votes
   - Caches results to `workspace/iproject/activity/`

✅ **Basic report generation**
   - `generate_status_report("last week")` works
   - Output is markdown format
   - Includes GitHub + OpenDev sections

✅ **Manual testing successful**
   - Generate report for last 2 weeks of November
   - Report accurately reflects actual activities
   - Report saved to workspace

### Full Success - Post-Christmas (Q1 2026)

✅ **askme integration complete**
   - Natural language: `status report last week`
   - Multiple time ranges supported
   - Custom templates working

✅ **Workshop session ready**
   - Session #5 added to workshop/README.md
   - Hands-on exercise tested with colleague
   - Documented in `askme/STATUS_REPORTS.md`

✅ **Team adoption**
   - At least 2 team members using it weekly
   - Positive feedback on report quality
   - Reports used in actual team standups

---

## Next Steps

### Immediate (This Week)

1. **Review this design document**
   - User feedback on architecture
   - Confirm Phase 1 + 2 scope is correct
   - Adjust timeline if needed

2. **Create `activity-tracker-agent/` directory**
   - Set up FastMCP boilerplate
   - Implement `server.py` skeleton
   - Test MCP connectivity

3. **Implement Phase 1 deliverables**
   - `get_github_activity()` with real API calls
   - `get_opendev_activity()` with real API calls
   - Test with actual user data

### This Month (November 2025)

1. **Complete Phase 2**
   - Implement `generate_status_report()`
   - Create `results/status_report_template.md`
   - Test weekly report generation

2. **Dogfooding**
   - Generate your own weekly reports for 2-3 weeks
   - Iterate on template based on actual use
   - Fix bugs, improve caching

3. **Document learnings**
   - Update `activity-tracker-agent/README.md`
   - Create `activity-tracker-agent/TROUBLESHOOTING.md`
   - Add examples to `askme/STATUS_REPORTS.md`

### Q1 2026 (Post-Christmas)

1. **Complete Phase 3 + 4**
   - askme integration
   - Workshop session
   - Team rollout

2. **Enhancements**
   - Jira integration (track OSPRH tickets)
   - Trend analysis (month-over-month comparisons)
   - Quarterly reports (automated generation)

---

## Acknowledgments

This implementation would not have been possible without the pioneering work of **Francesco Pantano** and his [`standup_mcp`](https://gitlab.cee.redhat.com/fpantano/standup_mcp) project.

### What We Learned from Francesco's Work

**1. Production-Ready MCP Server Design**
   - Francesco's clean separation between MCP protocol handling and business logic
   - Thoughtful caching strategy to handle API rate limits gracefully
   - Robust error handling and fallback mechanisms

**2. Practical Workflow Automation**
   - Real-world understanding of what developers need in status reports
   - Integration with existing tools (`did`) rather than reinventing the wheel
   - Focus on copy-paste readiness for Slack (immediate team value)

**3. FastMCP Best Practices**
   - Clear tool definitions with comprehensive docstrings
   - Proper type hints for MCP protocol compliance
   - Minimal dependencies, maximum functionality

**4. Developer Experience**
   - Straightforward configuration (`~/.did/config`)
   - Clear documentation and examples
   - Time range parsing that "just works" (`"last week"`, etc.)

### How This Design Honors His Approach

While we adapted Francesco's design for our specific OpenStack Horizon workflow, we preserved his core architectural principles:

✅ **Caching First** - Respect API rate limits with intelligent caching  
✅ **User-Friendly Time Ranges** - Natural language like `"last week"`  
✅ **Structured Data** - Clean JSON formats for downstream processing  
✅ **MCP Protocol Compliance** - Following FastMCP best practices  
✅ **Workspace Integration** - Persisted data for historical tracking (extending his append-only cache concept)

Francesco's work proved that automating status reports via MCP is not only feasible but can be elegant, maintainable, and truly valuable for development teams. His `standup_mcp` serves as a reference implementation that demonstrates the power of MCP for workflow automation beyond code review.

**Thank you, Francesco, for sharing your excellent work and inspiring this implementation!** 🙌

---

## Appendices

### A. Example Weekly Report (Target Output)

```markdown
# Status Report: Week 2025-W47

**Period**: 2025-11-15 to 2025-11-22  
**Generated**: 2025-11-22 16:30:00

---

## Summary

- **GitHub**: 2 PRs created, 5 PRs reviewed, 12 commits
- **OpenDev**: 1 review posted (2 patchsets), 3 comments, 2 votes

---

## GitHub Activity

### Pull Requests Created (2)

- **horizon-operator#402**: Add support for custom configuration overrides (OPEN)
  - Created: 2025-11-16
  - Implements ConfigMap mounting for horizon.conf customization
  - Related: OSPRH-12802

- **horizon#510**: De-angularize Key Pairs: Add Django-based Create form (MERGED)
  - Created: 2025-11-18
  - Merged: 2025-11-20
  - First patchset for OSPRH-12802 de-angularization effort

### Pull Requests Reviewed (5)

- **data-plane-adoption#1031**: Dependency bump for ansible-runner
  - 2 comments, ✅ Approved

- **ci-framework#3102**: Fix Horizon deployment in devstack scenario
  - 1 comment, 💬 Commented (requested changes)

- **swift-operator#374**: Update Swift ring management
  - 1 comment, ✅ Approved

- **manila-operator#461**: Fix share backend configuration
  - 3 comments, 💬 Commented

- **keystone-operator#89**: Add LDAP integration support
  - 1 comment, ✅ Approved

### Commits (12)

- **horizon** `f23ca76`: De-angularize Key Pairs: Add Django-based Create form
- **horizon** `28e4be1`: Rebase on top of chevron changes (966349)
- **horizon-operator** `a1b2c3d`: Add ConfigMap volume mount
- **horizon-operator** `d4e5f6g`: Update deployment documentation
- _(8 more commits in personal testing repos)_

---

## OpenDev Activity

### Reviews Posted (1)

- **Review 967269**: De-angularize Key Pairs: Add Django-based Create form
  - Project: openstack/horizon
  - Patchsets: 2 (rebased after 966349 merged)
  - Status: Merged
  - Topic: de-angularize

### Comments & Votes (3 comments, 2 votes)

- **Review 966349** (Patchset 5): Code-Review +1 | "Chevrons work great, tested locally"
- **Review 967773** (Patchset 1): Code-Review +1 | "LGTM, clean implementation"
- **Review 967100** (Patchset 2): Comment | "Consider adding test coverage for edge case"

---

## Key Themes

1. **De-angularization Progress (OSPRH-12802)**
   - Completed and merged Patchset 1 (Generate Key Pair form)
   - Submitted to Gerrit as Review 967269
   - Successfully rebased on top of chevron changes (966349)
   - Local testing confirmed modal form works correctly

2. **Operator Configuration Enhancements**
   - horizon-operator PR 402 adds ConfigMap support
   - Enables custom horizon.conf overrides for deployments
   - Documentation updated for new configuration pattern

3. **Code Review Activities**
   - Focused on operator maintenance (Swift, Manila, Keystone)
   - Provided feedback on CI framework Horizon deployment
   - Approved dependency updates for data-plane-adoption

---

## Blockers

None

---

## Next Week's Focus

- [ ] Start Patchset 2: Import Key Pair form conversion
- [ ] Address review comments on horizon-operator#402
- [ ] Continue operator code reviews
- [ ] Update OSPRH-12802 sprint planning

---

_Generated by mymcp activity-tracker on 2025-11-22 16:30:00_  
_Data cached at: `workspace/iproject/activity/2025-W47.json`_
```

### B. References

#### Primary Inspiration
- **standup_mcp by Francesco Pantano**: https://gitlab.cee.redhat.com/fpantano/standup_mcp
  - The reference implementation that inspired this design
  - Demonstrates production-ready MCP server architecture
  - Excellent example of FastMCP best practices

#### Tools & Technologies
- **did tool**: https://github.com/psss/did
  - Command-line tool used by `standup_mcp`
  - Comprehensive plugin ecosystem for activity tracking
- **FastMCP**: https://github.com/pydantic/fastmcp
  - Python framework for building MCP servers
  - Used by both `standup_mcp` and our implementation
- **MCP Specification**: https://modelcontextprotocol.io/
  - Official Model Context Protocol specification

#### API Documentation
- **GitHub REST API**: https://docs.github.com/en/rest
- **Gerrit REST API**: https://gerrit-review.googlesource.com/Documentation/rest-api.html

---

**Document Version**: 1.0  
**Created**: 2025-11-22  
**Author**: Cursor AI (with @omcgonag requirements)  
**Inspired By**: Francesco Pantano's [`standup_mcp`](https://gitlab.cee.redhat.com/fpantano/standup_mcp)  
**Status**: Draft - Awaiting User Review

---

*Special thanks to Francesco Pantano for his pioneering work in MCP-based workflow automation. His `standup_mcp` project demonstrates that elegant solutions to complex problems are possible when architecture, UX, and developer empathy align.*



