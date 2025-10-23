#!/usr/bin/env python3
"""
OpenDev.Review MCP Agent
An MCP server that analyzes OpenDev Gerrit reviews for code review.
"""

import os
import sys
import json
import requests
import re
import asyncio
from datetime import datetime
from fastmcp import FastMCP

def extract_change_number(review_url):
    """Extract change number from OpenDev.Review URL."""
    # Pattern to match URLs like: https://review.opendev.org/c/openstack/horizon/+/963261
    pattern = r'review\.opendev\.org/c/[^/]+/[^/]+/\+/(\d+)'
    match = re.search(pattern, review_url)
    if match:
        return match.group(1)
    return None

def gerrit_review_fetcher(review_url: str):
    """
    Fetches review data from OpenDev's Gerrit system.
    
    Args:
        review_url: The full URL to the OpenDev.Review change (e.g., 
                   https://review.opendev.org/c/openstack/horizon/+/963261)
    
    Returns:
        Dictionary containing review metadata and analysis prompt
    """
    if "review.opendev.org" not in review_url:
        return {"error": "Invalid OpenDev Gerrit URL provided."}

    # Extract change number from the URL
    change_number = extract_change_number(review_url)
    if not change_number:
        return {"error": "Could not extract change number from URL. Expected format: https://review.opendev.org/c/project/repo/+/CHANGE_NUMBER"}

    # Gerrit REST API endpoints
    change_url = f"https://review.opendev.org/changes/{change_number}/detail"
    files_url = f"https://review.opendev.org/changes/{change_number}/revisions/current/files"
    comments_url = f"https://review.opendev.org/changes/{change_number}/comments"

    try:
        # Fetch the change details
        response = requests.get(change_url, timeout=10)
        response.raise_for_status()
        # Gerrit API responses start with a security prefix that needs to be stripped
        json_content = response.text
        if json_content.startswith(")]}'"):
            json_content = json_content[4:]
        change_data = json.loads(json_content)

        # Fetch the list of files changed
        files_response = requests.get(files_url, timeout=10)
        files_response.raise_for_status()
        files_json_content = files_response.text
        if files_json_content.startswith(")]}'"):
            files_json_content = files_json_content[4:]
        files_data = json.loads(files_json_content)

        # Fetch comments if available
        comments_response = requests.get(comments_url, timeout=10)
        if comments_response.status_code == 200:
            comments_json_content = comments_response.text
            if comments_json_content.startswith(")]}'"):
                comments_json_content = comments_json_content[4:]
            comments_data = json.loads(comments_json_content)
        else:
            comments_data = {}

        # Process the change data
        title = change_data.get('subject', 'No title available')
        author = change_data.get('owner', {}).get('name', 'Unknown author')
        author_email = change_data.get('owner', {}).get('email', '')
        project = change_data.get('project', 'Unknown project')
        branch = change_data.get('branch', 'Unknown branch')
        status = change_data.get('status', 'Unknown status')
        created = change_data.get('created', 'Unknown creation date')
        updated = change_data.get('updated', 'Unknown update date')
        
        # Extract topic if available
        topic = change_data.get('topic', '')
        
        # Get commit message
        commit_message = change_data.get('commitMessage', '')
        
        # Process files changed
        files_changed = []
        file_stats = []
        
        for file_path, file_info in files_data.items():
            if file_path == '/COMMIT_MSG':
                continue
                
            files_changed.append(file_path)
            
            # Extract file statistics
            lines_inserted = file_info.get('lines_inserted', 0)
            lines_deleted = file_info.get('lines_deleted', 0)
            file_stats.append({
                'file': file_path,
                'insertions': lines_inserted,
                'deletions': lines_deleted,
                'net_changes': lines_inserted - lines_deleted
            })

        # Calculate total changes
        total_insertions = sum(stat['insertions'] for stat in file_stats)
        total_deletions = sum(stat['deletions'] for stat in file_stats)
        total_files = len(files_changed)

        # Process comments for review insights
        review_comments = []
        if comments_data:
            for file_path, file_comments in comments_data.items():
                for comment in file_comments:
                    review_comments.append({
                        'file': file_path,
                        'line': comment.get('line', 0),
                        'message': comment.get('message', ''),
                        'author': comment.get('author', {}).get('name', 'Unknown')
                    })

        # Construct the review prompt
        review_prompt = f"""
Analyze the OpenDev.Review change for {project}:

**Change Summary:**
- Title: {title}
- Author: {author} ({author_email})
- Project: {project}
- Branch: {branch}
- Status: {status}
- Files Changed: {total_files}
- Lines: +{total_insertions}/-{total_deletions}

**Files Modified:**
{chr(10).join([f"- {file}" for file in files_changed[:10]])}
{f"... and {len(files_changed) - 10} more files" if len(files_changed) > 10 else ""}

**Review Focus Areas:**
1. Code quality and adherence to OpenStack standards
2. Security implications of the changes
3. Performance impact
4. Backward compatibility
5. Test coverage and documentation
6. Compliance with project coding guidelines

Please provide a comprehensive code review focusing on these areas.
"""

        return {
            "change_number": change_number,
            "title": title,
            "author": author,
            "author_email": author_email,
            "project": project,
            "branch": branch,
            "status": status,
            "topic": topic,
            "created": created,
            "updated": updated,
            "commit_message": commit_message,
            "files_changed": files_changed,
            "file_stats": file_stats,
            "total_files": total_files,
            "total_insertions": total_insertions,
            "total_deletions": total_deletions,
            "review_comments": review_comments,
            "review_prompt": review_prompt.strip()
        }

    except requests.RequestException as e:
        return {"error": f"Failed to fetch review data: {str(e)}"}
    except KeyError as e:
        return {"error": f"Unexpected data format: missing key {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

async def main():
    """Main function to set up and run the MCP server."""
    mcp = FastMCP(
        name="opendev-reviewer",
        instructions="An agent that analyzes and summarizes OpenDev Gerrit reviews for code review.",
        tools=[gerrit_review_fetcher]
    )

    # Run the server using standard I/O (stdio) transport
    await mcp.run_stdio_async()

if __name__ == "__main__":
    asyncio.run(main())
