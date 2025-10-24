#!/usr/bin/env python3
"""
GitHub PR Review MCP Agent
An MCP server that analyzes GitHub Pull Requests for code review.
"""

import os
import sys
import json
import asyncio
import re
from github import Github, GithubException, Auth
from fastmcp import FastMCP

def extract_pr_info(pr_url: str):
    """Extract owner, repo, and PR number from GitHub URL."""
    # Pattern to match URLs like: https://github.com/owner/repo/pull/123
    pattern = r'github\.com/([^/]+)/([^/]+)/pull/(\d+)'
    match = re.search(pattern, pr_url)
    if match:
        return {
            'owner': match.group(1),
            'repo': match.group(2),
            'pr_number': int(match.group(3))
        }
    return None

def github_pr_fetcher(pr_url: str):
    """
    Fetches PR data from GitHub's API.
    
    Args:
        pr_url: The full URL to the GitHub PR (e.g., 
               https://github.com/openstack-k8s-operators/horizon-operator/pull/402)
    
    Returns:
        Dictionary containing PR metadata and analysis prompt
    """
    if "github.com" not in pr_url:
        return {"error": "Invalid GitHub URL provided."}

    # Extract PR info from URL
    pr_info = extract_pr_info(pr_url)
    if not pr_info:
        return {"error": "Could not extract PR info from URL. Expected format: https://github.com/owner/repo/pull/NUMBER"}

    # Get GitHub token from environment variable
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token:
        return {
            "error": "GITHUB_TOKEN environment variable not set. Please set it to your GitHub personal access token.",
            "instructions": "To set the token: export GITHUB_TOKEN='your_token_here'"
        }

    try:
        # Initialize GitHub client
        auth = Auth.Token(github_token)
        g = Github(auth=auth)
        
        # Get the repository and pull request
        repo = g.get_repo(f"{pr_info['owner']}/{pr_info['repo']}")
        pr = repo.get_pull(pr_info['pr_number'])
        
        # Get PR metadata
        title = pr.title
        author = pr.user.login
        author_email = pr.user.email if pr.user.email else "N/A"
        state = pr.state
        created_at = pr.created_at.isoformat()
        updated_at = pr.updated_at.isoformat()
        merged = pr.merged
        merged_at = pr.merged_at.isoformat() if pr.merged_at else None
        body = pr.body if pr.body else "No description provided."
        
        # Get file changes
        files_changed = []
        total_additions = 0
        total_deletions = 0
        
        for file in pr.get_files():
            files_changed.append({
                'filename': file.filename,
                'status': file.status,
                'additions': file.additions,
                'deletions': file.deletions,
                'changes': file.changes,
                'patch': file.patch if hasattr(file, 'patch') else None
            })
            total_additions += file.additions
            total_deletions += file.deletions
        
        # Get review comments
        review_comments = []
        for comment in pr.get_review_comments():
            review_comments.append({
                'author': comment.user.login,
                'body': comment.body,
                'path': comment.path,
                'created_at': comment.created_at.isoformat()
            })
        
        # Get issue comments (PR comments)
        pr_comments = []
        for comment in pr.get_issue_comments():
            pr_comments.append({
                'author': comment.user.login,
                'body': comment.body,
                'created_at': comment.created_at.isoformat()
            })
        
        # Create file stats summary
        file_stats = "\n".join([
            f"  {f['filename']}: +{f['additions']} -{f['deletions']} ({f['status']})"
            for f in files_changed
        ])
        
        # Build review prompt
        review_prompt = f"""
Please review the following GitHub Pull Request:

**PR #{pr_info['pr_number']}: {title}**
- Author: {author}
- State: {state} {'(merged)' if merged else ''}
- Repository: {pr_info['owner']}/{pr_info['repo']}
- Created: {created_at}
- Updated: {updated_at}

**Description:**
{body}

**Files Changed ({len(files_changed)} files):**
{file_stats}

**Summary:**
- Total additions: {total_additions}
- Total deletions: {total_deletions}

**Review Comments:** {len(review_comments)} code review comments
**PR Comments:** {len(pr_comments)} general comments

Please provide a comprehensive code review focusing on:
1. Code quality and best practices
2. Security implications of the changes
3. Performance impact
4. Backward compatibility
5. Test coverage and documentation
6. Compliance with project coding guidelines
"""

        return {
            "pr_number": pr_info['pr_number'],
            "title": title,
            "author": author,
            "author_email": author_email,
            "state": state,
            "merged": merged,
            "merged_at": merged_at,
            "repository": f"{pr_info['owner']}/{pr_info['repo']}",
            "created_at": created_at,
            "updated_at": updated_at,
            "description": body,
            "files_changed": files_changed,
            "file_stats": file_stats,
            "total_files": len(files_changed),
            "total_additions": total_additions,
            "total_deletions": total_deletions,
            "review_comments": review_comments,
            "pr_comments": pr_comments,
            "review_prompt": review_prompt.strip()
        }

    except GithubException as e:
        return {"error": f"GitHub API error: {e.status} - {e.data.get('message', str(e))}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

# --- Main MCP Server Setup ---
async def main():
    """Main function to set up and run the MCP server."""
    mcp = FastMCP(
        name="github-reviewer",
        instructions="An agent that analyzes and summarizes GitHub Pull Requests for code review.",
        tools=[github_pr_fetcher]
    )

    # Run the server using standard I/O (stdio) transport
    await mcp.run_stdio_async()

if __name__ == "__main__":
    asyncio.run(main())
