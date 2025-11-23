"""
mymcp Configuration Helper

Provides centralized path configuration for askme templates and keys.
This allows users to define their repository path once and have it
work everywhere.
"""

import os
from pathlib import Path


def get_repo_root():
    """
    Get the mymcp repository root directory.
    
    Checks in order:
    1. MYMCP_REPO_PATH environment variable
    2. Parent directory of this file (askme/../)
    
    Returns:
        Path to mymcp repository root
    """
    if 'MYMCP_REPO_PATH' in os.environ:
        return Path(os.environ['MYMCP_REPO_PATH'])
    
    # Default: parent directory of askme/
    return Path(__file__).parent.parent.resolve()


def get_config():
    """
    Get all mymcp configuration paths.
    
    Returns:
        dict with configuration keys:
        - repo_path: Repository root
        - workspace: Workspace directory (gitignored)
        - workspace_project: Workspace project directory (iproject)
        - activity_dir: Activity tracking data
        - results_dir: Review assessments
        - analysis_dir: Feature investigations
        - askme_templates: askme template directory
        - askme_keys: askme keys directory
    """
    repo_path = get_repo_root()
    
    # Allow override of workspace project location
    workspace_project = os.environ.get(
        'MYMCP_WORKSPACE_PROJECT',
        str(repo_path / 'workspace' / 'iproject')
    )
    
    return {
        'repo_path': str(repo_path),
        'workspace': str(repo_path / 'workspace'),
        'workspace_project': workspace_project,
        'activity_dir': f"{workspace_project}/activity",
        'results_dir': f"{workspace_project}/results",
        'analysis_dir': f"{workspace_project}/analysis",
        'askme_templates': str(repo_path / 'askme' / 'templates'),
        'askme_keys': str(repo_path / 'askme' / 'keys'),
    }


def expand_path_vars(text, config=None):
    """
    Expand path variables in text.
    
    Replaces:
    - {MYMCP_REPO_PATH} with repository root
    - {WORKSPACE_PATH} with workspace directory
    - {WORKSPACE_PROJECT} with workspace project directory
    - <mymcp-repo-path> with repository root (for documentation)
    
    Args:
        text: String containing path variables
        config: Optional config dict (from get_config())
    
    Returns:
        String with variables expanded
    """
    if config is None:
        config = get_config()
    
    replacements = {
        '{MYMCP_REPO_PATH}': config['repo_path'],
        '{WORKSPACE_PATH}': config['workspace'],
        '{WORKSPACE_PROJECT}': config['workspace_project'],
        '<mymcp-repo-path>': config['repo_path'],
    }
    
    result = text
    for var, value in replacements.items():
        result = result.replace(var, value)
    
    return result


if __name__ == '__main__':
    # Print configuration when run directly
    config = get_config()
    print("mymcp Configuration:")
    for key, value in config.items():
        print(f"  {key:20s} = {value}")

