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
            repo_name = '/'.join(repo_full_name)
            pr_number = pr['number']
            
            # Fetch comments and reviews for complexity scoring
            comments = []
            reviews = []
            try:
                # Get PR comments
                comments_response = requests.get(
                    f'https://api.github.com/repos/{repo_name}/issues/{pr_number}/comments',
                    headers=headers,
                    params={'per_page': 100}
                )
                if comments_response.status_code == 200:
                    comments = comments_response.json()
                
                # Get PR reviews
                reviews_response = requests.get(
                    f'https://api.github.com/repos/{repo_name}/pulls/{pr_number}/reviews',
                    headers=headers,
                    params={'per_page': 100}
                )
                if reviews_response.status_code == 200:
                    reviews = reviews_response.json()
            except Exception as e:
                print(f"Warning: Could not fetch comments for PR {pr_number}: {e}", file=sys.stderr)
            
            result['prs_created'].append({
                'repo': repo_name,
                'number': pr_number,
                'title': pr['title'],
                'state': pr['state'],
                'created_at': pr['created_at'],
                'updated_at': pr.get('updated_at', ''),
                'url': pr['html_url'],
                'html_url': pr['html_url'],
                'comments': comments,
                'reviews': reviews
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
        # Include MESSAGES and ALL_REVISIONS for complexity scoring
        owner_query = f"owner:{username} after:{start_date} before:{end_date}"
        owner_response = requests.get(
            f'{base_url}/changes/',
            params={'q': owner_query, 'o': ['DETAILED_ACCOUNTS', 'MESSAGES', 'ALL_REVISIONS']}
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
                'url': f"{base_url}/c/{change.get('project', '')}/+/{change.get('_number', 0)}",
                'messages': change.get('messages', []),  # Include messages for complexity scoring
                'revisions': change.get('revisions', {})  # Include revisions for complexity scoring
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
            project_id = mr.get('project_id')
            mr_iid = mr['iid']
            
            # Fetch notes (comments) for complexity scoring
            notes = []
            try:
                notes_response = requests.get(
                    f'{GITLAB_URL}/api/v4/projects/{project_id}/merge_requests/{mr_iid}/notes',
                    headers=headers,
                    params={'per_page': 100}
                )
                if notes_response.status_code == 200:
                    notes = notes_response.json()
            except Exception as e:
                print(f"Warning: Could not fetch notes for MR {mr_iid}: {e}", file=sys.stderr)
            
            result['mrs_created'].append({
                'project': mr.get('references', {}).get('full', ''),
                'project_id': project_id,
                'iid': mr_iid,
                'title': mr['title'],
                'state': mr['state'],
                'created_at': mr['created_at'],
                'updated_at': mr.get('updated_at', ''),
                'url': mr['web_url'],
                'notes': notes
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


@mcp.tool()
def generate_in_progress_report() -> str:
    """
    Generate an "In Progress" report showing current ownership status.
    
    This report shows all open/active items owned by you across platforms:
    - OpenDev: Active reviews (not merged/abandoned)
    - GitHub: Open PRs
    - GitLab: Open MRs
    - Jira: Open tickets (and tickets requiring update)
    
    Always fetches fresh data (no caching) since this is current status.
    
    Returns:
        Markdown formatted in-progress report
    """
    try:
        print("Fetching fresh ownership data...", file=sys.stderr)
        
        # Fetch data for "all time" to get all open items
        # Use a very old start date to capture everything
        start_date = "2020-01-01"
        # Use tomorrow's date for end_date because Gerrit's "before:" is exclusive
        # and we want to include items updated today (especially for UTC timezone differences)
        end_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Fetch fresh data from all platforms
        github_data = get_github_activity(start_date, end_date)
        opendev_data = get_opendev_activity(start_date, end_date)
        gitlab_data = get_gitlab_activity(start_date, end_date)
        jira_data = get_jira_activity(start_date, end_date)
        
        # Helper functions
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
        
        def calculate_success_rating(days_tracked):
            """
            Calculate success rating based on days tracked.
            
            Rating System:
            - A+ : Completed in under 14 days (one 2-week sprint)
            - A  : Completed in under 28 days (two 2-week sprints)
            - B  : Completed in under 42 days (three 2-week sprints)
            - F  : Over 42 days (more than three sprints)
            """
            try:
                days = int(days_tracked) if days_tracked != 'N/A' else 999
            except (ValueError, TypeError):
                days = 999
            
            if days < 14:
                return 'A+'
            elif days < 28:
                return 'A'
            elif days < 42:
                return 'B'
            else:
                return 'F'
        
        def get_rating_emoji(rating):
            """Get emoji for rating display."""
            return {
                'A+': '🌟',
                'A': '✅',
                'B': '⚠️',
                'F': '🔴'
            }.get(rating, '❓')
        
        def calculate_complexity_score(item_data, item_type, my_username=None):
            """
            Calculate complexity score for an item.
            
            Scoring:
            - +1 for each comment (any commenter)
            - +1 for each unique reviewer who commented
            - +3 for each of MY comments
            - +2 bonus if my comment led to new patchset within 1 week
            
            Returns: (score, breakdown_dict)
            """
            score = 0
            breakdown = {
                'total_comments': 0,
                'unique_reviewers': 0,
                'my_comments': 0,
                'responsive_patchsets': 0
            }
            
            # For OpenDev reviews
            if item_type == 'opendev':
                messages = item_data.get('messages', [])
                revisions = item_data.get('revisions', {})
                
                # Count comments and unique reviewers
                reviewers = set()
                my_comments = 0
                
                for msg in messages:
                    author = msg.get('author', {}).get('username', '')
                    breakdown['total_comments'] += 1
                    score += 1  # +1 per comment
                    
                    if author and author != '_anonymous':
                        reviewers.add(author)
                    
                    # Check if this is my comment
                    if my_username and author == my_username:
                        my_comments += 1
                        score += 2  # +3 total for my comments (1 base + 2 bonus)
                
                breakdown['unique_reviewers'] = len(reviewers)
                score += len(reviewers)  # +1 per unique reviewer
                breakdown['my_comments'] = my_comments
                
                # Count patchsets (revisions)
                num_patchsets = len(revisions) if revisions else 1
                if num_patchsets > 1 and my_comments > 0:
                    # Simplified: assume responsive if multiple patchsets and I commented
                    responsive_bonus = min(my_comments, num_patchsets - 1)
                    breakdown['responsive_patchsets'] = responsive_bonus
                    score += responsive_bonus * 2  # +2 per responsive patchset
            
            # For Jira tickets
            elif item_type == 'jira':
                comments = item_data.get('comments', [])
                
                reviewers = set()
                my_comments = 0
                
                for comment in comments:
                    author = comment.get('author', '')
                    breakdown['total_comments'] += 1
                    score += 1
                    
                    if author:
                        reviewers.add(author)
                    
                    if my_username and author == my_username:
                        my_comments += 1
                        score += 2
                
                breakdown['unique_reviewers'] = len(reviewers)
                score += len(reviewers)
                breakdown['my_comments'] = my_comments
            
            # For GitLab MRs
            elif item_type == 'gitlab':
                notes = item_data.get('notes', [])
                
                reviewers = set()
                my_comments = 0
                
                for note in notes:
                    author = note.get('author', {}).get('username', '')
                    breakdown['total_comments'] += 1
                    score += 1
                    
                    if author:
                        reviewers.add(author)
                    
                    if my_username and author == my_username:
                        my_comments += 1
                        score += 2
                
                breakdown['unique_reviewers'] = len(reviewers)
                score += len(reviewers)
                breakdown['my_comments'] = my_comments
            
            # For GitHub PRs
            elif item_type == 'github':
                comments = item_data.get('comments', [])
                reviews = item_data.get('reviews', [])
                
                reviewers = set()
                my_comments = 0
                
                for comment in comments + reviews:
                    author = comment.get('user', {}).get('login', '')
                    breakdown['total_comments'] += 1
                    score += 1
                    
                    if author:
                        reviewers.add(author)
                    
                    if my_username and author == my_username:
                        my_comments += 1
                        score += 2
                
                breakdown['unique_reviewers'] = len(reviewers)
                score += len(reviewers)
                breakdown['my_comments'] = my_comments
            
            return score, breakdown
        
        def get_complexity_display(score):
            """Get display string for complexity score."""
            if score == 0:
                return "—"
            elif score <= 5:
                return f"{score} 🟢"  # Low complexity
            elif score <= 15:
                return f"{score} 🟡"  # Medium complexity
            elif score <= 30:
                return f"{score} 🟠"  # High complexity
            else:
                return f"{score} 🔴"  # Very high complexity
        
        def calculate_estimated_days(complexity_score):
            """
            Calculate estimated days to complete based on complexity score.
            
            Base time by complexity:
            - 0-5 (Low): 0.5 days
            - 6-15 (Medium): 1.5 days
            - 16-30 (High): 3 days
            - 31+ (Very High): 5 days
            
            Returns: (ai_assisted_days, manual_days)
            """
            if complexity_score <= 5:
                return (0.5, 1.5)
            elif complexity_score <= 15:
                return (1.5, 4.0)
            elif complexity_score <= 30:
                return (3.0, 8.0)
            else:
                return (5.0, 15.0)
        
        def calculate_priority(item_type, is_awaiting_review=False, has_fix_version=False, 
                               is_owned_by_me=False, days_tracked=0):
            """
            Calculate priority (P1-P4) for an item.
            
            P1: Blockers - Items blocking others (awaiting your review)
            P2: High - Your work with fix version set
            P3: Medium - Your own work items
            P4: Low - Everything else (watching, backlog)
            
            Returns: (priority_number, priority_label, reason)
            """
            if is_awaiting_review:
                return (1, "P1", "blocking others")
            elif has_fix_version and is_owned_by_me:
                return (2, "P2", "has fix version")
            elif is_owned_by_me:
                return (3, "P3", "your work")
            else:
                return (4, "P4", "watching/backlog")
        
        def calculate_target_date(first_seen_str, estimated_days):
            """
            Calculate target completion date.
            
            Target = first_seen + estimated_days (skipping weekends)
            
            Returns: target date string in YYYY-MM-DD format
            """
            try:
                if first_seen_str:
                    first_seen = datetime.strptime(first_seen_str, "%Y-%m-%d")
                else:
                    first_seen = datetime.now()
                
                # Add estimated days (simple approach - just add calendar days)
                # A more sophisticated version would skip weekends
                target = first_seen + timedelta(days=estimated_days)
                
                # If target is in the past, set to today + estimated_days
                if target < datetime.now():
                    target = datetime.now() + timedelta(days=estimated_days)
                
                return target.strftime("%Y-%m-%d")
            except:
                return (datetime.now() + timedelta(days=estimated_days)).strftime("%Y-%m-%d")
        
        def get_priority_display(priority_num):
            """Get display string for priority."""
            displays = {
                1: "🔴 P1",
                2: "🟠 P2",
                3: "🟡 P3",
                4: "🟢 P4"
            }
            return displays.get(priority_num, "P4")
        
        def load_tracking_history():
            """Load the tracking history file that persists first_seen dates."""
            history_file = os.path.join(ACTIVITY_DIR, "tracking_history.json")
            if os.path.exists(history_file):
                try:
                    with open(history_file, 'r') as f:
                        return json.load(f)
                except (json.JSONDecodeError, IOError):
                    pass
            return {'items': {}, 'quarterly_stats': [], 'last_quarter': None}
        
        def save_tracking_history(history):
            """Save the tracking history file with timestamped backup for verification."""
            history_file = os.path.join(ACTIVITY_DIR, "tracking_history.json")
            backup_dir = os.path.join(ACTIVITY_DIR, "tracking_backups")
            
            try:
                # Create backup directory if it doesn't exist
                os.makedirs(backup_dir, exist_ok=True)
                
                # Create timestamped backup of current file before overwriting
                if os.path.exists(history_file):
                    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
                    backup_file = os.path.join(backup_dir, f"tracking_history_{timestamp}.json")
                    
                    # Copy current file to backup
                    import shutil
                    shutil.copy2(history_file, backup_file)
                    print(f"Backup created: {backup_file}", file=sys.stderr)
                    
                    # Quick diff check: compare item counts
                    try:
                        with open(history_file, 'r') as f:
                            old_history = json.load(f)
                        old_items = len(old_history.get('items', {}))
                        new_items = len(history.get('items', {}))
                        old_completions = len(old_history.get('quarterly_stats', []))
                        new_completions = len(history.get('quarterly_stats', []))
                        
                        if old_items != new_items or old_completions != new_completions:
                            print(f"📊 Tracking changes: Items {old_items}→{new_items}, Completions {old_completions}→{new_completions}", file=sys.stderr)
                    except:
                        pass  # Don't fail if diff check fails
                    
                    # Cleanup old backups (keep last 14 days worth)
                    try:
                        cutoff_date = datetime.now() - timedelta(days=14)
                        for backup in os.listdir(backup_dir):
                            if backup.startswith('tracking_history_') and backup.endswith('.json'):
                                # Extract date from filename: tracking_history_2025-12-04_103000.json
                                date_str = backup.replace('tracking_history_', '').replace('.json', '').split('_')[0]
                                try:
                                    backup_date = datetime.strptime(date_str, '%Y-%m-%d')
                                    if backup_date < cutoff_date:
                                        os.remove(os.path.join(backup_dir, backup))
                                        print(f"Cleaned up old backup: {backup}", file=sys.stderr)
                                except:
                                    pass  # Skip files with unexpected naming
                    except Exception as e:
                        print(f"Warning: Could not cleanup old backups: {e}", file=sys.stderr)
                
                # Save the new history
                with open(history_file, 'w') as f:
                    json.dump(history, f, indent=2, default=str)
                    
            except IOError as e:
                print(f"Warning: Could not save tracking history: {e}", file=sys.stderr)
        
        def get_item_key(item_type, item_id):
            """Generate unique key for tracking an item."""
            return f"{item_type}:{item_id}"
        
        def update_tracking_history(history, current_items):
            """
            Update tracking history with current items.
            - Add first_seen for new items
            - Keep existing first_seen for known items
            """
            today = datetime.now().strftime('%Y-%m-%d')
            
            for item in current_items:
                key = get_item_key(item['type'], item['id'])
                if key not in history['items']:
                    # New item - record first_seen
                    history['items'][key] = {
                        'first_seen': today,
                        'type': item['type'],
                        'id': item['id'],
                        'title': item.get('title', item.get('subject', item.get('summary', 'N/A')))[:50],
                        'is_mine': item.get('is_mine', True)
                    }
            return history
        
        def record_completion(history, item, days_tracked, rating):
            """Record a completed item to quarterly stats."""
            today = datetime.now()
            quarter = f"{today.year}-Q{(today.month - 1) // 3 + 1}"
            
            completion_record = {
                'date': today.strftime('%Y-%m-%d'),
                'type': item.get('type', 'unknown'),
                'id': item.get('id', 'N/A'),
                'title': item.get('title', 'N/A')[:50],
                'owner': item.get('owner', 'N/A'),
                'credit_due': item.get('credit_due', ''),  # Reviewers who gave +1/+2
                'days_tracked': days_tracked,
                'rating': rating,
                'is_mine': item.get('is_mine', True),
                'quarter': quarter
            }
            
            history['quarterly_stats'].append(completion_record)
            
            # Clean up the item from active tracking
            key = get_item_key(item.get('type', ''), item.get('id', ''))
            if key in history['items']:
                del history['items'][key]
            
            return history
        
        def get_days_tracked(history, item_type, item_id):
            """Get the number of days an item has been tracked."""
            key = get_item_key(item_type, item_id)
            if key in history['items']:
                first_seen = history['items'][key].get('first_seen')
                if first_seen:
                    try:
                        first_date = datetime.strptime(first_seen, '%Y-%m-%d')
                        delta = datetime.now() - first_date
                        return delta.days
                    except:
                        pass
            return 'N/A'
        
        def get_first_seen(history, item_type, item_id):
            """Get the first_seen date for an item."""
            key = get_item_key(item_type, item_id)
            if key in history['items']:
                return history['items'][key].get('first_seen', 'N/A')
            return 'N/A'
        
        def is_new_this_sprint(first_seen_str, sprint_days=14):
            """
            Check if an item was added within the current sprint.
            
            Args:
                first_seen_str: Date string in YYYY-MM-DD format
                sprint_days: Number of days in a sprint (default 14)
            
            Returns:
                True if item was added within the sprint period
            """
            try:
                if not first_seen_str or first_seen_str == 'N/A':
                    return True  # New items without history are considered new
                first_seen = datetime.strptime(first_seen_str, '%Y-%m-%d')
                days_since = (datetime.now() - first_seen).days
                return days_since <= sprint_days
            except:
                return False
        
        def format_entered_date(first_seen_str, sprint_days=14):
            """
            Format the Entered date with a NEW indicator if within sprint.
            
            Args:
                first_seen_str: Date string in YYYY-MM-DD format
                sprint_days: Number of days in a sprint (default 14)
            
            Returns:
                Formatted string with optional 🆕 indicator
            """
            if not first_seen_str or first_seen_str == 'N/A':
                today = datetime.now().strftime('%Y-%m-%d')
                return f"🆕 {today}"  # New item, mark with today
            
            if is_new_this_sprint(first_seen_str, sprint_days):
                return f"🆕 {first_seen_str}"
            return first_seen_str
        
        # Load tracking history
        tracking_history = load_tracking_history()
        
        def compare_states_for_success(previous, current, history):
            """Compare previous and current states to find completed items (Success Stories)."""
            success_stories = []
            
            # Build sets of current IDs for quick lookup
            current_ids = {
                'opendev': set(r['id'] for r in current.get('opendev_reviews', [])),
                'github': set(p['id'] for p in current.get('github_prs', [])),
                'gitlab': set(m['id'] for m in current.get('gitlab_mrs', [])),
                'jira': set(t['id'] for t in current.get('jira_tickets', [])),
                'jira_watching': set(t['id'] for t in current.get('jira_watching', [])),
                'opendev_review': set(r['id'] for r in current.get('awaiting_review', {}).get('opendev', [])),
                'gitlab_review': set(m['id'] for m in current.get('awaiting_review', {}).get('gitlab', [])),
                'github_review': set(p['id'] for p in current.get('awaiting_review', {}).get('github', [])),
            }
            
            # Check OpenDev reviews that disappeared (merged/abandoned)
            for review in previous.get('opendev_reviews', []):
                if review['id'] not in current_ids['opendev']:
                    days = get_days_tracked(history, 'opendev', review['id'])
                    rating = calculate_success_rating(days)
                    story = {
                        'platform': '🟠 OpenDev',
                        'type': 'opendev',
                        'id': review['id'],
                        'title': review.get('subject', 'N/A')[:50],
                        'url': review.get('url', '#'),
                        'reason': 'Merged/Closed',
                        'is_mine': True,
                        'icon': '🎉',
                        'days_tracked': days,
                        'rating': rating,
                        'rating_emoji': get_rating_emoji(rating)
                    }
                    success_stories.append(story)
                    record_completion(history, story, days, rating)
            
            # Check GitHub PRs that disappeared (merged/closed)
            for pr in previous.get('github_prs', []):
                if pr['id'] not in current_ids['github']:
                    days = get_days_tracked(history, 'github', pr['id'])
                    rating = calculate_success_rating(days)
                    story = {
                        'platform': '🔵 GitHub',
                        'type': 'github',
                        'id': f"#{pr['id']}",
                        'title': pr.get('title', 'N/A')[:50],
                        'url': pr.get('url', '#'),
                        'reason': 'Merged/Closed',
                        'is_mine': True,
                        'icon': '🎉',
                        'days_tracked': days,
                        'rating': rating,
                        'rating_emoji': get_rating_emoji(rating)
                    }
                    success_stories.append(story)
                    record_completion(history, story, days, rating)
            
            # Check GitLab MRs that disappeared (merged/closed)
            for mr in previous.get('gitlab_mrs', []):
                if mr['id'] not in current_ids['gitlab']:
                    days = get_days_tracked(history, 'gitlab', mr['id'])
                    rating = calculate_success_rating(days)
                    story = {
                        'platform': '🦊 GitLab',
                        'type': 'gitlab',
                        'id': f"!{mr['id']}",
                        'title': mr.get('title', 'N/A')[:50],
                        'url': mr.get('url', '#'),
                        'reason': 'Merged/Closed',
                        'is_mine': True,
                        'icon': '🎉',
                        'days_tracked': days,
                        'rating': rating,
                        'rating_emoji': get_rating_emoji(rating)
                    }
                    success_stories.append(story)
                    record_completion(history, story, days, rating)
            
            # Check Jira tickets that disappeared (closed/resolved)
            for ticket in previous.get('jira_tickets', []):
                if ticket['id'] not in current_ids['jira']:
                    days = get_days_tracked(history, 'jira', ticket['id'])
                    rating = calculate_success_rating(days)
                    story = {
                        'platform': '📋 Jira',
                        'type': 'jira',
                        'id': ticket['id'],
                        'title': ticket.get('summary', 'N/A')[:50],
                        'url': ticket.get('url', '#'),
                        'reason': 'Closed/Resolved',
                        'is_mine': True,
                        'icon': '🎉',
                        'days_tracked': days,
                        'rating': rating,
                        'rating_emoji': get_rating_emoji(rating)
                    }
                    success_stories.append(story)
                    record_completion(history, story, days, rating)
            
            # Check watched Jira tickets that disappeared (someone else closed them)
            for ticket in previous.get('jira_watching', []):
                if ticket['id'] not in current_ids['jira_watching']:
                    days = get_days_tracked(history, 'jira_watching', ticket['id'])
                    rating = calculate_success_rating(days)
                    story = {
                        'platform': '📋 Jira (Watching)',
                        'type': 'jira_watching',
                        'id': ticket['id'],
                        'title': ticket.get('summary', 'N/A')[:50],
                        'url': ticket.get('url', '#'),
                        'reason': f"Closed by {ticket.get('owner', 'someone')}",
                        'is_mine': False,
                        'icon': '⭐',
                        'days_tracked': days,
                        'rating': rating,
                        'rating_emoji': get_rating_emoji(rating)
                    }
                    success_stories.append(story)
                    record_completion(history, story, days, rating)
            
            # Check reviews awaiting my vote that disappeared (merged or I'm no longer reviewer)
            for review in previous.get('awaiting_review', {}).get('opendev', []):
                if review['id'] not in current_ids['opendev_review']:
                    days = get_days_tracked(history, 'opendev_review', review['id'])
                    rating = calculate_success_rating(days)
                    story = {
                        'platform': '🟠 OpenDev (Review)',
                        'type': 'opendev_review',
                        'id': review['id'],
                        'title': review.get('subject', 'N/A')[:50],
                        'url': review.get('url', '#'),
                        'reason': f"Completed ({review.get('owner', 'owner')}'s review)",
                        'is_mine': False,
                        'icon': '⭐',
                        'days_tracked': days,
                        'rating': rating,
                        'rating_emoji': get_rating_emoji(rating)
                    }
                    success_stories.append(story)
                    record_completion(history, story, days, rating)
            
            for mr in previous.get('awaiting_review', {}).get('gitlab', []):
                if mr['id'] not in current_ids['gitlab_review']:
                    days = get_days_tracked(history, 'gitlab_review', mr['id'])
                    rating = calculate_success_rating(days)
                    story = {
                        'platform': '🦊 GitLab (Review)',
                        'type': 'gitlab_review',
                        'id': f"!{mr['id']}",
                        'title': mr.get('title', 'N/A')[:50],
                        'url': mr.get('url', '#'),
                        'reason': f"Completed ({mr.get('owner', 'owner')}'s MR)",
                        'is_mine': False,
                        'icon': '⭐',
                        'days_tracked': days,
                        'rating': rating,
                        'rating_emoji': get_rating_emoji(rating)
                    }
                    success_stories.append(story)
                    record_completion(history, story, days, rating)
            
            for pr in previous.get('awaiting_review', {}).get('github', []):
                if pr['id'] not in current_ids['github_review']:
                    days = get_days_tracked(history, 'github_review', pr['id'])
                    rating = calculate_success_rating(days)
                    story = {
                        'platform': '🔵 GitHub (Review)',
                        'type': 'github_review',
                        'id': f"#{pr['id']}",
                        'title': pr.get('title', 'N/A')[:50],
                        'url': pr.get('url', '#'),
                        'reason': f"Completed ({pr.get('owner', 'owner')}'s PR)",
                        'is_mine': False,
                        'icon': '⭐',
                        'days_tracked': days,
                        'rating': rating,
                        'rating_emoji': get_rating_emoji(rating)
                    }
                    success_stories.append(story)
                    record_completion(history, story, days, rating)
            
            return success_stories
        
        def get_platform_icon(item_type):
            """Get platform icon from item type."""
            icons = {
                'opendev': '🟠 OpenDev',
                'github': '🔵 GitHub',
                'gitlab': '🦊 GitLab',
                'jira': '📋 Jira',
                'jira_watching': '📋 Jira',
                'opendev_review': '🟠 OpenDev (Review)',
                'gitlab_review': '🦊 GitLab (Review)',
                'github_review': '🔵 GitHub (Review)'
            }
            return icons.get(item_type, item_type)
        
        def build_item_url(item_type, item_id):
            """Build URL for an item based on type."""
            clean_id = str(item_id).replace('!', '')
            if item_type in ['opendev', 'opendev_review']:
                return f"https://review.opendev.org/c/openstack/horizon/+/{clean_id}"
            elif item_type in ['gitlab', 'gitlab_review']:
                return f"https://gitlab.cee.redhat.com/eng/openstack/horizon/-/merge_requests/{clean_id}"
            elif item_type in ['github', 'github_review']:
                return f"https://github.com/openstack-k8s-operators/horizon-operator/pull/{clean_id}"
            elif item_type in ['jira', 'jira_watching']:
                return f"https://issues.redhat.com/browse/{item_id}"
            return "#"
        
        def generate_sprint_flow_summary(history, current_items_count, sprint_days=14):
            """
            Generate a Sprint Flow Summary showing in/out rates.
            
            Args:
                history: Tracking history with items and quarterly_stats
                current_items_count: Total number of currently active items
                sprint_days: Number of days in a sprint (default 14)
            
            Returns:
                Markdown formatted sprint flow summary
            """
            lines = []
            lines.append("## 📊 Sprint Flow Summary")
            lines.append("")
            
            today = datetime.now()
            sprint_start = today - timedelta(days=sprint_days)
            sprint_start_str = sprint_start.strftime('%Y-%m-%d')
            
            # Count items that ENTERED this sprint (first_seen within sprint_days)
            items_entered = 0
            for key, item_data in history.get('items', {}).items():
                first_seen = item_data.get('first_seen', '')
                if first_seen and first_seen >= sprint_start_str:
                    items_entered += 1
            
            # Count items that EXITED this sprint (completed within sprint_days)
            items_exited = 0
            for completion in history.get('quarterly_stats', []):
                completed_date = completion.get('date', '')
                if completed_date and completed_date >= sprint_start_str:
                    items_exited += 1
            
            # Calculate net change
            net_change = items_entered - items_exited
            net_icon = "📈" if net_change > 0 else "📉" if net_change < 0 else "➡️"
            net_display = f"+{net_change}" if net_change > 0 else str(net_change)
            
            lines.append(f"**Sprint Period**: {sprint_start_str} to {today.strftime('%Y-%m-%d')} ({sprint_days} days)")
            lines.append("")
            lines.append("| Metric | Count | Description |")
            lines.append("|--------|-------|-------------|")
            lines.append(f"| 🆕 **Entered** | {items_entered} | New items added this sprint |")
            lines.append(f"| ✅ **Exited** | {items_exited} | Items completed this sprint |")
            lines.append(f"| {net_icon} **Net Change** | {net_display} | In rate minus out rate |")
            lines.append(f"| 📋 **Current Total** | {current_items_count} | Active items in backlog |")
            lines.append("")
            
            # Add insight
            if net_change > 2:
                lines.append("> ⚠️ **Backlog growing** - More items entering than exiting. Consider capacity planning.")
            elif net_change < -2:
                lines.append("> 🎉 **Great progress!** - Completing more than adding. Backlog is shrinking!")
            else:
                lines.append("> ✅ **Balanced flow** - Intake roughly matches completion rate.")
            lines.append("")
            
            return "\n".join(lines)
        
        def generate_success_stories_section(success_stories, history, unplanned_done=None):
            """Generate markdown section for success stories with ratings.
            
            This section now shows PERSISTENT data from quarterly_stats,
            not just the diff from the last run.
            """
            if unplanned_done is None:
                unplanned_done = []
            
            lines = []
            lines.append("## 🏆 Success Stories")
            lines.append("")
            lines.append("_All completed items this quarter (persistent)_")
            lines.append("")
            
            # Rating legend
            lines.append("> **Rating System:** 🌟 A+ (<14 days) | ✅ A (<28 days) | ⚠️ B (<42 days) | 🔴 F (>42 days)")
            lines.append("")
            
            # Get ALL items from quarterly_stats (persistent history)
            quarterly_stats = history.get('quarterly_stats', [])
            today = datetime.now()
            current_quarter = f"{today.year}-Q{(today.month - 1) // 3 + 1}"
            quarter_items = [s for s in quarterly_stats if s.get('quarter') == current_quarter]
            
            # Separate into mine vs team from quarterly_stats
            my_victories = [s for s in quarter_items if s.get('is_mine', False)]
            team_progress = [s for s in quarter_items if not s.get('is_mine', False)]
            
            # Also add any NEW success stories from this run (not yet in quarterly_stats)
            for story in success_stories:
                story_key = f"{story.get('type', '')}:{story.get('id', '')}"
                # Check if already in quarterly_stats
                existing = any(f"{q.get('type', '')}:{q.get('id', '')}" == story_key for q in quarter_items)
                if not existing:
                    if story.get('is_mine', False):
                        my_victories.append(story)
                    else:
                        team_progress.append(story)
            
            # Show placeholder if no completions at all
            if not my_victories and not team_progress:
                lines.append("### 🎉 Your Victories (0)")
                lines.append("")
                lines.append("_No completed items this quarter... but here's what success will look like!_")
                lines.append("")
                lines.append("| Platform | Item | Entered | Exited | Days | Rating |")
                lines.append("|----------|------|---------|--------|------|--------|")
                lines.append("| 🟠 OpenDev | [999999](https://example.com) 🦄 Fix the unfixable bug that... | 2025-10-21 | 2025-12-01 | 41 | ⚠️ B |")
                lines.append("| 📋 Jira | [OSPRH-99999](https://example.com) 🎯 Implement world peace in Ho... | 2025-11-25 | 2025-12-02 | 7 | 🌟 A+ |")
                lines.append("")
                lines.append("_^ Example placeholder - complete some items to see your real victories here!_")
                lines.append("")
                return "\n".join(lines)
            
            # Your Victories (items you owned)
            if my_victories:
                lines.append(f"### 🎉 Your Victories ({len(my_victories)})")
                lines.append("")
                lines.append("_Items you owned that are now complete_")
                lines.append("")
                lines.append("| Platform | Item | Entered | Exited | Days | Rating |")
                lines.append("|----------|------|---------|--------|------|--------|")
                for item in sorted(my_victories, key=lambda x: x.get('date', x.get('completed', '')), reverse=True):
                    platform = get_platform_icon(item.get('type', ''))
                    item_id = str(item.get('id', 'N/A')).lstrip('!')  # Remove ! prefix from GitLab MR IDs
                    title = item.get('title', 'N/A')[:40] + ('...' if len(item.get('title', '')) > 40 else '')
                    url = item.get('url', build_item_url(item.get('type', ''), item_id))
                    exited = item.get('date', item.get('completed', 'N/A'))[:10] if item.get('date') or item.get('completed') else 'N/A'
                    # Calculate entered date from exited - days_tracked
                    days = item.get('days_tracked', 'N/A')
                    try:
                        if exited != 'N/A' and days != 'N/A':
                            exited_dt = datetime.strptime(exited, '%Y-%m-%d')
                            entered_dt = exited_dt - timedelta(days=int(days))
                            entered = entered_dt.strftime('%Y-%m-%d')
                        else:
                            entered = 'N/A'
                    except:
                        entered = 'N/A'
                    rating = item.get('rating', 'N/A')
                    rating_emoji = get_rating_emoji(rating)
                    
                    # Format as MR-XX for GitLab, PR-XX for GitHub
                    if 'gitlab' in item.get('type', ''):
                        display_id = f"MR-{item_id}"
                    elif 'github' in item.get('type', ''):
                        display_id = f"PR-{item_id}"
                    else:
                        display_id = item_id
                    
                    item_display = f"[{display_id}]({url}) {title}"
                    lines.append(f"| {platform} | {item_display} | {entered} | {exited} | {days} | {rating_emoji} {rating} |")
                lines.append("")
            
            # Team Progress (items you were watching/reviewing) - NOW PERSISTENT!
            if team_progress:
                lines.append(f"### ⭐ Team Progress ({len(team_progress)})")
                lines.append("")
                lines.append("_Items you were watching/reviewing that are now complete (persistent this quarter)_")
                lines.append("")
                lines.append("| Platform | Item | Owner | Entered | Exited | Days | Rating |")
                lines.append("|----------|------|-------|---------|--------|------|--------|")
                for item in sorted(team_progress, key=lambda x: x.get('date', x.get('completed', '')), reverse=True):
                    platform = get_platform_icon(item.get('type', ''))
                    item_id = str(item.get('id', 'N/A')).lstrip('!')  # Remove ! prefix from GitLab MR IDs
                    title = item.get('title', 'N/A')[:30] + ('...' if len(item.get('title', '')) > 30 else '')
                    url = item.get('url', build_item_url(item.get('type', ''), item_id))
                    owner = item.get('owner', 'N/A')
                    exited = item.get('date', item.get('completed', 'N/A'))[:10] if item.get('date') or item.get('completed') else 'N/A'
                    # Calculate entered date from exited - days_tracked
                    days = item.get('days_tracked', 'N/A')
                    try:
                        if exited != 'N/A' and days != 'N/A':
                            exited_dt = datetime.strptime(exited, '%Y-%m-%d')
                            entered_dt = exited_dt - timedelta(days=int(days))
                            entered = entered_dt.strftime('%Y-%m-%d')
                        else:
                            entered = 'N/A'
                    except:
                        entered = 'N/A'
                    rating = item.get('rating', 'N/A')
                    rating_emoji = get_rating_emoji(rating)
                    
                    # Format as MR-XX for GitLab, PR-XX for GitHub
                    if 'gitlab' in item.get('type', ''):
                        display_id = f"MR-{item_id}"
                    elif 'github' in item.get('type', ''):
                        display_id = f"PR-{item_id}"
                    else:
                        display_id = item_id
                    
                    item_display = f"[{display_id}]({url}) {title}"
                    lines.append(f"| {platform} | {item_display} | {owner} | {entered} | {exited} | {days} | {rating_emoji} {rating} |")
                lines.append("")
            
            # Completed Unplanned Work (from unplanned_done.txt)
            if unplanned_done:
                lines.append("### 🔧 Unplanned Work Completed")
                lines.append("")
                lines.append("_Interrupts, firefights, and ad-hoc tasks that got done_")
                lines.append("")
                lines.append("| Date | Category | Description | Hours | Outcome |")
                lines.append("|------|----------|-------------|-------|---------|")
                
                # Show last 5 unplanned completed items
                for item in sorted(unplanned_done, key=lambda x: x.get('date', ''), reverse=True)[:5]:
                    icon = get_unplanned_category_icon(item['category'])
                    desc = item['description'][:30] + ('...' if len(item['description']) > 30 else '')
                    outcome = item.get('outcome', '')[:20] + ('...' if len(item.get('outcome', '')) > 20 else '')
                    lines.append(f"| {item['date']} | {icon} {item['category']} | {desc} | {item['hours']} | {outcome} |")
                
                if len(unplanned_done) > 5:
                    lines.append(f"| ... | | _{len(unplanned_done) - 5} more_ | | |")
                lines.append("")
            
            # Quarterly summary
            total_quarter = len(my_victories) + len(team_progress)
            if total_quarter > 0:
                # Calculate rating distribution
                all_items = my_victories + team_progress
                ratings = {'A+': 0, 'A': 0, 'B': 0, 'F': 0}
                for item in all_items:
                    r = item.get('rating', 'F')
                    if r in ratings:
                        ratings[r] += 1
                
                lines.append(f"### 📊 Quarterly Summary ({current_quarter})")
                lines.append("")
                lines.append(f"**{total_quarter} items completed this quarter**")
                lines.append("")
                lines.append("| Rating | Count | Percentage |")
                lines.append("|--------|-------|------------|")
                for r in ['A+', 'A', 'B', 'F']:
                    count = ratings[r]
                    pct = (count / total_quarter * 100) if total_quarter > 0 else 0
                    emoji = get_rating_emoji(r)
                    lines.append(f"| {emoji} {r} | {count} | {pct:.1f}% |")
                lines.append("")
            
            return "\n".join(lines)
        
        def generate_timeline_estimates_section(current_state, tracking_history):
            """
            Generate markdown section for AI Timeline Estimates.
            
            This section shows:
            - Estimated completion time (AI-assisted vs manual)
            - Priority ranking
            - Target completion dates
            - Work schedule
            """
            lines = []
            lines.append("## ⏱️ AI Timeline Estimates")
            lines.append("")
            lines.append("_AI-calculated time estimates and priority scheduling_")
            lines.append("")
            
            # Collect all items with estimates
            all_items = []
            today_str = datetime.now().strftime("%Y-%m-%d")
            
            # Process OpenDev reviews (owned by me)
            for item in current_state.get('opendev', []):
                if item.get('status') in ['NEW', 'ACTIVE']:
                    complexity = item.get('complexity_score', 0)
                    ai_days, manual_days = calculate_estimated_days(complexity)
                    first_seen = tracking_history.get('items', {}).get(f"opendev_{item['number']}", {}).get('first_seen', today_str)
                    target = calculate_target_date(first_seen, ai_days)
                    
                    # Determine if it has a fix version (use subject as proxy)
                    has_fix_version = 'osprh' in item.get('subject', '').lower()
                    
                    priority_num, priority_label, priority_reason = calculate_priority(
                        'opendev',
                        is_awaiting_review=False,
                        has_fix_version=has_fix_version,
                        is_owned_by_me=True
                    )
                    
                    all_items.append({
                        'platform': '🟠 OpenDev',
                        'id': item.get('number'),
                        'title': item.get('subject', 'N/A')[:35] + ('...' if len(item.get('subject', '')) > 35 else ''),
                        'url': item.get('url', '#'),
                        'owner': 'me',
                        'complexity': complexity,
                        'ai_days': ai_days,
                        'manual_days': manual_days,
                        'priority_num': priority_num,
                        'priority_label': priority_label,
                        'priority_reason': priority_reason,
                        'target': target,
                        'first_seen': first_seen
                    })
            
            # Process GitHub PRs (owned by me)
            for item in current_state.get('github', []):
                complexity = item.get('complexity_score', 0)
                ai_days, manual_days = calculate_estimated_days(complexity)
                first_seen = tracking_history.get('items', {}).get(f"github_{item['number']}", {}).get('first_seen', today_str)
                target = calculate_target_date(first_seen, ai_days)
                
                priority_num, priority_label, priority_reason = calculate_priority(
                    'github',
                    is_awaiting_review=False,
                    has_fix_version=False,
                    is_owned_by_me=True
                )
                
                all_items.append({
                    'platform': '🔵 GitHub',
                    'id': item.get('number'),
                    'title': item.get('title', 'N/A')[:35] + ('...' if len(item.get('title', '')) > 35 else ''),
                    'url': item.get('url', '#'),
                    'owner': 'me',
                    'complexity': complexity,
                    'ai_days': ai_days,
                    'manual_days': manual_days,
                    'priority_num': priority_num,
                    'priority_label': priority_label,
                    'priority_reason': priority_reason,
                    'target': target,
                    'first_seen': first_seen
                })
            
            # Process GitLab MRs (owned by me)
            for item in current_state.get('gitlab', []):
                complexity = item.get('complexity_score', 0)
                ai_days, manual_days = calculate_estimated_days(complexity)
                first_seen = tracking_history.get('items', {}).get(f"gitlab_{item['iid']}", {}).get('first_seen', today_str)
                target = calculate_target_date(first_seen, ai_days)
                
                priority_num, priority_label, priority_reason = calculate_priority(
                    'gitlab',
                    is_awaiting_review=False,
                    has_fix_version=False,
                    is_owned_by_me=True
                )
                
                all_items.append({
                    'platform': '🦊 GitLab',
                    'id': item.get('iid'),
                    'title': item.get('title', 'N/A')[:35] + ('...' if len(item.get('title', '')) > 35 else ''),
                    'url': item.get('url', '#'),
                    'owner': 'me',
                    'complexity': complexity,
                    'ai_days': ai_days,
                    'manual_days': manual_days,
                    'priority_num': priority_num,
                    'priority_label': priority_label,
                    'priority_reason': priority_reason,
                    'target': target,
                    'first_seen': first_seen
                })
            
            # Process Jira tickets (owned by me)
            for item in current_state.get('jira', []):
                complexity = item.get('complexity_score', 0)
                ai_days, manual_days = calculate_estimated_days(complexity)
                first_seen = tracking_history.get('items', {}).get(f"jira_{item['key']}", {}).get('first_seen', today_str)
                target = calculate_target_date(first_seen, ai_days)
                
                # Check if has fix version
                has_fix_version = bool(item.get('fix_version'))
                
                priority_num, priority_label, priority_reason = calculate_priority(
                    'jira',
                    is_awaiting_review=False,
                    has_fix_version=has_fix_version,
                    is_owned_by_me=True
                )
                
                all_items.append({
                    'platform': '📋 Jira',
                    'id': item.get('key'),
                    'title': item.get('summary', 'N/A')[:35] + ('...' if len(item.get('summary', '')) > 35 else ''),
                    'url': item.get('url', '#'),
                    'owner': 'me',
                    'complexity': complexity,
                    'ai_days': ai_days,
                    'manual_days': manual_days,
                    'priority_num': priority_num,
                    'priority_label': priority_label,
                    'priority_reason': priority_reason,
                    'target': target,
                    'first_seen': first_seen
                })
            
            # Add items awaiting review (P1 - blocking others)
            for item in current_state.get('opendev_awaiting', []):
                if not item.get('has_voted'):
                    complexity = item.get('complexity_score', 0)
                    ai_days, manual_days = calculate_estimated_days(complexity)
                    first_seen = tracking_history.get('items', {}).get(f"opendev_review_{item['number']}", {}).get('first_seen', today_str)
                    target = calculate_target_date(first_seen, ai_days)
                    
                    all_items.append({
                        'platform': '🟠 OpenDev',
                        'id': f"Review {item.get('number')}",
                        'title': item.get('subject', 'N/A')[:35] + ('...' if len(item.get('subject', '')) > 35 else ''),
                        'url': item.get('url', '#'),
                        'owner': item.get('owner', 'N/A'),
                        'complexity': complexity,
                        'ai_days': ai_days,
                        'manual_days': manual_days,
                        'priority_num': 1,
                        'priority_label': 'P1',
                        'priority_reason': 'blocking teammate',
                        'target': target,
                        'first_seen': first_seen
                    })
            
            for item in current_state.get('gitlab_awaiting', []):
                if not item.get('has_approved'):
                    complexity = item.get('complexity_score', 0)
                    ai_days, manual_days = calculate_estimated_days(complexity)
                    first_seen = tracking_history.get('items', {}).get(f"gitlab_review_{item['iid']}", {}).get('first_seen', today_str)
                    target = calculate_target_date(first_seen, ai_days)
                    
                    all_items.append({
                        'platform': '🦊 GitLab',
                        'id': f"MR-{item.get('iid')}",
                        'title': item.get('title', 'N/A')[:35] + ('...' if len(item.get('title', '')) > 35 else ''),
                        'url': item.get('url', '#'),
                        'owner': item.get('owner', 'N/A'),
                        'complexity': complexity,
                        'ai_days': ai_days,
                        'manual_days': manual_days,
                        'priority_num': 1,
                        'priority_label': 'P1',
                        'priority_reason': 'blocking teammate',
                        'target': target,
                        'first_seen': first_seen
                    })
            
            for item in current_state.get('github_awaiting', []):
                if not item.get('has_reviewed'):
                    complexity = item.get('complexity_score', 0)
                    ai_days, manual_days = calculate_estimated_days(complexity)
                    first_seen = tracking_history.get('items', {}).get(f"github_review_{item['number']}", {}).get('first_seen', today_str)
                    target = calculate_target_date(first_seen, ai_days)
                    
                    all_items.append({
                        'platform': '🔵 GitHub',
                        'id': f"PR-{item.get('number')}",
                        'title': item.get('title', 'N/A')[:35] + ('...' if len(item.get('title', '')) > 35 else ''),
                        'url': item.get('url', '#'),
                        'owner': item.get('owner', 'N/A'),
                        'complexity': complexity,
                        'ai_days': ai_days,
                        'manual_days': manual_days,
                        'priority_num': 1,
                        'priority_label': 'P1',
                        'priority_reason': 'blocking teammate',
                        'target': target,
                        'first_seen': first_seen
                    })
            
            if not all_items:
                lines.append("_No active items to estimate. Nice work!_ 🎉")
                lines.append("")
                return "\n".join(lines)
            
            # Sort by priority (P1 first), then by target date
            all_items.sort(key=lambda x: (x['priority_num'], x['target']))
            
            # Priority legend
            lines.append("> **Priority:** 🔴 P1 (blocking others) | 🟠 P2 (has fix version) | 🟡 P3 (your work) | 🟢 P4 (watching)")
            lines.append("")
            
            # Work schedule table
            lines.append("### 📅 Work Schedule")
            lines.append("")
            lines.append("_Items sorted by priority and target date_")
            lines.append("")
            lines.append("| Priority | Platform | Item | Owner | AI Est. | Target | Complexity |")
            lines.append("|----------|----------|------|-------|---------|--------|------------|")
            
            for item in all_items[:15]:  # Limit to top 15
                priority_display = get_priority_display(item['priority_num'])
                complexity_display = get_complexity_display(item['complexity'])
                ai_est = f"{item['ai_days']}d"
                owner = item.get('owner', 'me')
                
                lines.append(f"| {priority_display} | {item['platform']} | [{item['id']}]({item['url']}) {item['title']} | {owner} | {ai_est} | {item['target']} | {complexity_display} |")
            
            if len(all_items) > 15:
                lines.append(f"| ... | | _{len(all_items) - 15} more items_ | | | | |")
            
            lines.append("")
            
            # Summary stats
            total_ai_days = sum(item['ai_days'] for item in all_items)
            total_manual_days = sum(item['manual_days'] for item in all_items)
            p1_count = len([i for i in all_items if i['priority_num'] == 1])
            
            lines.append("### 📊 Summary")
            lines.append("")
            lines.append(f"- **Total Items**: {len(all_items)}")
            lines.append(f"- **P1 (Blocking)**: {p1_count}")
            lines.append(f"- **Total AI-Assisted Time**: {total_ai_days:.1f} days")
            lines.append(f"- **Total Manual Time**: {total_manual_days:.1f} days")
            lines.append(f"- **AI Time Savings**: {total_manual_days - total_ai_days:.1f} days ({((total_manual_days - total_ai_days) / total_manual_days * 100):.0f}%)" if total_manual_days > 0 else "")
            lines.append("")
            
            return "\n".join(lines)
        
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
        
        def get_unplanned_category_icon(category):
            """Get icon for unplanned work category."""
            icons = {
                'INTERRUPT': '💬',
                'MEETING': '📅',
                'FIREFIGHT': '🔥',
                'LEARNING': '📚',
                'HELPING': '🤝',
                'ADMIN': '📋',
                'OTHER': '📌'
            }
            return icons.get(category.upper(), '📌')
        
        def parse_unplanned_file(filepath):
            """Parse unplanned.txt file and return list of items."""
            items = []
            if not os.path.exists(filepath):
                return items
            
            try:
                with open(filepath, 'r') as f:
                    for line in f:
                        line = line.strip()
                        # Skip comments and empty lines
                        if not line or line.startswith('#'):
                            continue
                        
                        # Parse: YYYY-MM-DD | Category | Description | Hours
                        parts = [p.strip() for p in line.split('|')]
                        if len(parts) >= 4:
                            items.append({
                                'date': parts[0],
                                'category': parts[1].upper(),
                                'description': parts[2],
                                'hours': parts[3]
                            })
            except Exception as e:
                print(f"Warning: Could not parse unplanned file: {e}", file=sys.stderr)
            
            return items
        
        def parse_unplanned_done_file(filepath):
            """Parse unplanned_done.txt file and return list of completed items."""
            items = []
            if not os.path.exists(filepath):
                return items
            
            try:
                with open(filepath, 'r') as f:
                    for line in f:
                        line = line.strip()
                        # Skip comments and empty lines
                        if not line or line.startswith('#'):
                            continue
                        
                        # Parse: YYYY-MM-DD | Category | Description | Actual Hours | Outcome
                        parts = [p.strip() for p in line.split('|')]
                        if len(parts) >= 5:
                            items.append({
                                'date': parts[0],
                                'category': parts[1].upper(),
                                'description': parts[2],
                                'hours': parts[3],
                                'outcome': parts[4]
                            })
            except Exception as e:
                print(f"Warning: Could not parse unplanned done file: {e}", file=sys.stderr)
            
            return items
        
        def generate_unplanned_section(unplanned_items, unplanned_done_items):
            """Generate markdown section for unplanned work."""
            lines = []
            lines.append("## 🔧 Unplanned Work")
            lines.append("")
            
            if not unplanned_items and not unplanned_done_items:
                lines.append("_No unplanned work tracked. Use `~/Work/mymcp/unplanned-add.sh` to add items._")
                lines.append("")
                lines.append("```bash")
                lines.append("# Quick add:")
                lines.append("~/Work/mymcp/unplanned-add.sh INTERRUPT \"Description\" 1.5")
                lines.append("```")
                lines.append("")
                return "\n".join(lines)
            
            # Active unplanned work
            if unplanned_items:
                total_hours = sum(float(item.get('hours', 0)) for item in unplanned_items)
                lines.append(f"**Currently Tracking: {len(unplanned_items)} item(s) ({total_hours:.1f} hours estimated)**")
                lines.append("")
                lines.append("| Date | Category | Description | Est. Hours |")
                lines.append("|------|----------|-------------|------------|")
                for item in sorted(unplanned_items, key=lambda x: x['date'], reverse=True):
                    icon = get_unplanned_category_icon(item['category'])
                    lines.append(f"| {item['date']} | {icon} {item['category']} | {item['description'][:40]}{'...' if len(item['description']) > 40 else ''} | {item['hours']} |")
                lines.append("")
            else:
                lines.append("_No active unplanned work items._")
                lines.append("")
            
            # Recently completed unplanned work (last 7 days)
            if unplanned_done_items:
                # Filter to last 7 days
                today = datetime.now()
                recent_done = []
                for item in unplanned_done_items:
                    try:
                        item_date = datetime.strptime(item['date'], '%Y-%m-%d')
                        if (today - item_date).days <= 7:
                            recent_done.append(item)
                    except:
                        recent_done.append(item)  # Include if can't parse date
                
                if recent_done:
                    total_done_hours = sum(float(item.get('hours', 0)) for item in recent_done)
                    lines.append(f"### ✅ Completed This Week ({len(recent_done)} items, {total_done_hours:.1f} hours)")
                    lines.append("")
                    lines.append("| Date | Category | Description | Hours | Outcome |")
                    lines.append("|------|----------|-------------|-------|---------|")
                    for item in sorted(recent_done, key=lambda x: x['date'], reverse=True)[:5]:
                        icon = get_unplanned_category_icon(item['category'])
                        desc = item['description'][:30] + ('...' if len(item['description']) > 30 else '')
                        outcome = item.get('outcome', '')[:25] + ('...' if len(item.get('outcome', '')) > 25 else '')
                        lines.append(f"| {item['date']} | {icon} {item['category']} | {desc} | {item['hours']} | {outcome} |")
                    lines.append("")
            
            # Quick add reminder
            lines.append("_Quick add: `~/Work/mymcp/unplanned-add.sh CATEGORY \"Description\" HOURS`_")
            lines.append("")
            
            return "\n".join(lines)
        
        # Fetch reviews where I'm a reviewer (people waiting for my review)
        # OpenDev: Query for reviews where I'm added as reviewer but haven't voted
        print("Fetching reviews awaiting your review...", file=sys.stderr)
        
        opendev_awaiting_review = []
        try:
            base_url = "https://review.opendev.org"
            # Query for open reviews where I'm a reviewer
            reviewer_query = f"reviewer:{OPENDEV_USERNAME} status:open -owner:{OPENDEV_USERNAME}"
            reviewer_response = requests.get(
                f'{base_url}/changes/',
                params={'q': reviewer_query, 'o': ['DETAILED_ACCOUNTS', 'LABELS']}
            )
            reviewer_response.raise_for_status()
            
            reviewer_data_text = reviewer_response.text
            if reviewer_data_text.startswith(")]}'\n"):
                reviewer_data_text = reviewer_data_text[5:]
            reviewer_data = json.loads(reviewer_data_text)
            
            for change in reviewer_data:
                # Check if user has already voted
                labels = change.get('labels', {})
                has_voted = False
                for label_name, label_data in labels.items():
                    for vote in label_data.get('all', []):
                        if vote.get('username', '') == OPENDEV_USERNAME and vote.get('value', 0) != 0:
                            has_voted = True
                            break
                    if has_voted:
                        break
                
                # Include if not voted yet, or include all for visibility
                owner_info = change.get('owner', {})
                owner_name = owner_info.get('name', owner_info.get('username', 'Unknown'))
                opendev_awaiting_review.append({
                    'number': change.get('_number', 0),
                    'subject': change.get('subject', ''),
                    'project': change.get('project', ''),
                    'status': change.get('status', ''),
                    'created': change.get('created', ''),
                    'updated': change.get('updated', ''),
                    'owner': owner_name,
                    'has_voted': has_voted,
                    'url': f"{base_url}/c/{change.get('project', '')}/+/{change.get('_number', 0)}"
                })
        except Exception as e:
            print(f"Warning: Could not fetch OpenDev reviews awaiting review: {e}", file=sys.stderr)
        
        # GitLab: Query for MRs where I'm a reviewer
        # Note: GitLab CEE's global reviewer_id query doesn't work reliably,
        # so we search across projects the user has recently interacted with
        gitlab_awaiting_review = []
        if GITLAB_TOKEN:
            try:
                headers = {'PRIVATE-TOKEN': GITLAB_TOKEN}
                
                # Get user ID first
                user_response = requests.get(
                    f'{GITLAB_URL}/api/v4/users',
                    headers=headers,
                    params={'username': GITLAB_USERNAME}
                )
                user_response.raise_for_status()
                users = user_response.json()
                
                if users:
                    user_id = users[0]['id']
                    
                    # First, try the global reviewer_id query (works on some GitLab instances)
                    mrs_response = requests.get(
                        f'{GITLAB_URL}/api/v4/merge_requests',
                        headers=headers,
                        params={
                            'reviewer_id': user_id,
                            'state': 'opened',
                            'per_page': 50
                        }
                    )
                    mrs_response.raise_for_status()
                    global_mrs = mrs_response.json()
                    
                    # If global query returns nothing, search in projects user is member of
                    if not global_mrs:
                        # Get projects user is a member of (recently active)
                        projects_response = requests.get(
                            f'{GITLAB_URL}/api/v4/projects',
                            headers=headers,
                            params={
                                'membership': 'true',
                                'order_by': 'last_activity_at',
                                'per_page': 20  # Check top 20 recently active projects
                            }
                        )
                        if projects_response.status_code == 200:
                            projects = projects_response.json()
                            for project in projects:
                                project_id = project.get('id')
                                # Get open MRs in this project
                                project_mrs_response = requests.get(
                                    f'{GITLAB_URL}/api/v4/projects/{project_id}/merge_requests',
                                    headers=headers,
                                    params={'state': 'opened', 'per_page': 50}
                                )
                                if project_mrs_response.status_code == 200:
                                    for mr in project_mrs_response.json():
                                        # Check if user is in reviewers list
                                        reviewers = mr.get('reviewers', [])
                                        is_reviewer = any(r.get('id') == user_id or r.get('username') == GITLAB_USERNAME 
                                                         for r in reviewers)
                                        if is_reviewer:
                                            # Avoid duplicates
                                            if not any(m.get('id') == mr.get('id') for m in global_mrs):
                                                global_mrs.append(mr)
                    
                    # Deduplicate MRs by URL
                    seen_urls = set()
                    unique_mrs = []
                    for mr in global_mrs:
                        url = mr.get('web_url', '')
                        if url and url not in seen_urls:
                            seen_urls.add(url)
                            unique_mrs.append(mr)
                    
                    for mr in unique_mrs:
                        # Check if I've already approved
                        has_approved = False
                        try:
                            # Get approval state
                            project_id = mr.get('project_id')
                            mr_iid = mr.get('iid')
                            approvals_response = requests.get(
                                f'{GITLAB_URL}/api/v4/projects/{project_id}/merge_requests/{mr_iid}/approvals',
                                headers=headers
                            )
                            if approvals_response.status_code == 200:
                                approvals = approvals_response.json()
                                for approver in approvals.get('approved_by', []):
                                    if approver.get('user', {}).get('id') == user_id:
                                        has_approved = True
                                        break
                        except:
                            pass  # If we can't check approvals, assume not approved
                        
                        author = mr.get('author', {})
                        # Extract project name from web_url (e.g., https://gitlab.cee.redhat.com/eng/openstack/horizon/-/merge_requests/15)
                        web_url = mr.get('web_url', '')
                        project_name = web_url.split('/-/')[0].split('/')[-1] if '/-/' in web_url else 'N/A'
                        gitlab_awaiting_review.append({
                            'iid': mr.get('iid'),
                            'title': mr.get('title', ''),
                            'project': project_name,
                            'state': mr.get('state', ''),
                            'created_at': mr.get('created_at', ''),
                            'updated_at': mr.get('updated_at', ''),
                            'owner': author.get('name', author.get('username', 'Unknown')),
                            'has_approved': has_approved,
                            'url': mr.get('web_url', '#')
                        })
            except Exception as e:
                print(f"Warning: Could not fetch GitLab MRs awaiting review: {e}", file=sys.stderr)
        
        # GitHub: Query for PRs where I'm a requested reviewer
        github_awaiting_review = []
        if GITHUB_TOKEN:
            try:
                headers = {
                    'Authorization': f'Bearer {GITHUB_TOKEN}',
                    'Accept': 'application/vnd.github+json',
                    'X-GitHub-Api-Version': '2022-11-28'
                }
                
                # GitHub Search API: PRs where I'm a requested reviewer
                # This searches for open PRs that have requested my review
                search_query = f"is:pr is:open review-requested:{GITHUB_USERNAME}"
                prs_response = requests.get(
                    'https://api.github.com/search/issues',
                    headers=headers,
                    params={'q': search_query, 'per_page': 50}
                )
                prs_response.raise_for_status()
                
                for pr in prs_response.json().get('items', []):
                    # Extract repo info from URL
                    # URL format: https://api.github.com/repos/owner/repo/issues/123
                    html_url = pr.get('html_url', '')
                    repo_full = '/'.join(html_url.split('/')[3:5]) if html_url else 'unknown'
                    repo_name = repo_full.split('/')[-1] if repo_full else 'unknown'
                    
                    author = pr.get('user', {})
                    github_awaiting_review.append({
                        'number': pr.get('number'),
                        'title': pr.get('title', ''),
                        'repo': repo_name,
                        'repo_full': repo_full,
                        'state': pr.get('state', ''),
                        'created_at': pr.get('created_at', ''),
                        'updated_at': pr.get('updated_at', ''),
                        'owner': author.get('login', 'Unknown'),
                        'has_reviewed': False,  # If review-requested, we haven't reviewed yet
                        'url': html_url
                    })
                
                # Also check for PRs where I've been asked to review but already submitted a review
                # (These show up differently - as "reviewed" but PR still open)
                reviewed_query = f"is:pr is:open reviewed-by:{GITHUB_USERNAME}"
                reviewed_response = requests.get(
                    'https://api.github.com/search/issues',
                    headers=headers,
                    params={'q': reviewed_query, 'per_page': 50}
                )
                if reviewed_response.status_code == 200:
                    for pr in reviewed_response.json().get('items', []):
                        # Check if we already have this PR
                        pr_number = pr.get('number')
                        html_url = pr.get('html_url', '')
                        if not any(p.get('url') == html_url for p in github_awaiting_review):
                            repo_full = '/'.join(html_url.split('/')[3:5]) if html_url else 'unknown'
                            repo_name = repo_full.split('/')[-1] if repo_full else 'unknown'
                            author = pr.get('user', {})
                            github_awaiting_review.append({
                                'number': pr_number,
                                'title': pr.get('title', ''),
                                'repo': repo_name,
                                'repo_full': repo_full,
                                'state': pr.get('state', ''),
                                'created_at': pr.get('created_at', ''),
                                'updated_at': pr.get('updated_at', ''),
                                'owner': author.get('login', 'Unknown'),
                                'has_reviewed': True,  # We've already reviewed
                                'url': html_url
                            })
            except Exception as e:
                print(f"Warning: Could not fetch GitHub PRs awaiting review: {e}", file=sys.stderr)
        
        # Jira: Query for tickets where I'm a watcher (but not assignee)
        # These are tickets someone wants me to be aware of / review
        jira_watching = []
        if JIRA_API_TOKEN and JIRA_URL:
            try:
                jira_client = JIRA(server=JIRA_URL, token_auth=JIRA_API_TOKEN)
                
                # Query for open tickets where I'm a watcher but NOT the assignee
                # This finds tickets others want me to pay attention to
                watcher_jql = f'watcher = "{JIRA_EMAIL}" AND assignee != "{JIRA_EMAIL}" AND status not in (Done, Closed, Resolved) ORDER BY updated DESC'
                watched_issues = jira_client.search_issues(
                    watcher_jql,
                    maxResults=50,
                    fields='key,summary,issuetype,status,priority,created,updated,assignee,reporter'
                )
                
                for issue in watched_issues:
                    # Get assignee name or reporter if no assignee
                    assignee = issue.fields.assignee
                    reporter = issue.fields.reporter
                    owner = 'Unassigned'
                    if assignee:
                        owner = assignee.displayName if hasattr(assignee, 'displayName') else str(assignee)
                    elif reporter:
                        owner = reporter.displayName if hasattr(reporter, 'displayName') else str(reporter)
                    
                    jira_watching.append({
                        'key': issue.key,
                        'summary': issue.fields.summary,
                        'type': str(issue.fields.issuetype),
                        'status': str(issue.fields.status),
                        'priority': str(issue.fields.priority) if issue.fields.priority else 'None',
                        'created_at': issue.fields.created,
                        'updated_at': issue.fields.updated,
                        'created': issue.fields.created[:10] if issue.fields.created else 'N/A',
                        'updated': issue.fields.updated[:10] if issue.fields.updated else 'N/A',
                        'owner': owner,
                        'url': f"{JIRA_URL}/browse/{issue.key}"
                    })
            except Exception as e:
                print(f"Warning: Could not fetch Jira watched tickets: {e}", file=sys.stderr)
        
        # Generate markdown report
        report_lines = []
        report_lines.append("# In Progress")
        report_lines.append("")
        report_lines.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        report_lines.append("_Current ownership status across all platforms_")
        report_lines.append("")
        report_lines.append("> **Legend:** 🆕 = New this sprint (≤14 days) | Entered = When item was first tracked | Exited = When item was completed")
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("")
        
        # PRIORITY SECTION: People Waiting for Your Review
        report_lines.append("## 🔔 People Waiting for Your Review")
        report_lines.append("")
        report_lines.append("_Reviews/PRs/MRs where you are listed as a reviewer_")
        report_lines.append("")
        
        has_any_awaiting = False
        
        # OpenDev reviews awaiting my review
        if opendev_awaiting_review:
            has_any_awaiting = True
            # Filter to only those not yet voted on
            not_voted = [r for r in opendev_awaiting_review if not r.get('has_voted')]
            already_voted = [r for r in opendev_awaiting_review if r.get('has_voted')]
            
            if not_voted:
                report_lines.append(f"### 🟠 OpenDev: Needs Your Vote ({len(not_voted)})")
                report_lines.append("")
                report_lines.append("| Review | Owner | Project | Subject | Updated | Days | Link |")
                report_lines.append("|--------|-------|---------|---------|---------|------|------|")
                for review in not_voted:
                    review_num = review.get('number', 'N/A')
                    owner = review.get('owner', 'N/A')
                    project = review.get('project', 'N/A').split('/')[-1] if review.get('project') else 'N/A'
                    subject = review.get('subject', 'N/A')
                    if len(subject) > 40:
                        subject = subject[:37] + '...'
                    updated = review.get('updated', 'N/A')[:10] if review.get('updated') else 'N/A'
                    days_idle = days_since_update(review.get('updated'))
                    url = review.get('url', '#')
                    
                    report_lines.append(f"| [{review_num}]({url}) | {owner} | {project} | {subject} | {updated} | {days_idle} | [Review]({url}) |")
                report_lines.append("")
            
            if already_voted:
                report_lines.append(f"### ✅ OpenDev: Already Voted ({len(already_voted)})")
                report_lines.append("")
                report_lines.append("_You've voted on these, but they're still open_")
                report_lines.append("")
                report_lines.append("| Review | Owner | Project | Subject | Updated | Link |")
                report_lines.append("|--------|-------|---------|---------|---------|------|")
                for review in already_voted[:5]:  # Limit to 5
                    review_num = review.get('number', 'N/A')
                    owner = review.get('owner', 'N/A')
                    project = review.get('project', 'N/A').split('/')[-1] if review.get('project') else 'N/A'
                    subject = review.get('subject', 'N/A')
                    if len(subject) > 40:
                        subject = subject[:37] + '...'
                    updated = review.get('updated', 'N/A')[:10] if review.get('updated') else 'N/A'
                    url = review.get('url', '#')
                    
                    report_lines.append(f"| [{review_num}]({url}) | {owner} | {project} | {subject} | {updated} | [View]({url}) |")
                if len(already_voted) > 5:
                    report_lines.append(f"| ... | | | _{len(already_voted) - 5} more_ | | |")
                report_lines.append("")
        
        # GitLab MRs awaiting my review
        if gitlab_awaiting_review:
            has_any_awaiting = True
            # Filter to only those not yet approved
            not_approved = [r for r in gitlab_awaiting_review if not r.get('has_approved')]
            already_approved = [r for r in gitlab_awaiting_review if r.get('has_approved')]
            
            if not_approved:
                report_lines.append(f"### 🦊 GitLab: Needs Your Review ({len(not_approved)})")
                report_lines.append("")
                report_lines.append("| MR | Owner | Project | Updated | Days |")
                report_lines.append("|----|-------|---------|---------|------|")
                for mr in not_approved:
                    mr_iid = mr.get('iid', 'N/A')
                    owner = mr.get('owner', 'N/A')
                    project = mr.get('project', 'N/A').split('/')[-1] if mr.get('project') else 'N/A'
                    title = mr.get('title', 'N/A')
                    if len(title) > 50:
                        title = title[:47] + '...'
                    updated = mr.get('updated_at', 'N/A')[:10] if mr.get('updated_at') else 'N/A'
                    days_idle = days_since_update(mr.get('updated_at'))
                    url = mr.get('url', '#')
                    
                    # Format: MR-15: Use server filter mode for flavors tables
                    mr_link = f"[MR-{mr_iid}: {title}]({url})"
                    report_lines.append(f"| {mr_link} | {owner} | {project} | {updated} | {days_idle} |")
                report_lines.append("")
            
            if already_approved:
                report_lines.append(f"### ✅ GitLab: Already Approved ({len(already_approved)})")
                report_lines.append("")
                report_lines.append("_You've approved these, but they're still open_")
                report_lines.append("")
                report_lines.append("| MR | Owner | Project | Updated |")
                report_lines.append("|----|-------|---------|---------|")
                for mr in already_approved[:5]:  # Limit to 5
                    mr_iid = mr.get('iid', 'N/A')
                    owner = mr.get('owner', 'N/A')
                    project = mr.get('project', 'N/A').split('/')[-1] if mr.get('project') else 'N/A'
                    title = mr.get('title', 'N/A')
                    if len(title) > 50:
                        title = title[:47] + '...'
                    updated = mr.get('updated_at', 'N/A')[:10] if mr.get('updated_at') else 'N/A'
                    url = mr.get('url', '#')
                    
                    # Format: MR-15: Use server filter mode for flavors tables
                    mr_link = f"[MR-{mr_iid}: {title}]({url})"
                    report_lines.append(f"| {mr_link} | {owner} | {project} | {updated} |")
                if len(already_approved) > 5:
                    report_lines.append(f"| ... | | _{len(already_approved) - 5} more_ | |")
                report_lines.append("")
        
        # GitHub PRs awaiting my review
        if github_awaiting_review:
            has_any_awaiting = True
            # Filter to only those not yet reviewed
            not_reviewed = [r for r in github_awaiting_review if not r.get('has_reviewed')]
            already_reviewed = [r for r in github_awaiting_review if r.get('has_reviewed')]
            
            if not_reviewed:
                report_lines.append(f"### 🔵 GitHub: Needs Your Review ({len(not_reviewed)})")
                report_lines.append("")
                report_lines.append("| PR | Owner | Repo | Updated | Days |")
                report_lines.append("|----|-------|------|---------|------|")
                for pr in not_reviewed:
                    pr_num = pr.get('number', 'N/A')
                    owner = pr.get('owner', 'N/A')
                    repo = pr.get('repo', 'N/A')
                    title = pr.get('title', 'N/A')
                    if len(title) > 50:
                        title = title[:47] + '...'
                    updated = pr.get('updated_at', 'N/A')[:10] if pr.get('updated_at') else 'N/A'
                    days_idle = days_since_update(pr.get('updated_at'))
                    url = pr.get('url', '#')
                    
                    # Format: PR-123: Add new feature for widgets
                    pr_link = f"[PR-{pr_num}: {title}]({url})"
                    report_lines.append(f"| {pr_link} | {owner} | {repo} | {updated} | {days_idle} |")
                report_lines.append("")
            
            if already_reviewed:
                report_lines.append(f"### ✅ GitHub: Already Reviewed ({len(already_reviewed)})")
                report_lines.append("")
                report_lines.append("_You've reviewed these, but they're still open_")
                report_lines.append("")
                report_lines.append("| PR | Owner | Repo | Updated |")
                report_lines.append("|----|-------|------|---------|")
                for pr in already_reviewed[:5]:  # Limit to 5
                    pr_num = pr.get('number', 'N/A')
                    owner = pr.get('owner', 'N/A')
                    repo = pr.get('repo', 'N/A')
                    title = pr.get('title', 'N/A')
                    if len(title) > 50:
                        title = title[:47] + '...'
                    updated = pr.get('updated_at', 'N/A')[:10] if pr.get('updated_at') else 'N/A'
                    url = pr.get('url', '#')
                    
                    # Format: PR-123: Add new feature for widgets
                    pr_link = f"[PR-{pr_num}: {title}]({url})"
                    report_lines.append(f"| {pr_link} | {owner} | {repo} | {updated} |")
                if len(already_reviewed) > 5:
                    report_lines.append(f"| ... | | _{len(already_reviewed) - 5} more_ | |")
                report_lines.append("")
        
        # Note: Jira watching section moved to be with other Jira tables at the end
        
        if not has_any_awaiting:
            report_lines.append("_No reviews awaiting your attention_")
            report_lines.append("")
        
        report_lines.append("---")
        report_lines.append("")
        
        # OpenDev Reviews Ownership
        report_lines.append("## 🟠 OpenDev: My Active Reviews")
        report_lines.append("")
        
        active_opendev_reviews = [
            r for r in opendev_data.get('reviews_posted', [])
            if r.get('status') not in ['MERGED', 'ABANDONED']
        ]
        
        if active_opendev_reviews:
            report_lines.append(f"**{len(active_opendev_reviews)} active review(s)**")
            report_lines.append("")
            report_lines.append("| Review | Project | Subject | Status | Entered | Days | Complexity | Link |")
            report_lines.append("|--------|---------|---------|--------|---------|------|------------|------|")
            for review in active_opendev_reviews:
                review_num = review.get('number', 'N/A')
                project = review.get('project', 'N/A').split('/')[-1] if review.get('project') else 'N/A'
                subject = review.get('subject', 'N/A')
                if len(subject) > 35:
                    subject = subject[:32] + '...'
                status = review.get('status', 'N/A')
                url = review.get('url', '#')
                
                # Get tracking info
                first_seen = get_first_seen(tracking_history, 'opendev', str(review_num))
                entered_display = format_entered_date(first_seen)
                days_tracked = get_days_tracked(tracking_history, 'opendev', str(review_num))
                rating = calculate_success_rating(days_tracked)
                rating_emoji = get_rating_emoji(rating)
                
                # Calculate complexity
                complexity_score, _ = calculate_complexity_score(review, 'opendev', OPENDEV_USERNAME)
                complexity_display = get_complexity_display(complexity_score)
                
                status_icon = "🟢" if status == "NEW" else "🟡"
                days_display = f"{days_tracked} {rating_emoji}" if days_tracked != 'N/A' else 'N/A'
                report_lines.append(f"| [{review_num}]({url}) | {project} | {subject} | {status_icon} {status} | {entered_display} | {days_display} | {complexity_display} | [View]({url}) |")
            report_lines.append("")
        else:
            report_lines.append("_No active reviews_")
            report_lines.append("")
        
        # GitHub PRs Ownership
        report_lines.append("## 🔵 GitHub: My Open PRs")
        report_lines.append("")
        
        open_github_prs = [
            pr for pr in github_data.get('prs_created', [])
            if pr.get('state') == 'open'
        ]
        
        if open_github_prs:
            report_lines.append(f"**{len(open_github_prs)} open PR(s)**")
            report_lines.append("")
            report_lines.append("| PR | Repository | Title | Status | Entered | Days | Complexity | Link |")
            report_lines.append("|----|------------|-------|--------|---------|------|------------|------|")
            for pr in open_github_prs:
                pr_num = pr.get('number', 'N/A')
                repo = pr.get('repo', 'N/A')
                title = pr.get('title', 'N/A')
                if len(title) > 40:
                    title = title[:37] + '...'
                state = pr.get('state', 'N/A')
                url = pr.get('html_url', pr.get('url', '#'))
                
                # Get tracking info
                first_seen = get_first_seen(tracking_history, 'github', str(pr_num))
                entered_display = format_entered_date(first_seen)
                days_tracked = get_days_tracked(tracking_history, 'github', str(pr_num))
                rating = calculate_success_rating(days_tracked)
                rating_emoji = get_rating_emoji(rating)
                days_display = f"{days_tracked} {rating_emoji}" if days_tracked != 'N/A' else 'N/A'
                
                # Calculate complexity
                complexity_score, _ = calculate_complexity_score(pr, 'github', GITHUB_USERNAME)
                complexity_display = get_complexity_display(complexity_score)
                
                report_lines.append(f"| [#{pr_num}]({url}) | {repo} | {title} | 🟢 {state.upper()} | {entered_display} | {days_display} | {complexity_display} | [View]({url}) |")
            report_lines.append("")
        else:
            report_lines.append("_No open PRs_")
            report_lines.append("")
        
        # GitLab MRs Ownership
        report_lines.append("## 🦊 GitLab: My Open MRs")
        report_lines.append("")
        
        open_gitlab_mrs = [
            mr for mr in gitlab_data.get('mrs_created', [])
            if mr.get('state') == 'opened'
        ]
        
        if open_gitlab_mrs:
            report_lines.append(f"**{len(open_gitlab_mrs)} open MR(s)**")
            report_lines.append("")
            report_lines.append("| MR | Project | Title | Status | Entered | Days | Complexity | Link |")
            report_lines.append("|----|---------|-------|--------|---------|------|------------|------|")
            for mr in open_gitlab_mrs:
                mr_iid = mr.get('iid', mr.get('id', 'N/A'))
                project = mr.get('project_name', mr.get('project', 'N/A'))
                # Strip MR reference from project name (e.g., "ci-framework/project!123" -> "ci-framework/project")
                if '!' in str(project):
                    project = str(project).split('!')[0]
                title = mr.get('title', 'N/A')
                if len(title) > 40:
                    title = title[:37] + '...'
                state = mr.get('state', 'N/A')
                url = mr.get('url', '#')
                
                # Get tracking info
                first_seen = get_first_seen(tracking_history, 'gitlab', str(mr_iid))
                entered_display = format_entered_date(first_seen)
                days_tracked = get_days_tracked(tracking_history, 'gitlab', str(mr_iid))
                rating = calculate_success_rating(days_tracked)
                rating_emoji = get_rating_emoji(rating)
                days_display = f"{days_tracked} {rating_emoji}" if days_tracked != 'N/A' else 'N/A'
                
                # Calculate complexity
                complexity_score, _ = calculate_complexity_score(mr, 'gitlab', GITLAB_USERNAME)
                complexity_display = get_complexity_display(complexity_score)
                
                report_lines.append(f"| [MR-{mr_iid}]({url}) | {project} | {title} | 🟢 {state.upper()} | {entered_display} | {days_display} | {complexity_display} | [View]({url}) |")
            report_lines.append("")
        else:
            report_lines.append("_No open MRs_")
            report_lines.append("")
        
        # ========== JIRA HEALTH HEATMAP ==========
        # Calculate ticket aging buckets for heatmap
        all_jira_tickets = [
            issue for issue in jira_data.get('issues_assigned', [])
            if issue.get('status') not in ['Done', 'Closed', 'Resolved']
        ]
        
        # Categorize by idle days
        fresh_tickets = []      # 0-3 days
        warm_tickets = []       # 4-7 days
        hot_tickets = []        # 8-14 days
        critical_tickets = []   # 14+ days
        
        for issue in all_jira_tickets:
            days_idle_str = days_since_update(issue.get('updated_at'))
            try:
                days_idle_num = int(days_idle_str) if days_idle_str.isdigit() else 0
            except:
                days_idle_num = 0
            
            if days_idle_num <= 3:
                fresh_tickets.append(issue)
            elif days_idle_num <= 7:
                warm_tickets.append(issue)
            elif days_idle_num <= 14:
                hot_tickets.append(issue)
            else:
                critical_tickets.append(issue)
        
        # Calculate health score (0-100)
        total_tickets = len(all_jira_tickets)
        if total_tickets > 0:
            # Weighted score: fresh=100%, warm=75%, hot=25%, critical=0%
            health_score = int((
                len(fresh_tickets) * 100 +
                len(warm_tickets) * 75 +
                len(hot_tickets) * 25 +
                len(critical_tickets) * 0
            ) / total_tickets)
        else:
            health_score = 100
        
        # Determine health emoji
        if health_score >= 80:
            health_emoji = "🟢"
            health_status = "Excellent"
        elif health_score >= 60:
            health_emoji = "🟡"
            health_status = "Good"
        elif health_score >= 40:
            health_emoji = "🟠"
            health_status = "Needs Attention"
        else:
            health_emoji = "🔴"
            health_status = "Critical"
        
        # Generate heatmap bars (max 20 chars wide)
        def make_bar(count, total, max_width=20):
            if total == 0:
                return ""
            width = int((count / total) * max_width) if total > 0 else 0
            return "█" * max(width, 1) if count > 0 else ""
        
        report_lines.append("## 🌡️ Jira Health Heatmap")
        report_lines.append("")
        report_lines.append(f"**Health Score: {health_score}/100 {health_emoji} {health_status}**")
        report_lines.append("")
        report_lines.append("```")
        report_lines.append(f"🟢 Fresh (0-3 days):    {make_bar(len(fresh_tickets), total_tickets):20s} {len(fresh_tickets)} ticket(s)")
        report_lines.append(f"🟡 Warm (4-7 days):     {make_bar(len(warm_tickets), total_tickets):20s} {len(warm_tickets)} ticket(s)")
        report_lines.append(f"🟠 Hot (8-14 days):     {make_bar(len(hot_tickets), total_tickets):20s} {len(hot_tickets)} ticket(s)")
        if len(critical_tickets) > 0:
            report_lines.append(f"🔴 Critical (14+ days): {make_bar(len(critical_tickets), total_tickets):20s} {len(critical_tickets)} ticket(s) ← ACTION NEEDED")
        else:
            report_lines.append(f"🔴 Critical (14+ days): {make_bar(len(critical_tickets), total_tickets):20s} {len(critical_tickets)} ticket(s)")
        report_lines.append("```")
        report_lines.append("")
        
        # Quick action summary
        if critical_tickets:
            report_lines.append(f"⚠️ **{len(critical_tickets)} ticket(s) need immediate attention:**")
            for issue in critical_tickets[:3]:  # Show top 3
                key = issue.get('key', 'N/A')
                summary = issue.get('summary', 'N/A')[:30] + ('...' if len(issue.get('summary', '')) > 30 else '')
                days_idle_str = days_since_update(issue.get('updated_at'))
                url = issue.get('url', '#')
                report_lines.append(f"- [{key}]({url}): {summary} ({days_idle_str} days idle)")
            if len(critical_tickets) > 3:
                report_lines.append(f"- _...and {len(critical_tickets) - 3} more_")
            report_lines.append("")
        elif hot_tickets:
            report_lines.append(f"📋 **{len(hot_tickets)} ticket(s) warming up** - consider updating soon")
            report_lines.append("")
        else:
            report_lines.append("✅ **All tickets are up to date!** Great job keeping Jira healthy.")
            report_lines.append("")
        
        report_lines.append("---")
        report_lines.append("")
        
        # Jira Tickets Ownership - Open tickets
        report_lines.append("## 📋 Jira: My Open Tickets")
        report_lines.append("")
        
        open_jira_issues = [
            issue for issue in jira_data.get('issues_assigned', [])
            if issue.get('status') not in ['Done', 'Closed', 'Resolved']
        ]
        
        if open_jira_issues:
            report_lines.append(f"**{len(open_jira_issues)} open ticket(s)**")
            report_lines.append("")
            report_lines.append("| Ticket | Summary | Type | Status | Entered | Days Tracked | Days Idle | Link |")
            report_lines.append("|--------|---------|------|--------|---------|--------------|-----------|------|")
            for issue in open_jira_issues:
                key = issue.get('key', 'N/A')
                summary = issue.get('summary', 'N/A')
                if len(summary) > 35:
                    summary = summary[:32] + '...'
                issue_type = issue.get('type', 'N/A')
                status = issue.get('status', 'N/A')
                updated = issue.get('updated_at', 'N/A')[:10] if issue.get('updated_at') else 'N/A'
                days_idle = days_since_update(issue.get('updated_at'))
                url = issue.get('url', '#')
                
                # Get tracking info
                first_seen = get_first_seen(tracking_history, 'jira', key)
                entered_display = format_entered_date(first_seen)
                days_tracked = get_days_tracked(tracking_history, 'jira', key)
                rating = calculate_success_rating(days_tracked)
                rating_emoji = get_rating_emoji(rating)
                days_display = f"{days_tracked} {rating_emoji}" if days_tracked != 'N/A' else 'N/A'
                
                status_icon = get_status_icon(status)
                report_lines.append(f"| [{key}]({url}) | {summary} | {issue_type} | {status_icon} {status} | {entered_display} | {days_display} | {days_idle} | [View]({url}) |")
            report_lines.append("")
        else:
            report_lines.append("_No open tickets_")
            report_lines.append("")
        
        # Jira Tickets Requiring Update - issues idle > 7 days
        report_lines.append("## 📋 Jira: Tickets Requiring Update")
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
        
        # Parse and add Unplanned Work section
        unplanned_file = os.path.join(ACTIVITY_DIR, "unplanned.txt")
        unplanned_done_file = os.path.join(ACTIVITY_DIR, "unplanned_done.txt")
        unplanned_items = parse_unplanned_file(unplanned_file)
        unplanned_done_items = parse_unplanned_done_file(unplanned_done_file)
        
        unplanned_section = generate_unplanned_section(unplanned_items, unplanned_done_items)
        report_lines.append(unplanned_section)
        report_lines.append("---")
        report_lines.append("")
        
        # Jira tickets I'm watching (but not assigned to) - grouped with other Jira tables
        report_lines.append("## 📋 Jira: Watching")
        report_lines.append("")
        report_lines.append("_Tickets you're watching but not assigned to_")
        report_lines.append("")
        
        if jira_watching:
            report_lines.append(f"**{len(jira_watching)} ticket(s)**")
            report_lines.append("")
            report_lines.append("| Ticket | Owner | Type | Summary | Status | Updated | Days Idle | Link |")
            report_lines.append("|--------|-------|------|---------|--------|---------|-----------|------|")
            for ticket in jira_watching[:10]:  # Limit to 10
                key = ticket.get('key', 'N/A')
                owner = ticket.get('owner', 'N/A')
                ticket_type = ticket.get('type', 'N/A')
                summary = ticket.get('summary', 'N/A')
                if len(summary) > 35:
                    summary = summary[:32] + '...'
                status = ticket.get('status', 'N/A')
                updated = ticket.get('updated', 'N/A')
                days_idle = days_since_update(ticket.get('updated_at'))
                url = ticket.get('url', '#')
                
                report_lines.append(f"| [{key}]({url}) | {owner} | {ticket_type} | {summary} | {status} | {updated} | {days_idle} | [View]({url}) |")
            if len(jira_watching) > 10:
                report_lines.append(f"| ... | | | _{len(jira_watching) - 10} more_ | | | | |")
            report_lines.append("")
        else:
            report_lines.append("_Not watching any tickets_")
            report_lines.append("")
        
        report_lines.append("---")
        report_lines.append("")
        report_lines.append(f"_Generated by mymcp activity-tracker on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_  ")
        report_lines.append(f"_Compared against previous run for Success Stories_")
        
        # Build current state for JSON caching
        current_state = {
            'generated': datetime.now().isoformat(),
            'opendev_reviews': [
                {
                    'id': str(r.get('number', '')),
                    'type': 'opendev',
                    'project': r.get('project', ''),
                    'subject': r.get('subject', ''),
                    'status': r.get('status', ''),
                    'owner': r.get('owner', ''),
                    'url': r.get('url', ''),
                    'updated': r.get('updated', ''),
                    'is_mine': True
                }
                for r in opendev_data.get('reviews_posted', [])
                if r.get('status') not in ['MERGED', 'ABANDONED']
            ],
            'github_prs': [
                {
                    'id': str(pr.get('number', '')),
                    'type': 'github',
                    'repo': pr.get('repo', ''),
                    'title': pr.get('title', ''),
                    'state': pr.get('state', ''),
                    'owner': 'me',
                    'url': pr.get('url', ''),
                    'updated': pr.get('updated_at', ''),
                    'is_mine': True
                }
                for pr in github_data.get('prs_created', [])
                if pr.get('state') == 'open'
            ],
            'gitlab_mrs': [
                {
                    'id': str(mr.get('iid', '')),
                    'type': 'gitlab',
                    'project': mr.get('project', ''),
                    'title': mr.get('title', ''),
                    'state': mr.get('state', ''),
                    'owner': 'me',
                    'url': mr.get('url', ''),
                    'updated': mr.get('updated_at', ''),
                    'is_mine': True
                }
                for mr in gitlab_data.get('mrs_created', [])
                if mr.get('state') == 'opened'
            ],
            'jira_tickets': [
                {
                    'id': issue.get('key', ''),
                    'type': 'jira',
                    'summary': issue.get('summary', ''),
                    'status': issue.get('status', ''),
                    'issue_type': issue.get('type', ''),
                    'owner': 'me',
                    'url': issue.get('url', ''),
                    'updated': issue.get('updated_at', ''),
                    'is_mine': True
                }
                for issue in jira_data.get('issues_assigned', [])
                if issue.get('status') not in ['Done', 'Closed', 'Resolved']
            ],
            'jira_watching': [
                {
                    'id': t.get('key', ''),
                    'type': 'jira_watching',
                    'summary': t.get('summary', ''),
                    'status': t.get('status', ''),
                    'issue_type': t.get('type', ''),
                    'owner': t.get('owner', ''),
                    'url': t.get('url', ''),
                    'updated': t.get('updated_at', ''),
                    'is_mine': False
                }
                for t in jira_watching
            ],
            'awaiting_review': {
                'opendev': [
                    {
                        'id': str(r.get('number', '')),
                        'type': 'opendev_review',
                        'owner': r.get('owner', ''),
                        'subject': r.get('subject', ''),
                        'url': r.get('url', ''),
                        'is_mine': False
                    }
                    for r in opendev_awaiting_review
                ],
                'gitlab': [
                    {
                        'id': str(mr.get('iid', '')),
                        'type': 'gitlab_review',
                        'owner': mr.get('owner', ''),
                        'title': mr.get('title', ''),
                        'url': mr.get('url', ''),
                        'is_mine': False
                    }
                    for mr in gitlab_awaiting_review
                ],
                'github': [
                    {
                        'id': str(pr.get('number', '')),
                        'type': 'github_review',
                        'owner': pr.get('owner', ''),
                        'title': pr.get('title', ''),
                        'url': pr.get('url', ''),
                        'is_mine': False
                    }
                    for pr in github_awaiting_review
                ]
            }
        }
        
        # Build flat list of all current items for tracking history
        all_current_items = []
        all_current_items.extend(current_state['opendev_reviews'])
        all_current_items.extend(current_state['github_prs'])
        all_current_items.extend(current_state['gitlab_mrs'])
        all_current_items.extend(current_state['jira_tickets'])
        all_current_items.extend(current_state['jira_watching'])
        all_current_items.extend(current_state['awaiting_review']['opendev'])
        all_current_items.extend(current_state['awaiting_review']['gitlab'])
        all_current_items.extend(current_state['awaiting_review']['github'])
        
        # Update tracking history with current items (records first_seen for new items)
        tracking_history = update_tracking_history(tracking_history, all_current_items)
        
        # Load previous state and compare for Success Stories
        previous_file = os.path.join(ACTIVITY_DIR, "in_progress_previous.json")
        current_file = os.path.join(ACTIVITY_DIR, "in_progress.json")
        success_stories = []
        
        if os.path.exists(current_file):
            try:
                with open(current_file, 'r') as f:
                    previous_state = json.load(f)
                
                # Compare and find items that disappeared (completed/closed/merged)
                # This also records completions to quarterly stats
                success_stories = compare_states_for_success(previous_state, current_state, tracking_history)
                
                # Archive current as previous before overwriting
                import shutil
                shutil.copy(current_file, previous_file)
                
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load previous state: {e}", file=sys.stderr)
        
        # Save current state
        try:
            with open(current_file, 'w') as f:
                json.dump(current_state, f, indent=2, default=str)
            print(f"State cached to {current_file}", file=sys.stderr)
        except IOError as e:
            print(f"Warning: Could not save state: {e}", file=sys.stderr)
        
        # Save tracking history (with first_seen dates and quarterly stats)
        save_tracking_history(tracking_history)
        
        # Count current active items for sprint flow summary
        current_items_count = (
            len(active_opendev_reviews) +
            len(open_github_prs) +
            len(open_gitlab_mrs) +
            len(open_jira_issues)
        )
        
        # Generate Sprint Flow Summary
        sprint_flow_section = generate_sprint_flow_summary(tracking_history, current_items_count)
        
        # Insert Success Stories section at the top (after header)
        success_section = generate_success_stories_section(success_stories, tracking_history, unplanned_done_items)
        
        # Build timeline state with complexity scores for timeline estimates
        timeline_state = {
            'opendev': [
                {
                    'number': r.get('number'),
                    'subject': r.get('subject', ''),
                    'status': r.get('status', ''),
                    'url': r.get('url', ''),
                    'complexity_score': calculate_complexity_score(r, 'opendev', OPENDEV_USERNAME)[0]
                }
                for r in opendev_data.get('reviews_posted', [])
                if r.get('status') not in ['MERGED', 'ABANDONED']
            ],
            'github': [
                {
                    'number': pr.get('number'),
                    'title': pr.get('title', ''),
                    'url': pr.get('url', ''),
                    'complexity_score': calculate_complexity_score(pr, 'github', GITHUB_USERNAME)[0]
                }
                for pr in github_data.get('prs_created', [])
                if pr.get('state') == 'open'
            ],
            'gitlab': [
                {
                    'iid': mr.get('iid'),
                    'title': mr.get('title', ''),
                    'url': mr.get('url', ''),
                    'complexity_score': calculate_complexity_score(mr, 'gitlab', GITLAB_USERNAME)[0]
                }
                for mr in gitlab_data.get('mrs_created', [])
                if mr.get('state') == 'opened'
            ],
            'jira': [
                {
                    'key': issue.get('key'),
                    'summary': issue.get('summary', ''),
                    'url': issue.get('url', ''),
                    'fix_version': issue.get('fix_version'),
                    'complexity_score': calculate_complexity_score(issue, 'jira')[0]
                }
                for issue in jira_data.get('issues_assigned', [])
                if issue.get('status') not in ['Done', 'Closed', 'Resolved']
            ],
            'opendev_awaiting': [
                {
                    'number': r.get('number'),
                    'subject': r.get('subject', ''),
                    'url': r.get('url', ''),
                    'owner': r.get('owner', 'N/A'),
                    'has_voted': r.get('has_voted', False),
                    'complexity_score': calculate_complexity_score(r, 'opendev', OPENDEV_USERNAME)[0]
                }
                for r in opendev_awaiting_review
            ],
            'gitlab_awaiting': [
                {
                    'iid': mr.get('iid'),
                    'title': mr.get('title', ''),
                    'url': mr.get('url', ''),
                    'owner': mr.get('owner', 'N/A'),
                    'has_approved': mr.get('has_approved', False),
                    'complexity_score': calculate_complexity_score(mr, 'gitlab', GITLAB_USERNAME)[0]
                }
                for mr in gitlab_awaiting_review
            ],
            'github_awaiting': [
                {
                    'number': pr.get('number'),
                    'title': pr.get('title', ''),
                    'url': pr.get('url', ''),
                    'owner': pr.get('owner', 'N/A'),
                    'has_reviewed': pr.get('has_reviewed', False),
                    'complexity_score': calculate_complexity_score(pr, 'github', GITHUB_USERNAME)[0]
                }
                for pr in github_awaiting_review
            ]
        }
        
        # Generate Timeline Estimates section
        timeline_section = generate_timeline_estimates_section(timeline_state, tracking_history)
        
        # Build the final report
        report = "\n".join(report_lines)
        
        # Insert Success Stories and Timeline AFTER the "My Open MRs" section
        # This keeps People Waiting, OpenDev, GitHub, GitLab sections first
        # Look for the marker after GitLab section (before Jira Health or Jira Assigned)
        if success_section or timeline_section:
            # Find the Jira Health Heatmap or Jira Assigned section as insertion point
            jira_marker = "## 🌡️ Jira Health Heatmap"
            jira_assigned_marker = "## 📋 Jira: Assigned to Me"
            
            insertion_marker = None
            if jira_marker in report:
                insertion_marker = jira_marker
            elif jira_assigned_marker in report:
                insertion_marker = jira_assigned_marker
            
            if insertion_marker:
                parts = report.split(insertion_marker, 1)
                if len(parts) == 2:
                    sections_to_insert = ""
                    if sprint_flow_section:
                        sections_to_insert += sprint_flow_section + "\n\n---\n\n"
                    if success_section:
                        sections_to_insert += success_section + "\n\n---\n\n"
                    if timeline_section:
                        sections_to_insert += timeline_section + "\n\n---\n\n"
                    report = parts[0] + sections_to_insert + insertion_marker + parts[1]
        
        # Save report to workspace
        report_file = os.path.join(ACTIVITY_DIR, "in_progress.md")
        try:
            with open(report_file, 'w') as f:
                f.write(report)
            print(f"In-progress report saved to {report_file}", file=sys.stderr)
        except IOError as e:
            print(f"Warning: Could not save report to {report_file}: {e}", file=sys.stderr)
        
        return report
        
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



