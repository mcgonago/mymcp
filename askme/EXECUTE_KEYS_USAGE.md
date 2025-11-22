# Execute Keys - Quick Reference

These keys allow you to execute common workflows with simple commands in Cursor chat.

---

## Review Assessment Keys

### `review-assess` - Full Review Assessment

**Usage:**
```
execute key review-assess for review https://review.opendev.org/c/openstack/horizon/+/967773
```

**Short forms:**
```
assess review https://review.opendev.org/c/openstack/horizon/+/967773
analyze review 967773
review-assess https://github.com/org/repo/pull/5192
```

**What it does:**
1. Runs: `./scripts/fetch-review.sh --with-assessment <type> <url>`
2. Automatically completes full assessment
3. Saves to: `workspace/iproject/results/review_<number>.md`

**Supports:**
- OpenDev Gerrit: `review.opendev.org`
- GitHub PRs: `github.com`
- GitLab MRs: `gitlab.cee.redhat.com`

---

### `review-assess-master` - Assessment with Master Comparison

**Usage:**
```
execute key review-assess-master for review https://review.opendev.org/c/openstack/horizon/+/967773
```

**What it does:**
Same as `review-assess` but includes:
- `--with-master` flag (clones master branch for comparison)
- Diff comparison in analysis
- Side-by-side code comparison

**Use when:**
- You want to see exact differences from master
- Review is complex and needs context
- You're doing deep technical analysis

---

### `review-check` - Check Review for Updates

**Usage:**
```
check review 967773
execute key review-check for 967773
```

**What it does:**
1. Reads existing `workspace/iproject/results/review_<number>.md`
2. Queries MCP agent for latest state
3. Detects changes:
   - New patchsets
   - New comments
   - Status changes (merged, abandoned)
4. Updates assessment with check history
5. Creates new patchset assessment if needed

**Use when:**
- Morning check-in on reviews you're tracking
- Want to see if there are updates
- Don't need to re-fetch code

---

## How It Works

### URL Detection

The AI automatically detects review type from URL:

| URL Pattern | Type | MCP Agent |
|-------------|------|-----------|
| `review.opendev.org` | opendev | @opendev-reviewer-agent |
| `github.com` | github | @github-reviewer-agent |
| `gitlab.cee.redhat.com` | gitlab | @gitlab-cee-agent |

### Execution Flow

```
You say: "assess review https://review.opendev.org/c/openstack/horizon/+/967773"
         ↓
AI detects: OpenDev review, review number 967773
         ↓
AI runs: ./scripts/fetch-review.sh --with-assessment opendev <url>
         ↓
Script: Creates workspace/iproject/results/review_967773.md (template)
         ↓
AI reads: Code changes from workspace/horizon-967773/
         ↓
AI queries: @opendev-reviewer-agent for metadata
         ↓
AI completes: Full assessment document (all sections)
         ↓
AI reports: Summary, key findings, recommendation
```

---

## Examples

### Example 1: Quick Assessment

```
You: assess review 967773

AI: [Runs fetch-review.sh, completes assessment]

📋 Assessment Summary
Review: 967773 - Fix inconsistent borders
Recommendation: -1 (Needs Work)
Issue: Invalid CSS syntax
Location: workspace/iproject/results/review_967773.md
```

### Example 2: Full URL with Master

```
You: execute key review-assess-master for review https://review.opendev.org/c/openstack/horizon/+/967773

AI: [Fetches review + master, completes assessment with comparison]

📋 Assessment Summary
Review: 967773 - Fix inconsistent borders
Files: 1 changed (+2/-0)
Comparison: vs master branch
Recommendation: -1 (Invalid CSS)
Location: workspace/iproject/results/review_967773.md
```

### Example 3: Check for Updates

```
You: check review 967773

AI: [Reads existing assessment, queries latest state]

Check #3 - 2025-11-22

Status: New Patchset 2 detected
Changes:
  - Author uploaded Patchset 2
  - Fixed CSS syntax (added 'solid #ddd')
  - 1 new comment from reviewer

Action: Created workspace/iproject/results/review_967773_patchset_2.md

Next steps:
  - Review new patchset assessment
  - Compare with patchset 1
  - Update your vote if fix is correct
```

### Example 4: GitHub PR

```
You: assess review https://github.com/RedHatInsights/rhsm-subscriptions/pull/5232

AI: [Detects GitHub, fetches PR, completes assessment]

📋 Assessment Summary
Review: PR 5232 - Add database cleanup job
Recommendation: +1 (Approve with minor suggestions)
Location: workspace/iproject/results/review_pr_5232.md
```

---

## Command Variations

All of these work:

```
# Full form
execute key review-assess for review https://review.opendev.org/c/openstack/horizon/+/967773

# Short forms
assess review 967773
analyze review https://...
review-assess 967773
check review 967773

# With master
assess review 967773 with master
execute key review-assess-master for 967773

# Just the URL (if review type is clear)
assess https://review.opendev.org/c/openstack/horizon/+/967773
```

---

## Key Files Location

```
mymcp/askme/keys/
├── review_assess.yaml              # Main assessment key
├── review_assess_with_master.yaml  # With master comparison
└── review_check.yaml               # Check for updates
```

---

## Tips

### 1. **Use Short Forms in Chat**

Instead of typing the full command, use natural language:

```
✅ "assess review 967773"
✅ "check 967773"
✅ "analyze this review: <url>"

❌ "execute key review-assess for review https://..." (too long!)
```

### 2. **Check Before Assessing**

If you've already assessed a review, use `check` instead of `assess`:

```
# First time
assess review 967773  → Creates full assessment

# Later
check review 967773   → Checks for updates, adds to history
```

### 3. **Use Master for Complex Reviews**

For substantial changes, include master comparison:

```
assess review 967773 with master
```

### 4. **Morning Workflow**

Check all your tracked reviews:

```
check review 967773
check review 965215
check review 966349
```

---

## Configuration

### Workspace Project

Assessments are saved to your configured workspace project:

```bash
# Check current config
cat workspace/.workspace-config

# Example output:
WORKSPACE_PROJECT_DIR=iproject
```

Assessments go to: `workspace/iproject/results/review_<number>.md`

### Default Options

Edit `askme/keys/review_assess.yaml` to change defaults:

```yaml
default_options:
  - --with-assessment  # Always included
  - --with-master      # Add this to always include master
```

---

## Troubleshooting

### "Review not found"

Make sure the URL is correct and accessible:

```
❌ https://review.opendev.org/967773  (missing full path)
✅ https://review.opendev.org/c/openstack/horizon/+/967773
```

### "Assessment already exists"

The script reuses existing code directories. To force re-fetch:

```bash
# Delete the directory
rm -rf workspace/horizon-967773

# Then re-run
assess review 967773
```

### "Can't detect review type"

Make sure the URL matches a known pattern:
- OpenDev: `review.opendev.org`
- GitHub: `github.com`
- GitLab: `gitlab.cee.redhat.com`

---

## See Also

- [askme/README.md](README.md) - Main askme framework documentation
- [analysis/HOW_TO_ASK.md](../analysis/HOW_TO_ASK.md) - How to ask for analysis
- [WORKSPACE_PROJECT.md](../WORKSPACE_PROJECT.md) - Workspace project setup
- [results/README.md](../results/README.md) - Assessment documentation

---

**Last Updated:** 2025-11-22  
**Version:** 1.0

