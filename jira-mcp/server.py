#!/usr/bin/env python

import os
from dotenv import load_dotenv
from jira import JIRA
from fastmcp import FastMCP
from fastapi import HTTPException
import json

# ─── 1. Load environment variables ─────────────────────────────────────────────
load_dotenv()

JIRA_URL       = os.getenv("JIRA_URL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

if not all([JIRA_URL, JIRA_API_TOKEN]):
    raise RuntimeError("Missing JIRA_URL or JIRA_API_TOKEN environment variables")

# ─── 2. Create a Jira client ───────────────────────────────────────────────────
#    Uses token_auth (API token) for authentication.
jira_client = JIRA(server=JIRA_URL, token_auth=JIRA_API_TOKEN)

# ─── 3. Instantiate the MCP server ─────────────────────────────────────────────
mcp = FastMCP("Jira Context Server")

# ─── 4. Register the get_jira tool ─────────────────────────────────────────────
@mcp.tool()
def get_jira(issue_key: str) -> str:
    """
    Fetch the Jira issue identified by 'issue_key' using jira_client,
    then return a Markdown string: "# ISSUE-KEY: summary\n\ndescription"
    """
    try:
        issue = jira_client.issue(issue_key)
    except Exception as e:
        # If the JIRA client raises an error (e.g. issue not found),
        # wrap it in an HTTPException so MCP/Client sees a 4xx/5xx.
        raise HTTPException(status_code=404, detail=f"Failed to fetch Jira issue {issue_key}: {e}")

    # Extract summary & description fields
    summary     = issue.fields.summary or ""
    description = issue.fields.description or ""

    return f"# {issue_key}: {summary}\n\n{description}"

def to_markdown(obj):
    if isinstance(obj, dict):
        return '```json\n' + json.dumps(obj, indent=2) + '\n```'
    elif hasattr(obj, 'raw'):
        return '```json\n' + json.dumps(obj.raw, indent=2) + '\n```'
    elif isinstance(obj, list):
        return '\n'.join([to_markdown(o) for o in obj])
    else:
        return str(obj)

@mcp.tool()
def search_issues(jql: str, max_results: int = 10) -> str:
    """Search issues using JQL."""
    try:
        issues = jira_client.search_issues(jql, maxResults=max_results)
        return to_markdown([i.raw for i in issues])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"JQL search failed: {e}")

@mcp.tool()
def search_users(query: str, max_results: int = 10) -> str:
    """Search users by query."""
    try:
        users = jira_client.search_users(query, maxResults=max_results)
        return to_markdown([u.raw for u in users])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to search users: {e}")

@mcp.tool()
def list_projects() -> str:
    """List all projects."""
    try:
        projects = jira_client.projects()
        return to_markdown([p.raw for p in projects])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch projects: {e}")

@mcp.tool()
def get_project(project_key: str) -> str:
    """Get a project by key."""
    try:
        project = jira_client.project(project_key)
        return to_markdown(project)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Failed to fetch project: {e}")

@mcp.tool()
def get_project_components(project_key: str) -> str:
    """Get components for a project."""
    try:
        components = jira_client.project_components(project_key)
        return to_markdown([c.raw for c in components])
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Failed to fetch components: {e}")

@mcp.tool()
def get_project_versions(project_key: str) -> str:
    """Get versions for a project."""
    try:
        versions = jira_client.project_versions(project_key)
        return to_markdown([v.raw for v in versions])
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Failed to fetch versions: {e}")

@mcp.tool()
def get_project_roles(project_key: str) -> str:
    """Get roles for a project."""
    try:
        roles = jira_client.project_roles(project_key)
        return to_markdown(roles)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Failed to fetch roles: {e}")

@mcp.tool()
def get_project_permission_scheme(project_key: str) -> str:
    """Get permission scheme for a project."""
    try:
        scheme = jira_client.project_permissionscheme(project_key)
        return to_markdown(scheme.raw)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Failed to fetch permission scheme: {e}")

@mcp.tool()
def get_project_issue_types(project_key: str) -> str:
    """Get issue types for a project."""
    try:
        types = jira_client.project_issue_types(project_key)
        return to_markdown([t.raw for t in types])
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Failed to fetch issue types: {e}")

@mcp.tool()
def get_current_user() -> str:
    """Get current user info."""
    try:
        user = jira_client.myself()
        return to_markdown(user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch current user: {e}")

@mcp.tool()
def get_user(account_id: str) -> str:
    """Get user by account ID."""
    try:
        user = jira_client.user(account_id)
        return to_markdown(user.raw)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Failed to fetch user: {e}")

@mcp.tool()
def get_assignable_users_for_project(project_key: str, query: str = "", max_results: int = 10) -> str:
    """Get assignable users for a project."""
    try:
        users = jira_client.search_assignable_users_for_projects(query, project_key, maxResults=max_results)
        return to_markdown([u.raw for u in users])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get assignable users: {e}")

@mcp.tool()
def get_assignable_users_for_issue(issue_key: str, query: str = "", max_results: int = 10) -> str:
    """Get assignable users for an issue."""
    try:
        users = jira_client.search_assignable_users_for_issues(query, issueKey=issue_key, maxResults=max_results)
        return to_markdown([u.raw for u in users])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get assignable users: {e}")

@mcp.tool()
def list_boards(max_results: int = 10) -> str:
    """List boards."""
    try:
        boards = jira_client.boards(maxResults=max_results)
        return to_markdown([b.raw for b in boards])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch boards: {e}")

@mcp.tool()
def get_board(board_id: int) -> str:
    """Get board by ID."""
    try:
        board = jira_client.board(board_id)
        return to_markdown(board.raw)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Failed to fetch board: {e}")

@mcp.tool()
def list_sprints(board_id: int, max_results: int = 10) -> str:
    """List sprints for a board."""
    try:
        sprints = jira_client.sprints(board_id, maxResults=max_results)
        return to_markdown([s.raw for s in sprints])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch sprints: {e}")

@mcp.tool()
def get_sprint(sprint_id: int) -> str:
    """Get sprint by ID."""
    try:
        sprint = jira_client.sprint(sprint_id)
        return to_markdown(sprint.raw)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Failed to fetch sprint: {e}")

@mcp.tool()
def get_issues_for_board(board_id: int, max_results: int = 10) -> str:
    """Get issues for a board."""
    try:
        issues = jira_client.get_issues_for_board(board_id, maxResults=max_results)
        return to_markdown([i.raw for i in issues])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch issues for board: {e}")

@mcp.tool()
def get_issues_for_sprint(board_id: int, sprint_id: int, max_results: int = 10) -> str:
    """Get issues for a sprint in a board."""
    try:
        issues = jira_client.get_all_issues_for_sprint_in_board(board_id, sprint_id, maxResults=max_results)
        return to_markdown([i.raw for i in issues])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch issues for sprint: {e}")

# ─── 5. Run the HTTP-based MCP server on port 8000 ───────────────────────────────
if __name__ == "__main__":
    mcp.run()
