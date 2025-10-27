#!/usr/bin/env python3
"""
GitLab Issue/MR Review MCP Agent
An MCP server that analyzes GitLab Issues and Merge Requests from internal Red Hat GitLab.
"""

import os
import sys
import json
import asyncio
import requests
from urllib.parse import quote_plus
from fastmcp import FastMCP

def extract_gitlab_info(issue_path: str):
    """
    Extract project path, resource type, and ID from GitLab path.
    
    Example: 'group/project/issues/123' or 'group/project/merge_requests/456'
    """
    parts = issue_path.split('/')
    if len(parts) < 4:
        return None
    
    # The project path is everything up to the resource type (e.g., 'group/project')
    project_name_with_namespace = '/'.join(parts[:-2])
    resource_type = parts[-2]  # 'issues' or 'merge_requests'
    target_id = parts[-1]
    
    return {
        'project_path': project_name_with_namespace,
        'resource_type': resource_type,
        'id': target_id
    }

def gitlab_issue_fetcher(issue_path: str):
    """
    Fetches details for a specific GitLab Issue or Merge Request.
    
    Args:
        issue_path: Path format: 'group/project/issues/123' or 'group/project/merge_requests/456'
    
    Returns:
        Dictionary containing issue/MR metadata and analysis prompt
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
    
    # Extract info from path
    info = extract_gitlab_info(issue_path)
    if not info:
        return {"error": "Invalid path format. Use format like 'group/project/issues/123' or 'group/project/merge_requests/456'"}
    
    try:
        # URL-encode the project path for the API call
        project_id_encoded = quote_plus(info['project_path'])
        
        # Construct the specific endpoint
        endpoint = f"{GITLAB_URL}/projects/{project_id_encoded}/{info['resource_type']}/{info['id']}"
        
        headers = {"Private-Token": gitlab_token}
        
        response = requests.get(endpoint, headers=headers, timeout=10)
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
            return {"error": f"Resource not found. Please check the path format and ensure you have access to this {info['resource_type']}."}
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
        instructions="An agent that analyzes and summarizes GitLab issues and merge requests from internal Red Hat GitLab (gitlab.cee.redhat.com).",
        tools=[gitlab_issue_fetcher]
    )

    # Run the server using standard I/O (stdio) transport
    await mcp.run_stdio_async()

if __name__ == "__main__":
    asyncio.run(main())

