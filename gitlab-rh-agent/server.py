#!/usr/bin/env python3
"""
GitLab Issue/MR/Commit Review MCP Agent
An MCP server that analyzes GitLab Issues, Merge Requests, and Commits from internal Red Hat GitLab.
"""

import os
import sys
import json
import asyncio
import requests
import re
import warnings
from urllib.parse import quote_plus, urlparse
from fastmcp import FastMCP

# Suppress SSL warnings for internal GitLab (self-signed cert)
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

def extract_gitlab_info(input_path: str):
    """
    Extract project path, resource type, and ID from GitLab path or URL.
    
    Supports:
    - Path format: 'group/project/issues/123' or 'group/project/merge_requests/456' or 'group/project/commit/abc123'
    - URL format: 'https://gitlab.cee.redhat.com/group/project/-/commit/abc123'
    """
    # If it's a URL, extract the path components
    if input_path.startswith('http://') or input_path.startswith('https://'):
        parsed = urlparse(input_path)
        # Extract path: /group/project/-/commit/sha or /group/project/-/issues/123
        path = parsed.path.lstrip('/')
        
        # Handle URL format: group/project/-/commit/sha
        if '/-/' in path:
            parts = path.split('/-/')
            project_path = parts[0]
            resource_parts = parts[1].split('/')
            if len(resource_parts) >= 2:
                resource_type = resource_parts[0]  # 'commit', 'issues', 'merge_requests'
                target_id = resource_parts[1]
                return {
                    'project_path': project_path,
                    'resource_type': resource_type,
                    'id': target_id
                }
    
    # Handle direct path format: group/project/issues/123 or group/project/commit/sha
    parts = input_path.split('/')
    if len(parts) < 4:
        return None
    
    # The project path is everything up to the resource type (e.g., 'group/project')
    project_name_with_namespace = '/'.join(parts[:-2])
    resource_type = parts[-2]  # 'issues', 'merge_requests', or 'commit'
    target_id = parts[-1]
    
    return {
        'project_path': project_name_with_namespace,
        'resource_type': resource_type,
        'id': target_id
    }

def gitlab_resource_fetcher(resource_path: str):
    """
    Fetches details for a specific GitLab resource (Issue, Merge Request, or Commit).
    
    Args:
        resource_path: Supports multiple formats:
                      - Path: 'group/project/issues/123' or 'group/project/merge_requests/456' or 'group/project/commit/abc123'
                      - URL: 'https://gitlab.cee.redhat.com/group/project/-/commit/abc123'
    
    Returns:
        Dictionary containing resource metadata and analysis prompt
    """
    # Configuration
    GITLAB_URL = "https://gitlab.cee.redhat.com/api/v4"
    
    # Get GitLab token from environment variable
    gitlab_token = os.getenv('GITLAB_TOKEN')
    if not gitlab_token:
        return {
            "error": "GITLAB_TOKEN environment variable not set. Please set it to your GitLab personal access token.",
            "instructions": "To set the token: export GITLAB_TOKEN='your_token_here'"
        }
    
    # Extract info from path or URL
    info = extract_gitlab_info(resource_path)
    if not info:
        return {"error": "Invalid format. Supported formats: 'group/project/issues/123', 'group/project/merge_requests/456', 'group/project/commit/sha', or full URLs"}
    
    try:
        # URL-encode the project path for the API call
        project_id_encoded = quote_plus(info['project_path'])
        headers = {"Private-Token": gitlab_token}
        
        # Handle commits differently from issues/MRs
        if info['resource_type'] == 'commit':
            # Fetch commit details
            endpoint = f"{GITLAB_URL}/projects/{project_id_encoded}/repository/commits/{info['id']}"
            response = requests.get(endpoint, headers=headers, timeout=10, verify=False)
            response.raise_for_status()
            commit_data = response.json()
            
            # Fetch commit diff
            diff_endpoint = f"{GITLAB_URL}/projects/{project_id_encoded}/repository/commits/{info['id']}/diff"
            diff_response = requests.get(diff_endpoint, headers=headers, timeout=10, verify=False)
            diff_response.raise_for_status()
            diff_data = diff_response.json()
            
            # Extract commit details
            title = commit_data.get("title")
            message = commit_data.get("message", "")
            author_name = commit_data.get("author_name", "Unknown")
            author_email = commit_data.get("author_email", "")
            committer_name = commit_data.get("committer_name", "Unknown")
            authored_date = commit_data.get("authored_date", "Unknown")
            committed_date = commit_data.get("committed_date", "Unknown")
            web_url = commit_data.get("web_url")
            stats = commit_data.get("stats", {})
            additions = stats.get("additions", 0)
            deletions = stats.get("deletions", 0)
            total_changes = stats.get("total", 0)
            
            # Format diff summary
            files_changed = []
            for diff in diff_data[:10]:  # Limit to first 10 files
                file_path = diff.get("new_path", diff.get("old_path", "unknown"))
                files_changed.append(f"  - {file_path}")
            
            files_summary = "\n".join(files_changed)
            if len(diff_data) > 10:
                files_summary += f"\n  ... and {len(diff_data) - 10} more files"
            
            # Build analysis prompt
            analysis_prompt = f"""
Please analyze the following GitLab Commit:

**Commit: {title}**
- SHA: {info['id'][:8]}
- Author: {author_name} <{author_email}>
- Committer: {committer_name}
- Project: {info['project_path']}
- Authored: {authored_date}
- Committed: {committed_date}
- Changes: +{additions} -{deletions} ({total_changes} lines total)

**Commit Message:**
{message}

**Files Changed ({len(diff_data)}):**
{files_summary}

**URL:** {web_url}

Please provide analysis focusing on:
1. What is the purpose and scope of this commit?
2. Are there any security implications (CVEs, vulnerabilities)?
3. What are the key technical changes?
4. Potential risks or areas requiring careful review
5. Suggested testing or validation steps
"""

            return {
                "resource_type": "Commit",
                "sha": info['id'],
                "short_sha": info['id'][:8],
                "title": title,
                "message": message,
                "author_name": author_name,
                "author_email": author_email,
                "committer_name": committer_name,
                "authored_date": authored_date,
                "committed_date": committed_date,
                "web_url": web_url,
                "stats": {
                    "additions": additions,
                    "deletions": deletions,
                    "total": total_changes
                },
                "files_changed": len(diff_data),
                "analysis_prompt": analysis_prompt.strip()
            }
        
        else:
            # Handle issues and merge requests
            endpoint = f"{GITLAB_URL}/projects/{project_id_encoded}/{info['resource_type']}/{info['id']}"
            response = requests.get(endpoint, headers=headers, timeout=10, verify=False)
            response.raise_for_status()
            data = response.json()
            
            # Determine if this is an issue or merge request
            resource_name = "Issue" if info['resource_type'] == "issues" else "Merge Request"
            
            # Extract common fields
            title = data.get("title")
            state = data.get("state")
            description = data.get("description", "No description provided.")
            web_url = data.get("web_url")
            author = data.get("author", {}).get("username", "Unknown")
            created_at = data.get("created_at", "Unknown")
            updated_at = data.get("updated_at", "Unknown")
            assignees = [a.get("username") for a in data.get("assignees", [])]
            labels = data.get("labels", [])
            
            # Build analysis prompt
            analysis_prompt = f"""
Please analyze the following GitLab {resource_name}:

**{resource_name} #{info['id']}: {title}**
- Author: {author}
- State: {state}
- Project: {info['project_path']}
- Created: {created_at}
- Updated: {updated_at}
- Assignees: {', '.join(assignees) if assignees else 'None'}
- Labels: {', '.join(labels) if labels else 'None'}

**Description:**
{description[:500]}{'...' if len(description) > 500 else ''}

**URL:** {web_url}

Please provide analysis focusing on:
1. The nature and scope of the {resource_name.lower()}
2. Current state and progress
3. Key areas of concern or attention needed
4. Suggested next steps or actions
"""

            return {
                "resource_type": resource_name,
                "id": info['id'],
                "title": title,
                "state": state,
                "description": description,
                "web_url": web_url,
                "author": author,
                "created_at": created_at,
                "updated_at": updated_at,
                "assignees": assignees,
                "labels": labels,
                "analysis_prompt": analysis_prompt.strip()
            }

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return {"error": f"Resource not found. Please check the format and ensure you have access to this {info.get('resource_type', 'resource')}."}
        elif e.response.status_code == 401:
            return {"error": "Authentication failed. Please check your GITLAB_TOKEN."}
        else:
            return {"error": f"API Request Failed: {e.response.status_code} - {e.response.text}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"API Request Failed: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

# --- Main MCP Server Setup ---
async def main():
    """Main function to set up and run the MCP server."""
    mcp = FastMCP(
        name="gitlab-cee-agent",
        instructions="An agent that analyzes and summarizes GitLab issues, merge requests, and commits from internal Red Hat GitLab (gitlab.cee.redhat.com).",
        tools=[gitlab_resource_fetcher]
    )

    # Run the server using standard I/O (stdio) transport
    await mcp.run_stdio_async()

if __name__ == "__main__":
    asyncio.run(main())



