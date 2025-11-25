#!/usr/bin/env python3
"""
Activity Tracker MCP Server for mymcp

Aggregates GitHub and OpenDev activities for status report generation.
Leverages existing mymcp infrastructure while providing focused activity tracking.

Author: mymcp project
Created: 2025-11-22
"""

from mcp.server.fastmcp import FastMCP
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json
import os
import sys
import requests
from dateutil import parser as date_parser
from jira import JIRA

# Initialize FastMCP server
mcp = FastMCP("Activity Tracker")

def load_env_from_file(filepath: str) -> Dict[str, str]:
    """Load environment variables from a .env file."""
    env_vars = {}
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        # Remove quotes if present
                        value = value.strip().strip('"').strip("'")
                        env_vars[key] = value
        except Exception as e:
            print(f"Warning: Could not load {filepath}: {e}", file=sys.stderr)
    return env_vars

# Auto-discover credentials from existing MCP agents
MYMCP_REPO_PATH = os.path.dirname(os.path.abspath(__file__))
MYMCP_REPO_PATH = os.path.dirname(MYMCP_REPO_PATH)  # Go up one level to repo root

# Load from github-agent if exists
github_env = load_env_from_file(os.path.join(MYMCP_REPO_PATH, 'github-agent', '.env'))
# Load from gitlab-rh-agent if exists
gitlab_env = load_env_from_file(os.path.join(MYMCP_REPO_PATH, 'gitlab-rh-agent', '.env'))
# Load from jira-agent if exists (check both locations)
jira_env = load_env_from_file(os.path.join(MYMCP_REPO_PATH, 'jira-agent', '.env'))
# Also check ~/.rh-jira-agent.env (per jira-agent/README.md configuration)
rh_jira_env = load_env_from_file(os.path.expanduser('~/.rh-jira-agent.env'))
# Merge jira configs (~/.rh-jira-agent.env takes precedence)
jira_env = {**jira_env, **rh_jira_env}

# Configuration from environment (with fallback to agent .env files)
WORKSPACE_PROJECT = os.environ.get(
    'WORKSPACE_PROJECT',
    os.path.expanduser('~/Work/mymcp/workspace/iproject')
)
ACTIVITY_DIR = os.environ.get(
    'ACTIVITY_DIR',
    os.path.join(WORKSPACE_PROJECT, 'activity')
)
GITHUB_USERNAME = os.environ.get('GITHUB_USERNAME', 'omcgonag')
OPENDEV_USERNAME = os.environ.get('OPENDEV_USERNAME', 'omcgonag')
GITLAB_USERNAME = os.environ.get('GITLAB_USERNAME', 'omcgonag')
# Support both JIRA_EMAIL and JIRA_USERNAME (jira-agent uses JIRA_USERNAME)
JIRA_EMAIL = os.environ.get('JIRA_EMAIL', jira_env.get('JIRA_EMAIL', jira_env.get('JIRA_USERNAME', '')))
CACHE_MAX_AGE_HOURS = int(os.environ.get('CACHE_MAX_AGE_HOURS', '24'))
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', github_env.get('GITHUB_TOKEN', ''))
GITLAB_TOKEN = os.environ.get('GITLAB_TOKEN', gitlab_env.get('GITLAB_TOKEN', ''))
GITLAB_URL = os.environ.get('GITLAB_URL', gitlab_env.get('GITLAB_URL', 'https://gitlab.cee.redhat.com'))
JIRA_URL = os.environ.get('JIRA_URL', jira_env.get('JIRA_URL', ''))
JIRA_API_TOKEN = os.environ.get('JIRA_API_TOKEN', jira_env.get('JIRA_API_TOKEN', ''))

# Ensure activity directory exists
os.makedirs(ACTIVITY_DIR, exist_ok=True)


def parse_date_range(time_range: str) -> Tuple[str, str]:
    """
    Parse time range string into start/end dates.
    
    Supported formats:
    - "this week" - Current week (Monday to today)
    - "last week" - Previous week (Monday to Sunday)
    - "yesterday" - Single day
    - "YYYY-MM-DD to YYYY-MM-DD" - Custom range
    
    Args:
        time_range: Time range string
    
    Returns:
        Tuple of (start_date, end_date) in YYYY-MM-DD format
    
    Raises:
        ValueError: If time range format is invalid
    """
    today = datetime.now()
    
    if time_range == "this week":
        # Start of week (Monday)
        start = today - timedelta(days=today.weekday())
        # End = today + 1 day to capture today's UTC timestamps (for users in negative UTC offsets)
        end = today + timedelta(days=1)
    elif time_range == "last week":
        # Start of last week (Monday)
        start = today - timedelta(days=today.weekday() + 7)
        # End of last week (Sunday)
        end = start + timedelta(days=6)
    elif time_range == "yesterday":
        start = end = today - timedelta(days=1)
    elif " to " in time_range:
        # Custom range: "YYYY-MM-DD to YYYY-MM-DD"
        parts = time_range.split(" to ")
        if len(parts) != 2:
            raise ValueError(f"Invalid date range format: {time_range}")
        start_str, end_str = parts
        start = datetime.strptime(start_str.strip(), "%Y-%m-%d")
        end = datetime.strptime(end_str.strip(), "%Y-%m-%d")
    else:
        raise ValueError(
            f"Invalid time range: {time_range}. "
            f"Supported: 'this week', 'last week', 'yesterday', 'YYYY-MM-DD to YYYY-MM-DD'"
        )
    
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


def get_week_number(date_str: str) -> str:
    """
    Get ISO week number (YYYY-Www) for a date.
    
    Args:
        date_str: Date in YYYY-MM-DD format
    
    Returns:
        Week number in YYYY-Www format (e.g., "2025-W47")
    """
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    # Use %W for week number (Monday as first day of week)
    return dt.strftime("%Y-W%W")


def get_cached_activity(week_number: str) -> Optional[Dict]:
    """
    Retrieve cached activity data for a week.
    
    Args:
        week_number: Week in YYYY-Www format
    
    Returns:
        Cached activity data if fresh (< CACHE_MAX_AGE_HOURS old), None otherwise
    """
    cache_file = os.path.join(ACTIVITY_DIR, f"{week_number}.json")
    
    if not os.path.exists(cache_file):
        return None
    
    # Check cache age
    cache_mtime = os.path.getmtime(cache_file)
    cache_age_hours = (datetime.now().timestamp() - cache_mtime) / 3600
    
    if cache_age_hours > CACHE_MAX_AGE_HOURS:
        # Cache is stale
        return None
    
    # Load and return cached data
    try:
        with open(cache_file, 'r') as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        print(f"Warning: Error reading cache file {cache_file}: {e}", file=sys.stderr)
        return None


def cache_activity(week_number: str, data: Dict) -> None:
    """
    Cache activity data for a week.
    
    Args:
        week_number: Week in YYYY-Www format
        data: Activity data to cache
    """
    cache_file = os.path.join(ACTIVITY_DIR, f"{week_number}.json")
    
    try:
        with open(cache_file, 'w') as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        print(f"Warning: Error writing cache file {cache_file}: {e}", file=sys.stderr)


@mcp.tool()
def get_github_activity(
    start_date: str,
    end_date: str,
    username: str = None
) -> Dict:
    """
    Fetch GitHub activity for a user in the given date range.
    
    Queries GitHub API for:
    - PRs created by user
    - PRs reviewed by user
    - Commits authored by user
    - Issues created by user
    - Issue comments posted by user
    
    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        username: GitHub username (defaults to GITHUB_USERNAME from env)
    
    Returns:
        Dict with GitHub activities:
        {
            "username": str,
            "period": {"start": str, "end": str},
            "commits": [{"repo": str, "sha": str, "message": str, "date": str}, ...],
            "prs_created": [{"repo": str, "number": int, "title": str, "state": str}, ...],
            "prs_reviewed": [{"repo": str, "number": int, "title": str, "comments": int}, ...],
            "issues_created": [...],
            "issues_commented": [...]
        }
    """
    if username is None:
        username = GITHUB_USERNAME
    
    if not GITHUB_TOKEN:
        return {
            "error": "GITHUB_TOKEN not configured",
            "username": username,
            "period": {"start": start_date, "end": end_date}
        }
    
    headers = {
        'Authorization': f'Bearer {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28'
    }
    
    result = {
        "username": username,
        "period": {"start": start_date, "end": end_date},
        "commits": [],
        "prs_created": [],
        "prs_reviewed": [],
        "issues_created": [],
        "issues_commented": []
    }
    
    try:
        # Query 1: PRs created by user
        prs_query = f"author:{username} type:pr created:{start_date}..{end_date}"
        prs_response = requests.get(
            'https://api.github.com/search/issues',
            headers=headers,
            params={'q': prs_query, 'per_page': 100}
        )
        prs_response.raise_for_status()
        prs_data = prs_response.json()
        
        for pr in prs_data.get('items', []):
            repo_full_name = pr['repository_url'].split('/')[-2:]
            result['prs_created'].append({
                'repo': '/'.join(repo_full_name),
                'number': pr['number'],
                'title': pr['title'],
                'state': pr['state'],
                'created_at': pr['created_at'],
                'url': pr['html_url']
            })
        
        # Query 2: PRs reviewed by user
        # Note: GitHub search doesn't directly support "reviewed-by", so we use a workaround
        # Get user's recent events and filter for review events
        events_response = requests.get(
            f'https://api.github.com/users/{username}/events',
            headers=headers,
            params={'per_page': 100}
        )
        events_response.raise_for_status()
        events_data = events_response.json()
        
        reviewed_prs = {}
        for event in events_data:
            # Filter for PullRequestReviewEvent and PullRequestReviewCommentEvent
            if event['type'] in ['PullRequestReviewEvent', 'PullRequestReviewCommentEvent']:
                event_date = datetime.fromisoformat(event['created_at'].replace('Z', '+00:00'))
                if start_date <= event_date.strftime('%Y-%m-%d') <= end_date:
                    pr = event['payload'].get('pull_request', {})
                    if pr:
                        pr_key = f"{pr.get('base', {}).get('repo', {}).get('full_name', '')}#{pr.get('number', '')}"
                        if pr_key not in reviewed_prs:
                            reviewed_prs[pr_key] = {
                                'repo': pr.get('base', {}).get('repo', {}).get('full_name', ''),
                                'number': pr.get('number', 0),
                                'title': pr.get('title', ''),
                                'comments': 1,
                                'url': pr.get('html_url', '')
                            }
                        else:
                            reviewed_prs[pr_key]['comments'] += 1
        
        result['prs_reviewed'] = list(reviewed_prs.values())
        
        # Query 3: Commits by user
        # Note: GitHub commit search requires special header
        commits_query = f"author:{username} committer-date:{start_date}..{end_date}"
        commits_response = requests.get(
            'https://api.github.com/search/commits',
            headers={**headers, 'Accept': 'application/vnd.github.cloak-preview+json'},
            params={'q': commits_query, 'per_page': 100}
        )
        commits_response.raise_for_status()
        commits_data = commits_response.json()
        
        for commit in commits_data.get('items', []):
            result['commits'].append({
                'repo': commit['repository']['full_name'],
                'sha': commit['sha'][:7],
                'message': commit['commit']['message'].split('\n')[0],  # First line only
                'date': commit['commit']['committer']['date'],
                'url': commit['html_url']
            })
        
        # Query 4: Issues created
        issues_query = f"author:{username} type:issue created:{start_date}..{end_date}"
        issues_response = requests.get(
            'https://api.github.com/search/issues',
            headers=headers,
            params={'q': issues_query, 'per_page': 100}
        )
        issues_response.raise_for_status()
        issues_data = issues_response.json()
        
        for issue in issues_data.get('items', []):
            repo_full_name = issue['repository_url'].split('/')[-2:]
            result['issues_created'].append({
                'repo': '/'.join(repo_full_name),
                'number': issue['number'],
                'title': issue['title'],
                'state': issue['state'],
                'created_at': issue['created_at'],
                'url': issue['html_url']
            })
        
    except requests.exceptions.RequestException as e:
        result['error'] = f"GitHub API error: {str(e)}"
    
    return result


@mcp.tool()
def get_opendev_activity(
    start_date: str,
    end_date: str,
    username: str = None
) -> Dict:
    """
    Fetch OpenDev review activity for a user in the given date range.
    
    Queries Gerrit API for:
    - Reviews posted (changes authored)
    - Comments posted
    - Votes given (Code-Review, Workflow)
    - Reviews received (changes where user was reviewer)
    
    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        username: OpenDev username (defaults to OPENDEV_USERNAME from env)
    
    Returns:
        Dict with OpenDev activities:
        {
            "username": str,
            "period": {"start": str, "end": str},
            "reviews_posted": [{"number": int, "subject": str, "project": str, ...}, ...],
            "comments_posted": [...],
            "votes_given": [...],
            "reviews_received": [...]
        }
    """
    if username is None:
        username = OPENDEV_USERNAME
    
    base_url = "https://review.opendev.org"
    
    result = {
        "username": username,
        "period": {"start": start_date, "end": end_date},
        "reviews_posted": [],
        "comments_posted": [],
        "votes_given": [],
        "reviews_received": []
    }
    
    try:
        # Query 1: Changes authored by user in date range
        owner_query = f"owner:{username} after:{start_date} before:{end_date}"
        owner_response = requests.get(
            f'{base_url}/changes/',
            params={'q': owner_query, 'o': 'DETAILED_ACCOUNTS'}
        )
        owner_response.raise_for_status()
        
        # Strip XSSI protection prefix
        owner_data_text = owner_response.text
        if owner_data_text.startswith(")]}'\n"):
            owner_data_text = owner_data_text[5:]
        owner_data = json.loads(owner_data_text)
        
        for change in owner_data:
            result['reviews_posted'].append({
                'number': change.get('_number', 0),
                'subject': change.get('subject', ''),
                'project': change.get('project', ''),
                'status': change.get('status', ''),
                'created': change.get('created', ''),
                'updated': change.get('updated', ''),
                'owner': username,  # This is from owner query, so owner is the user
                'url': f"{base_url}/c/{change.get('project', '')}/+/{change.get('_number', 0)}"
            })
        
        # Query 2: Changes reviewed by user (where they voted or commented)
        reviewer_query = f"reviewer:{username} after:{start_date}"
        reviewer_response = requests.get(
            f'{base_url}/changes/',
            params={'q': reviewer_query, 'o': ['DETAILED_ACCOUNTS', 'MESSAGES', 'ALL_REVISIONS', 'LABELS']}
        )
        reviewer_response.raise_for_status()
        
        # Strip XSSI protection prefix
        reviewer_data_text = reviewer_response.text
        if reviewer_data_text.startswith(")]}'\n"):
            reviewer_data_text = reviewer_data_text[5:]
        reviewer_data = json.loads(reviewer_data_text)
        
        # Extract comments and votes
        for change in reviewer_data:
            change_number = change.get('_number', 0)
            
            # Look through messages for comments by our user
            for message in change.get('messages', []):
                if message.get('author', {}).get('username', '') == username:
                    message_date = message.get('date', '')[:10]  # YYYY-MM-DD
                    if start_date <= message_date <= end_date:
                        result['comments_posted'].append({
                            'review': change_number,
                            'project': change.get('project', ''),
                            'subject': change.get('subject', ''),
                            'message': message.get('message', '')[:100],  # Preview only
                            'date': message.get('date', ''),
                            'url': f"{base_url}/c/{change.get('project', '')}/+/{change_number}"
                        })
            
            # Look through labels for votes by our user
            labels = change.get('labels', {})
            for label_name, label_data in labels.items():
                for vote in label_data.get('all', []):
                    if vote.get('username', '') == username:
                        vote_date = vote.get('date', '')[:10] if 'date' in vote else ''
                        if vote_date and start_date <= vote_date <= end_date:
                            result['votes_given'].append({
                                'review': change_number,
                                'project': change.get('project', ''),
                                'subject': change.get('subject', ''),
                                'label': label_name,
                                'value': vote.get('value', 0),
                                'date': vote.get('date', ''),
                                'url': f"{base_url}/c/{change.get('project', '')}/+/{change_number}"
                            })
        
    except requests.exceptions.RequestException as e:
        result['error'] = f"OpenDev API error: {str(e)}"
    except json.JSONDecodeError as e:
        result['error'] = f"OpenDev API JSON parse error: {str(e)}"
    
    return result


@mcp.tool()
def get_gitlab_activity(
    start_date: str,
    end_date: str,
    username: str = None
) -> Dict:
    """
    Fetch GitLab activity for a user in the given date range.
    
    Queries GitLab API for:
    - Merge requests created by user
    - Merge requests reviewed by user  
    - Commits authored by user
    - Issues created by user
    - Issue comments posted by user
    
    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        username: GitLab username (defaults to GITLAB_USERNAME from env)
    
    Returns:
        Dict with GitLab activities:
        {
            "username": str,
            "period": {"start": str, "end": str},
            "mrs_created": [{"project": str, "iid": int, "title": str, "state": str}, ...],
            "mrs_reviewed": [{"project": str, "iid": int, "title": str, "comments": int}, ...],
            "commits": [{"project": str, "sha": str, "message": str, "date": str}, ...],
            "issues_created": [...],
            "issues_commented": [...]
        }
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
        "mrs_created": [],
        "mrs_reviewed": [],
        "commits": [],
        "issues_created": [],
        "issues_commented": []
    }
    
    try:
        # Get user ID first
        user_response = requests.get(
            f'{GITLAB_URL}/api/v4/users',
            headers=headers,
            params={'username': username}
        )
        user_response.raise_for_status()
        users = user_response.json()
        
        if not users:
            result['error'] = f"User '{username}' not found"
            return result
        
        user_id = users[0]['id']
        
        # Query 1: Merge requests created by user
        mrs_response = requests.get(
            f'{GITLAB_URL}/api/v4/merge_requests',
            headers=headers,
            params={
                'author_id': user_id,
                'created_after': f"{start_date}T00:00:00Z",
                'created_before': f"{end_date}T23:59:59Z",
                'per_page': 100
            }
        )
        mrs_response.raise_for_status()
        
        for mr in mrs_response.json():
            result['mrs_created'].append({
                'project': mr.get('references', {}).get('full', ''),
                'iid': mr['iid'],
                'title': mr['title'],
                'state': mr['state'],
                'created_at': mr['created_at'],
                'url': mr['web_url']
            })
        
        # Query 2: User events for reviews/comments
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
        
        reviewed_mrs = {}
        for event in events_response.json():
            event_date = event.get('created_at', '')[:10]
            if not (start_date <= event_date <= end_date):
                continue
                
            # Track MR reviews (comments on MRs)
            if event.get('action_name') == 'commented on' and event.get('target_type') == 'MergeRequest':
                target = event.get('target', {})
                mr_key = f"{target.get('project_id')}!{target.get('iid')}"
                if mr_key not in reviewed_mrs:
                    reviewed_mrs[mr_key] = {
                        'project': target.get('references', {}).get('full', ''),
                        'iid': target.get('iid', 0),
                        'title': target.get('title', ''),
                        'comments': 1,
                        'url': target.get('web_url', '')
                    }
                else:
                    reviewed_mrs[mr_key]['comments'] += 1
            
            # Track issue comments
            if event.get('action_name') == 'commented on' and event.get('target_type') == 'Issue':
                target = event.get('target', {})
                result['issues_commented'].append({
                    'project': target.get('references', {}).get('full', ''),
                    'iid': target.get('iid', 0),
                    'title': target.get('title', ''),
                    'date': event_date,
                    'url': target.get('web_url', '')
                })
        
        result['mrs_reviewed'] = list(reviewed_mrs.values())
        
        # Query 3: Issues created
        issues_response = requests.get(
            f'{GITLAB_URL}/api/v4/issues',
            headers=headers,
            params={
                'author_id': user_id,
                'created_after': f"{start_date}T00:00:00Z",
                'created_before': f"{end_date}T23:59:59Z",
                'per_page': 100
            }
        )
        issues_response.raise_for_status()
        
        for issue in issues_response.json():
            result['issues_created'].append({
                'project': issue.get('references', {}).get('full', ''),
                'iid': issue['iid'],
                'title': issue['title'],
                'state': issue['state'],
                'created_at': issue['created_at'],
                'url': issue['web_url']
            })
        
        # Query 4: Commits (limited, as this can be large)
        # Note: GitLab API doesn't have a direct "all commits by user" endpoint
        # We'll skip this for now or implement via projects if needed
        
    except requests.exceptions.RequestException as e:
        result['error'] = f"GitLab API error: {str(e)}"
    
    return result


@mcp.tool()
def get_jira_activity(
    start_date: str,
    end_date: str,
    email: str = None
) -> Dict:
    """
    Fetch Jira activity for a user in the given date range.
    
    Queries Jira API for:
    - Issues created by user
    - Issues assigned to user
    - Issues resolved by user
    - Comments posted by user
    
    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        email: Jira user email (defaults to JIRA_EMAIL from env)
    
    Returns:
        Dict with Jira activities:
        {
            "email": str,
            "period": {"start": str, "end": str},
            "issues_created": [{"key": str, "summary": str, "type": str, "status": str}, ...],
            "issues_assigned": [...],
            "issues_resolved": [...],
            "comments_posted": [...]
        }
    """
    if email is None:
        email = JIRA_EMAIL
    
    if not JIRA_API_TOKEN or not JIRA_URL:
        return {
            "error": "JIRA_API_TOKEN or JIRA_URL not configured",
            "email": email,
            "period": {"start": start_date, "end": end_date}
        }
    
    result = {
        "email": email,
        "period": {"start": start_date, "end": end_date},
        "issues_created": [],
        "issues_assigned": [],
        "issues_resolved": [],
        "comments_posted": []
    }
    
    try:
        # Initialize JIRA client with token_auth (same as jira-agent)
        jira_client = JIRA(server=JIRA_URL, token_auth=JIRA_API_TOKEN)
        
        # Query 1: Issues created by user (in the date range)
        created_jql = f'creator = "{email}" AND created >= "{start_date}" AND created <= "{end_date}"'
        created_issues = jira_client.search_issues(
            created_jql,
            maxResults=100,
            fields='key,summary,issuetype,status,priority,created,updated'
        )
        
        for issue in created_issues:
            result['issues_created'].append({
                'key': issue.key,
                'summary': issue.fields.summary,
                'type': issue.fields.issuetype.name,
                'status': issue.fields.status.name,
                'priority': issue.fields.priority.name if hasattr(issue.fields, 'priority') and issue.fields.priority else 'None',
                'created_at': issue.fields.created,
                'updated_at': issue.fields.updated,
                'created': issue.fields.created[:10] if issue.fields.created else 'N/A',
                'url': f"{JIRA_URL}/browse/{issue.key}"
            })
        
        # Query 2: Issues assigned to user (ALL assigned, not just updated in period)
        # This query fetches all issues assigned to user for ownership tracking
        assigned_jql = f'assignee = "{email}" AND status not in (Done, Closed, Resolved) ORDER BY updated DESC'
        assigned_issues = jira_client.search_issues(
            assigned_jql,
            maxResults=100,
            fields='key,summary,issuetype,status,priority,created,updated'
        )
        
        for issue in assigned_issues:
            result['issues_assigned'].append({
                'key': issue.key,
                'summary': issue.fields.summary,
                'type': issue.fields.issuetype.name,
                'status': issue.fields.status.name,
                'priority': issue.fields.priority.name if hasattr(issue.fields, 'priority') and issue.fields.priority else 'None',
                'created_at': issue.fields.created,
                'updated_at': issue.fields.updated,
                'created': issue.fields.created[:10] if issue.fields.created else 'N/A',
                'updated': issue.fields.updated[:10] if issue.fields.updated else 'N/A',
                'url': f"{JIRA_URL}/browse/{issue.key}"
            })
        
        # Query 3: Issues resolved by user (in the date range)
        resolved_jql = f'assignee = "{email}" AND resolved >= "{start_date}" AND resolved <= "{end_date}"'
        resolved_issues = jira_client.search_issues(
            resolved_jql,
            maxResults=100,
            fields='key,summary,issuetype,status,priority,created,resolutiondate'
        )
        
        for issue in resolved_issues:
            resolutiondate = getattr(issue.fields, 'resolutiondate', None)
            result['issues_resolved'].append({
                'key': issue.key,
                'summary': issue.fields.summary,
                'type': issue.fields.issuetype.name,
                'status': issue.fields.status.name,
                'priority': issue.fields.priority.name if hasattr(issue.fields, 'priority') and issue.fields.priority else 'None',
                'created_at': issue.fields.created,
                'resolved_at': resolutiondate if resolutiondate else '',
                'resolved': resolutiondate[:10] if resolutiondate else 'N/A',
                'url': f"{JIRA_URL}/browse/{issue.key}"
            })
        
        # Note: Comments query would require iterating through issues and checking comment authors
        # This can be added if needed, but may be API-intensive
        
    except Exception as e:
        result['error'] = f"Jira API error: {str(e)}"
    
    return result


@mcp.tool()
def generate_status_report(
    time_range: str = "last week",
    format: str = "markdown"
) -> str:
    """
    Generate a status report for the given time range.
    
    Combines GitHub, OpenDev, GitLab, and Jira activities, caches data,
    and formats according to the specified format.
    
    Args:
        time_range: Time range string (e.g., "this week", "last week", "YYYY-MM-DD to YYYY-MM-DD")
        format: Output format ("markdown" or "json")
    
    Returns:
        Formatted status report
    """
    try:
        # Parse date range
        start_date, end_date = parse_date_range(time_range)
        week_number = get_week_number(start_date)
        
        # Check cache
        cached_data = get_cached_activity(week_number)
        
        if cached_data:
            github_data = cached_data.get('github', {})
            opendev_data = cached_data.get('opendev', {})
            gitlab_data = cached_data.get('gitlab', {})
            jira_data = cached_data.get('jira', {})
            print(f"Using cached data for week {week_number}", file=sys.stderr)
        else:
            # Fetch fresh data
            print(f"Fetching fresh data for {start_date} to {end_date}...", file=sys.stderr)
            github_data = get_github_activity(start_date, end_date)
            opendev_data = get_opendev_activity(start_date, end_date)
            gitlab_data = get_gitlab_activity(start_date, end_date)
            jira_data = get_jira_activity(start_date, end_date)
            
            # Cache it
            cache_data = {
                'github': github_data,
                'opendev': opendev_data,
                'gitlab': gitlab_data,
                'jira': jira_data,
                'generated_at': datetime.now().isoformat()
            }
            cache_activity(week_number, cache_data)
            print(f"Cached data to {week_number}.json", file=sys.stderr)
        
        # Format report
        if format == "json":
            return json.dumps({
                'github': github_data,
                'opendev': opendev_data,
                'gitlab': gitlab_data,
                'jira': jira_data
            }, indent=2)
        else:
            # Generate markdown report with activity tables
            report_lines = []
            report_lines.append(f"# Status Report: Week {week_number}")
            report_lines.append("")
            report_lines.append(f"**Period**: {start_date} to {end_date}  ")
            report_lines.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report_lines.append("")
            report_lines.append("---")
            report_lines.append("")
            
            # Helper functions for report generation
            def days_since_update(date_str):
                """Calculate days since last update"""
                try:
                    if not date_str:
                        return "N/A"
                    update_date = date_parser.parse(date_str)
                    now = datetime.now(update_date.tzinfo) if update_date.tzinfo else datetime.now()
                    delta = now - update_date
                    return str(delta.days)
                except:
                    return "N/A"
            
            def get_status_icon(status):
                """Get appropriate status icon based on status text"""
                status_lower = status.lower()
                if 'in progress' in status_lower or 'progress' in status_lower:
                    return "🟡"
                elif 'review' in status_lower:
                    return "🟢"
                elif 'backlog' in status_lower or 'planning' in status_lower or 'new' in status_lower:
                    return "🟢"
                elif 'done' in status_lower or 'closed' in status_lower or 'resolved' in status_lower or 'merged' in status_lower:
                    return "🟣"
                else:
                    return "🟢"  # Default to green
            
            # Summary - Activity Tables format
            report_lines.append("## 📊 Activity Summary")
            report_lines.append("")
            gh_prs_created = len(github_data.get('prs_created', []))
            gh_prs_reviewed = len(github_data.get('prs_reviewed', []))
            gh_commits = len(github_data.get('commits', []))
            gh_issues = len(github_data.get('issues_created', []))
            
            od_reviews = len(opendev_data.get('reviews_posted', []))
            od_comments = len(opendev_data.get('comments_posted', []))
            od_votes = len(opendev_data.get('votes_given', []))
            
            gl_mrs_created = len(gitlab_data.get('mrs_created', []))
            gl_mrs_reviewed = len(gitlab_data.get('mrs_reviewed', []))
            gl_issues = len(gitlab_data.get('issues_created', []))
            gl_comments = len(gitlab_data.get('issues_commented', []))
            
            jira_created = len(jira_data.get('issues_created', []))
            jira_resolved = len(jira_data.get('issues_resolved', []))
            jira_assigned = len(jira_data.get('issues_assigned', []))
            
            # Track merged reviews owned by user for "Other" column
            merged_reviews = []
            for review in opendev_data.get('reviews_posted', []):
                if review.get('status') == 'MERGED':
                    merged_reviews.append(review)
            
            # Build "Other" column content
            gh_other = "-"
            od_other = "-"
            total_other = "-"
            
            if merged_reviews:
                # Format: "X merged: [review](url) description"
                merged_count = len(merged_reviews)
                if merged_count == 1:
                    review = merged_reviews[0]
                    description = review['subject'][:50] + '...' if len(review['subject']) > 50 else review['subject']
                    od_other = f"{merged_count} merged: [{review['number']}]({review['url']}) {description}"
                else:
                    # Multiple merged reviews
                    merged_links = []
                    for review in merged_reviews[:3]:  # Show first 3
                        merged_links.append(f"[{review['number']}]({review['url']})")
                    od_other = f"{merged_count} merged: " + ", ".join(merged_links)
                    if merged_count > 3:
                        od_other += f" (+{merged_count - 3} more)"
                
                total_other = f"**{merged_count} merged**"
            
            report_lines.append("| Platform | PRs/MRs/Reviews | Comments | Commits | Issues | Votes/Resolved | Other |")
            report_lines.append("|----------|-----------------|----------|---------|--------|----------------|-------|")
            report_lines.append(f"| **GitHub** | {gh_prs_created} | {gh_prs_reviewed} reviews | {gh_commits} | {gh_issues} | 0 | {gh_other} |")
            report_lines.append(f"| **OpenDev** | {od_reviews} new | {od_comments} | 0 | 0 | {od_votes} | {od_other} |")
            gl_other = f"{gl_mrs_created} MRs" if gl_mrs_created > 0 else "-"
            report_lines.append(f"| **GitLab** | {gl_mrs_created} | {gl_mrs_reviewed + gl_comments} | 0 | {gl_issues} | 0 | {gl_other} |")
            jira_other = f"{jira_resolved} resolved" if jira_resolved > 0 else "-"
            report_lines.append(f"| **Jira** | 0 | 0 | 0 | {jira_created} | {jira_resolved} | {jira_other} |")
            total_prs = gh_prs_created + od_reviews + gl_mrs_created
            total_comments = gh_prs_reviewed + od_comments + gl_mrs_reviewed + gl_comments
            total_issues = gh_issues + gl_issues + jira_created
            report_lines.append(f"| **Total** | **{total_prs}** | **{total_comments}** | **{gh_commits}** | **{total_issues}** | **{od_votes + jira_resolved}** | {total_other} |")
            report_lines.append("")
            report_lines.append("---")
            report_lines.append("")
            
            # GitHub Activity with tables
            report_lines.append("## 🔵 GitHub Activity")
            report_lines.append("")
            
            if gh_prs_created > 0:
                report_lines.append(f"### Pull Requests Created ({gh_prs_created})")
                report_lines.append("")
                report_lines.append("| Repository | PR | Title | Status | Created | Link |")
                report_lines.append("|------------|-----|-------|--------|---------|------|")
                for pr in github_data.get('prs_created', []):
                    status_icon = "🟢" if pr['state'] == 'open' else "🟣"
                    report_lines.append(f"| {pr['repo']} | [#{pr['number']}]({pr['url']}) | {pr['title']} | {status_icon} {pr['state'].upper()} | {pr['created_at'][:10]} | [View]({pr['url']}) |")
                report_lines.append("")
            
            if gh_prs_reviewed > 0:
                report_lines.append(f"### Pull Requests Reviewed ({gh_prs_reviewed})")
                report_lines.append("")
                report_lines.append("| Repository | PR | Title | Comments | Link |")
                report_lines.append("|------------|-----|-------|----------|------|")
                for pr in github_data.get('prs_reviewed', []):
                    report_lines.append(f"| {pr['repo']} | [#{pr['number']}]({pr['url']}) | {pr['title']} | {pr['comments']} | [View]({pr['url']}) |")
                report_lines.append("")
            
            if gh_commits > 0:
                report_lines.append(f"### Commits ({gh_commits})")
                report_lines.append("")
                report_lines.append("| Repository | SHA | Message | Date | Link |")
                report_lines.append("|------------|-----|---------|------|------|")
                for commit in github_data.get('commits', [])[:20]:  # Limit to first 20
                    report_lines.append(f"| {commit['repo']} | `{commit['sha']}` | {commit['message']} | {commit['date'][:10]} | [View]({commit['url']}) |")
                if gh_commits > 20:
                    report_lines.append("")
                    report_lines.append(f"_... and {gh_commits - 20} more commits_")
                report_lines.append("")
            
            if gh_issues > 0:
                report_lines.append(f"### Issues Created ({gh_issues})")
                report_lines.append("")
                report_lines.append("| Repository | Issue | Title | Status | Created | Link |")
                report_lines.append("|------------|-------|-------|--------|---------|------|")
                for issue in github_data.get('issues_created', []):
                    status_icon = "🟢" if issue['state'] == 'open' else "🟣"
                    report_lines.append(f"| {issue['repo']} | [#{issue['number']}]({issue['url']}) | {issue['title']} | {status_icon} {issue['state'].upper()} | {issue['created_at'][:10]} | [View]({issue['url']}) |")
                report_lines.append("")
            
            if not any([gh_prs_created, gh_prs_reviewed, gh_commits, gh_issues]):
                report_lines.append("_No GitHub activity in this period_")
                report_lines.append("")
            
            report_lines.append("---")
            report_lines.append("")
            
            # OpenDev Activity with tables
            report_lines.append("## 🟠 OpenDev Activity")
            report_lines.append("")
            
            if od_reviews > 0:
                report_lines.append(f"### Reviews Posted ({od_reviews})")
                report_lines.append("")
                report_lines.append("| Review | Owner | Project | Description | Status | Created | Latest |")
                report_lines.append("|--------|-------|---------|-------------|--------|---------|--------|")
                for review in opendev_data.get('reviews_posted', []):
                    status_icon = "🟢" if review['status'] == 'NEW' else "🟣" if review['status'] == 'MERGED' else "🔴"
                    # Truncate subject to ~60 chars for description
                    description = review['subject'][:60] + '...' if len(review['subject']) > 60 else review['subject']
                    
                    # Format status with merge date if merged
                    if review['status'] == 'MERGED':
                        merge_date = review.get('updated', '')[:10]  # Use updated date as merge date
                        status_display = f"{status_icon} **MERGED** ({merge_date})"
                    elif review['status'] == 'ABANDONED':
                        status_display = f"{status_icon} ABANDONED"
                    else:  # NEW or other
                        status_display = f"{status_icon} {review['status']}"
                    
                    owner = review.get('owner', opendev_data.get('username', ''))
                    
                    # Latest patchset link would need revision data - use review link for now
                    report_lines.append(f"| [{review['number']}]({review['url']}) | {owner} | {review['project']} | {description} | {status_display} | {review['created'][:10]} | [View]({review['url']}) |")
                report_lines.append("")
            
            if od_comments > 0 or od_votes > 0:
                report_lines.append(f"### Activity Timeline ({od_comments} comments, {od_votes} votes)")
                report_lines.append("")
                
                # Combine and sort by date
                combined = []
                for comment in opendev_data.get('comments_posted', []):
                    combined.append(('comment', comment))
                for vote in opendev_data.get('votes_given', []):
                    combined.append(('vote', vote))
                combined.sort(key=lambda x: x[1].get('date', ''), reverse=True)
                
                report_lines.append("| Date | Review | Project | Action | Details | Link |")
                report_lines.append("|------|--------|---------|--------|---------|------|")
                
                for item_type, item in combined[:20]:  # Limit to first 20
                    date_str = item.get('date', '')[:10] if item.get('date') else 'N/A'
                    if item_type == 'comment':
                        message_preview = item['message'][:60].replace('\n', ' ').replace('|', '\\|')
                        report_lines.append(f"| {date_str} | [{item['review']}]({item['url']}) | {item['project']} | 💬 Comment | {message_preview}... | [View]({item['url']}) |")
                    else:  # vote
                        vote_emoji = "✅" if item['value'] > 0 else "❌" if item['value'] < 0 else "💬"
                        report_lines.append(f"| {date_str} | [{item['review']}]({item['url']}) | {item['project']} | {vote_emoji} Vote | {item['label']} {item['value']:+d} | [View]({item['url']}) |")
                
                if len(combined) > 20:
                    report_lines.append("")
                    report_lines.append(f"_... and {len(combined) - 20} more comments/votes_")
                report_lines.append("")
            
            if not any([od_reviews, od_comments, od_votes]):
                report_lines.append("_No OpenDev activity in this period_")
                report_lines.append("")
            
            report_lines.append("---")
            report_lines.append("")
            
            # GitLab Activity with tables
            report_lines.append("## 🦊 GitLab Activity")
            report_lines.append("")
            
            if gl_mrs_created > 0:
                report_lines.append(f"### Merge Requests Created ({gl_mrs_created})")
                report_lines.append("")
                report_lines.append("| Project | MR | Title | Status | Created | Link |")
                report_lines.append("|---------|-----|-------|--------|---------|------|")
                for mr in gitlab_data.get('mrs_created', []):
                    status_icon = "🟢" if mr['state'] == 'opened' else "🟣" if mr['state'] == 'merged' else "🔴"
                    report_lines.append(f"| {mr['project']} | [!{mr['iid']}]({mr['url']}) | {mr['title']} | {status_icon} {mr['state'].upper()} | {mr['created_at'][:10]} | [View]({mr['url']}) |")
                report_lines.append("")
            
            if gl_mrs_reviewed > 0:
                report_lines.append(f"### Merge Requests Reviewed ({gl_mrs_reviewed})")
                report_lines.append("")
                report_lines.append("| Project | MR | Title | Comments | Link |")
                report_lines.append("|---------|-----|-------|----------|------|")
                for mr in gitlab_data.get('mrs_reviewed', []):
                    report_lines.append(f"| {mr['project']} | [!{mr['iid']}]({mr['url']}) | {mr['title']} | {mr['comments']} | [View]({mr['url']}) |")
                report_lines.append("")
            
            if gl_issues > 0:
                report_lines.append(f"### Issues Created ({gl_issues})")
                report_lines.append("")
                report_lines.append("| Project | Issue | Title | Status | Created | Link |")
                report_lines.append("|---------|-------|-------|--------|---------|------|")
                for issue in gitlab_data.get('issues_created', []):
                    status_icon = "🟢" if issue['state'] == 'opened' else "🟣"
                    report_lines.append(f"| {issue['project']} | [#{issue['iid']}]({issue['url']}) | {issue['title']} | {status_icon} {issue['state'].upper()} | {issue['created_at'][:10]} | [View]({issue['url']}) |")
                report_lines.append("")
            
            if not any([gl_mrs_created, gl_mrs_reviewed, gl_issues]):
                report_lines.append("_No GitLab activity in this period_")
                report_lines.append("")
            
            report_lines.append("---")
            report_lines.append("")
            
            # Jira Activity with tables
            report_lines.append("## 📋 Jira Activity")
            report_lines.append("")
            
            if jira_created > 0:
                report_lines.append(f"### Issues Created ({jira_created})")
                report_lines.append("")
                report_lines.append("| Key | Summary | Type | Status | Created | Link |")
                report_lines.append("|-----|---------|------|--------|---------|------|")
                for issue in jira_data.get('issues_created', []):
                    status = issue.get('status', 'N/A')
                    status_icon = get_status_icon(status)
                    report_lines.append(f"| [{issue['key']}]({issue['url']}) | {issue['summary']} | {issue['type']} | {status_icon} {status} | {issue['created']} | [View]({issue['url']}) |")
                report_lines.append("")
            
            if jira_resolved > 0:
                report_lines.append(f"### Issues Resolved ({jira_resolved})")
                report_lines.append("")
                report_lines.append("| Key | Summary | Type | Status | Resolved | Link |")
                report_lines.append("|-----|---------|------|--------|----------|------|")
                for issue in jira_data.get('issues_resolved', []):
                    status = issue.get('status', 'N/A')
                    status_icon = get_status_icon(status)
                    report_lines.append(f"| [{issue['key']}]({issue['url']}) | {issue['summary']} | {issue['type']} | {status_icon} {status} | {issue['resolved']} | [View]({issue['url']}) |")
                report_lines.append("")
            
            if jira_assigned > 0 and jira_assigned != jira_resolved:
                report_lines.append(f"### Issues Assigned/Updated ({jira_assigned})")
                report_lines.append("")
                report_lines.append("| Key | Summary | Type | Status | Updated | Link |")
                report_lines.append("|-----|---------|------|--------|---------|------|")
                for issue in jira_data.get('issues_assigned', []):
                    status = issue.get('status', 'N/A')
                    status_icon = get_status_icon(status)
                    report_lines.append(f"| [{issue['key']}]({issue['url']}) | {issue['summary']} | {issue['type']} | {status_icon} {status} | {issue['updated']} | [View]({issue['url']}) |")
                report_lines.append("")
            
            if not any([jira_created, jira_resolved, jira_assigned]):
                report_lines.append("_No Jira activity in this period_")
                report_lines.append("")
            
            report_lines.append("---")
            report_lines.append("")
            
            # Ownership sections - show all open/active items owned by user
            report_lines.append("---")
            report_lines.append("")
            report_lines.append("## 👤 Ownership Status")
            report_lines.append("")
            report_lines.append("_Items currently owned by you across all platforms_")
            report_lines.append("")
            
            # OpenDev Reviews Ownership
            report_lines.append("### 🟠 OpenDev: My Active Reviews")
            report_lines.append("")
            
            active_opendev_reviews = [
                r for r in opendev_data.get('reviews_posted', [])
                if r.get('status') not in ['MERGED', 'ABANDONED']
            ]
            
            if active_opendev_reviews:
                report_lines.append(f"**{len(active_opendev_reviews)} active review(s)**")
                report_lines.append("")
                report_lines.append("| Review | Project | Subject | Status | Created | Last Updated | Days Idle | Link |")
                report_lines.append("|--------|---------|---------|--------|---------|--------------|-----------|------|")
                for review in active_opendev_reviews:
                    review_num = review.get('number', 'N/A')
                    project = review.get('project', 'N/A').split('/')[-1] if review.get('project') else 'N/A'
                    subject = review.get('subject', 'N/A')
                    if len(subject) > 50:
                        subject = subject[:47] + '...'
                    status = review.get('status', 'N/A')
                    created = review.get('created', 'N/A')[:10] if review.get('created') else 'N/A'
                    updated = review.get('updated', 'N/A')[:10] if review.get('updated') else 'N/A'
                    days_idle = days_since_update(review.get('updated'))
                    url = review.get('url', '#')
                    
                    status_icon = "🟢" if status == "NEW" else "🟡"
                    report_lines.append(f"| [{review_num}]({url}) | {project} | {subject} | {status_icon} {status} | {created} | {updated} | {days_idle} | [View]({url}) |")
                report_lines.append("")
            else:
                report_lines.append("_No active reviews_")
                report_lines.append("")
            
            # GitHub PRs Ownership
            report_lines.append("### 🔵 GitHub: My Open PRs")
            report_lines.append("")
            
            open_github_prs = [
                pr for pr in github_data.get('prs_created', [])
                if pr.get('state') == 'open'
            ]
            
            if open_github_prs:
                report_lines.append(f"**{len(open_github_prs)} open PR(s)**")
                report_lines.append("")
                report_lines.append("| PR | Repository | Title | Status | Created | Last Updated | Days Idle | Link |")
                report_lines.append("|----|------------|-------|--------|---------|--------------|-----------|------|")
                for pr in open_github_prs:
                    pr_num = pr.get('number', 'N/A')
                    repo = pr.get('repo', 'N/A')
                    title = pr.get('title', 'N/A')
                    if len(title) > 50:
                        title = title[:47] + '...'
                    state = pr.get('state', 'N/A')
                    created = pr.get('created_at', 'N/A')[:10] if pr.get('created_at') else 'N/A'
                    updated = pr.get('updated_at', 'N/A')[:10] if pr.get('updated_at') else 'N/A'
                    days_idle = days_since_update(pr.get('updated_at'))
                    url = pr.get('html_url', '#')
                    
                    report_lines.append(f"| [#{pr_num}]({url}) | {repo} | {title} | 🟢 {state.upper()} | {created} | {updated} | {days_idle} | [View]({url}) |")
                report_lines.append("")
            else:
                report_lines.append("_No open PRs_")
                report_lines.append("")
            
            # GitLab MRs Ownership
            report_lines.append("### 🦊 GitLab: My Open MRs")
            report_lines.append("")
            
            open_gitlab_mrs = [
                mr for mr in gitlab_data.get('mrs_created', [])
                if mr.get('state') == 'opened'
            ]
            
            if open_gitlab_mrs:
                report_lines.append(f"**{len(open_gitlab_mrs)} open MR(s)**")
                report_lines.append("")
                report_lines.append("| MR | Project | Title | Status | Created | Last Updated | Days Idle | Link |")
                report_lines.append("|----|---------|-------|--------|---------|--------------|-----------|------|")
                for mr in open_gitlab_mrs:
                    mr_id = mr.get('id', 'N/A')
                    project = mr.get('project_name', 'N/A')
                    title = mr.get('title', 'N/A')
                    if len(title) > 50:
                        title = title[:47] + '...'
                    state = mr.get('state', 'N/A')
                    created = mr.get('created_at', 'N/A')[:10] if mr.get('created_at') else 'N/A'
                    updated = mr.get('updated_at', 'N/A')[:10] if mr.get('updated_at') else 'N/A'
                    days_idle = days_since_update(mr.get('updated_at'))
                    url = mr.get('url', '#')
                    
                    report_lines.append(f"| [!{mr_id}]({url}) | {project} | {title} | 🟢 {state.upper()} | {created} | {updated} | {days_idle} | [View]({url}) |")
                report_lines.append("")
            else:
                report_lines.append("_No open MRs_")
                report_lines.append("")
            
            # Jira Tickets Ownership - Open tickets
            report_lines.append("### 📋 Jira: My Open Tickets")
            report_lines.append("")
            
            open_jira_issues = [
                issue for issue in jira_data.get('issues_assigned', [])
                if issue.get('status') not in ['Done', 'Closed', 'Resolved']
            ]
            
            if open_jira_issues:
                report_lines.append(f"**{len(open_jira_issues)} open ticket(s)**")
                report_lines.append("")
                report_lines.append("| Ticket | Summary | Type | Status | Priority | Created | Last Updated | Days Idle | Link |")
                report_lines.append("|--------|---------|------|--------|----------|---------|--------------|-----------|------|")
                for issue in open_jira_issues:
                    key = issue.get('key', 'N/A')
                    summary = issue.get('summary', 'N/A')
                    if len(summary) > 40:
                        summary = summary[:37] + '...'
                    issue_type = issue.get('type', 'N/A')
                    status = issue.get('status', 'N/A')
                    priority = issue.get('priority', 'N/A')
                    created = issue.get('created_at', 'N/A')[:10] if issue.get('created_at') else 'N/A'
                    updated = issue.get('updated_at', 'N/A')[:10] if issue.get('updated_at') else 'N/A'
                    days_idle = days_since_update(issue.get('updated_at'))
                    url = issue.get('url', '#')
                    
                    status_icon = get_status_icon(status)
                    report_lines.append(f"| [{key}]({url}) | {summary} | {issue_type} | {status_icon} {status} | {priority} | {created} | {updated} | {days_idle} | [View]({url}) |")
                report_lines.append("")
            else:
                report_lines.append("_No open tickets_")
                report_lines.append("")
            
            # Jira Tickets Requiring Update - issues idle > 7 days
            report_lines.append("### 📋 Jira: Tickets Requiring Update")
            report_lines.append("")
            report_lines.append("_Tickets idle for more than 7 days_")
            report_lines.append("")
            
            stale_jira_issues = [
                issue for issue in jira_data.get('issues_assigned', [])
                if issue.get('status') not in ['Done', 'Closed', 'Resolved']
                and days_since_update(issue.get('updated_at')).isdigit()
                and int(days_since_update(issue.get('updated_at'))) > 7
            ]
            
            if stale_jira_issues:
                report_lines.append(f"**{len(stale_jira_issues)} ticket(s) need attention**")
                report_lines.append("")
                report_lines.append("| Ticket | Summary | Type | Status | Priority | Created | Last Updated | Days Idle | Link |")
                report_lines.append("|--------|---------|------|--------|----------|---------|--------------|-----------|------|")
                for issue in stale_jira_issues:
                    key = issue.get('key', 'N/A')
                    summary = issue.get('summary', 'N/A')
                    if len(summary) > 40:
                        summary = summary[:37] + '...'
                    issue_type = issue.get('type', 'N/A')
                    status = issue.get('status', 'N/A')
                    priority = issue.get('priority', 'N/A')
                    created = issue.get('created_at', 'N/A')[:10] if issue.get('created_at') else 'N/A'
                    updated = issue.get('updated_at', 'N/A')[:10] if issue.get('updated_at') else 'N/A'
                    days_idle = days_since_update(issue.get('updated_at'))
                    url = issue.get('url', '#')
                    
                    # Red icon for stale items
                    status_icon = "🔴"
                    report_lines.append(f"| [{key}]({url}) | {summary} | {issue_type} | {status_icon} {status} | {priority} | {created} | {updated} | **{days_idle}** | [View]({url}) |")
                report_lines.append("")
            else:
                report_lines.append("_No tickets requiring immediate attention_")
                report_lines.append("")
            
            report_lines.append("---")
            report_lines.append("")
            
            # Footer sections
            report_lines.append("## 📝 Key Themes")
            report_lines.append("")
            report_lines.append("_To be filled by AI analysis based on activities above_")
            report_lines.append("")
            report_lines.append("## 🚧 Blockers")
            report_lines.append("")
            report_lines.append("_None identified in this period_")
            report_lines.append("")
            report_lines.append("---")
            report_lines.append("")
            report_lines.append(f"_Generated by mymcp activity-tracker on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_  ")
            report_lines.append(f"_Data cached at: `{week_number}.json` (this directory)_")
            
            report = "\n".join(report_lines)
            
            # Save report to workspace
            report_file = os.path.join(ACTIVITY_DIR, f"{week_number}_report.md")
            try:
                with open(report_file, 'w') as f:
                    f.write(report)
                print(f"Report saved to {report_file}", file=sys.stderr)
            except IOError as e:
                print(f"Warning: Could not save report to {report_file}: {e}", file=sys.stderr)
            
            return report
            
    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stdio":
        # Run as MCP server
        mcp.run()
    else:
        # CLI mode for testing
        print("Activity Tracker MCP Server")
        print("===========================")
        print()
        print("Testing generate_status_report('last week')...")
        print()
        print(generate_status_report("last week"))



