# Quick Start: Using Ask Automation for Your Next Feature

This guide shows you how to use the ask automation system for your next feature development.

## Scenario: Starting OSPRH-16421 (Images Table Chevrons)

You're about to start working on OSPRH-16421 which adds chevrons to the Images table, similar to what was done for Key Pairs in Review 966349.

### Step 1: Create Your First Ask Key File

```bash
cd <mymcp-repo-path>

cat > askme/keys/osprh_16421_initial_investigation.yaml <<'EOF'
type: analysis_doc_create
output_document: analysis/analysis_new_feature_osprh_16421/spike.md
context_description: |
  Starting work on OSPRH-16421: Add chevrons to the Images table
  
  Reference implementation: Review 966349 (Key Pairs expandable rows)
  Current task: Initial investigation and spike document
  
  Key questions to answer:
  - How similar is Images table structure to Key Pairs?
  - What are the key differences to consider?
  - Can we reuse the same pattern?
specific_questions: |
  Please analyze the Images table implementation and compare it to the Key Pairs approach.
  
  1. What is the current structure of the Images table?
  2. Where is it defined (file paths)?
  3. What data fields would we display in the expanded row?
  4. Are there any Images-specific considerations (e.g., image status, visibility)?
  5. Can we follow the same 4-phase approach from Review 966349?
  
  Please create a spike document outlining:
  - Problem definition
  - Proposed solution (referencing Key Pairs pattern)
  - Key technical considerations
  - Incremental work items (patchsets)
  - Estimated complexity and timeline
EOF
```

### Step 2: Generate the Ask

```bash
./ask_me.sh analysis_doc_create askme/keys/osprh_16421_initial_investigation.yaml
```

**Output** (ready to copy & paste to AI):

```
ask:

For your answers to my inquiry below - please create a new analysis/analysis_new_feature_osprh_16421/spike.md

Starting work on OSPRH-16421: Add chevrons to the Images table

Reference implementation: Review 966349 (Key Pairs expandable rows)
Current task: Initial investigation and spike document

Key questions to answer:
- How similar is Images table structure to Key Pairs?
- What are the key differences to consider?
- Can we reuse the same pattern?

Please analyze the Images table implementation and compare it to the Key Pairs approach.

1. What is the current structure of the Images table?
2. Where is it defined (file paths)?
3. What data fields would we display in the expanded row?
4. Are there any Images-specific considerations (e.g., image status, visibility)?
5. Can we follow the same 4-phase approach from Review 966349?

Please create a spike document outlining:
- Problem definition
- Proposed solution (referencing Key Pairs pattern)
- Key technical considerations
- Incremental work items (patchsets)
- Estimated complexity and timeline

✅ Ask generated successfully!
💡 Copy the output above and paste it to your AI assistant.
```

### Step 3: Copy & Paste to Cursor

1. Select the generated ask text (between the `ask:` line and the success message)
2. Copy it (Ctrl+C / Cmd+C)
3. Open Cursor
4. Paste into the chat (Ctrl+V / Cmd+V)
5. Press Enter

### Step 4: After You Get the Response

The AI will create `analysis/analysis_new_feature_osprh_16421/spike.md` with all the details you need.

### Step 5: Next Ask - Setup Your Workspace

Now you're ready to set up your working directory:

```bash
cat > askme/keys/osprh_16421_setup_workspace.yaml <<'EOF'
type: code_implement_workspace
workspace_path: <mymcp-repo-path>/workspace/horizon-osprh-16421-working
workspace_name: horizon-osprh-16421-working
git_setup_commands: |
  git clone https://review.opendev.org/openstack/horizon horizon-osprh-16421-working
  cd horizon-osprh-16421-working
  git checkout -b osprh-16421-images-chevrons
  git config user.name "Your Name"
  git config user.email "your.email@example.com"
EOF

./ask_me.sh code_implement_workspace askme/keys/osprh_16421_setup_workspace.yaml
```

## Pattern: Your Development Cycle

As you work through the feature, you'll create key files for each phase:

### Investigation Phase
- `osprh_16421_initial_investigation.yaml` (analysis_doc_create)
- `osprh_16421_compare_patterns.yaml` (investigate_patterns)

### Implementation Phase
- `osprh_16421_setup_workspace.yaml` (code_implement_workspace)
- `osprh_16421_implement_phase1.yaml` (code_implement_workspace)
- `osprh_16421_implement_phase2.yaml` (code_implement_workspace)

### Review Response Phase
- `osprh_16421_review_comment_1.yaml` (code_review_response)
- `osprh_16421_review_comment_2.yaml` (code_review_response)

### Completion Phase
- `osprh_16421_phase_done.yaml` (phase_done)

## Tips for Key File Naming

**Good naming pattern**:
```
<ticket>_<phase>_<specific-action>.yaml
```

**Examples**:
- `osprh_16421_spike_initial.yaml`
- `osprh_16421_impl_chevron_column.yaml`
- `osprh_16421_review_css_feedback.yaml`
- `osprh_16421_done_gerrit_topic.yaml`

This naming makes it easy to:
1. Find relevant asks later
2. Understand what each ask was for
3. Track your development progression
4. Reference in commit messages or analysis docs

## Clipboard Integration (Linux)

Save even more time by piping directly to clipboard:

```bash
# Install xclip if not already installed
sudo dnf install xclip

# Generate and copy in one step
./ask_me.sh analysis_doc_create askme/keys/osprh_16421_initial_investigation.yaml | xclip -selection clipboard

# Now just paste (Ctrl+V) into Cursor!
```

**macOS**:
```bash
./ask_me.sh analysis_doc_create askme/keys/osprh_16421_initial_investigation.yaml | pbcopy
```

## Template Reference

Quick reminder of when to use each template:

| Template | Use When | Example |
|----------|----------|---------|
| `analysis_doc_create` | Starting investigation, creating analysis docs | Spike document, problem analysis |
| `code_implement_workspace` | Ready to implement changes | After spike approved, ready to code |
| `code_review_response` | Responding to reviewer comments | Gerrit comment needs addressed |
| `investigate_patterns` | Researching framework patterns | How does Horizon do X? |
| `phase_done` | Wrapping up phase, transition | Ready for +2, setting topic |

## Common Placeholders Quick Reference

| Placeholder | YAML Key | Example Value |
|-------------|----------|---------------|
| `{OUTPUT_DOCUMENT}` | `output_document` | `analysis/analysis_new_feature_osprh_16421/spike.md` |
| `{CONTEXT_DESCRIPTION}` | `context_description` | Background info (multiline) |
| `{SPECIFIC_QUESTIONS}` | `specific_questions` | Your questions (multiline) |
| `{WORKSPACE_PATH}` | `workspace_path` | `<mymcp-repo-path>/workspace/horizon-...` |
| `{REVIEW_URL}` | `review_url` | `https://review.opendev.org/c/openstack/horizon/+/970000` |
| `{REVIEWER_NAME}` | `reviewer_name` | `Radomir Dopieralski` |

## Next Steps

1. **Create your first key file** for OSPRH-16421
2. **Generate the ask** with `./ask_me.sh`
3. **Copy & paste** to Cursor
4. **Track your key files** in git:
   ```bash
   git add askme/keys/osprh_16421_*.yaml
   git commit -m "Add ask automation keys for OSPRH-16421"
   ```

## Getting Help

- **Full guide**: `askme/README.md`
- **Pattern analysis**: `analysis/docs/ask_me_database.md`
- **Implementation summary**: `docs/ASK_AUTOMATION_IMPLEMENTATION_SUMMARY.md`
- **Usage help**: `./ask_me.sh` (no arguments)

## Remember

The system is designed to **save you time** and **improve consistency**. Don't worry about getting it perfect - just:

1. Copy an example key file
2. Modify the values
3. Generate the ask
4. Iterate if needed

**You'll get faster with each use!**

---

Ready to start? Create your first key file and generate your first automated ask! 🚀

