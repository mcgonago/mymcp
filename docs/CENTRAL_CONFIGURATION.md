# Central Configuration for mymcp

## Overview

The mymcp repository uses a **central configuration system** to define paths once and use them everywhere. This eliminates hardcoded absolute paths and makes the repository portable across different users and environments.

## Configuration File

### Location

```
<mymcp-repo-path>/.mymcp-config
```

### Contents

```bash
# mymcp Repository Configuration
export MYMCP_REPO_PATH="${MYMCP_REPO_PATH:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"
export MYMCP_WORKSPACE="${MYMCP_REPO_PATH}/workspace"
export MYMCP_WORKSPACE_PROJECT="${MYMCP_WORKSPACE_PROJECT:-${MYMCP_WORKSPACE}/iproject}"
export MYMCP_ACTIVITY_DIR="${MYMCP_WORKSPACE_PROJECT}/activity"
export MYMCP_RESULTS_DIR="${MYMCP_WORKSPACE_PROJECT}/results"
export MYMCP_ANALYSIS_DIR="${MYMCP_WORKSPACE_PROJECT}/analysis"
export MYMCP_ASKME_TEMPLATES="${MYMCP_REPO_PATH}/askme/templates"
export MYMCP_ASKME_KEYS="${MYMCP_REPO_PATH}/askme/keys"
```

### Auto-Detection

The configuration file **automatically detects** the repository root by finding its own location. Users don't need to manually set paths unless they want to override defaults.

##Usage in Shell Scripts

### Source the Configuration

```bash
#!/bin/bash
# Load mymcp configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/.mymcp-config"

# Now you can use the variables
cd "${MYMCP_WORKSPACE}"
echo "Working in: ${MYMCP_WORKSPACE}"
```

### Available Variables

| Variable | Description | Example Value |
|----------|-------------|---------------|
| `MYMCP_REPO_PATH` | Repository root | `/home/user/Work/mymcp` |
| `MYMCP_WORKSPACE` | Workspace directory (gitignored) | `/home/user/Work/mymcp/workspace` |
| `MYMCP_WORKSPACE_PROJECT` | Workspace project (iproject) | `/home/user/Work/mymcp/workspace/iproject` |
| `MYMCP_ACTIVITY_DIR` | Activity tracking data | `/home/user/Work/mymcp/workspace/iproject/activity` |
| `MYMCP_RESULTS_DIR` | Review assessments | `/home/user/Work/mymcp/workspace/iproject/results` |
| `MYMCP_ANALYSIS_DIR` | Feature investigations | `/home/user/Work/mymcp/workspace/iproject/analysis` |
| `MYMCP_ASKME_TEMPLATES` | askme templates | `/home/user/Work/mymcp/askme/templates` |
| `MYMCP_ASKME_KEYS` | askme keys | `/home/user/Work/mymcp/askme/keys` |

## Usage in Python Scripts

### Import the Helper Module

```python
from askme.mymcp_config import get_config, expand_path_vars

# Get all configuration paths
config = get_config()
print(f"Repository: {config['repo_path']}")
print(f"Workspace: {config['workspace']}")

# Expand path variables in text
text = "cd {MYMCP_REPO_PATH}/workspace"
expanded = expand_path_vars(text, config)
print(expanded)  # cd /home/user/Work/mymcp/workspace
```

### Available Functions

**`get_repo_root()`**
- Returns the mymcp repository root directory
- Checks `MYMCP_REPO_PATH` environment variable first
- Falls back to parent directory of `askme/`

**`get_config()`**
- Returns a dictionary with all configuration paths
- Keys: `repo_path`, `workspace`, `workspace_project`, `activity_dir`, `results_dir`, `analysis_dir`, `askme_templates`, `askme_keys`

**`expand_path_vars(text, config=None)`**
- Expands path variables in text
- Replaces: `{MYMCP_REPO_PATH}`, `{WORKSPACE_PATH}`, `{WORKSPACE_PROJECT}`, `<mymcp-repo-path>`
- Optionally takes a config dict (calls `get_config()` if not provided)

## Usage in askme Templates

### Path Variables

askme templates can use these variables, which will be automatically expanded when running `ask_me.sh`:

| Variable in Template | Expands To | Usage |
|---------------------|------------|-------|
| `{MYMCP_REPO_PATH}` | Repository root | Full path to mymcp clone |
| `{WORKSPACE_PATH}` | Workspace directory | Temporary checkouts |
| `{WORKSPACE_PROJECT}` | Workspace project | User's work directory (iproject) |
| `<mymcp-repo-path>` | Repository root | Documentation placeholder |

### Example Template

**`askme/templates/code_implement_workspace.template`**:

```markdown
Please implement the following changes:

{TASK_DESCRIPTION}

## Workspace

: cd {WORKSPACE_PATH}
: cd {WORKSPACE_NAME}

Show me how you would do this work in this {WORKSPACE_NAME} directory?
```

### Example Key File

**`askme/keys/my_task.yaml`**:

```yaml
type: code_implement_workspace
task_description: Fix the chevron expansion behavior
workspace_name: horizon-967773
workspace_path: {WORKSPACE_PATH}  # This will be expanded!
```

When you run `./ask_me.sh code_implement_workspace askme/keys/my_task.yaml`, the `{WORKSPACE_PATH}` in the YAML will be expanded to your actual workspace path.

## Usage in Documentation

### Markdown Files

In documentation, use the `<mymcp-repo-path>` placeholder:

```markdown
## Setup

```bash
cd <mymcp-repo-path>/workspace
./scripts/fetch-review.sh opendev https://...
```
```

This makes documentation portable - users just replace `<mymcp-repo-path>` with their actual clone location.

## Customization

### Override Repository Path

If you want to use a different repository path (e.g., you cloned mymcp to a non-standard location):

```bash
export MYMCP_REPO_PATH="/path/to/my/mymcp/clone"
source /path/to/my/mymcp/clone/.mymcp-config
```

### Override Workspace Project

If you want to use a different workspace project (e.g., a custom directory instead of `iproject`):

```bash
export MYMCP_WORKSPACE_PROJECT="/path/to/my/custom/workspace"
source /path/to/mymcp/.mymcp-config
```

### Example: Custom Setup

```bash
# Use custom clone location
export MYMCP_REPO_PATH="${HOME}/repos/mymcp"

# Use custom workspace project
export MYMCP_WORKSPACE_PROJECT="${HOME}/my_horizon_work"

# Load configuration
source "${MYMCP_REPO_PATH}/.mymcp-config"

# Now all paths are customized
echo "Activity data: ${MYMCP_ACTIVITY_DIR}"
# Output: Activity data: /home/user/my_horizon_work/activity
```

## Integration with Scripts

### ask_me.sh

The `ask_me.sh` script automatically:

1. Sources `.mymcp-config` at startup
2. Expands path variables in generated output
3. Replaces `{MYMCP_REPO_PATH}`, `{WORKSPACE_PATH}`, `{WORKSPACE_PROJECT}`, `<mymcp-repo-path>`

### fetch-review.sh

The `workspace/fetch-review.sh` script can be updated to use:

```bash
source "$(dirname "$0")/../.mymcp-config"
cd "${MYMCP_WORKSPACE}"
```

### test-mcp-setup.sh

The verification script can use:

```bash
source "./.mymcp-config"
echo "Testing agents in: ${MYMCP_REPO_PATH}"
```

## Migration Guide

### For Existing Documentation

1. **Replace absolute paths**:
   ```markdown
   # Before
   cd <mymcp-repo-path>/workspace
   
   # After
   cd <mymcp-repo-path>/workspace
   ```

2. **Use variables in scripts**:
   ```bash
   # Before
   WORKSPACE="<mymcp-repo-path>/workspace"
   
   # After
   source "./.mymcp-config"
   WORKSPACE="${MYMCP_WORKSPACE}"
   ```

3. **Update askme keys**:
   ```yaml
   # Before
   workspace_path: <mymcp-repo-path>/workspace
   
   # After
   workspace_path: {WORKSPACE_PATH}
   ```

### For New Work

- ✅ Use `{MYMCP_REPO_PATH}` in askme keys
- ✅ Use `<mymcp-repo-path>` in documentation
- ✅ Source `.mymcp-config` in shell scripts
- ✅ Import `askme.mymcp_config` in Python scripts

## Benefits

### 1. Portability ✅
- Repository works on any user's machine
- No hardcoded paths to update
- Workshop attendees can clone and use immediately

### 2. Maintainability ✅
- Single source of truth for paths
- Easy to reorganize directory structure
- Centralized path management

### 3. Flexibility ✅
- Users can customize workspace locations
- Supports multiple workspace projects
- Easy to adapt to different environments

### 4. Consistency ✅
- Same path variables everywhere
- Predictable behavior across scripts
- Reduced errors from path mismatches

## Troubleshooting

### Check Configuration

To see your current configuration:

```bash
# Bash
source ./.mymcp-config
# (automatically prints configuration)

# Python
python3 askme/mymcp_config.py
```

### Verify Path Expansion

Test if path variables are expanding correctly:

```bash
./ask_me.sh code_implement_workspace askme/keys/example_implement_chevron_fix.yaml | grep -i "workspace"
```

Should show actual paths, not `{WORKSPACE_PATH}` placeholders.

### Reset to Defaults

If you've set custom environment variables and want to reset:

```bash
unset MYMCP_REPO_PATH
unset MYMCP_WORKSPACE_PROJECT
source ./.mymcp-config
```

## Related Documentation

- **Workspace Policy**: `docs/WORKSPACE_POLICY.md`
- **askme Framework**: `askme/README.md`
- **Review Automation**: `usecases/review_automation/README.md`
- **Path Updates Summary**: `workspace/iproject/PATH_UPDATES_SUMMARY.md`

---

**Version**: 1.0  
**Created**: 2025-11-23  
**Purpose**: Centralized path configuration for portable, maintainable mymcp repository

