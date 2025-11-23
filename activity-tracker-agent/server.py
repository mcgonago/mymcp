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

# Initialize FastMCP server
mcp = FastMCP("Activity Tracker")

# Configuration from environment
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
CACHE_MAX_AGE_HOURS = int(os.environ.get('CACHE_MAX_AGE_HOURS', '24'))
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')

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
        end = today
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
            params={'q': reviewer_query, 'o': ['DETAILED_ACCOUNTS', 'MESSAGES', 'ALL_REVISIONS']}
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
def generate_status_report(
    time_range: str = "last week",
    format: str = "markdown"
) -> str:
    """
    Generate a status report for the given time range.
    
    Combines GitHub and OpenDev activities, caches data,
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
            print(f"Using cached data for week {week_number}", file=sys.stderr)
        else:
            # Fetch fresh data
            print(f"Fetching fresh data for {start_date} to {end_date}...", file=sys.stderr)
            github_data = get_github_activity(start_date, end_date)
            opendev_data = get_opendev_activity(start_date, end_date)
            
            # Cache it
            cache_data = {
                'github': github_data,
                'opendev': opendev_data,
                'generated_at': datetime.now().isoformat()
            }
            cache_activity(week_number, cache_data)
            print(f"Cached data to {week_number}.json", file=sys.stderr)
        
        # Format report
        if format == "json":
            return json.dumps({
                'github': github_data,
                'opendev': opendev_data
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
            
            report_lines.append("| Platform | PRs/Reviews | Comments | Commits | Issues | Votes | Other |")
            report_lines.append("|----------|-------------|----------|---------|--------|-------|-------|")
            report_lines.append(f"| **GitHub** | {gh_prs_created} | {gh_prs_reviewed} reviews | {gh_commits} | {gh_issues} | 0 | {gh_other} |")
            report_lines.append(f"| **OpenDev** | {od_reviews} new | {od_comments} | 0 | 0 | {od_votes} | {od_other} |")
            report_lines.append(f"| **Total** | **{gh_prs_created + od_reviews}** | **{gh_prs_reviewed + od_comments}** | **{gh_commits}** | **{gh_issues}** | **{od_votes}** | {total_other} |")
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



