# Template Variables Feature - Implementation Summary

**Feature Added**: 2025-11-23  
**Status**: ✅ Complete and Tested

---

## Problem Solved

### Before (Your Question)

> *"Does that mean I need to create a askme/keys/osprh_99999.yaml?"*  
> *"Why can't the ask_me.sh framework take in something like:*  
> *`./ask_me.sh analysis_doc_create osprh_16421 askme/keys/osprh_xxxxx.yaml`*  
> *where we substitute the ticket number 16421 appropriately"*

**Yes, you were right!** The old system required creating a new YAML file for each ticket, which was repetitive and violated DRY principles.

### After (Now Implemented)

You can now use **one template file** and pass values on the command line:

```bash
# Use the same template for any ticket!
./ask_me.sh analysis_doc_create askme/keys/osprh_template.yaml \
    TICKET_NUMBER=16421 \
    FEATURE_NAME="Add expandable rows to Images table"

./ask_me.sh analysis_doc_create askme/keys/osprh_template.yaml \
    TICKET_NUMBER=99999 \
    FEATURE_NAME="Different feature"
```

---

## What Was Implemented

### 1. Enhanced ask_me.sh Script

**File Modified**: `ask_me.sh`

**Changes:**
- ✅ Accepts additional command-line arguments (`VAR=value`)
- ✅ Parses variable assignments into associative array
- ✅ New function: `substitute_template_vars()` - Replaces placeholders in YAML
- ✅ Supports three placeholder formats: `{VAR}`, `${VAR}`, `{{VAR}}`
- ✅ Case-insensitive matching (TICKET_NUMBER matches {ticket_number})
- ✅ Automatic cleanup of temporary files
- ✅ Updated usage message with examples

**New Workflow:**
```
Command line → Parse variables → Substitute in YAML → Normal processing
```

### 2. Template YAML File

**File Created**: `askme/keys/osprh_template.yaml`

**Purpose**: Reusable template for OSPRH ticket analysis

**Template Variables:**
- `{TICKET_NUMBER}` - OSPRH ticket number
- `{FEATURE_NAME}` - Feature description
- `{REFERENCE_TICKET}` - Related ticket (optional)
- `{REFERENCE_REVIEW}` - Related review (optional)

**Usage Example:**
```bash
./ask_me.sh analysis_doc_create askme/keys/osprh_template.yaml \
    TICKET_NUMBER=16421 \
    FEATURE_NAME="Add expandable rows to Images table" \
    REFERENCE_TICKET=12803 \
    REFERENCE_REVIEW=966349
```

### 3. Comprehensive Documentation

**Files Created:**
1. **`askme/TEMPLATE_VARIABLES.md`** (Full documentation)
   - Complete usage guide
   - Substitution order explanation
   - Best practices
   - Troubleshooting
   - Advanced usage examples
   - Migration guide

2. **`askme/TEMPLATE_VARIABLES_SUMMARY.md`** (This file)
   - Quick implementation summary
   - What was changed
   - How to use it

**Files Updated:**
1. **`askme/README.md`**
   - Added template variables section
   - Updated quick start examples

2. **`docs/USE_CASE_ASK_ME.md`**
   - Updated command anatomy
   - Added Stage 3: Template Variable Substitution
   - Updated stage numbers throughout
   - Added Mode 2 documentation

---

## How It Works

### Three-Stage Substitution

```
┌─────────────────────────────────────────────────────────────┐
│  Substitution Order                                          │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    ├─ STAGE 1: Template Variables (Command Line)
                    │  └─ {TICKET_NUMBER} → 16421
                    │     {FEATURE_NAME} → "Add expandable rows"
                    │
                    ├─ STAGE 2: YAML Placeholders (YAML → Template)
                    │  └─ {OUTPUT_DOCUMENT} → value from YAML
                    │     {SPECIFIC_QUESTIONS} → value from YAML
                    │
                    └─ STAGE 3: Path Variables (.mymcp-config)
                       └─ {WORKSPACE_PATH} → /actual/path/workspace
                          {WORKSPACE_PROJECT} → /actual/path/iproject
```

### Example Flow

**Input (Command Line):**
```bash
./ask_me.sh analysis_doc_create askme/keys/osprh_template.yaml \
    TICKET_NUMBER=16421 \
    FEATURE_NAME="Add expandable rows"
```

**Step 1: Template YAML has:**
```yaml
output_document: "{WORKSPACE_PROJECT}/analysis/osprh_{TICKET_NUMBER}/spike.md"
context_description: |
  Working on OSPRH-{TICKET_NUMBER}: {FEATURE_NAME}
```

**Step 2: After template variable substitution:**
```yaml
output_document: "{WORKSPACE_PROJECT}/analysis/osprh_16421/spike.md"
context_description: |
  Working on OSPRH-16421: Add expandable rows
```

**Step 3: After YAML → Template substitution:**
```
Output document: {WORKSPACE_PROJECT}/analysis/osprh_16421/spike.md

Context: Working on OSPRH-16421: Add expandable rows
```

**Step 4: After path expansion:**
```
Output document: /home/user/Work/mymcp/workspace/iproject/analysis/osprh_16421/spike.md

Context: Working on OSPRH-16421: Add expandable rows
```

---

## Usage Examples

### Basic Usage

```bash
./ask_me.sh analysis_doc_create askme/keys/osprh_template.yaml \
    TICKET_NUMBER=16421 \
    FEATURE_NAME="Add expandable rows to Images table"
```

### Full Usage (All Variables)

```bash
./ask_me.sh analysis_doc_create askme/keys/osprh_template.yaml \
    TICKET_NUMBER=16421 \
    FEATURE_NAME="Add expandable rows to Images table" \
    REFERENCE_TICKET=12803 \
    REFERENCE_REVIEW=966349
```

### Different Tickets (Same Template)

```bash
# Ticket 16421
./ask_me.sh analysis_doc_create askme/keys/osprh_template.yaml \
    TICKET_NUMBER=16421 \
    FEATURE_NAME="Expandable rows for Images"

# Ticket 99999
./ask_me.sh analysis_doc_create askme/keys/osprh_template.yaml \
    TICKET_NUMBER=99999 \
    FEATURE_NAME="Dark mode toggle"

# Ticket 12345
./ask_me.sh analysis_doc_create askme/keys/osprh_template.yaml \
    TICKET_NUMBER=12345 \
    FEATURE_NAME="API performance improvements"
```

---

## Testing Results

**Test Command:**
```bash
./ask_me.sh analysis_doc_create askme/keys/osprh_template.yaml \
    TICKET_NUMBER=16421 \
    FEATURE_NAME="Add expandable rows to Images table" \
    REFERENCE_TICKET=12803 \
    REFERENCE_REVIEW=966349
```

**Output:**
```
   Variable: TICKET_NUMBER=16421
   Variable: FEATURE_NAME=Add expandable rows to Images table
   Variable: REFERENCE_TICKET=12803
   Variable: REFERENCE_REVIEW=966349
📝 Generating ask from:
   Template: analysis_doc_create.template
   Key file: askme/keys/osprh_template.yaml
   Applied 4 template variable(s)

ask:

For your answers to my inquiry below - please create a new /home/omcgonag/Work/mymcp/workspace/iproject/analysis/analysis_new_feature_osprh_16421/spike.md

Working on OSPRH-16421: Add expandable rows to Images table

This feature request requires investigation to determine:
- Technical approach
- Implementation complexity
- Potential risks
- Breakdown into reviewable patchsets

Similar work (if applicable):
- Reference Ticket: OSPRH-12803
- Reference Review: https://review.opendev.org/c/openstack/horizon/+/966349

[... questions follow ...]

✅ Ask generated successfully!
```

**Result**: ✅ All substitutions worked correctly!

---

## Benefits

### For You

1. **No More Duplicate YAML Files**
   - Before: `osprh_16421.yaml`, `osprh_99999.yaml`, `osprh_12345.yaml`, ...
   - After: One `osprh_template.yaml` for all tickets

2. **Faster Workflow**
   - Before: Create/edit YAML file → Run script
   - After: Run script with values on command line

3. **Less Maintenance**
   - Before: Update format? Edit every YAML file
   - After: Update format? Edit one template

4. **Scriptable**
   ```bash
   # Can now easily automate
   for ticket in 16421 99999 12345; do
       ./ask_me.sh analysis_doc_create askme/keys/osprh_template.yaml \
           TICKET_NUMBER=$ticket \
           FEATURE_NAME="Feature $ticket"
   done
   ```

### For the System

1. **DRY Principle** - Don't Repeat Yourself
2. **Flexible** - Works with old YAML files (backward compatible)
3. **Extensible** - Easy to add more template files
4. **Well-documented** - Complete guides available

---

## Backward Compatibility

**Important**: The old way still works!

```bash
# Old way (still works)
./ask_me.sh analysis_doc_create askme/keys/example_fix_chevron_id.yaml

# New way (with template variables)
./ask_me.sh analysis_doc_create askme/keys/osprh_template.yaml TICKET_NUMBER=16421
```

---

## Files Changed/Created

### Modified Files
- ✅ `ask_me.sh` - Enhanced with template variable support
- ✅ `askme/README.md` - Added template variables section
- ✅ `docs/USE_CASE_ASK_ME.md` - Updated with new feature documentation

### New Files
- ✅ `askme/keys/osprh_template.yaml` - Example template YAML
- ✅ `askme/TEMPLATE_VARIABLES.md` - Complete documentation
- ✅ `askme/TEMPLATE_VARIABLES_SUMMARY.md` - This summary

---

## Next Steps

### Try It Now!

```bash
cd /home/omcgonag/Work/mymcp

# Use the template for ticket 16421
./ask_me.sh analysis_doc_create askme/keys/osprh_template.yaml \
    TICKET_NUMBER=16421 \
    FEATURE_NAME="Add expandable rows to Images table"

# Use it for another ticket
./ask_me.sh analysis_doc_create askme/keys/osprh_template.yaml \
    TICKET_NUMBER=99999 \
    FEATURE_NAME="My new feature"
```

### Create Your Own Templates

1. Identify repetitive YAML files
2. Extract common structure
3. Replace changing values with `{VARIABLE_NAME}`
4. Save as `*_template.yaml`
5. Use with command-line variables!

### Read the Documentation

- **Quick Start**: `askme/README.md`
- **Complete Guide**: `askme/TEMPLATE_VARIABLES.md`
- **Technical Details**: `docs/USE_CASE_ASK_ME.md`

---

## Summary

✅ **Problem**: Had to create new YAML file for each similar task  
✅ **Solution**: Template variables - reuse one file with command-line values  
✅ **Implementation**: Fully functional, tested, documented  
✅ **Backward Compatible**: Old method still works  
✅ **Ready to Use**: Try it with `osprh_template.yaml`!

**Your workflow is now more efficient and follows the DRY principle!** 🎉

---

## Questions?

- See `askme/TEMPLATE_VARIABLES.md` for complete documentation
- See `docs/USE_CASE_ASK_ME.md` for technical details
- Example template: `askme/keys/osprh_template.yaml`

