# Template Variables in ask_me.sh

**Feature**: Pass values on the command line to substitute into YAML template files

**Version**: Added 2025-11-23

---

## Overview

Instead of creating a new YAML key file for each similar task, you can create **one reusable template** and pass values on the command line.

### Problem This Solves

**Before** (without template variables):
```bash
# Need separate YAML file for each ticket
askme/keys/osprh_16421.yaml
askme/keys/osprh_99999.yaml
askme/keys/osprh_12345.yaml
# ... one file per ticket (repetitive!)
```

**After** (with template variables):
```bash
# One template file, reused with different values
askme/keys/osprh_template.yaml

# Use it for any ticket:
./ask_me.sh analysis_doc_create askme/keys/osprh_template.yaml TICKET_NUMBER=16421
./ask_me.sh analysis_doc_create askme/keys/osprh_template.yaml TICKET_NUMBER=99999
./ask_me.sh analysis_doc_create askme/keys/osprh_template.yaml TICKET_NUMBER=12345
```

---

## Usage

### Basic Syntax

```bash
./ask_me.sh <template-type> <key-file> [VAR=value ...]
```

### Examples

#### Example 1: Single Variable

```bash
./ask_me.sh analysis_doc_create askme/keys/osprh_template.yaml TICKET_NUMBER=16421
```

#### Example 2: Multiple Variables

```bash
./ask_me.sh analysis_doc_create askme/keys/osprh_template.yaml \
    TICKET_NUMBER=16421 \
    FEATURE_NAME="Add expandable rows to Images table"
```

#### Example 3: Variables with Spaces

```bash
./ask_me.sh analysis_doc_create askme/keys/osprh_template.yaml \
    TICKET_NUMBER=99999 \
    FEATURE_NAME="Implement dark mode toggle" \
    REFERENCE_REVIEW=966349
```

---

## Creating a Template YAML

### Step 1: Identify Repetitive Values

Look at your existing YAML files and find what changes between them:

```yaml
# osprh_16421.yaml
output_document: "...osprh_16421/spike.md"
context_description: |
  Working on OSPRH-16421: Add expandable rows...

# osprh_99999.yaml
output_document: "...osprh_99999/spike.md"
context_description: |
  Working on OSPRH-99999: Different feature...
```

The parts that change:
- Ticket number: `16421` vs `99999`
- Feature description

### Step 2: Replace with Template Variables

Use `{VAR_NAME}` placeholders:

```yaml
type: analysis_doc_create
output_document: "{WORKSPACE_PROJECT}/analysis/analysis_new_feature_osprh_{TICKET_NUMBER}/spike.md"
context_description: |
  Working on OSPRH-{TICKET_NUMBER}: {FEATURE_NAME}
```

### Step 3: Document the Variables

Add a comment block at the top:

```yaml
# Template Variables:
#   {TICKET_NUMBER}  - The OSPRH ticket number
#   {FEATURE_NAME}   - Brief feature description
#   {REFERENCE_REVIEW} - (Optional) Related review number

type: analysis_doc_create
# ... rest of template
```

---

## Variable Naming Rules

### Valid Variable Names

```bash
TICKET_NUMBER=16421        ✅ Valid
FEATURE_NAME="My Feature"  ✅ Valid
REF_REVIEW=966349          ✅ Valid
MY_VAR_123=value           ✅ Valid
```

**Rules:**
- Must start with uppercase letter or underscore
- Can contain: uppercase letters, digits, underscores
- Format: `VAR_NAME=value`

### Invalid Variable Names

```bash
ticket_number=16421   ❌ Lowercase not allowed
123VAR=value          ❌ Can't start with digit
my-var=value          ❌ Hyphens not allowed
var name=value        ❌ No spaces in name
```

---

## Template Variable Formats

The script supports **three placeholder formats** in your YAML:

### Format 1: Single Braces (Recommended)

```yaml
output_document: "path/to/osprh_{TICKET_NUMBER}/spike.md"
```

**Best for**: Most cases, clean syntax

### Format 2: Dollar Braces

```yaml
output_document: "path/to/osprh_${TICKET_NUMBER}/spike.md"
```

**Best for**: When you need shell-style variable syntax

### Format 3: Double Braces

```yaml
output_document: "path/to/osprh_{{TICKET_NUMBER}}/spike.md"
```

**Best for**: When you want to distinguish from path variables like `{WORKSPACE_PATH}`

### Which Format to Use?

**Recommendation**: Use `{VAR_NAME}` (single braces) for simplicity.

All three formats work identically - choose based on:
- Personal preference
- Consistency with your other templates
- Avoiding conflicts with other placeholder types

---

## Complete Example

### Template File: `askme/keys/osprh_template.yaml`

```yaml
# Template for OSPRH ticket analysis
#
# Usage:
#   ./ask_me.sh analysis_doc_create askme/keys/osprh_template.yaml \
#       TICKET_NUMBER=16421 \
#       FEATURE_NAME="Add expandable rows"
#
# Variables:
#   {TICKET_NUMBER}    - OSPRH ticket number
#   {FEATURE_NAME}     - Feature description
#   {REFERENCE_TICKET} - Related ticket (optional)
#   {REFERENCE_REVIEW} - Related review (optional)

type: analysis_doc_create
output_document: "{WORKSPACE_PROJECT}/analysis/analysis_new_feature_osprh_{TICKET_NUMBER}/spike.md"

context_description: |
  Working on OSPRH-{TICKET_NUMBER}: {FEATURE_NAME}
  
  Reference Implementation:
  - Ticket: OSPRH-{REFERENCE_TICKET}
  - Review: https://review.opendev.org/c/openstack/horizon/+/{REFERENCE_REVIEW}

specific_questions: |
  1. How should we implement: {FEATURE_NAME}?
  
  2. What are the architectural considerations?
  
  3. What are the key risks?
```

### Usage

```bash
# Minimal usage (only required variables)
./ask_me.sh analysis_doc_create askme/keys/osprh_template.yaml \
    TICKET_NUMBER=16421 \
    FEATURE_NAME="Add expandable rows to Images table"

# Full usage (all variables)
./ask_me.sh analysis_doc_create askme/keys/osprh_template.yaml \
    TICKET_NUMBER=16421 \
    FEATURE_NAME="Add expandable rows to Images table" \
    REFERENCE_TICKET=12803 \
    REFERENCE_REVIEW=966349
```

### Resulting Substitution

**Before** (in template):
```yaml
output_document: "{WORKSPACE_PROJECT}/analysis/analysis_new_feature_osprh_{TICKET_NUMBER}/spike.md"
context_description: |
  Working on OSPRH-{TICKET_NUMBER}: {FEATURE_NAME}
```

**After** (with TICKET_NUMBER=16421, FEATURE_NAME="Add expandable rows"):
```yaml
output_document: "{WORKSPACE_PROJECT}/analysis/analysis_new_feature_osprh_16421/spike.md"
context_description: |
  Working on OSPRH-16421: Add expandable rows to Images table
```

**After path expansion**:
```yaml
output_document: "/home/user/Work/mymcp/workspace/iproject/analysis/analysis_new_feature_osprh_16421/spike.md"
context_description: |
  Working on OSPRH-16421: Add expandable rows to Images table
```

---

## Substitution Order

Understanding the order of substitutions helps debug issues:

```
┌─────────────────────────────────────────────────────────────┐
│  Substitution Order                                          │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    ├─ 1. Template Variables (Command Line)
                    │  └─ {TICKET_NUMBER} → 16421
                    │     {FEATURE_NAME} → "Add expandable rows"
                    │
                    ├─ 2. YAML Placeholders (From YAML → Template)
                    │  └─ {OUTPUT_DOCUMENT} → value from YAML
                    │     {CONTEXT_DESCRIPTION} → value from YAML
                    │
                    └─ 3. Path Variables (From .mymcp-config)
                       └─ {WORKSPACE_PATH} → /actual/path/workspace
                          {WORKSPACE_PROJECT} → /actual/path/workspace/iproject
```

**Example Flow:**

```
Step 0 (Template YAML):
  output_document: "{WORKSPACE_PROJECT}/analysis/osprh_{TICKET_NUMBER}/spike.md"

Step 1 (Template variable substitution):
  TICKET_NUMBER=16421 passed on command line
  Result: "{WORKSPACE_PROJECT}/analysis/osprh_16421/spike.md"

Step 2 (YAML → Template substitution):
  Template has: {OUTPUT_DOCUMENT}
  YAML provides: "{WORKSPACE_PROJECT}/analysis/osprh_16421/spike.md"
  Result in ask: "{WORKSPACE_PROJECT}/analysis/osprh_16421/spike.md"

Step 3 (Path expansion):
  {WORKSPACE_PROJECT} → /home/user/Work/mymcp/workspace/iproject
  Final result: "/home/user/Work/mymcp/workspace/iproject/analysis/osprh_16421/spike.md"
```

---

## Best Practices

### 1. Document Your Variables

Always include a comment block explaining what variables are expected:

```yaml
# Template Variables:
#   {TICKET_NUMBER}  - Required: OSPRH ticket number
#   {FEATURE_NAME}   - Required: Brief description
#   {COMPONENT}      - Optional: Component name (default: horizon)
```

### 2. Provide Default Values

For optional variables, include fallback text in your template:

```yaml
context_description: |
  Working on OSPRH-{TICKET_NUMBER}: {FEATURE_NAME}
  Component: {COMPONENT}
  # If COMPONENT not provided, this will show: Component: {COMPONENT}
  # User will see they need to provide it
```

**Better approach** - use conditional text:

```yaml
context_description: |
  Working on OSPRH-{TICKET_NUMBER}: {FEATURE_NAME}
  
  # If you see {COMPONENT} below, you forgot to pass COMPONENT=value
  Component: {COMPONENT}
```

### 3. Use Descriptive Variable Names

```yaml
# Good
TICKET_NUMBER=16421
FEATURE_NAME="Add expandable rows"
REFERENCE_REVIEW=966349

# Less clear
TICKET=16421
NAME="Add expandable rows"
REF=966349
```

### 4. Group Related Templates

```bash
askme/keys/
├── osprh_template.yaml           # General OSPRH ticket analysis
├── bug_fix_template.yaml          # Bug fix analysis
├── feature_template.yaml          # New feature planning
└── refactor_template.yaml         # Refactoring analysis
```

### 5. Version Your Templates

Add version/date comments:

```yaml
# OSPRH Analysis Template
# Version: 2.0
# Last Updated: 2025-11-23
# 
# Changelog:
#   2.0 - Added REFERENCE_TICKET and REFERENCE_REVIEW variables
#   1.0 - Initial template

# Template Variables:
# ...
```

---

## Troubleshooting

### Variable Not Substituted

**Symptom**: Output still shows `{VARIABLE_NAME}` instead of value

**Causes & Solutions:**

1. **Typo in command line**
   ```bash
   # Wrong
   ./ask_me.sh ... TICKET_NUMER=16421
                         ^^^^^^ typo
   
   # Correct
   ./ask_me.sh ... TICKET_NUMBER=16421
   ```

2. **Case mismatch**
   ```bash
   # YAML uses: {ticket_number}
   # Command uses: TICKET_NUMBER=16421
   # These don't match!
   
   # Solution: Script converts to lowercase, so use uppercase on command line
   TICKET_NUMBER=16421  → tries to replace {TICKET_NUMBER} and {ticket_number}
   ```

3. **Wrong placeholder format**
   ```yaml
   # YAML has: @TICKET_NUMBER@  (custom format)
   # Command: TICKET_NUMBER=16421
   # Won't match because script looks for {VAR}, ${VAR}, or {{VAR}}
   
   # Solution: Use supported formats
   {TICKET_NUMBER}   ✅
   ${TICKET_NUMBER}  ✅
   {{TICKET_NUMBER}} ✅
   @TICKET_NUMBER@   ❌
   ```

### Special Characters in Value

**Symptom**: Variable with special characters breaks substitution

**Example:**
```bash
# This might break
FEATURE_NAME="Add & remove items"
              ^^ ampersand
```

**Solution**: Quote the value properly:

```bash
# Single quotes (safest for special chars)
FEATURE_NAME='Add & remove items'

# Double quotes (allows variable expansion)
FEATURE_NAME="Add & remove items"

# Escape special characters
FEATURE_NAME="Add \& remove items"
```

### Variable Not Passed to Script

**Symptom**: Script doesn't recognize variable

**Debug:**
```bash
# Add -x for debug output
bash -x ./ask_me.sh analysis_doc_create askme/keys/template.yaml TICKET_NUMBER=16421

# Look for lines showing variable parsing
# You should see:
#   + var_name=TICKET_NUMBER
#   + var_value=16421
```

**Common cause**: Missing `=` or space issues

```bash
# Wrong
./ask_me.sh template.yaml TICKET_NUMBER 16421
                          ^^^^^^^^^^^^^ missing =

# Correct
./ask_me.sh template.yaml TICKET_NUMBER=16421
```

---

## Advanced Usage

### Combining with Path Variables

```yaml
# Template uses both template vars and path vars
output_document: "{WORKSPACE_PROJECT}/analysis/osprh_{TICKET_NUMBER}/spike.md"
                 ^^^^^^^^^^^^^^^^^^^           ^^^^^^^^^^^^^^
                 Path variable                 Template variable
```

**Command:**
```bash
./ask_me.sh analysis_doc_create askme/keys/template.yaml TICKET_NUMBER=16421
```

**Result** (after all substitutions):
```
/home/user/Work/mymcp/workspace/iproject/analysis/osprh_16421/spike.md
```

### Multiple Templates for Different Use Cases

**Feature analysis:**
```bash
./ask_me.sh analysis_doc_create askme/keys/feature_template.yaml \
    TICKET_NUMBER=16421 \
    FEATURE_TYPE=expandable_rows
```

**Bug fix:**
```bash
./ask_me.sh analysis_doc_create askme/keys/bugfix_template.yaml \
    TICKET_NUMBER=99999 \
    BUG_SEVERITY=critical
```

**Refactoring:**
```bash
./ask_me.sh code_implement_workspace askme/keys/refactor_template.yaml \
    COMPONENT=tables \
    REFACTOR_TYPE=modernization
```

---

## Migration Guide

### Migrating Existing YAML Files to Templates

If you have many similar YAML files, convert them to templates:

**Step 1**: Identify the pattern

```bash
# You have:
askme/keys/osprh_16421.yaml
askme/keys/osprh_99999.yaml
askme/keys/osprh_12345.yaml
```

**Step 2**: Find common structure

```yaml
# All have similar content:
output_document: "...osprh_XXXXX/spike.md"
context: "Working on OSPRH-XXXXX: ..."
```

**Step 3**: Create template

```yaml
# askme/keys/osprh_template.yaml
output_document: "...osprh_{TICKET_NUMBER}/spike.md"
context: "Working on OSPRH-{TICKET_NUMBER}: {FEATURE_NAME}"
```

**Step 4**: Test

```bash
# Test with one ticket
./ask_me.sh analysis_doc_create askme/keys/osprh_template.yaml \
    TICKET_NUMBER=16421 \
    FEATURE_NAME="Test feature"

# Compare output with old method
./ask_me.sh analysis_doc_create askme/keys/osprh_16421.yaml

# If identical (except for content), template works!
```

**Step 5**: Archive old files

```bash
mkdir askme/keys/archive/
mv askme/keys/osprh_*.yaml askme/keys/archive/
# Keep the template
mv askme/keys/archive/osprh_template.yaml askme/keys/
```

---

## Examples from Real Use Cases

### Example 1: OSPRH Ticket Analysis

```bash
./ask_me.sh analysis_doc_create askme/keys/osprh_template.yaml \
    TICKET_NUMBER=16421 \
    FEATURE_NAME="Add expandable rows to Images table" \
    REFERENCE_TICKET=12803 \
    REFERENCE_REVIEW=966349
```

### Example 2: Bug Fix Investigation

```bash
./ask_me.sh analysis_doc_create askme/keys/bugfix_template.yaml \
    TICKET_NUMBER=88888 \
    BUG_DESCRIPTION="Memory leak in table rendering" \
    SEVERITY=high \
    AFFECTED_COMPONENT=openstack_dashboard/dashboards/project/images
```

### Example 3: Code Review Response

```bash
./ask_me.sh code_review_response askme/keys/review_comment_template.yaml \
    REVIEW_NUMBER=967269 \
    PATCHSET=5 \
    REVIEWER=john_doe \
    FILE_PATH=openstack_dashboard/dashboards/project/images/tables.py
```

---

## See Also

- [`askme/README.md`](README.md) - Overview of the ask automation system
- [`docs/USE_CASE_ASK_ME.md`](../docs/USE_CASE_ASK_ME.md) - Complete technical documentation
- [`askme/PATH_VARIABLES.md`](PATH_VARIABLES.md) - Path variable reference
- Example template: [`askme/keys/osprh_template.yaml`](keys/osprh_template.yaml)

---

**Version**: 1.0  
**Created**: 2025-11-23  
**Feature**: Template Variables for ask_me.sh

