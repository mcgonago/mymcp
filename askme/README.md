# Ask Me Automation System

Automated prompt generation system for AI-assisted feature development workflows.

## Overview

This system allows you to generate consistent, well-formatted "ask" prompts by using templates and YAML key files. It was designed based on patterns identified from the successful Review 966349 (Key Pairs de-angularization) development cycle.

## Quick Start

### 1. Generate an ask from a template

```bash
./ask_me.sh <template-type> <key-file> [VAR=value ...]
```

### 2. Basic Example

```bash
./ask_me.sh analysis_doc_create askme/keys/example_fix_chevron_id.yaml
```

### 3. With Template Variables (NEW!)

```bash
# Reuse one template for multiple tickets
./ask_me.sh analysis_doc_create askme/keys/osprh_template.yaml \
    TICKET_NUMBER=16421 \
    FEATURE_NAME="Add expandable rows to Images table"
```

This will output a formatted ask that you can copy and paste to your AI assistant.

> [!TIP]
> **New Feature**: Use template variables to avoid creating a new YAML file for each similar task!  
> See [TEMPLATE_VARIABLES.md](TEMPLATE_VARIABLES.md) for complete documentation.

## Available Templates

| Template Type | Purpose | Use When |
|---------------|---------|----------|
| `analysis_doc_create` | Create analysis document with investigation | Starting a new investigation or problem analysis |
| `code_implement_workspace` | Implement code changes in workspace | Ready to implement recommended changes |
| `code_review_response` | Respond to code review comment | Addressing reviewer feedback |
| `investigate_patterns` | Investigate framework patterns | Researching best practices or design patterns |
| `phase_done` | Wrap-up and phase transition | Completing a phase, final questions |

## Directory Structure

```
mymcp/
├── ask_me.sh                          # Main automation script
├── askme/
│   ├── README.md                      # This file
│   ├── templates/                     # Template files
│   │   ├── analysis_doc_create.template
│   │   ├── code_implement_workspace.template
│   │   ├── code_review_response.template
│   │   ├── investigate_patterns.template
│   │   └── phase_done.template
│   └── keys/                          # YAML key files (your configs)
│       ├── example_fix_chevron_id.yaml
│       ├── example_implement_chevron_fix.yaml
│       ├── example_review_comment_css_gap.yaml
│       ├── example_template_pattern.yaml
│       └── example_phase_done_gerrit_topic.yaml
└── analysis/
    └── docs/
        └── ask_me_database.md         # Complete documentation
```

## Creating a Key File

Key files are YAML files that contain the values to substitute into templates.

### Example: `my_new_question.yaml`

```yaml
type: analysis_doc_create
output_document: analysis/analysis_new_feature_osprh_16421.org
context_description: |
  We are working on adding chevrons to the Images table.
  Review: https://review.opendev.org/c/openstack/horizon/+/970000
  This is similar to what we did for Key Pairs in Review 966349.
specific_questions: |
  How can we implement expandable rows for the Images table?
  
  Should we follow the same pattern as Key Pairs?
  What are the key differences to consider?
```

### Key File Format

```yaml
type: <template-type>
<placeholder_name>: <value>
<placeholder_name>: |
  multiline
  value
  preserved
```

**Important**: 
- Use lowercase with underscores for placeholder names in YAML
- The script automatically converts them to UPPERCASE for template substitution
- Example: `output_document` in YAML → `{OUTPUT_DOCUMENT}` in template

## Common Placeholders

### Document & Path
- `output_document` - Where to create the analysis document
- `workspace_path` - Path to working directory
- `workspace_name` - Name of workspace directory

### Review & Git
- `review_url` - Gerrit review URL
- `review_comment_url` - Specific comment URL
- `patchset_number` - Patchset identifier
- `git_setup_commands` - Git commands executed

### Content
- `context_description` - Background information
- `specific_questions` - The actual questions
- `reviewer_name` - Name of reviewer
- `reviewer_comment` - Comment text
- `code_diff` - Code changes to discuss

See `analysis/docs/ask_me_database.md` for complete list.

## Usage Examples

### Example 1: Create Analysis for New Problem

```bash
# Create a key file
cat > askme/keys/my_images_chevrons.yaml <<EOF
type: analysis_doc_create
output_document: analysis/analysis_osprh_16421_images_chevrons.org
context_description: |
  Working on OSPRH-16421: Add chevrons to Images table
  Reference: Review 966349 (Key Pairs) as pattern
specific_questions: |
  How should we implement expandable rows for Images?
  What are the key differences from Key Pairs implementation?
EOF

# Generate the ask
./ask_me.sh analysis_doc_create askme/keys/my_images_chevrons.yaml

# Copy output and paste to AI assistant
```

### Example 2: Respond to Code Review Comment

```bash
# Use example template
./ask_me.sh code_review_response askme/keys/example_review_comment_css_gap.yaml

# Or create your own key file for a new comment
cat > askme/keys/my_review_comment.yaml <<EOF
type: code_review_response
output_document: analysis/analysis_review_comment_response.org
review_comment_url: https://review.opendev.org/c/openstack/horizon/+/970000/5
reviewer_name: John Doe
patchset_number: Patchset 5
specific_investigation: |
  Please explain the suggested approach and its benefits
reviewer_comment: |
  Consider using a helper function here instead of duplicating logic
file_path: openstack_dashboard/dashboards/project/images/tables.py
code_context: |
  def get_image_id(self, datum):
      return datum.id
EOF

./ask_me.sh code_review_response askme/keys/my_review_comment.yaml
```

### Example 3: Ready to Implement Changes

```bash
./ask_me.sh code_implement_workspace askme/keys/example_implement_chevron_fix.yaml
```

### Example 4: Phase Wrap-up

```bash
./ask_me.sh phase_done askme/keys/example_phase_done_gerrit_topic.yaml
```

## Requirements

The script requires one of the following:

### Option 1: yq (Recommended)
```bash
# Install yq (YAML processor)
# On macOS:
brew install yq

# On Linux:
wget https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64 -O /usr/local/bin/yq
chmod +x /usr/local/bin/yq

# On Fedora/RHEL:
sudo dnf install yq
```

### Option 2: Python with PyYAML (Fallback)
```bash
pip install pyyaml
```

The script automatically detects which one is available and uses it.

## Tips & Best Practices

### 1. **Use Descriptive Key File Names**
```bash
# Good
askme/keys/images_chevron_initial_investigation.yaml
askme/keys/review_966349_comment_css_padding.yaml

# Less good
askme/keys/thing1.yaml
askme/keys/ask.yaml
```

### 2. **Keep Example Files**
The `example_*.yaml` files show the format and common patterns. Don't delete them!

### 3. **Version Control Your Key Files**
Key files document your development process. Commit them:
```bash
git add askme/keys/my_feature_*.yaml
git commit -m "Add ask automation keys for feature X"
```

### 4. **Reuse Patterns**
Copy an example file as starting point:
```bash
cp askme/keys/example_fix_chevron_id.yaml askme/keys/my_new_issue.yaml
# Edit my_new_issue.yaml
```

### 5. **Test Your Key File**
Generate the ask before sending to AI to ensure proper formatting:
```bash
./ask_me.sh analysis_doc_create askme/keys/my_new_issue.yaml | less
```

## Troubleshooting

### Error: "Template 'xyz' not found"
Check that the template type matches one of the available templates:
```bash
ls -1 askme/templates/
```

### Error: "Key file not found"
Ensure the path is correct. You can use relative or absolute paths:
```bash
# Relative from repo root
./ask_me.sh analysis_doc_create askme/keys/myfile.yaml

# Absolute path
./ask_me.sh analysis_doc_create /home/user/Work/mymcp/askme/keys/myfile.yaml
```

### Multiline Values Not Working
Make sure to use the `|` pipe character for multiline values in YAML:
```yaml
# Correct
specific_questions: |
  Line 1
  Line 2
  Line 3

# Wrong
specific_questions: "Line 1\nLine 2\nLine 3"
```

### Placeholder Not Substituted
- Check that your YAML key uses lowercase with underscores
- The template uses UPPERCASE: `{OUTPUT_DOCUMENT}`
- The YAML key should be: `output_document`

## Advanced Usage

### Custom Templates

You can create your own templates:

1. Create a new template file in `askme/templates/`:
```bash
cat > askme/templates/my_custom.template <<'EOF'
ask:

Custom template for {SPECIFIC_USE_CASE}

Context: {CONTEXT}

Question: {QUESTION}
EOF
```

2. Create a matching key file:
```bash
cat > askme/keys/my_custom_use.yaml <<EOF
type: my_custom
specific_use_case: debugging production issue
context: Server logs show 500 errors
question: How to trace the root cause?
EOF
```

3. Use it:
```bash
./ask_me.sh my_custom askme/keys/my_custom_use.yaml
```

### Integration with Cursor/IDE

You can pipe the output directly to your clipboard:

**macOS:**
```bash
./ask_me.sh analysis_doc_create askme/keys/myfile.yaml | pbcopy
```

**Linux (with xclip):**
```bash
./ask_me.sh analysis_doc_create askme/keys/myfile.yaml | xclip -selection clipboard
```

**Linux (with xsel):**
```bash
./ask_me.sh analysis_doc_create askme/keys/myfile.yaml | xsel --clipboard
```

Then just paste (Ctrl+V / Cmd+V) into your AI assistant!

## Complete Documentation

For complete documentation including:
- All identified patterns from Review 966349
- Detailed placeholder descriptions
- Statistics and analysis
- Future enhancements

See: `analysis/docs/ask_me_database.md`

## Contributing

When you discover new useful ask patterns:

1. Document the pattern in `analysis/docs/ask_me_database.md`
2. Create a new template in `askme/templates/`
3. Add an example key file in `askme/keys/`
4. Update this README with usage examples

## License

This automation system is part of the mymcp repository and follows the same license.

---

**Version**: 1.0  
**Created**: November 15, 2025  
**Based on**: Review 966349 analysis (19 ask documents)  
**Last Updated**: November 15, 2025

