# Path Variables in askme Keys

## Overview

askme key files can use path variables that are automatically expanded when running `ask_me.sh`. This makes your keys portable across different users and repository locations.

## Available Variables

| Variable | Expands To | Example |
|----------|------------|---------|
| `{MYMCP_REPO_PATH}` | Repository root | `/home/user/Work/mymcp` |
| `{WORKSPACE_PATH}` | Workspace directory | `/home/user/Work/mymcp/workspace` |
| `{WORKSPACE_PROJECT}` | Workspace project (iproject) | `/home/user/Work/mymcp/workspace/iproject` |

## Usage

### Simple Values (Must Quote!)

When using path variables as standalone values in YAML, **you must quote them** to prevent YAML from interpreting them as mappings:

```yaml
# ✅ CORRECT - Quoted
type: code_implement_workspace
workspace_path: "{WORKSPACE_PATH}"
workspace_name: horizon-967773

# ❌ WRONG - Not quoted (yq will interpret as mapping)
workspace_path: {WORKSPACE_PATH}
```

**Why quote?** In YAML, `{key: value}` is a mapping/dictionary. Without quotes, yq thinks `{WORKSPACE_PATH}` is a mapping with a key named `WORKSPACE_PATH` and no value.

### In Multiline Strings (No Quotes Needed)

When path variables are embedded in multiline strings, quotes are not needed:

```yaml
# ✅ CORRECT - No quotes needed in multiline strings
commands: |
  cd {WORKSPACE_PATH}
  git clone https://...
  cd {WORKSPACE_NAME}
```

### In Concatenated Strings

You can concatenate path variables with other text:

```yaml
# ✅ CORRECT - Variable in quoted string
full_path: "{WORKSPACE_PATH}/horizon-967773"

# ✅ ALSO CORRECT - In multiline string
commands: |
  cd {WORKSPACE_PATH}/horizon-967773/openstack_dashboard
  ls -la
```

## Examples

### Example 1: Code Implementation

```yaml
type: code_implement_workspace
workspace_path: "{WORKSPACE_PATH}"  # Quoted!
workspace_name: horizon-osprh-12803-working
git_setup_commands: |
  git clone https://review.opendev.org/openstack/horizon {WORKSPACE_NAME}
  cd {WORKSPACE_NAME}
  git fetch https://review.opendev.org/openstack/horizon refs/changes/49/966349/5
  git checkout FETCH_HEAD
```

**Result after expansion**:
```
: cd /home/user/Work/mymcp/workspace
: git clone https://review.opendev.org/openstack/horizon horizon-osprh-12803-working
cd horizon-osprh-12803-working
git fetch https://review.opendev.org/openstack/horizon refs/changes/49/966349/5
git checkout FETCH_HEAD
```

### Example 2: Investigation Patterns

```yaml
type: investigate_patterns
current_state_info: |
  Patchset 4 changes can be seen as:
  cd {WORKSPACE_PATH}/horizon-osprh-12803-patch-set-4
  git diff --stat abc123..def456
```

**Result after expansion**:
```
Patchset 4 changes can be seen as:
cd /home/user/Work/mymcp/workspace/horizon-osprh-12803-patch-set-4
git diff --stat abc123..def456
```

### Example 3: Phase Done

```yaml
type: phase_done
workspace_path: "{WORKSPACE_PROJECT}/analysis"  # Quoted and concatenated!
current_directory: "{WORKSPACE_PATH}/horizon-967773"  # Quoted!
```

## How It Works

### Expansion Flow

1. **ask_me.sh loads configuration**
   ```bash
   source ./.mymcp-config
   # Sets: MYMCP_WORKSPACE=/home/user/Work/mymcp/workspace
   ```

2. **YAML file is parsed**
   ```yaml
   workspace_path: "{WORKSPACE_PATH}"
   ```
   yq reads this as the string value: `"{WORKSPACE_PATH}"`

3. **Template substitution happens**
   Template gets the value `{WORKSPACE_PATH}` inserted

4. **Path variable expansion**
   ```bash
   expand_path_vars() replaces {WORKSPACE_PATH} with actual value
   ```

5. **Final output**
   ```
   : cd /home/user/Work/mymcp/workspace
   ```

## Common Mistakes

### Mistake 1: Forgot to Quote

```yaml
# ❌ WRONG
workspace_path: {WORKSPACE_PATH}
```

**Error**: yq interprets as mapping, produces `{WORKSPACE_PATH: ''}` in output

**Fix**: Add quotes:
```yaml
# ✅ CORRECT
workspace_path: "{WORKSPACE_PATH}"
```

### Mistake 2: Double Quoting Variables in Template

```yaml
# ❌ WRONG - Don't quote the variable in template usage
workspace_path: "{{WORKSPACE_PATH}}"
```

**Error**: Produces literal `{WORKSPACE_PATH}` in output (double braces)

**Fix**: Single braces only:
```yaml
# ✅ CORRECT
workspace_path: "{WORKSPACE_PATH}"
```

### Mistake 3: Using Wrong Variable Name

```yaml
# ❌ WRONG - Variable doesn't exist
workspace_path: "{WORKSPACE}"  # There's no such variable
```

**Fix**: Use exact variable name:
```yaml
# ✅ CORRECT
workspace_path: "{WORKSPACE_PATH}"
```

## Testing Path Expansion

To verify path variables are expanding correctly:

```bash
# Run askme and check output
./ask_me.sh code_implement_workspace your_key.yaml | grep -i "cd"

# Should show:
# : cd /home/your-user/Work/mymcp/workspace  (actual path)
# NOT:
# : cd {WORKSPACE_PATH}  (unexpanded)
```

## Customizing Paths

Users can customize where workspace lives:

```bash
# Set custom workspace project location
export MYMCP_WORKSPACE_PROJECT="${HOME}/my_horizon_work"

# Run askme - will use custom location
./ask_me.sh code_implement_workspace your_key.yaml

# Output will show:
# : cd /home/user/my_horizon_work  (custom path!)
```

## Related Documentation

- **Central Configuration**: `docs/CENTRAL_CONFIGURATION.md`
- **askme Framework**: `askme/README.md`
- **askme Templates**: `askme/templates/`
- **askme Keys**: `askme/keys/`

---

## Quick Reference

**Always quote standalone path variables in YAML:**

```yaml
# ✅ DO THIS
workspace_path: "{WORKSPACE_PATH}"
repo_path: "{MYMCP_REPO_PATH}"
project_path: "{WORKSPACE_PROJECT}"

# ❌ NOT THIS
workspace_path: {WORKSPACE_PATH}
```

**In multiline strings, no quotes needed:**

```yaml
# ✅ DO THIS
commands: |
  cd {WORKSPACE_PATH}
  ls -la
```

---

**Version**: 1.0  
**Created**: 2025-11-23  
**Purpose**: Guide for using path variables in askme key files

