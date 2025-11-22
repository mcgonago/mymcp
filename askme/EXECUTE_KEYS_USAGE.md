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

### `review-check` - Check Review for Updates (Basic)

**Usage:**
```
check review 967773
execute key review-check for 967773
```

**What it does:**
1. If no assessment exists → Creates initial assessment
2. If assessment exists → Checks for changes:
   - New patchsets
   - New comments
   - Status changes (merged, abandoned)
3. If NO changes → Shows nice visual "no changes" box
4. If changes detected → Shows summary and suggests next steps
5. Updates assessment with check history entry

**Use when:**
- Morning check-in on reviews you're tracking
- Want to know IF something changed (but not analyze it yet)
- Quick status check

**Output when no changes:**
```
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║   ✓ CHECKED review 967773 - No changes since last check       ║
║                                                                ║
║   • Patchset: 1                                               ║
║   • Status: NEW                                               ║
║   • Last checked: 2025-11-22 10:30 AM                         ║
║   • No new patchsets, comments, or status changes             ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
```

---

### `review-check-latest` - Check and Analyze Latest Patchset Only

**Usage:**
```
check review 967773 latest only
check review 967773 latest
execute key review-check-latest for 967773
```

**What it does:**
1. Checks for new patchsets
2. If new patchsets exist:
   - Skips intermediate patchsets
   - Fetches ONLY the latest patchset code
   - Creates assessment for latest patchset only
3. If no changes → Shows "no changes" box
4. Updates dashboard with link to latest patchset assessment

**Use when:**
- Only care about the CURRENT state of the review
- Author uploaded multiple patchsets quickly
- Don't need to track the evolution of changes

**Example:**
```
Review 967773 had PS1, PS2, PS3, PS4, PS5

"check review 967773 latest only"
→ Skips PS2, PS3, PS4
→ Creates review_967773_patchset_5.md only
→ Shows what changed from PS1 to PS5 (summary)
```

---

### `review-check-patchsets` - Create Individual Patchset Assessments

**Usage:**
```
check review 967773 create patchsets
check review 967773 all patchsets
execute key review-check-patchsets for 967773
```

**What it does:**
1. Detects ALL patchsets (current and historical)
2. Creates individual assessment for EACH patchset:
   - `review_967773_patchset_1.md`
   - `review_967773_patchset_2.md`
   - `review_967773_patchset_3.md`
   - etc.
3. Includes review comments in each patchset file (aligned by timestamp)
4. Creates dashboard (`review_967773.md`) with:
   - Links to all patchset assessments
   - Check history
   - Evolution summary

**Use when:**
- Want to understand the SEQUENCE of changes
- Multiple patchsets exist and you want to track evolution
- Need to see how author responded to feedback
- Want complete historical record

**Example:**
```
Review 967773 has 3 patchsets

"check review 967773 create patchsets"
→ Creates review_967773_patchset_1.md (initial CSS bug)
→ Creates review_967773_patchset_2.md (fixed CSS syntax)
→ Creates review_967773_patchset_3.md (rebased on master)
→ Creates review_967773.md (dashboard with links to all 3)
→ Includes comments in each patchset file based on when submitted

Result: You can read the patchsets in order to understand the full story
```

**Incremental behavior:**
If you already ran this once and new patchsets appear:
```
Already have: review_967773_patchset_1.md, review_967773_patchset_2.md
New PS3 uploaded

"check review 967773 create patchsets"
→ Skips PS1 and PS2 (already assessed)
→ Creates review_967773_patchset_3.md only
→ Updates dashboard with PS3 link
```

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

### Example 3: Basic Check (No Changes)

```
You: check review 967773

AI: [Reads existing assessment, queries latest state]

╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║   ✓ CHECKED review 967773 - No changes since last check       ║
║                                                                ║
║   • Patchset: 1                                               ║
║   • Status: NEW                                               ║
║   • Last checked: 2025-11-22 10:30 AM                         ║
║   • No new patchsets, comments, or status changes             ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
```

### Example 3a: Basic Check (Changes Detected)

```
You: check review 967773

AI: [Reads existing assessment, queries latest state]

📋 Check #3 - 2025-11-22 10:45 AM

🔔 Changes detected:
  • New patchset: Patchset 2 uploaded
  • 1 new comment from reviewer
  • Status: Still NEW

📊 Summary:
  • Previous: Patchset 1 (invalid CSS syntax)
  • Current: Patchset 2 (fixed CSS syntax)
  • Comment: "Looks good now, but please rebase on master"

💡 Next steps:
  1. Run "check review 967773 latest only" to analyze PS2
  2. Or run "check review 967773 create patchsets" for full history
```

### Example 3b: Check Latest Patchset Only

```
You: check review 967773 latest only

AI: [Detects PS1, PS2, PS3 exist, analyzes only PS3]

✅ Analyzed latest patchset for review 967773

📁 File created:
   • workspace/iproject/results/review_967773_patchset_3.md

🔄 Latest patchset (PS3):
   • Rebased on master (no functional changes)
   • Resolved merge conflict in tables.py
   • Status: Ready for review

📖 Assessment: workspace/iproject/results/review_967773_patchset_3.md
```

### Example 3c: Create All Patchset Assessments

```
You: check review 967773 create patchsets

AI: [Creates individual files for each patchset]

✅ Created patchset-based assessment for review 967773

📁 Files created:
   • workspace/iproject/results/review_967773.md (dashboard)
   • workspace/iproject/results/review_967773_patchset_1.md
   • workspace/iproject/results/review_967773_patchset_2.md
   • workspace/iproject/results/review_967773_patchset_3.md

📊 Patchset Evolution:
   PS1 (2025-11-19): Initial submission - Invalid CSS syntax
   ├─ Comment (Owen): Suggested adding 'solid #ddd'
   PS2 (2025-11-20): Fixed CSS, added color
   ├─ Comment (Ivan): LGTM, trivial
   PS3 (2025-11-21): Rebased on master, no functional changes

📖 Recommended reading order:
   1. review_967773_patchset_1.md (understand initial approach)
   2. review_967773_patchset_2.md (see what was fixed)
   3. review_967773_patchset_3.md (verify final state)

📋 Dashboard: workspace/iproject/results/review_967773.md
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
# Assessment (full analysis)
execute key review-assess for review https://review.opendev.org/c/openstack/horizon/+/967773
assess review 967773
analyze review https://...
assess review 967773 with master  # Include master comparison

# Checking (status and updates)
check review 967773                    # Basic check (shows if anything changed)
check review 967773 latest only        # Analyze only the latest patchset
check review 967773 create patchsets   # Create assessment for each patchset
execute key review-check for 967773    # Equivalent to basic check
execute key review-check-latest for 967773
execute key review-check-patchsets for 967773

# Short forms
assess 967773
check 967773
analyze review https://...
assess https://review.opendev.org/c/openstack/horizon/+/967773
```

---

## Key Files Location

```
mymcp/askme/keys/
├── review_assess.yaml              # Main assessment key
├── review_assess_with_master.yaml  # With master comparison
├── review_check.yaml               # Basic check (status only)
├── review_check_latest.yaml        # Check and analyze latest patchset
└── review_check_patchsets.yaml     # Create individual patchset assessments
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

### 2. **Choose the Right Check Command**

Match the check command to your needs:

```
# Quick status check (did anything change?)
check review 967773
→ Shows visual box if no changes, summary if changes detected

# Analyze only the latest patchset (ignore intermediate ones)
check review 967773 latest only
→ Creates assessment for current patchset only

# Full historical analysis (understand the evolution)
check review 967773 create patchsets
→ Creates individual assessment for each patchset
→ Best for understanding how review evolved based on feedback
```

**Decision tree:**
- **No existing assessment?** → Use `assess review 967773` (creates initial)
- **Want quick status?** → Use `check review 967773` (just tells you what changed)
- **New patchset, only care about current state?** → Use `check review 967773 latest only`
- **Multiple patchsets, want to understand evolution?** → Use `check review 967773 create patchsets`

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

