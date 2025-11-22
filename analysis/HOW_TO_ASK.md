# How to Ask: Getting the Most from Cursor AI

This guide explains how to phrase your questions to get the best results from Cursor AI for code reviews, feature development, and analysis.

---

## Table of Contents

- [Review Analysis](#review-analysis)
- [Feature Development](#feature-development)
- [Code Investigation](#code-investigation)
- [Quick Reference](#quick-reference)
- [Advanced Patterns](#advanced-patterns)

---

## Review Analysis

### Just Want an Assessment?

**Simple approach (recommended):**
```
Analyze review 967773
```

```
Analyze PR 5192
```

```
Check review 966349 for updates
```

**What I'll do:**
1. Run `fetch-review.sh --with-assessment` to get the code
2. Read the changes with `git show HEAD`
3. Complete the full assessment in `results/review_XXXXX.md`
4. Give you my recommendation (+2/+1/0/-1)

**No need to run the script yourself!** Just tell me the review number or paste the URL.

### Want Specific Options?

**If you need master branch comparison:**
```
Analyze review 967773, compare with master
```

### Running the Script Yourself?

**If you prefer to control fetch parameters:**
```bash
# You run:
./scripts/fetch-review.sh --with-assessment opendev <url>

# Then tell me:
Please analyze review 967773
```

**I'll automatically:**
- Find the assessment file in results/
- Read the code from workspace/
- Complete all sections
- Save back to results/

---

## Feature Development

### Starting a New Feature

**Option 1: Full automatic (spike + patchsets):**
```
Full spike for OSPRH-12802
```

```
Create full feature plan for OSPRH-12802: spike and patchsets
```

**What I'll create:**
- `analysis/analysis_new_feature_osprh_12802/spike.md`
- `analysis/analysis_new_feature_osprh_12802/patchset_1_<name>.md`
- `analysis/analysis_new_feature_osprh_12802/patchset_2_<name>.md`
- `analysis/analysis_new_feature_osprh_12802/README.md`

**Option 2: Step by step (more control):**
```
Create spike for OSPRH-12802
[review spike]
Now create patchset documents
```

**Option 3: Just planning help (no files yet):**
```
Help me plan OSPRH-12802 - converting Key Pair create form from AngularJS to Python
```

**I'll respond with:**
- Suggested approach
- Complexity estimate
- Patchset breakdown
- Ask if you want me to create the documents

### Implementing a Patchset

**After spike/patchset documents exist:**
```
Implement patchset 1 for OSPRH-12802
```

```
Please make the code changes from patchset_1_generate_key_pair_form.md
```

**What I'll do:**
1. Read the patchset document
2. Create/modify the files
3. Track progress in WIP document
4. Update design document with decisions

### Asking for Design Documentation

**After implementation:**
```
Create design document for patchset 1
```

```
Document the thought process for patchset_1_generate_key_pair_form.md
```

**What I'll create:**
- `analysis/analysis_new_feature_<issue>/patchset_1_<name>_design.md`
- Code references with GitHub links
- Flow diagrams
- Detailed rationale for each change

---

## Code Investigation

### Finding Code Patterns

**When you need examples:**
```
Find me examples of SelfHandlingForm in Horizon
```

```
Where are modal forms implemented in Horizon?
```

```
How does Horizon handle key pair creation currently?
```

**I'll use:**
- `codebase_search` for semantic understanding
- `grep` for exact matches
- Provide code references with links

### Understanding Existing Code

**For analysis:**
```
Explain how the volumes panel handles create forms
```

```
What's the pattern for Django modal views in Horizon?
```

```
Analyze how Review 966349 implemented expandable rows
```

**I'll provide:**
- Code references
- Explanation of patterns
- Links to relevant files
- How to adapt for your use case

---

## Quick Reference

### Review Workflows

| You Say | I Do |
|---------|------|
| "Analyze review 967773" | Fetch, read, assess, recommend |
| "Check 967773" | Check for updates, summarize changes |
| "Analyze PR 5192" | Fetch GitHub PR, complete assessment |

### Feature Development

| You Say | I Do |
|---------|------|
| "Full spike for OSPRH-12802" | Create spike + all patchsets |
| "Create spike for OSPRH-12802" | Create spike, suggest patchsets |
| "Help me plan OSPRH-12802" | Analyze and propose approach |
| "Implement patchset 1" | Execute the patchset plan |

### Code Investigation

| You Say | I Do |
|---------|------|
| "Find examples of X in Horizon" | Search and provide references |
| "How does X work?" | Explain with code examples |
| "What pattern should I use for Y?" | Recommend with examples |

---

## Advanced Patterns

### Chaining Requests

**You can combine actions:**
```
Analyze review 967773, then create a summary for the team
```

```
Find how volumes handles modals, then apply that pattern to patchset 1
```

```
Check review 966349 status, if merged, rebase my patchset on main
```


### Complexity Adjustments

**If you want detailed analysis:**
```
Deep dive on review 967773
```

```
Comprehensive assessment of PR 5192
```

**If you want quick summary:**
```
Quick look at review 967773
```

```
TL;DR for PR 5192
```

---

## What NOT to Do

### ❌ Don't Over-Specify Technical Details

**Instead of:**
```bash
cd /home/omcgonag/Work/mymcp/workspace && \
  ./scripts/fetch-review.sh --with-assessment opendev \
  https://review.opendev.org/c/openstack/horizon/+/967773 && \
  cd horizon-967773 && git show HEAD && cd .. && \
  [tell me to analyze it]
```

**Just say:**
```
Analyze review 967773
```

I'll handle all the technical steps!

### ❌ Don't Ask for Confirmation Unless Needed

**Instead of:**
```
Can you analyze review 967773?
Should I run the script first?
Do you need me to fetch the code?
```

**Just say:**
```
Analyze review 967773
```

I'll do what's needed and tell you if I need help.

### ❌ Don't Repeat Context

**Instead of:**
```
Analyze review 967773 for OpenStack Horizon project on OpenDev Gerrit
[wait for response]
The review is at https://review.opendev.org/c/openstack/horizon/+/967773
[wait for response]
It's about fixing borders
```

**Just say:**
```
Analyze review 967773
```

I'll fetch all the metadata automatically.

---

## Pro Tips

### 1. Use Natural Language

I understand context better than commands:
- ✅ "What changed in the latest patchset?"
- ✅ "Has anyone commented on my review?"
- ❌ "git diff patchset1 patchset2"

### 2. Reference Previous Work

I remember our conversation:
- ✅ "Like we did for 966349, create patchsets for this"
- ✅ "Use the same pattern as last time"
- ✅ "Similar to the spike we just created"

### 3. State Your Goal

Tell me what you're trying to achieve:
- ✅ "I need to respond to review comments on 967773"
- ✅ "I want to understand the de-angularization pattern"
- ✅ "I need to estimate complexity for sprint planning"

### 4. One Question at a Time (Usually)

**Good:**
```
Analyze review 967773
[wait for assessment]
Now check if 966349 merged
[wait for status]
Rebase my work on main
```

**Also good (if related):**
```
Check if review 966349 merged, and if so, help me rebase my patchset on main
```

**Confusing:**
```
Analyze 967773 and also help me plan OSPRH-12802 and check if 966349 merged 
and explain how modals work and create a spike
```

### 5. Trust the Automation

I'm designed to handle the full workflow:
- ✅ "Analyze review 967773" → I fetch, read, assess, save
- ✅ "Implement patchset 1" → I code, test, document
- ✅ "Check 966349" → I fetch status, detect changes, update

You don't need to micromanage the steps!

---

## Examples from Real Work

### Review 966349 (Key Pairs Expandable Rows)

**What was asked:**
```
I need to implement expandable rows for the Key Pairs table
```

**What I created:**
- Spike analysis
- 20+ patchset documents
- WIP tracking for each session
- Design documents with flow diagrams
- Final review submission

**Result:** ✅ Merged with +2 approval

### Review 967269 (Create Key Pair Form)

**What was asked:**
```
Full spike for OSPRH-12802
```

**What I created:**
- Complete spike analysis
- Patchset breakdown
- Implementation code
- Design documentation

**Result:** ✅ 1-day implementation (50% faster than estimated)

### Review 967773 (Fix Borders)

**What was asked:**
```
Analyze review 967773
```

**What I did:**
- Fetched the review
- Analyzed the CSS changes
- Identified invalid syntax
- Provided corrected code
- Recommended -1 with fix

**Result:** ✅ Complete assessment with actionable feedback

---

## Customization

### Add to Your Cursor Rules

If you want me to always auto-create patchsets after a spike:

```markdown
## Feature Development Automation

When user asks to "create spike for <issue>":
1. Create spike.md in analysis/analysis_new_feature_<issue>/
2. Analyze complexity
3. Automatically create all patchset documents
4. Create README.md with overview

Do not ask for confirmation - create all files immediately.
```

### Create Your Own Shortcuts

You can establish patterns:
- "Full spike" = spike + patchsets + README
- "Quick spike" = just spike.md
- "Deep review" = full assessment + testing recommendations
- "Quick check" = just status update

Tell me your preference once, and I'll remember for the session.

---

## Summary

**The Golden Rule:**

> **Tell me WHAT you want, not HOW to do it.**

**Examples:**
- ✅ "Analyze review 967773" (what)
- ❌ "Run fetch-review.sh then git show then fill in the template" (how)

**Trust the automation:**
- I know the workflows
- I know the tools
- I know your patterns
- I'll ask if I need clarification

**Be specific when it matters:**
- Depth (quick vs deep)
- Output (summary vs full doc)
- Options (compare with master, create experiment)

**Everything else:**
- Just ask naturally
- I'll figure out the details

---

**Last Updated:** 2025-11-21  
**See Also:**
- [Feature Development Guide](../usecases/analysis_new_feature/README.md)
- [Review Automation Guide](../usecases/review_automation/README.md)
- [Results Directory Guide](../results/README.md)

