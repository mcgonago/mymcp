# USE CASE: ask_me.sh - Automated Ask Generation System

**Purpose**: Complete technical documentation of how `ask_me.sh` processes requests from start to finish

**Last Updated**: 2025-11-23

---

## Table of Contents

1. [Overview](#overview)
2. [Command Anatomy](#command-anatomy)
3. [System Architecture](#system-architecture)
4. [Processing Flow](#processing-flow)
5. [File Resolution](#file-resolution)
6. [Configuration Loading](#configuration-loading)
7. [YAML Parsing Mechanisms](#yaml-parsing-mechanisms)
8. [Template Substitution Engine](#template-substitution-engine)
9. [Path Variable Expansion](#path-variable-expansion)
10. [Output Generation](#output-generation)
11. [Complete Example Walkthrough](#complete-example-walkthrough)
12. [Error Handling](#error-handling)
13. [Troubleshooting Guide](#troubleshooting-guide)

---

## Overview

The `ask_me.sh` script is an **automated prompt generation system** that:
- Takes a **template file** (pre-written prompt structure with placeholders)
- Takes a **YAML key file** (your specific values)
- Merges them together by substituting placeholders
- Expands path variables for portability
- Outputs a ready-to-use prompt for AI assistants

### Why It Exists

**Problem**: Manually writing detailed prompts is time-consuming and inconsistent.

**Solution**: Separate structure (template) from content (YAML key), automate merging.

**Benefits**:
- ✅ Consistent prompt formatting
- ✅ Reusable patterns
- ✅ Version-controlled documentation of your questions
- ✅ Portable across different machines
- ✅ Reduces cognitive load

---

## Command Anatomy

### Standard Command Syntax

```bash
./ask_me.sh <template-type> <key-file> [VAR=value ...]
```

### Three Invocation Modes

#### Mode 1: Basic (No Variables)

```bash
./ask_me.sh <template-type> <key-file>
```

**Example:**
```bash
./ask_me.sh code_implement_workspace askme/keys/example_implement_chevron_fix.yaml
```

**What it does:**
1. Uses the specified template: `askme/templates/code_implement_workspace.template`
2. Uses the specified key file: `askme/keys/example_implement_chevron_fix.yaml`
3. No template variable substitution

#### Mode 2: With Template Variables (NEW!)

```bash
./ask_me.sh <template-type> <key-file> VAR=value [VAR2=value2 ...]
```

**Example:**
```bash
./ask_me.sh analysis_doc_create askme/keys/osprh_template.yaml \
    TICKET_NUMBER=16421 \
    FEATURE_NAME="Add expandable rows to Images table"
```

**What it does:**
1. Uses the specified template: `askme/templates/analysis_doc_create.template`
2. Reads the key file: `askme/keys/osprh_template.yaml`
3. **First substitutes template variables** (`{TICKET_NUMBER}` → `16421`)
4. Then performs normal YAML → template substitution
5. Finally expands path variables

**Benefits:**
- ✅ Reuse one YAML file for many similar tasks
- ✅ No need to create a new file for each ticket
- ✅ Pass values on command line
- ✅ Great for automation and scripting

**See:** [askme/TEMPLATE_VARIABLES.md](../askme/TEMPLATE_VARIABLES.md) for complete documentation

#### Mode 2: Single-Argument (Shorthand) - If Implemented

```bash
./ask_me.sh osprh_16421
```

**What it would need:**
1. A key file at: `askme/keys/osprh_16421.yaml`
2. That YAML file must contain a `type:` field specifying which template to use

**Key file would look like:**
```yaml
type: analysis_doc_create
output_document: workspace/iproject/analysis/analysis_new_feature_osprh_16421/spike.md
context_description: |
  Working on OSPRH-16421: Add expandable rows to Images table
  Similar to OSPRH-12803 (Key Pairs) in Review 966349
specific_questions: |
  How should we implement expandable rows for the Images table?
  What are the key architectural decisions?
```

**Currently:** The script expects 2 arguments. For `./ask_me.sh osprh_16421` to work, you'd need:
```bash
./ask_me.sh <template-type> askme/keys/osprh_16421.yaml
```

For the rest of this document, we'll use the **standard two-argument mode**.

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      ask_me.sh System                            │
│                                                                  │
│  ┌────────────┐     ┌──────────────┐     ┌────────────────┐   │
│  │  Template  │     │  YAML Key    │     │  .mymcp-config │   │
│  │   Files    │     │    Files     │     │  (paths)       │   │
│  └─────┬──────┘     └──────┬───────┘     └────────┬───────┘   │
│        │                   │                      │            │
│        │                   │                      │            │
│        └───────────────────┼──────────────────────┘            │
│                            │                                    │
│                            ▼                                    │
│                  ┌──────────────────┐                          │
│                  │  ask_me.sh       │                          │
│                  │  (Main Script)   │                          │
│                  └────────┬─────────┘                          │
│                           │                                     │
│         ┌─────────────────┼─────────────────┐                 │
│         │                 │                 │                  │
│         ▼                 ▼                 ▼                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ Validation  │  │ Parsing     │  │ Substitution│          │
│  │ - Template  │  │ - yq or     │  │ - Replace   │          │
│  │ - Key file  │  │ - Python    │  │   {VARS}    │          │
│  └─────────────┘  └─────────────┘  └──────┬──────┘          │
│                                            │                   │
│                                            ▼                   │
│                                  ┌─────────────────┐          │
│                                  │ Path Expansion  │          │
│                                  │ - {WORKSPACE_   │          │
│                                  │   PATH}         │          │
│                                  └────────┬────────┘          │
│                                           │                    │
│                                           ▼                    │
│                                  ┌─────────────────┐          │
│                                  │ Output to       │          │
│                                  │ stdout          │          │
│                                  └─────────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

### Component Details

| Component | Location | Purpose | Input | Output |
|-----------|----------|---------|-------|--------|
| **ask_me.sh** | Root directory | Main orchestrator | CLI args | Formatted prompt |
| **Templates** | `askme/templates/` | Prompt structures with placeholders | None | Template content |
| **Key Files** | `askme/keys/` | User-specific values | User edits | YAML data |
| **Config** | `.mymcp-config` | Path definitions | Environment | Bash variables |
| **yq / Python** | System dependency | YAML parser | YAML file | Key-value pairs |

---

## Processing Flow

### Complete Execution Flow

**Note**: This flow includes the new template variables feature (Stage 3)

```
┌─────────────────────────────────────────────────────────────────┐
│  STAGE 1: Command Line Parsing & Initialization                 │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
        User runs: ./ask_me.sh code_implement_workspace \
                              askme/keys/example_implement_chevron_fix.yaml \
                              [VAR=value ...]
                        │
                        ├─ Parse Arguments
                        │  ├─ TEMPLATE_TYPE = "code_implement_workspace"
                        │  └─ KEY_FILE = "askme/keys/example_implement_chevron_fix.yaml"
                        │
                        ├─ Set Script Directory
                        │  └─ SCRIPT_DIR = "/home/user/Work/mymcp"
                        │
                        ├─ Load Configuration (.mymcp-config)
                        │  ├─ MYMCP_REPO_PATH = "/home/user/Work/mymcp"
                        │  ├─ MYMCP_WORKSPACE = "/home/user/Work/mymcp/workspace"
                        │  └─ MYMCP_WORKSPACE_PROJECT = ".../workspace/iproject"
                        │
                        └─ Continue to Stage 2
                        
┌─────────────────────────────────────────────────────────────────┐
│  STAGE 2: File Resolution & Validation                          │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ├─ Resolve Template Path
                        │  ├─ TEMPLATE_FILE = "${SCRIPT_DIR}/askme/templates/${TEMPLATE_TYPE}.template"
                        │  ├─ Expands to: "/home/user/Work/mymcp/askme/templates/code_implement_workspace.template"
                        │  └─ Check: Does file exist?
                        │     ├─ YES: Continue
                        │     └─ NO: Error "Template not found"
                        │
                        ├─ Resolve Key File Path
                        │  ├─ Is path absolute? (starts with /)
                        │  │  ├─ YES: Use as-is
                        │  │  └─ NO: Prepend SCRIPT_DIR
                        │  ├─ KEY_FILE_PATH = "${SCRIPT_DIR}/${KEY_FILE}"
                        │  ├─ Expands to: "/home/user/Work/mymcp/askme/keys/example_implement_chevron_fix.yaml"
                        │  └─ Check: Does file exist?
                        │     ├─ YES: Continue
                        │     └─ NO: Error "Key file not found"
                        │
                        └─ Continue to Stage 3

┌─────────────────────────────────────────────────────────────────┐
│  STAGE 3: Template Variable Substitution (NEW!)                 │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ├─ Check if any template variables provided
                        │  └─ If TEMPLATE_VARS array has entries:
                        │     │
                        │     ├─ Read YAML file content
                        │     │
                        │     ├─ For each variable (e.g., TICKET_NUMBER=16421):
                        │     │  └─ Replace {TICKET_NUMBER}, ${TICKET_NUMBER}, {{TICKET_NUMBER}}
                        │     │     in YAML content with: 16421
                        │     │
                        │     ├─ Write modified content to temp file
                        │     │  └─ /tmp/ask_me_yaml_$$
                        │     │
                        │     └─ Update KEY_FILE_PATH to point to temp file
                        │
                        └─ Continue to Stage 4

┌─────────────────────────────────────────────────────────────────┐
│  STAGE 4: YAML Parser Detection                                 │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ├─ Check if 'yq' is installed
                        │  └─ command -v yq &> /dev/null
                        │     ├─ Found: Use yq path (FAST)
                        │     └─ Not found: Use Python path (FALLBACK)
                        │
                        └─ Branch to appropriate parser (Stage 5a or 5b)

┌─────────────────────────────────────────────────────────────────┐
│  STAGE 5a: Template Substitution (yq path)                      │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ├─ Read Template File
                        │  └─ TEMPLATE_CONTENT = "ask:\n\nI already have done the following..."
                        │
                        ├─ Extract YAML Keys
                        │  └─ yq eval 'keys | .[]' <key-file>
                        │     Result: ["type", "workspace_path", "workspace_name", "git_setup_commands"]
                        │
                        ├─ For Each Key:
                        │  │
                        │  ├─ Get value from YAML
                        │  │  └─ value=$(yq eval ".workspace_path" <key-file>)
                        │  │     Result: "{WORKSPACE_PATH}"
                        │  │
                        │  ├─ Convert key to UPPERCASE placeholder
                        │  │  └─ "workspace_path" → "WORKSPACE_PATH"
                        │  │
                        │  └─ Replace {WORKSPACE_PATH} in template with value
                        │     └─ Uses awk for multiline-safe substitution
                        │
                        └─ RESULT = Template with all placeholders replaced
                        
┌─────────────────────────────────────────────────────────────────┐
│  STAGE 5b: Template Substitution (Python path)                  │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ├─ Check Python + PyYAML available
                        │  └─ python3 -c "import yaml"
                        │     ├─ YES: Continue
                        │     └─ NO: Error with installation instructions
                        │
                        ├─ Execute Python Parser
                        │  ├─ Load YAML file → data dict
                        │  ├─ Read template file → template string
                        │  ├─ Use regex to find all {PLACEHOLDER} patterns
                        │  ├─ For each placeholder:
                        │  │  ├─ Convert to lowercase: WORKSPACE_PATH → workspace_path
                        │  │  ├─ Lookup in data dict
                        │  │  ├─ Replace if found, keep if not found
                        │  │  └─ Handle multiline strings properly
                        │  └─ Return substituted template
                        │
                        └─ RESULT = Template with all placeholders replaced

┌─────────────────────────────────────────────────────────────────┐
│  STAGE 6: Path Variable Expansion                               │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ├─ expand_path_vars() function called on RESULT
                        │
                        ├─ Replace path placeholders with actual values:
                        │  ├─ "<mymcp-repo-path>" → "/home/user/Work/mymcp"
                        │  ├─ "{MYMCP_REPO_PATH}" → "/home/user/Work/mymcp"
                        │  ├─ "{WORKSPACE_PATH}" → "/home/user/Work/mymcp/workspace"
                        │  └─ "{WORKSPACE_PROJECT}" → "/home/user/Work/mymcp/workspace/iproject"
                        │
                        └─ RESULT = Fully expanded, ready-to-use prompt

┌─────────────────────────────────────────────────────────────────┐
│  STAGE 7: Output Generation                                     │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ├─ Print RESULT to stdout
                        │  └─ User can copy or pipe to clipboard
                        │
                        ├─ Print success message (to stderr)
                        │  └─ "✅ Ask generated successfully!"
                        │
                        ├─ Print usage hint (to stderr)
                        │  └─ "💡 Copy the output above..."
                        │
                        └─ Exit with status 0 (success)
```

---

## File Resolution

### How the Script Finds Files

#### Template Resolution

```
Template Type: "code_implement_workspace"
                │
                ├─ SCRIPT_DIR = $(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
                │  └─ Gets absolute path to where ask_me.sh lives
                │     Example: "/home/user/Work/mymcp"
                │
                ├─ TEMPLATES_DIR = "${SCRIPT_DIR}/askme/templates"
                │  └─ Example: "/home/user/Work/mymcp/askme/templates"
                │
                └─ TEMPLATE_FILE = "${TEMPLATES_DIR}/${TEMPLATE_TYPE}.template"
                   └─ Example: "/home/user/Work/mymcp/askme/templates/code_implement_workspace.template"
```

#### Key File Resolution

```
Key File Argument: "askme/keys/example_implement_chevron_fix.yaml"
                │
                ├─ Is it an absolute path? (starts with /)
                │  ├─ YES: Use directly
                │  │  └─ KEY_FILE_PATH = "$KEY_FILE"
                │  │
                │  └─ NO: Prepend SCRIPT_DIR
                │     └─ KEY_FILE_PATH = "${SCRIPT_DIR}/${KEY_FILE}"
                │        Example: "/home/user/Work/mymcp/askme/keys/example_implement_chevron_fix.yaml"
                │
                └─ File Existence Check
                   ├─ if [ ! -f "$KEY_FILE_PATH" ]; then
                   ├─ YES exists: Continue
                   └─ NO doesn't exist: error() and exit 1
```

### Path Resolution Examples

| Input | Type | Resolved Path |
|-------|------|---------------|
| `askme/keys/myfile.yaml` | Relative | `/home/user/Work/mymcp/askme/keys/myfile.yaml` |
| `/tmp/myfile.yaml` | Absolute | `/tmp/myfile.yaml` |
| `keys/myfile.yaml` | Relative | `/home/user/Work/mymcp/keys/myfile.yaml` |
| `~/myfile.yaml` | Tilde expansion | `/home/user/myfile.yaml` (bash expands ~) |

---

## Configuration Loading

### .mymcp-config Loading Sequence

```
┌─────────────────────────────────────────────────────────────────┐
│  Configuration Loading (Lines 37-45 of ask_me.sh)               │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ├─ Check: Does .mymcp-config exist?
                        │  │
                        │  ├─ YES: Source it
                        │  │  │
                        │  │  ├─ source "${SCRIPT_DIR}/.mymcp-config"
                        │  │  │
                        │  │  └─ This exports:
                        │  │     ├─ MYMCP_REPO_PATH (auto-detected)
                        │  │     ├─ MYMCP_WORKSPACE (${REPO}/workspace)
                        │  │     ├─ MYMCP_WORKSPACE_PROJECT (${WORKSPACE}/iproject)
                        │  │     ├─ MYMCP_ACTIVITY_DIR (${PROJECT}/activity)
                        │  │     ├─ MYMCP_RESULTS_DIR (${PROJECT}/results)
                        │  │     ├─ MYMCP_ANALYSIS_DIR (${PROJECT}/analysis)
                        │  │     ├─ MYMCP_ASKME_TEMPLATES (${REPO}/askme/templates)
                        │  │     └─ MYMCP_ASKME_KEYS (${REPO}/askme/keys)
                        │  │
                        │  └─ NO: Use fallback defaults
                        │     │
                        │     ├─ export MYMCP_REPO_PATH="${SCRIPT_DIR}"
                        │     ├─ export MYMCP_WORKSPACE="${MYMCP_REPO_PATH}/workspace"
                        │     └─ export MYMCP_WORKSPACE_PROJECT="${MYMCP_WORKSPACE}/iproject"
                        │
                        └─ Variables now available for path expansion
```

### What .mymcp-config Provides

**.mymcp-config contents:**
```bash
# Auto-detects repository root
export MYMCP_REPO_PATH="${MYMCP_REPO_PATH:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"

# Derived paths
export MYMCP_WORKSPACE="${MYMCP_REPO_PATH}/workspace"
export MYMCP_WORKSPACE_PROJECT="${MYMCP_WORKSPACE_PROJECT:-${MYMCP_WORKSPACE}/iproject}"
export MYMCP_ACTIVITY_DIR="${MYMCP_WORKSPACE_PROJECT}/activity"
# ... etc
```

**Why this matters:**
- ✅ Makes paths portable across different machines
- ✅ User doesn't need to edit paths
- ✅ Works whether repo is at `/home/alice/mymcp` or `/home/bob/projects/mymcp`

---

## YAML Parsing Mechanisms

### Two Parsers: yq vs Python

The script supports **two different YAML parsers** with automatic fallback:

```
┌─────────────────────────────────────────────────────────────────┐
│  Parser Selection Logic                                          │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
            Check: command -v yq &> /dev/null
                        │
           ┌────────────┴────────────┐
           │                         │
          YES                       NO
           │                         │
           ▼                         ▼
    ┌──────────────┐        ┌──────────────────┐
    │  Use yq      │        │ Check Python +   │
    │  (Preferred) │        │ PyYAML           │
    │              │        │                  │
    │  Pros:       │        │ Pros:            │
    │  - Fast      │        │ - Widely         │
    │  - Native    │        │   available      │
    │  - Robust    │        │ - No extra       │
    │              │        │   install        │
    │  Cons:       │        │                  │
    │  - Must      │        │ Cons:            │
    │    install   │        │ - Slower         │
    └──────────────┘        │ - Inline code    │
                            └──────────────────┘
```

### Parser 1: yq (Lines 189-227)

**How it works:**

```bash
# Step 1: Read template into memory
TEMPLATE_CONTENT=$(cat "$TEMPLATE_FILE")

# Step 2: Get all keys from YAML
YAML_KEYS=$(yq eval 'keys | .[]' "$KEY_FILE_PATH")
# Result (one per line):
# type
# workspace_path
# workspace_name
# git_setup_commands

# Step 3: For each key, get value and substitute
while IFS= read -r key; do
    if [ -n "$key" ] && [ "$key" != "type" ]; then
        # Get value
        value=$(yq eval ".${key}" "$KEY_FILE_PATH")
        
        # Convert key to uppercase: workspace_path → WORKSPACE_PATH
        placeholder=$(echo "$key" | tr '[:lower:]' '[:upper:]')
        
        # Replace in template using awk (multiline-safe)
        echo "$RESULT" | awk -v placeholder="{${placeholder}}" -v value="$value" '
        {
            if (index($0, placeholder) > 0) {
                sub(placeholder, value)
            }
            print
        }' > /tmp/ask_me_tmp_$$
        
        RESULT=$(cat /tmp/ask_me_tmp_$$)
        rm -f /tmp/ask_me_tmp_$$
    fi
done <<< "$YAML_KEYS"
```

**Example Substitution:**

```
Key: workspace_path
Value: "{WORKSPACE_PATH}"
Placeholder: {WORKSPACE_PATH}

Template line: "I already have done the following\n\n: cd {WORKSPACE_PATH}\n"
After sub:     "I already have done the following\n\n: cd {WORKSPACE_PATH}\n"
                (value itself contains {WORKSPACE_PATH}, will be expanded later)
```

### Parser 2: Python + PyYAML (Lines 138-186)

**How it works:**

```python
import sys
import yaml
import re

# Step 1: Load YAML
with open(sys.argv[1], 'r') as f:
    data = yaml.safe_load(f)
# Result: Python dict
# {
#   'type': 'code_implement_workspace',
#   'workspace_path': '{WORKSPACE_PATH}',
#   'workspace_name': 'horizon-osprh-12803-working',
#   'git_setup_commands': 'git clone...\ncd...\n...'
# }

# Step 2: Read template
with open(sys.argv[2], 'r') as f:
    template = f.read()

# Step 3: Define replacement function
def replace_placeholder(match):
    key = match.group(1)  # Extract "WORKSPACE_PATH" from "{WORKSPACE_PATH}"
    yaml_key = key.lower()  # Convert to "workspace_path"
    
    if yaml_key in data:
        value = data[yaml_key]
        # Handle multiline values
        if isinstance(value, str) and '\n' in value:
            return value  # Preserve formatting
        return str(value)
    else:
        return match.group(0)  # Keep placeholder if not found

# Step 4: Replace all placeholders
result = re.sub(r'\{([A-Z_]+)\}', replace_placeholder, template)

print(result)
```

**Regex Pattern Explained:**

```
r'\{([A-Z_]+)\}'
  \{              Literal opening brace
    (             Start capture group
     [A-Z_]+      One or more uppercase letters or underscores
    )             End capture group
  \}              Literal closing brace

Matches: {WORKSPACE_PATH}, {GIT_SETUP_COMMANDS}, {OUTPUT_DOCUMENT}
Doesn't match: {lowercase}, {Mixed-Case}, {123}, workspace_path
```

---

## Template Substitution Engine

### Placeholder Naming Convention

**YAML Key → Placeholder Mapping:**

```
YAML file (lowercase, underscores):    Template (UPPERCASE in braces):
────────────────────────────────────   ───────────────────────────────
workspace_path                    →    {WORKSPACE_PATH}
git_setup_commands                →    {GIT_SETUP_COMMANDS}
output_document                   →    {OUTPUT_DOCUMENT}
specific_questions                →    {SPECIFIC_QUESTIONS}
reviewer_comment                  →    {REVIEWER_COMMENT}
```

**Why this convention?**
- ✅ YAML uses Python/shell convention (lowercase_with_underscores)
- ✅ Templates use clear visual markers (UPPERCASE in braces)
- ✅ Easy to convert: `tr '[:lower:]' '[:upper:]'`
- ✅ Obvious what's a placeholder vs. literal text

### Substitution Example

**Input Template** (`code_implement_workspace.template`):
```
ask:

I already have done the following

: cd {WORKSPACE_PATH}
: {GIT_SETUP_COMMANDS}

I want you to make all your recommended changes

Show me how you would do this work in this {WORKSPACE_NAME} directory?
```

**Input YAML** (`example_implement_chevron_fix.yaml`):
```yaml
type: code_implement_workspace
workspace_path: "{WORKSPACE_PATH}"
workspace_name: horizon-osprh-12803-working
git_setup_commands: |
  git clone https://review.opendev.org/openstack/horizon horizon-osprh-12803-working
  cd horizon-osprh-12803-working
  git fetch https://review.opendev.org/openstack/horizon refs/changes/49/966349/5
  git checkout FETCH_HEAD
  git checkout -b osprh-12803-template-refactor
```

**After Substitution** (still has {WORKSPACE_PATH}):
```
ask:

I already have done the following

: cd {WORKSPACE_PATH}
: git clone https://review.opendev.org/openstack/horizon horizon-osprh-12803-working
  cd horizon-osprh-12803-working
  git fetch https://review.opendev.org/openstack/horizon refs/changes/49/966349/5
  git checkout FETCH_HEAD
  git checkout -b osprh-12803-template-refactor

I want you to make all your recommended changes

Show me how you would do this work in this horizon-osprh-12803-working directory?
```

**After Path Expansion** (final output):
```
ask:

I already have done the following

: cd /home/user/Work/mymcp/workspace
: git clone https://review.opendev.org/openstack/horizon horizon-osprh-12803-working
  cd horizon-osprh-12803-working
  git fetch https://review.opendev.org/openstack/horizon refs/changes/49/966349/5
  git checkout FETCH_HEAD
  git checkout -b osprh-12803-template-refactor

I want you to make all your recommended changes

Show me how you would do this work in this horizon-osprh-12803-working directory?
```

### Multiline Handling

**Challenge**: YAML multiline values must be preserved exactly

**YAML Input:**
```yaml
git_setup_commands: |
  git clone https://example.com/repo
  cd repo
  git checkout feature-branch
```

**Python parser** (handles this automatically via PyYAML's string parsing)

**yq parser** (uses awk for line-by-line substitution):
```bash
awk -v placeholder="{GIT_SETUP_COMMANDS}" -v value="$value" '
{
    if (index($0, placeholder) > 0) {
        sub(placeholder, value)  # Replace placeholder with multiline value
    }
    print
}'
```

The `sub()` function in awk replaces the first occurrence and handles newlines correctly when `value` contains them.

---

## Path Variable Expansion

### The expand_path_vars() Function

**Purpose**: Replace portable path placeholders with actual system paths

**Location**: Lines 48-56 in `ask_me.sh`

**Code:**
```bash
expand_path_vars() {
    local text="$1"
    # Replace common path placeholders with actual values
    text="${text//<mymcp-repo-path>/${MYMCP_REPO_PATH}}"
    text="${text//\{MYMCP_REPO_PATH\}/${MYMCP_REPO_PATH}}"
    text="${text//\{WORKSPACE_PATH\}/${MYMCP_WORKSPACE}}"
    text="${text//\{WORKSPACE_PROJECT\}/${MYMCP_WORKSPACE_PROJECT}}"
    echo "$text"
}
```

### Bash String Substitution Syntax

```
${variable//pattern/replacement}
   │        ││       │
   │        ││       └─ Replacement text
   │        │└─ Pattern to find
   │        └─ Replace ALL occurrences (not just first)
   └─ Variable to operate on
```

**Example:**
```bash
text="Go to {WORKSPACE_PATH} and check {WORKSPACE_PATH}/results"
MYMCP_WORKSPACE="/home/user/Work/mymcp/workspace"

result="${text//\{WORKSPACE_PATH\}/${MYMCP_WORKSPACE}}"
# Result: "Go to /home/user/Work/mymcp/workspace and check /home/user/Work/mymcp/workspace/results"
```

### Why Escape the Braces?

```bash
text="${text//\{WORKSPACE_PATH\}/${MYMCP_WORKSPACE}}"
             ││               ││
             │└─ Literal }    │└─ Literal }
             └─ Literal {     └─ Literal {
```

**Without escaping:**
```bash
text="${text//{WORKSPACE_PATH}/${MYMCP_WORKSPACE}}"
             │                │
             └─ Bash tries to expand {WORKSPACE_PATH} as a brace expansion
                Result: Error or unexpected behavior
```

**With escaping:**
```bash
text="${text//\{WORKSPACE_PATH\}/${MYMCP_WORKSPACE}}"
             │                 │
             └─ Treats { and } as literal characters
                Result: Finds and replaces "{WORKSPACE_PATH}" as expected
```

### Expansion Sequence

```
┌─────────────────────────────────────────────────────────────────┐
│  Path Variable Expansion Order                                   │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ├─ 1. <mymcp-repo-path>
                        │  └─ Legacy format from older docs
                        │
                        ├─ 2. {MYMCP_REPO_PATH}
                        │  └─ Repository root directory
                        │     Example: /home/user/Work/mymcp
                        │
                        ├─ 3. {WORKSPACE_PATH}
                        │  └─ Workspace directory (for temporary checkouts)
                        │     Example: /home/user/Work/mymcp/workspace
                        │
                        └─ 4. {WORKSPACE_PROJECT}
                           └─ Workspace project directory (user's work)
                              Example: /home/user/Work/mymcp/workspace/iproject
```

### Why Two-Stage Substitution?

**Stage 1**: Template substitution (YAML values → template placeholders)
```
{WORKSPACE_PATH} in template ← workspace_path: "{WORKSPACE_PATH}" in YAML
```

**Stage 2**: Path expansion (Portable paths → Actual paths)
```
{WORKSPACE_PATH} in result → /home/user/Work/mymcp/workspace
```

**Benefit**: 
- YAML files can use `"{WORKSPACE_PATH}"` as a value
- This makes YAML files portable across machines
- Each user's `.mymcp-config` defines their actual paths
- Final output has real paths the AI can use

**Example Flow:**

```
Template:          : cd {WORKSPACE_PATH}
                       ↓
YAML substitution: : cd {WORKSPACE_PATH}
  (workspace_path: "{WORKSPACE_PATH}" in YAML)
                       ↓
Path expansion:    : cd /home/user/Work/mymcp/workspace
  (MYMCP_WORKSPACE=/home/user/Work/mymcp/workspace from .mymcp-config)
```

---

## Output Generation

### Output Streams

The script uses **two output streams**:

```
┌─────────────────────────────────────────────────────────────────┐
│  Output Streams                                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  stdout (File Descriptor 1)                   │  stderr (FD 2)  │
│  ─────────────────────────────────────────   │  ───────────────│
│  - The actual generated ask prompt            │  - Info messages│
│  - What user copies/pipes                     │  - Warnings     │
│  - Clean, parseable output                    │  - Errors       │
│                                                │  - Status msgs  │
│  Example:                                      │                 │
│    ask:                                        │  Example:       │
│                                                │    📝 Generating│
│    I already have done the following          │    ✅ Success!  │
│    ...                                         │    💡 Copy...   │
│                                                │                 │
└─────────────────────────────────────────────────────────────────┘
```

### Why This Matters

**Piping to clipboard:**
```bash
./ask_me.sh code_implement_workspace askme/keys/myfile.yaml | xclip -selection clipboard
```

- **stdout** (the ask) goes to xclip
- **stderr** (status messages) appears on terminal
- Result: Clipboard has clean prompt, user sees status

**Redirecting to file:**
```bash
./ask_me.sh analysis_doc_create askme/keys/myfile.yaml > my_prompt.txt
```

- **stdout** → `my_prompt.txt` (clean ask only)
- **stderr** → terminal (status messages)

### Output Code

**Main output** (Line 186 or 226):
```bash
echo "$RESULT"
```
- Goes to stdout
- This is the generated ask

**Status messages** (Lines 230-231):
```bash
success "✅ Ask generated successfully!"
info "💡 Copy the output above and paste it to your AI assistant."
```
- The `success()` and `info()` functions output to stdout (lines 89-91, 94-96)
- BUT they could be modified to use `>&2` to send to stderr

**Current implementation** outputs everything to stdout, but best practice would be:
```bash
echo -e "${GREEN}$1${NC}" >&2  # Send to stderr
```

---

## Complete Example Walkthrough

Let's trace **exactly** what happens when you run:

```bash
./ask_me.sh code_implement_workspace askme/keys/example_implement_chevron_fix.yaml
```

### Step-by-Step Execution

#### Step 1: Script Initialization

```bash
# Script starts
set -e  # Exit on any error

# Colors defined (lines 25-30)
RED='\033[0;31m'
GREEN='\033[0;32m'
# ... etc

# Script directory determined (line 33)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Result: "/home/omcgonag/Work/mymcp"

# Subdirectories defined (lines 34-35)
TEMPLATES_DIR="${SCRIPT_DIR}/askme/templates"
# Result: "/home/omcgonag/Work/mymcp/askme/templates"

KEYS_DIR="${SCRIPT_DIR}/askme/keys"
# Result: "/home/omcgonag/Work/mymcp/askme/keys"
```

#### Step 2: Configuration Loading

```bash
# Check for .mymcp-config (line 38)
if [ -f "${SCRIPT_DIR}/.mymcp-config" ]; then
    source "${SCRIPT_DIR}/.mymcp-config"
    # This exports:
    # MYMCP_REPO_PATH="/home/omcgonag/Work/mymcp"
    # MYMCP_WORKSPACE="/home/omcgonag/Work/mymcp/workspace"
    # MYMCP_WORKSPACE_PROJECT="/home/omcgonag/Work/mymcp/workspace/iproject"
    # ... and more
fi
```

#### Step 3: Argument Parsing

```bash
# Check argument count (line 104)
if [ $# -ne 2 ]; then
    usage  # Would exit here if wrong number of args
fi

# Parse arguments (lines 108-109)
TEMPLATE_TYPE="$1"  # "code_implement_workspace"
KEY_FILE="$2"       # "askme/keys/example_implement_chevron_fix.yaml"
```

#### Step 4: File Resolution

```bash
# Resolve key file path (lines 112-116)
if [[ "$KEY_FILE" = /* ]]; then
    # Absolute path check
    KEY_FILE_PATH="$KEY_FILE"
else
    # Relative path - prepend script dir
    KEY_FILE_PATH="${SCRIPT_DIR}/${KEY_FILE}"
fi
# Result: "/home/omcgonag/Work/mymcp/askme/keys/example_implement_chevron_fix.yaml"

# Build template path (line 119)
TEMPLATE_FILE="${TEMPLATES_DIR}/${TEMPLATE_TYPE}.template"
# Result: "/home/omcgonag/Work/mymcp/askme/templates/code_implement_workspace.template"
```

#### Step 5: Validation

```bash
# Check template exists (lines 120-122)
if [ ! -f "$TEMPLATE_FILE" ]; then
    error "Template '${TEMPLATE_TYPE}' not found at: ${TEMPLATE_FILE}"
    # Would exit with error if not found
fi
# ✓ File exists

# Check key file exists (lines 125-127)
if [ ! -f "$KEY_FILE_PATH" ]; then
    error "Key file not found at: ${KEY_FILE_PATH}"
    # Would exit with error if not found
fi
# ✓ File exists
```

#### Step 6: Info Messages

```bash
# Print generation info (lines 129-132)
info "📝 Generating ask from:"
echo "   Template: ${TEMPLATE_TYPE}.template"
# Output: "   Template: code_implement_workspace.template"
echo "   Key file: ${KEY_FILE}"
# Output: "   Key file: askme/keys/example_implement_chevron_fix.yaml"
echo ""
```

#### Step 7: Parser Selection

```bash
# Check for yq (line 135)
if ! command -v yq &> /dev/null; then
    # yq not found, use Python fallback
    # (Lines 136-186)
else
    # yq found, use yq path
    # (Lines 189-227)
fi
```

**Assuming yq is installed**, we proceed with yq path...

#### Step 8: Template Loading (yq path)

```bash
# Read template (lines 191-192)
TEMPLATE_CONTENT=$(cat "$TEMPLATE_FILE")
# Result:
# "ask:
#
# I already have done the following
#
# : cd {WORKSPACE_PATH}
# : {GIT_SETUP_COMMANDS}
#
# I want you to make all your recommended changes
#
# Show me how you would do this work in this {WORKSPACE_NAME} directory?
# "
```

#### Step 9: YAML Keys Extraction

```bash
# Get all keys from YAML (lines 194-195)
YAML_KEYS=$(yq eval 'keys | .[]' "$KEY_FILE_PATH")
# Result (newline-separated):
# type
# workspace_path
# workspace_name
# git_setup_commands
```

#### Step 10: Substitution Loop

```bash
# Initialize result (line 198)
RESULT="$TEMPLATE_CONTENT"

# Loop through each key (lines 200-221)
while IFS= read -r key; do
    if [ -n "$key" ] && [ "$key" != "type" ]; then
        # Iteration 1: key = "workspace_path"
        
        # Get value from YAML (line 203)
        value=$(yq eval ".workspace_path" "$KEY_FILE_PATH")
        # Result: "{WORKSPACE_PATH}"
        
        # Convert to uppercase (line 206)
        placeholder=$(echo "workspace_path" | tr '[:lower:]' '[:upper:]')
        # Result: "WORKSPACE_PATH"
        
        # Substitute in template (lines 209-216)
        echo "$RESULT" | awk -v placeholder="{WORKSPACE_PATH}" -v value="{WORKSPACE_PATH}" '
        {
            if (index($0, placeholder) > 0) {
                sub(placeholder, value)
            }
            print
        }' > /tmp/ask_me_tmp_12345
        
        RESULT=$(cat /tmp/ask_me_tmp_12345)
        rm -f /tmp/ask_me_tmp_12345
        
        # RESULT now has:
        # ": cd {WORKSPACE_PATH}"
        # (Value is still "{WORKSPACE_PATH}" - will be expanded next stage)
    fi
done <<< "$YAML_KEYS"

# Loop repeats for:
# - workspace_name → {WORKSPACE_NAME} → "horizon-osprh-12803-working"
# - git_setup_commands → {GIT_SETUP_COMMANDS} → multiline git commands
```

**After all substitutions**, RESULT contains:
```
ask:

I already have done the following

: cd {WORKSPACE_PATH}
: git clone https://review.opendev.org/openstack/horizon horizon-osprh-12803-working
  cd horizon-osprh-12803-working
  git fetch https://review.opendev.org/openstack/horizon refs/changes/49/966349/5
  git checkout FETCH_HEAD
  git checkout -b osprh-12803-template-refactor

I want you to make all your recommended changes

Show me how you would do this work in this horizon-osprh-12803-working directory?
```

#### Step 11: Path Expansion

```bash
# Expand path variables (line 224)
RESULT=$(expand_path_vars "$RESULT")

# Inside expand_path_vars():
text="$RESULT"
text="${text//<mymcp-repo-path>/${MYMCP_REPO_PATH}}"
# No matches

text="${text//\{MYMCP_REPO_PATH\}/${MYMCP_REPO_PATH}}"
# No matches

text="${text//\{WORKSPACE_PATH\}/${MYMCP_WORKSPACE}}"
# Replaces: {WORKSPACE_PATH} → /home/omcgonag/Work/mymcp/workspace

text="${text//\{WORKSPACE_PROJECT\}/${MYMCP_WORKSPACE_PROJECT}}"
# No matches

echo "$text"
```

**After expansion**, RESULT contains:
```
ask:

I already have done the following

: cd /home/omcgonag/Work/mymcp/workspace
: git clone https://review.opendev.org/openstack/horizon horizon-osprh-12803-working
  cd horizon-osprh-12803-working
  git fetch https://review.opendev.org/openstack/horizon refs/changes/49/966349/5
  git checkout FETCH_HEAD
  git checkout -b osprh-12803-template-refactor

I want you to make all your recommended changes

Show me how you would do this work in this horizon-osprh-12803-working directory?
```

#### Step 12: Output

```bash
# Output result to stdout (line 226)
echo "$RESULT"

# Output success messages (lines 230-231)
echo ""
success "✅ Ask generated successfully!"
info "💡 Copy the output above and paste it to your AI assistant."
```

**Terminal Output:**
```
📝 Generating ask from:
   Template: code_implement_workspace.template
   Key file: askme/keys/example_implement_chevron_fix.yaml

ask:

I already have done the following

: cd /home/omcgonag/Work/mymcp/workspace
: git clone https://review.opendev.org/openstack/horizon horizon-osprh-12803-working
  cd horizon-osprh-12803-working
  git fetch https://review.opendev.org/openstack/horizon refs/changes/49/966349/5
  git checkout FETCH_HEAD
  git checkout -b osprh-12803-template-refactor

I want you to make all your recommended changes

Show me how you would do this work in this horizon-osprh-12803-working directory?


✅ Ask generated successfully!
💡 Copy the output above and paste it to your AI assistant.
```

---

## Error Handling

### Error Types and Responses

```
┌─────────────────────────────────────────────────────────────────┐
│  Error Handling Matrix                                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Error Condition           │  Detection Point  │  Response       │
│  ─────────────────────────────────────────────────────────────  │
│  Wrong # of arguments      │  Line 104         │  usage()        │
│  Template not found        │  Line 120         │  error() + exit │
│  Key file not found        │  Line 125         │  error() + exit │
│  yq not installed          │  Line 135         │  Warn, fallback │
│  Python not installed      │  Line 177         │  error() + exit │
│  PyYAML not installed      │  Line 177         │  error() + exit │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Error Function

```bash
# Definition (lines 83-86)
error() {
    echo -e "${RED}Error: $1${NC}" >&2
    exit 1
}
```

**What it does:**
1. Prints "Error: <message>" in red
2. Sends output to stderr (`>&2`)
3. Exits with status 1 (failure)

**Example usage:**
```bash
if [ ! -f "$TEMPLATE_FILE" ]; then
    error "Template '${TEMPLATE_TYPE}' not found at: ${TEMPLATE_FILE}"
fi
```

**Terminal output:**
```
Error: Template 'nonexistent' not found at: /home/user/Work/mymcp/askme/templates/nonexistent.template
```

### Validation Flow

```
┌─────────────────────────────────────────────────────────────────┐
│  Validation Sequence                                             │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ├─ 1. Argument Count Check
                        │  └─ if [ $# -ne 2 ]; then usage; fi
                        │     └─ Ensures exactly 2 arguments
                        │
                        ├─ 2. Template File Exists
                        │  └─ if [ ! -f "$TEMPLATE_FILE" ]; then error...; fi
                        │     └─ Verifies template is readable file
                        │
                        ├─ 3. Key File Exists
                        │  └─ if [ ! -f "$KEY_FILE_PATH" ]; then error...; fi
                        │     └─ Verifies key file is readable file
                        │
                        ├─ 4. Parser Availability
                        │  ├─ if ! command -v yq &> /dev/null; then
                        │  │  └─ yq missing → try Python
                        │  └─ if ! python3 -c "import yaml"; then
                        │     └─ PyYAML missing → error with instructions
                        │
                        └─ All checks passed → Continue processing
```

---

## Troubleshooting Guide

### Common Issues and Solutions

#### Issue 1: "Template not found"

**Error Message:**
```
Error: Template 'my_template' not found at: /home/user/Work/mymcp/askme/templates/my_template.template
```

**Cause**: Template file doesn't exist or template type is misspelled

**Solution:**
```bash
# List available templates
ls -1 askme/templates/*.template

# Use exact template name (without .template extension)
./ask_me.sh code_implement_workspace askme/keys/myfile.yaml
                ^^^^^^^^^^^^^^^^^^^^^
                Must match a template file
```

#### Issue 2: "Key file not found"

**Error Message:**
```
Error: Key file not found at: /home/user/Work/mymcp/askme/keys/myfile.yaml
```

**Cause**: Key file doesn't exist or path is wrong

**Solution:**
```bash
# List available key files
ls -1 askme/keys/*.yaml

# Check your path
# Relative path (from mymcp repo root)
./ask_me.sh analysis_doc_create askme/keys/myfile.yaml

# Absolute path
./ask_me.sh analysis_doc_create /tmp/myfile.yaml
```

#### Issue 3: "yq is not installed" + "PyYAML not installed"

**Error Message:**
```
Error: Neither yq nor Python with PyYAML is installed. Please install one of them:
  - yq: https://github.com/mikefarah/yq
  - PyYAML: pip install pyyaml
```

**Cause**: No YAML parser available

**Solution (Option 1 - yq):**
```bash
# Fedora/RHEL
sudo dnf install yq

# Ubuntu/Debian
sudo apt install yq

# macOS
brew install yq

# Manual install
wget https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64 -O /usr/local/bin/yq
chmod +x /usr/local/bin/yq
```

**Solution (Option 2 - PyYAML):**
```bash
pip install pyyaml

# Or with pip3
pip3 install pyyaml

# Or in a virtual environment
python3 -m venv venv
source venv/bin/activate
pip install pyyaml
```

#### Issue 4: Placeholder not substituted

**Symptom**: Output still has `{PLACEHOLDER}` instead of value

**Example:**
```
ask:

Output document: {OUTPUT_DOCUMENT}
```

**Cause**: YAML key name doesn't match placeholder

**Solution:**
```yaml
# Wrong - key doesn't match placeholder
outputDocument: "myfile.md"  # Camel case

# Wrong - case mismatch
OUTPUT_DOCUMENT: "myfile.md"  # All uppercase

# Correct - lowercase with underscores
output_document: "myfile.md"  # Snake case
```

**Placeholder → YAML Key Mapping:**
```
Template placeholder:    {OUTPUT_DOCUMENT}
                            ↓ (convert to lowercase)
YAML key must be:        output_document
```

#### Issue 5: Multiline value broken

**Symptom**: Multiline YAML value appears on one line in output

**Wrong YAML:**
```yaml
specific_questions: "Line 1\nLine 2\nLine 3"
```

**Output (broken):**
```
Line 1\nLine 2\nLine 3
```

**Correct YAML:**
```yaml
specific_questions: |
  Line 1
  Line 2
  Line 3
```

**Output (fixed):**
```
Line 1
Line 2
Line 3
```

**Explanation:**
- Use `|` (pipe) for literal block scalar
- Preserves newlines and formatting
- Use `>` (greater-than) for folded block scalar (joins lines with spaces)

#### Issue 6: Path not expanded

**Symptom**: Output has `{WORKSPACE_PATH}` instead of actual path

**Cause**: `.mymcp-config` not sourced or variable not exported

**Debug:**
```bash
# Check if .mymcp-config exists
ls -la .mymcp-config

# Source it manually and check variables
source ./.mymcp-config
echo $MYMCP_WORKSPACE

# Run script again
./ask_me.sh code_implement_workspace askme/keys/myfile.yaml
```

**Solution:**
Ensure `.mymcp-config` is in the repository root and properly formatted.

#### Issue 7: Wrong directory when running script

**Symptom**: "Template not found" even though template exists

**Cause**: Running script from wrong directory

**Wrong:**
```bash
cd /tmp
/home/user/Work/mymcp/ask_me.sh analysis_doc_create askme/keys/myfile.yaml
# Error: Key file not found (looks for /tmp/askme/keys/myfile.yaml)
```

**Correct:**
```bash
cd /home/user/Work/mymcp
./ask_me.sh analysis_doc_create askme/keys/myfile.yaml

# Or use absolute paths
/home/user/Work/mymcp/ask_me.sh analysis_doc_create /home/user/Work/mymcp/askme/keys/myfile.yaml
```

**Why**: The script uses `SCRIPT_DIR` to find templates, but key file path resolution depends on current directory for relative paths.

---

## Creating Your Own Key File for osprh_16421

Since you want to run `./ask_me.sh osprh_16421`, here's how to create the key file:

### Step 1: Create the Key File

```bash
cat > askme/keys/osprh_16421.yaml <<'EOF'
type: analysis_doc_create
output_document: "{WORKSPACE_PROJECT}/analysis/analysis_new_feature_osprh_16421/spike.md"
context_description: |
  Working on OSPRH-16421: Add expandable rows (chevrons) to the Images table.
  
  This feature is similar to OSPRH-12803 (Key Pairs expandable rows) which was
  implemented in Review 966349.
  
  Reference Implementation: https://review.opendev.org/c/openstack/horizon/+/966349
  
  We want to apply the same pattern to the Images table to allow users to expand
  rows and view image details without navigating to a separate page.
  
specific_questions: |
  1. How should we implement expandable rows for the Images table?
  
  2. What are the key architectural differences between Images and Key Pairs
     that we need to consider?
  
  3. Should we follow the exact same pattern from Review 966349, or are there
     improvements we should make?
  
  4. What are the main technical risks for this implementation?
  
  5. How should we break this work into reviewable patchsets?
EOF
```

### Step 2: Choose the Template

The key file above uses `type: analysis_doc_create`, which means it will use the `analysis_doc_create.template`.

### Step 3: Run the Script

**Two-argument mode (recommended):**
```bash
./ask_me.sh analysis_doc_create askme/keys/osprh_16421.yaml
```

**Or**, if you want single-argument mode, you'd need to modify the script to:
1. Check if only one argument is provided
2. Assume it's a key file name
3. Look for `askme/keys/<argument>.yaml`
4. Read the `type:` field from that YAML
5. Use that as the template type

**Modified script logic (you'd add this):**
```bash
if [ $# -eq 1 ]; then
    # Single argument mode
    KEY_FILE="askme/keys/${1}.yaml"
    KEY_FILE_PATH="${SCRIPT_DIR}/${KEY_FILE}"
    
    if [ ! -f "$KEY_FILE_PATH" ]; then
        error "Key file not found at: ${KEY_FILE_PATH}"
    fi
    
    # Extract template type from YAML
    TEMPLATE_TYPE=$(yq eval '.type' "$KEY_FILE_PATH" 2>/dev/null || \
                    python3 -c "import yaml; print(yaml.safe_load(open('$KEY_FILE_PATH'))['type'])")
elif [ $# -eq 2 ]; then
    # Two argument mode (current implementation)
    TEMPLATE_TYPE="$1"
    KEY_FILE="$2"
else
    usage
fi
```

### Step 4: Expected Output

Running the command will generate:

```
📝 Generating ask from:
   Template: analysis_doc_create.template
   Key file: askme/keys/osprh_16421.yaml

ask:

[Content of analysis_doc_create.template with all placeholders filled in]

Output document: /home/omcgonag/Work/mymcp/workspace/iproject/analysis/analysis_new_feature_osprh_16421/spike.md

Context:
Working on OSPRH-16421: Add expandable rows (chevrons) to the Images table.

This feature is similar to OSPRH-12803 (Key Pairs expandable rows) which was
implemented in Review 966349.

[... rest of the context ...]

Questions:
1. How should we implement expandable rows for the Images table?

2. What are the key architectural differences between Images and Key Pairs
   that we need to consider?

[... rest of the questions ...]


✅ Ask generated successfully!
💡 Copy the output above and paste it to your AI assistant.
```

---

## Summary: The Complete Picture

### What Happens (High-Level)

```
1. You run: ./ask_me.sh <template> <key-file>
2. Script validates: Do these files exist?
3. Script loads: .mymcp-config for path variables
4. Script reads: Template file (structure with placeholders)
5. Script reads: YAML key file (your specific values)
6. Script merges: YAML values → Template placeholders
7. Script expands: {WORKSPACE_PATH} → /actual/path
8. Script outputs: Ready-to-use prompt
9. You copy/paste: To your AI assistant
```

### Why It's Useful

| Manual Prompt Writing | Using ask_me.sh |
|----------------------|-----------------|
| Type entire prompt every time | Reuse templates |
| Inconsistent formatting | Standardized structure |
| Hardcoded paths | Portable variables |
| No history | YAML files = documentation |
| Error-prone | Validated & automated |
| Slow | Fast |

### Files Involved

```
mymcp/
├── ask_me.sh                          ← Main script
├── .mymcp-config                      ← Path configuration
├── askme/
│   ├── templates/
│   │   ├── analysis_doc_create.template    ← Prompt structure
│   │   ├── code_implement_workspace.template
│   │   └── ...
│   └── keys/
│       ├── osprh_16421.yaml           ← Your values (to be created)
│       ├── example_implement_chevron_fix.yaml
│       └── ...
```

### Key Concepts

1. **Separation of Concerns**: Structure (template) vs. Content (YAML)
2. **Portability**: Path variables work on any machine
3. **Automation**: Script does the boring merging work
4. **Documentation**: YAML files preserve your questions
5. **Consistency**: Same template = same format every time

---

## Quick Reference Card

### Command Syntax

```bash
./ask_me.sh <template-type> <key-file>
```

### Available Template Types

- `analysis_doc_create` - Start new investigation
- `code_implement_workspace` - Implement changes
- `code_review_response` - Respond to review comments
- `investigate_patterns` - Research patterns
- `phase_done` - Wrap up phase

### YAML Key File Format

```yaml
type: <template-type>
<placeholder_name>: <value>
<multiline_placeholder>: |
  Line 1
  Line 2
```

### Path Variables (use in YAML values)

- `{WORKSPACE_PATH}` - `/path/to/mymcp/workspace`
- `{WORKSPACE_PROJECT}` - `/path/to/mymcp/workspace/iproject`
- `{MYMCP_REPO_PATH}` - `/path/to/mymcp`

### Common Operations

```bash
# Generate ask
./ask_me.sh analysis_doc_create askme/keys/myfile.yaml

# Copy to clipboard (Linux)
./ask_me.sh analysis_doc_create askme/keys/myfile.yaml | xclip -selection clipboard

# Save to file
./ask_me.sh analysis_doc_create askme/keys/myfile.yaml > prompt.txt

# List templates
ls -1 askme/templates/*.template

# List key files
ls -1 askme/keys/*.yaml
```

---

**Document Version**: 1.0  
**Created**: 2025-11-23  
**For**: Complete understanding of ask_me.sh processing

**See Also:**
- [`askme/README.md`](../askme/README.md) - Quick start guide
- [`askme/PATH_VARIABLES.md`](../askme/PATH_VARIABLES.md) - Path variables reference
- [`docs/CENTRAL_CONFIGURATION.md`](CENTRAL_CONFIGURATION.md) - Configuration system
- [`kb/KBA_Choosing_AI_Methods_for_Analysis_in_mymcp.md`](../kb/KBA_Choosing_AI_Methods_for_Analysis_in_mymcp.md) - AI methods comparison

