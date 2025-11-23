# Quick Start: Using mymcp Paths

This repository is **portable** - it works anywhere you clone it. Here's how to use paths correctly.

## For Users (Reading Documentation)

When you see `<mymcp-repo-path>` in documentation, replace it with where you cloned mymcp:

```bash
# Example in docs
cd <mymcp-repo-path>/workspace

# What you type (if you cloned to ~/Work/mymcp)
cd ~/Work/mymcp/workspace

# What you type (if you cloned to /opt/mymcp)
cd /opt/mymcp/workspace
```

**That's it!** Everything else is automatic.

## For Scripts

Scripts automatically detect paths - **you don't need to do anything**:

```bash
# Just run scripts normally
./ask_me.sh code_implement_workspace my_key.yaml
./workspace/fetch-review.sh opendev https://...
./scripts/check-links.sh

# They all auto-detect where mymcp is located!
```

## For askme Keys

Use quoted path variables in your YAML files:

```yaml
# ✅ CORRECT - Quoted!
type: code_implement_workspace
workspace_path: "{WORKSPACE_PATH}"
workspace_name: horizon-967773

# ❌ WRONG - Not quoted
workspace_path: {WORKSPACE_PATH}
```

See [askme/PATH_VARIABLES.md](askme/PATH_VARIABLES.md) for details.

## For Python Scripts

Import the configuration helper:

```python
from askme.mymcp_config import get_config

config = get_config()
workspace = config['workspace']
# workspace is automatically the correct path!
```

## Available Variables

| When You See | It Means |
|--------------|----------|
| `<mymcp-repo-path>` | Where you cloned mymcp |
| `{MYMCP_REPO_PATH}` | Same (in askme keys/templates) |
| `{WORKSPACE_PATH}` | `<mymcp-repo-path>/workspace` |
| `{WORKSPACE_PROJECT}` | `<mymcp-repo-path>/workspace/iproject` |

## Examples

### Example 1: Following Documentation

**Documentation says:**
```bash
cd <mymcp-repo-path>/workspace
./scripts/fetch-review.sh opendev https://...
```

**You type (if you cloned to ~/repos/mymcp):**
```bash
cd ~/repos/mymcp/workspace
./scripts/fetch-review.sh opendev https://...
```

### Example 2: Creating askme Key

**In your YAML file:**
```yaml
type: code_implement_workspace
workspace_path: "{WORKSPACE_PATH}"  # Don't forget quotes!
workspace_name: my-project
```

**When you run:**
```bash
./ask_me.sh code_implement_workspace my_key.yaml
```

**Output automatically has your actual path:**
```
: cd /your/actual/path/to/mymcp/workspace
: cd my-project
```

### Example 3: Writing a Script

**Your script:**
```bash
#!/bin/bash
# Load configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/.mymcp-config"

# Use variables
cd "${MYMCP_WORKSPACE}"
echo "Working in: ${MYMCP_WORKSPACE}"
```

**Works for any user automatically!**

## Checking Your Configuration

See where everything is located:

```bash
# Bash
source ./.mymcp-config
# Prints all paths

# Python
python3 askme/mymcp_config.py
# Prints all paths
```

## Customizing (Optional)

Want to use a different workspace location?

```bash
# Set custom workspace project
export MYMCP_WORKSPACE_PROJECT="${HOME}/my_custom_workspace"

# Load configuration
source ./.mymcp-config

# Now all tools use your custom location
```

## Common Issues

### Issue: askme Shows `{WORKSPACE_PATH}` Literally

**Problem:** YAML key not quoted

**Fix:**
```yaml
# ❌ WRONG
workspace_path: {WORKSPACE_PATH}

# ✅ CORRECT
workspace_path: "{WORKSPACE_PATH}"
```

### Issue: Script Can't Find Paths

**Problem:** Script not sourcing configuration

**Fix:** Add to top of script:
```bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/.mymcp-config"
```

## More Information

- **Complete Guide**: [docs/CENTRAL_CONFIGURATION.md](docs/CENTRAL_CONFIGURATION.md)
- **askme Variables**: [askme/PATH_VARIABLES.md](askme/PATH_VARIABLES.md)
- **Workspace System**: [WORKSPACE_PROJECT.md](WORKSPACE_PROJECT.md)
- **Full Summary**: [PATH_CLEANUP_SUMMARY.md](PATH_CLEANUP_SUMMARY.md)

---

**TL;DR**: Clone anywhere, replace `<mymcp-repo-path>` in docs with your path, scripts work automatically! 🚀

