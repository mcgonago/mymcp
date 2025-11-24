# Adding GitLab and Jira Activity Tracking

**Assessment Date**: 2025-11-23  
**Current Report**: `workspace/iproject/activity/2025-W46_report.md`  
**Feasibility**: **MEDIUM** (GitLab) / **EASY-MEDIUM** (Jira)

---

## Executive Summary

**How easy is it to add?**

| Platform | Difficulty | Time Estimate | Confidence |
|----------|-----------|---------------|------------|
| **GitLab** | Medium | 4-6 hours | High |
| **Jira** | Easy-Medium | 2-4 hours | High |

**Why this difficulty?**
- ✅ Your current code is well-structured (easy to extend)
- ✅ Jira MCP tools already exist in `mymcp`
- ⚠️ GitLab would need direct API calls (like GitHub)
- ⚠️ Need authentication tokens for both

**Total Effort**: 6-10 hours to add both platforms

---

## Current Architecture Analysis

### What You Have Already

Your `activity-tracker-agent/server.py` has a **clean, modular structure**:

```python
# Pattern for each platform:
1. get_<platform>_activity(start_date, end_date, username) → Dict
2. Cache results
3. generate_status_report() combines all platforms
```

**Platforms Currently Supported**:
- ✅ GitHub (lines 155-313)
- ✅ OpenDev/Gerrit (lines 316-442)

**What Makes Extension Easy**:
- Clear separation of concerns (one function per platform)
- Consistent data structure (all return similar Dict format)
- Modular report generation (each platform gets its own section)
- Caching works for any platform

---

## Adding GitLab Activity Tracking

### Difficulty: MEDIUM (4-6 hours)

### What You'd Track

GitLab activities for https://gitlab.cee.redhat.com:

1. **Merge Requests**
   - MRs created by user
   - MRs reviewed by user (comments, approvals)
   - MR state changes

2. **Commits**
   - Commits authored by user
   - Commits to specific projects

3. **Issues**
   - Issues created
   - Issues commented on
   - Issues assigned to user

4. **Comments**
   - MR comments/reviews
   - Issue comments
   - Commit comments

### Implementation Plan

#### Step 1: Add GitLab Configuration

**File**: `activity-tracker-agent/.env`

```bash
# Add these
GITLAB_URL=https://gitlab.cee.redhat.com
GITLAB_TOKEN=glpat-xxxxxxxxxxxxxxxxxxxx  # Personal access token
GITLAB_USERNAME=omcgonag
```

**File**: `activity-tracker-agent/server.py` (top section)

```python
# Add after existing config
GITLAB_URL = os.environ.get('GITLAB_URL', 'https://gitlab.cee.redhat.com')
GITLAB_TOKEN = os.environ.get('GITLAB_TOKEN', '')
GITLAB_USERNAME = os.environ.get('GITLAB_USERNAME', 'omcgonag')
```

#### Step 2: Add `get_gitlab_activity()` Function

**Insert after `get_opendev_activity()` (around line 443)**:

```python
@mcp.tool()
def get_gitlab_activity(
    start_date: str,
    end_date: str,
    username: str = None
) -> Dict:
    """
    Fetch GitLab activity for a user in the given date range.
    
    Queries GitLab API for:
    - Merge requests created/reviewed
    - Commits authored
    - Issues created/commented
    - Comments posted
    
    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        username: GitLab username (defaults to GITLAB_USERNAME from env)
    
    Returns:
        Dict with GitLab activities
    """
    if username is None:
        username = GITLAB_USERNAME
    
    if not GITLAB_TOKEN:
        return {
            "error": "GITLAB_TOKEN not configured",
            "username": username,
            "period": {"start": start_date, "end": end_date}
        }
    
    headers = {
        'PRIVATE-TOKEN': GITLAB_TOKEN
    }
    
    result = {
        "username": username,
        "period": {"start": start_date, "end": end_date},
        "merge_requests_created": [],
        "merge_requests_reviewed": [],
        "commits": [],
        "issues_created": [],
        "issues_commented": [],
        "comments_posted": []
    }
    
    try:
        # Get user ID first (needed for some queries)
        user_response = requests.get(
            f'{GITLAB_URL}/api/v4/users',
            headers=headers,
            params={'username': username}
        )
        user_response.raise_for_status()
        users = user_response.json()
        if not users:
            result['error'] = f"User {username} not found"
            return result
        user_id = users[0]['id']
        
        # Query 1: Merge Requests created by user
        mrs_response = requests.get(
            f'{GITLAB_URL}/api/v4/merge_requests',
            headers=headers,
            params={
                'author_id': user_id,
                'created_after': f'{start_date}T00:00:00Z',
                'created_before': f'{end_date}T23:59:59Z',
                'scope': 'all',
                'per_page': 100
            }
        )
        mrs_response.raise_for_status()
        for mr in mrs_response.json():
            result['merge_requests_created'].append({
                'project': mr['references']['full'].split('!')[0],
                'number': mr['iid'],
                'title': mr['title'],
                'state': mr['state'],
                'created_at': mr['created_at'],
                'url': mr['web_url']
            })
        
        # Query 2: User events (for reviews, comments)
        events_response = requests.get(
            f'{GITLAB_URL}/api/v4/users/{user_id}/events',
            headers=headers,
            params={
                'after': start_date,
                'before': end_date,
                'per_page': 100
            }
        )
        events_response.raise_for_status()
        for event in events_response.json():
            event_date = event['created_at'][:10]
            if start_date <= event_date <= end_date:
                # MR comments/approvals
                if event['action_name'] == 'commented on' and event.get('target_type') == 'MergeRequest':
                    target = event.get('target_title', '')
                    result['merge_requests_reviewed'].append({
                        'project': event.get('project_id', ''),
                        'title': target,
                        'action': 'commented',
                        'date': event['created_at'],
                        'url': event.get('target_url', '')
                    })
                
                # Commits
                elif event['action_name'] == 'pushed to':
                    for commit in event.get('push_data', {}).get('commit_to', []):
                        result['commits'].append({
                            'project': event.get('project_id', ''),
                            'sha': commit[:7] if commit else 'N/A',
                            'date': event['created_at'],
                            'url': event.get('target_url', '')
                        })
                
                # Issue comments
                elif event['action_name'] == 'commented on' and event.get('target_type') == 'Issue':
                    result['issues_commented'].append({
                        'project': event.get('project_id', ''),
                        'title': event.get('target_title', ''),
                        'date': event['created_at'],
                        'url': event.get('target_url', '')
                    })
        
        # Query 3: Issues created
        issues_response = requests.get(
            f'{GITLAB_URL}/api/v4/issues',
            headers=headers,
            params={
                'author_id': user_id,
                'created_after': f'{start_date}T00:00:00Z',
                'created_before': f'{end_date}T23:59:59Z',
                'scope': 'all',
                'per_page': 100
            }
        )
        issues_response.raise_for_status()
        for issue in issues_response.json():
            result['issues_created'].append({
                'project': issue['references']['full'].split('#')[0],
                'number': issue['iid'],
                'title': issue['title'],
                'state': issue['state'],
                'created_at': issue['created_at'],
                'url': issue['web_url']
            })
        
    except requests.exceptions.RequestException as e:
        result['error'] = f"GitLab API error: {str(e)}"
    
    return result
```

**Lines**: ~150 lines

#### Step 3: Update `generate_status_report()`

**Modify around line 478 to fetch GitLab data**:

```python
# Add after fetching opendev_data
gitlab_data = get_gitlab_activity(start_date, end_date)

# Update cache_data
cache_data = {
    'github': github_data,
    'opendev': opendev_data,
    'gitlab': gitlab_data,  # ADD THIS
    'generated_at': datetime.now().isoformat()
}
```

**Add GitLab section to report (around line 670)**:

```python
# GitLab Activity section (insert after OpenDev section)
report_lines.append("## 🟣 GitLab Activity")
report_lines.append("")

gl_mrs_created = len(gitlab_data.get('merge_requests_created', []))
gl_mrs_reviewed = len(gitlab_data.get('merge_requests_reviewed', []))
gl_commits = len(gitlab_data.get('commits', []))
gl_issues = len(gitlab_data.get('issues_created', []))

if gl_mrs_created > 0:
    report_lines.append(f"### Merge Requests Created ({gl_mrs_created})")
    report_lines.append("")
    report_lines.append("| Project | MR | Title | State | Created | Link |")
    report_lines.append("|---------|-----|-------|-------|---------|------|")
    for mr in gitlab_data.get('merge_requests_created', []):
        state_icon = "🟢" if mr['state'] == 'opened' else "🟣" if mr['state'] == 'merged' else "🔴"
        report_lines.append(f"| {mr['project']} | !{mr['number']} | {mr['title']} | {state_icon} {mr['state'].upper()} | {mr['created_at'][:10]} | [View]({mr['url']}) |")
    report_lines.append("")

# ... similar sections for MRs reviewed, commits, issues ...

if not any([gl_mrs_created, gl_mrs_reviewed, gl_commits, gl_issues]):
    report_lines.append("_No GitLab activity in this period_")
    report_lines.append("")

report_lines.append("---")
report_lines.append("")
```

**Update Summary Table** (around line 548):

```python
# Add GitLab row
gl_mrs = len(gitlab_data.get('merge_requests_created', []))
gl_comments = len(gitlab_data.get('merge_requests_reviewed', []))
# ...

report_lines.append(f"| **GitLab** | {gl_mrs} | {gl_comments} | {gl_commits} | {gl_issues} | 0 | - |")
```

### Testing GitLab Integration

```bash
# Set environment variables
export GITLAB_URL=https://gitlab.cee.redhat.com
export GITLAB_TOKEN=glpat-xxxxxxxxxxxxxxxxxxxx
export GITLAB_USERNAME=omcgonag

# Test directly
cd activity-tracker-agent
python3 server.py  # Should show GitLab section in report

# Or via MCP
@activity-tracker generate_status_report("this week")
```

---

## Adding Jira Activity Tracking

### Difficulty: EASY-MEDIUM (2-4 hours)

### What You'd Track

Jira activities (using existing MCP tools):

1. **Issues Created**
   - New issues authored by user
   
2. **Issues Updated**
   - Status changes (To Do → In Progress → Done)
   - Assignee changes
   - Comments added

3. **Issues Resolved**
   - Issues moved to Done/Resolved

### Implementation Plan

#### Step 1: Jira Configuration

**File**: `activity-tracker-agent/.env`

```bash
# Jira config (likely already exists for jiraMcp)
JIRA_URL=https://issues.redhat.com
JIRA_USERNAME=omcgonag
JIRA_API_TOKEN=xxxxxxxxxxxxxxxxxxxx
```

**File**: `activity-tracker-agent/server.py`

```python
# Add after GitLab config
JIRA_URL = os.environ.get('JIRA_URL', 'https://issues.redhat.com')
JIRA_USERNAME = os.environ.get('JIRA_USERNAME', 'omcgonag')
JIRA_TOKEN = os.environ.get('JIRA_API_TOKEN', '')
```

#### Step 2: Add `get_jira_activity()` Function

**Insert after `get_gitlab_activity()`**:

```python
@mcp.tool()
def get_jira_activity(
    start_date: str,
    end_date: str,
    username: str = None
) -> Dict:
    """
    Fetch Jira activity for a user in the given date range.
    
    Queries Jira API for:
    - Issues created by user
    - Issues updated by user
    - Issues resolved by user
    - Comments posted by user
    
    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        username: Jira username (defaults to JIRA_USERNAME from env)
    
    Returns:
        Dict with Jira activities
    """
    if username is None:
        username = JIRA_USERNAME
    
    if not JIRA_TOKEN:
        return {
            "error": "JIRA_API_TOKEN not configured",
            "username": username,
            "period": {"start": start_date, "end": end_date}
        }
    
    auth = (username, JIRA_TOKEN)
    headers = {'Content-Type': 'application/json'}
    
    result = {
        "username": username,
        "period": {"start": start_date, "end": end_date},
        "issues_created": [],
        "issues_updated": [],
        "issues_resolved": [],
        "comments_posted": []
    }
    
    try:
        # Query 1: Issues created by user
        created_jql = f'creator = "{username}" AND created >= "{start_date}" AND created <= "{end_date}"'
        created_response = requests.get(
            f'{JIRA_URL}/rest/api/2/search',
            auth=auth,
            headers=headers,
            params={'jql': created_jql, 'maxResults': 100}
        )
        created_response.raise_for_status()
        for issue in created_response.json().get('issues', []):
            result['issues_created'].append({
                'key': issue['key'],
                'summary': issue['fields']['summary'],
                'type': issue['fields']['issuetype']['name'],
                'status': issue['fields']['status']['name'],
                'created': issue['fields']['created'],
                'url': f"{JIRA_URL}/browse/{issue['key']}"
            })
        
        # Query 2: Issues updated by user
        updated_jql = f'updated >= "{start_date}" AND updated <= "{end_date}" AND updatedBy = "{username}"'
        updated_response = requests.get(
            f'{JIRA_URL}/rest/api/2/search',
            auth=auth,
            headers=headers,
            params={'jql': updated_jql, 'maxResults': 100, 'expand': 'changelog'}
        )
        updated_response.raise_for_status()
        for issue in updated_response.json().get('issues', []):
            # Track status changes
            changelog = issue.get('changelog', {}).get('histories', [])
            for history in changelog:
                if history.get('author', {}).get('name') == username:
                    for item in history.get('items', []):
                        if item['field'] == 'status':
                            result['issues_updated'].append({
                                'key': issue['key'],
                                'summary': issue['fields']['summary'],
                                'change': f"{item['fromString']} → {item['toString']}",
                                'date': history['created'],
                                'url': f"{JIRA_URL}/browse/{issue['key']}"
                            })
        
        # Query 3: Issues resolved by user
        resolved_jql = f'resolved >= "{start_date}" AND resolved <= "{end_date}" AND resolutiondate is not EMPTY AND (assignee = "{username}" OR creator = "{username}")'
        resolved_response = requests.get(
            f'{JIRA_URL}/rest/api/2/search',
            auth=auth,
            headers=headers,
            params={'jql': resolved_jql, 'maxResults': 100}
        )
        resolved_response.raise_for_status()
        for issue in resolved_response.json().get('issues', []):
            result['issues_resolved'].append({
                'key': issue['key'],
                'summary': issue['fields']['summary'],
                'resolution': issue['fields']['resolution']['name'],
                'resolved': issue['fields']['resolutiondate'],
                'url': f"{JIRA_URL}/browse/{issue['key']}"
            })
        
    except requests.exceptions.RequestException as e:
        result['error'] = f"Jira API error: {str(e)}"
    
    return result
```

**Lines**: ~120 lines

#### Step 3: Update Report Generation

Similar to GitLab, add Jira section to report:

```python
# Jira Activity section
report_lines.append("## 🔷 Jira Activity")
report_lines.append("")

jira_created = len(jira_data.get('issues_created', []))
jira_updated = len(jira_data.get('issues_updated', []))
jira_resolved = len(jira_data.get('issues_resolved', []))

if jira_created > 0:
    report_lines.append(f"### Issues Created ({jira_created})")
    report_lines.append("")
    report_lines.append("| Issue | Type | Summary | Status | Created | Link |")
    report_lines.append("|-------|------|---------|--------|---------|------|")
    for issue in jira_data.get('issues_created', []):
        report_lines.append(f"| [{issue['key']}]({issue['url']}) | {issue['type']} | {issue['summary']} | {issue['status']} | {issue['created'][:10]} | [View]({issue['url']}) |")
    report_lines.append("")

# ... similar for updated, resolved ...
```

---

## Updated Report Structure

After adding GitLab and Jira, your report would look like:

```markdown
# Status Report: Week 2025-W46

**Period**: 2025-11-17 to 2025-11-22

## 📊 Activity Summary

| Platform | PRs/Reviews/MRs | Comments | Commits | Issues | Votes | Other |
|----------|-----------------|----------|---------|--------|-------|-------|
| **GitHub** | 0 | 0 | 0 | 0 | 0 | - |
| **OpenDev** | 2 | 9 | 0 | 0 | 0 | 1 merged |
| **GitLab** | 3 | 5 | 12 | 1 | 0 | - |
| **Jira** | - | - | - | 5 | - | 2 resolved |
| **Total** | **5** | **14** | **12** | **6** | **0** | **3** |

---

## 🔵 GitHub Activity
_No GitHub activity in this period_

---

## 🟠 OpenDev Activity
### Reviews Posted (2)
...

---

## 🟣 GitLab Activity
### Merge Requests Created (3)
...

### Commits (12)
...

---

## 🔷 Jira Activity
### Issues Created (3)
...

### Issues Resolved (2)
...

---

## 📝 Key Themes
_To be filled_

## 🚧 Blockers
_None_
```

---

## Implementation Checklist

### For GitLab

- [ ] Add `GITLAB_URL`, `GITLAB_TOKEN`, `GITLAB_USERNAME` to `.env`
- [ ] Update `server.py` to load GitLab config
- [ ] Add `get_gitlab_activity()` function (~150 lines)
- [ ] Update `generate_status_report()` to fetch GitLab data
- [ ] Add GitLab section to markdown report
- [ ] Update summary table to include GitLab
- [ ] Update cache structure to include GitLab
- [ ] Test with real GitLab token
- [ ] Update `README.md` with GitLab config docs

**Time**: 4-6 hours

### For Jira

- [ ] Add `JIRA_URL`, `JIRA_USERNAME`, `JIRA_API_TOKEN` to `.env`
- [ ] Update `server.py` to load Jira config
- [ ] Add `get_jira_activity()` function (~120 lines)
- [ ] Update `generate_status_report()` to fetch Jira data
- [ ] Add Jira section to markdown report
- [ ] Update summary table to include Jira
- [ ] Update cache structure to include Jira
- [ ] Test with real Jira token
- [ ] Update `README.md` with Jira config docs

**Time**: 2-4 hours

---

## Risks and Challenges

### GitLab Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **API Rate Limits** | Medium | Medium | Cache aggressively, paginate wisely |
| **Token Expiry** | Medium | High | Document token refresh process |
| **Project Access** | Medium | Low | Query only projects user has access to |
| **API Changes** | Low | Medium | Use versioned API endpoints (v4) |

### Jira Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **Complex JQL** | Medium | Low | Test queries incrementally |
| **API Rate Limits** | Low | Medium | Use existing Jira MCP caching |
| **Permissions** | Medium | Medium | Query only issues user can see |
| **Changelog Parsing** | Medium | Low | Robust error handling |

---

## Alternative: Use Existing MCP Tools

### For GitLab

You have `gitlab-cee-agent` MCP tool already!

**Instead of direct API calls**, you could:
1. Use `mcp_gitlab-cee-agent_gitlab_resource_fetcher` for individual resources
2. Query for user's recent MRs, issues via GitLab's user events
3. Aggregate results

**Pros**: Reuses existing infrastructure  
**Cons**: May require multiple MCP calls, less efficient

### For Jira

You have `jiraMcp` tools already!

**Leverage existing tools**:
- `search_issues()` with custom JQL
- `get_jira()` for individual issues

**Pros**: Already authenticated, tested  
**Cons**: Need to aggregate results yourself

---

## Recommendation

**Phase 1: Add Jira (2-4 hours)** ✅ DO THIS FIRST
- Easier (existing MCP tools)
- Likely more useful (track ticket work)
- Lower risk

**Phase 2: Add GitLab (4-6 hours)** ✅ DO THIS SECOND
- More complex (API integration)
- Completes the picture
- Moderate risk

**Total Time**: 6-10 hours for both

**Confidence**: HIGH - Your current code structure makes this very doable.

---

## Next Steps

1. **Decide**: Do you want both or just one?
2. **Gather tokens**: 
   - GitLab: https://gitlab.cee.redhat.com/-/profile/personal_access_tokens
   - Jira: Your existing token (from jiraMcp config)
3. **Start with Jira** (easier, faster win)
4. **Then add GitLab**
5. **Test incrementally** (don't try to do everything at once)

---

**Want me to implement this for you?** Just say:
```
Add Jira and GitLab activity tracking to activity-tracker-agent
```

And I'll create the full implementation! 🚀

