# Review Check Framework - Complete Guide

This document explains the complete framework for checking and assessing reviews at different levels of detail.

---

## Overview

The review check framework supports three levels of analysis:

1. **Basic Check** (`check review 967773`) - Quick status update
2. **Latest Patchset** (`check review 967773 latest only`) - Analyze current state only
3. **Full Patchset History** (`check review 967773 create patchsets`) - Complete evolution tracking

Each serves a different purpose and creates different outputs.

---

## Decision Tree: Which Command to Use?

```
START: You want to check review 967773

┌─────────────────────────────────────────────────┐
│ Do you have an existing assessment?             │
└─────────────┬───────────────────────────────────┘
              │
         NO ──┤
              │         Use: assess review 967773
              │         Creates initial full assessment
              │
         YES ─┤
              │
              ▼
┌─────────────────────────────────────────────────┐
│ Just want to know IF something changed?         │
└─────────────┬───────────────────────────────────┘
              │
         YES ─┤
              │         Use: check review 967773
              │         Shows visual box if no changes
              │         Shows summary if changes detected
              │
         NO ──┤
              │
              ▼
┌─────────────────────────────────────────────────┐
│ Only care about CURRENT state of review?        │
└─────────────┬───────────────────────────────────┘
              │
         YES ─┤
              │         Use: check review 967773 latest only
              │         Analyzes only the latest patchset
              │         Skips intermediate patchsets
              │
         NO ──┤
              │
              ▼
┌─────────────────────────────────────────────────┐
│ Want to understand EVOLUTION across patchsets?  │
└─────────────┬───────────────────────────────────┘
              │
         YES ─┤
              │         Use: check review 967773 create patchsets
              │         Creates individual assessment for each PS
              │         Includes comment timeline
              │         Shows how review evolved
```

---

## Command Reference

### 1. Initial Assessment (First Time)

**Command:**
```
assess review 967773
assess review https://review.opendev.org/c/openstack/horizon/+/967773
```

**When to use:**
- First time analyzing a review
- No existing assessment

**What it creates:**
- `workspace/iproject/results/review_967773.md` - Full assessment

**Output:**
- Complete analysis of current patchset
- Uses `results/review_template.md` as template

---

### 2. Basic Check (Status Update)

**Command:**
```
check review 967773
```

**When to use:**
- Morning check-in
- Want to know IF anything changed
- Don't need full analysis yet

**What it does:**
- Queries latest state
- Compares with last check
- Reports changes

**Output if NO changes:**
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

**Output if changes detected:**
```
📋 Check #3 - 2025-11-22

🔔 Changes detected:
  • New patchset: Patchset 2 uploaded
  • 1 new comment
  • Status: Still NEW

💡 Suggested actions:
  1. Run "check review 967773 latest only" to analyze PS2
  2. Or run "check review 967773 create patchsets" for full history
```

**What it creates/updates:**
- Adds entry to "Check History" in existing assessment
- Updates metadata tracking

---

### 3. Latest Patchset Only

**Command:**
```
check review 967773 latest only
check review 967773 latest
```

**When to use:**
- New patchset detected, only care about current state
- Author uploaded multiple patchsets quickly (don't need to track each)
- Want quick analysis of latest changes

**What it does:**
- Detects all patchsets
- Skips intermediate patchsets
- Analyzes ONLY the latest
- Creates assessment for latest

**Example scenario:**
```
Review has PS1, PS2, PS3, PS4, PS5

You run: check review 967773 latest only

Result:
- Skips PS2, PS3, PS4 (doesn't create assessments)
- Fetches PS5 code
- Creates review_967773_patchset_5.md
- Shows summary of changes from PS1 to PS5
```

**What it creates:**
- `workspace/iproject/results/review_967773_patchset_5.md` (latest only)
- Updates check history

**Does NOT create:**
- Assessments for PS2, PS3, PS4 (intermediate patchsets)

---

### 4. Full Patchset History (Create All Patchsets)

**Command:**
```
check review 967773 create patchsets
check review 967773 all patchsets
```

**When to use:**
- Want to understand EVOLUTION of review
- Multiple patchsets and you want to track changes
- Need to see how author responded to feedback
- Want complete historical record

**What it does:**
- Detects ALL patchsets (1, 2, 3, ...)
- Creates individual assessment for EACH patchset
- Includes comments in each patchset file (aligned by time)
- Creates dashboard linking all patchsets
- Shows patchset evolution timeline

**Example scenario:**
```
Review has PS1, PS2, PS3

You run: check review 967773 create patchsets

Result:
- Creates review_967773_patchset_1.md (initial submission)
- Creates review_967773_patchset_2.md (first revision)
- Creates review_967773_patchset_3.md (current state)
- Creates review_967773.md (dashboard with links to all)
- Includes comments in each file based on when submitted
```

**What it creates:**
- `workspace/iproject/results/review_967773.md` - Dashboard
- `workspace/iproject/results/review_967773_patchset_1.md`
- `workspace/iproject/results/review_967773_patchset_2.md`
- `workspace/iproject/results/review_967773_patchset_3.md`
- (One file per patchset)

**Incremental behavior:**
If you already ran this and new patchsets appear:
```
Already have: review_967773_patchset_1.md, _patchset_2.md

New PS3 uploaded

You run: check review 967773 create patchsets

Result:
- Skips PS1 and PS2 (already assessed)
- Creates review_967773_patchset_3.md only
- Updates dashboard
```

---

## File Structure

### After Initial Assessment

```
workspace/iproject/results/
└── review_967773.md              # Single full assessment
```

### After "latest only" Check (with new PS2)

```
workspace/iproject/results/
├── review_967773.md              # Original assessment (now for PS1)
└── review_967773_patchset_2.md   # Latest patchset assessment
```

### After "create patchsets" (full history)

```
workspace/iproject/results/
├── review_967773.md                   # Dashboard (links to all patchsets)
├── review_967773_patchset_1.md        # Initial submission
├── review_967773_patchset_2.md        # First revision
└── review_967773_patchset_3.md        # Current state
```

**Dashboard** (`review_967773.md`) contains:
- Links to all patchset assessment files
- Check history
- Current status
- Evolution timeline
- Comment thread summary
- Overall recommendation

**Patchset files** (`review_967773_patchset_X.md`) contain:
- Full assessment for that specific patchset
- What changed from previous patchset
- Comments submitted during this patchset's lifetime
- Comparison with previous patchset
- Votes received

---

## Templates

### For Initial Assessment
**Template:** `results/review_template.md`

**Used by:**
- `assess review 967773`

**Creates:**
- `review_967773.md` (single file, full assessment)

### For Dashboard (Multi-Patchset)
**Template:** `results/review_dashboard_template.md`

**Used by:**
- `check review 967773 create patchsets`

**Creates:**
- `review_967773.md` (dashboard with links to patchsets)

### For Individual Patchset
**Template:** `results/review_patchset_template.md`

**Used by:**
- `check review 967773 latest only`
- `check review 967773 create patchsets`

**Creates:**
- `review_967773_patchset_1.md`
- `review_967773_patchset_2.md`
- etc.

---

## Patchset Tracking

### How Patchsets Are Detected

The AI uses the MCP agent to query review metadata:
```python
{
  "current_patchset": 3,
  "patchsets": [
    {"number": 1, "created": "2025-11-19T14:41:23Z"},
    {"number": 2, "created": "2025-11-20T09:15:42Z"},
    {"number": 3, "created": "2025-11-21T16:22:11Z"}
  ]
}
```

### How Comments Are Aligned

Comments are associated with patchsets based on:
1. **Timestamp** - When was the comment submitted?
2. **Patchset reference** - Does comment mention "Patchset 2" explicitly?
3. **File/line context** - Which patchset's code is being referenced?

**Example:**
```
PS1 uploaded: 2025-11-19 14:41
Comment (Owen): 2025-11-19 16:30 - "Add solid #ddd"
  → Goes in review_967773_patchset_1.md

PS2 uploaded: 2025-11-20 09:15
Comment (Ivan): 2025-11-20 10:45 - "LGTM"
  → Goes in review_967773_patchset_2.md

PS3 uploaded: 2025-11-21 16:22
Comment (You): 2025-11-21 18:00 - "Ready to merge"
  → Goes in review_967773_patchset_3.md
```

---

## Metadata Tracking

Each assessment file includes metadata in YAML format for the AI to track state:

### In Dashboard (`review_967773.md`)
```yaml
review_metadata:
  review_number: 967773
  project: openstack/horizon
  current_patchset: 3
  total_patchsets: 3
  status: NEW
  last_check_date: 2025-11-22T10:30:00Z
  last_check_patchset: 3
  patchset_files_created:
    - patchset_1
    - patchset_2
    - patchset_3
  check_count: 5
  assessment_type: "dashboard"
```

### In Patchset File (`review_967773_patchset_2.md`)
```yaml
patchset_metadata:
  review_number: 967773
  patchset_number: 2
  project: openstack/horizon
  uploaded_date: 2025-11-20T09:15:42Z
  assessment_date: 2025-11-20T11:00:00Z
  previous_patchset: 1
  next_patchset: 3
  status: "superseded"
  votes:
    plus_two: 0
    plus_one: 1
    zero: 0
    minus_one: 0
  comments_count: 2
  assessment_type: "patchset"
```

This metadata allows the AI to:
- Detect new patchsets since last check
- Know which patchset files already exist
- Skip already-assessed patchsets
- Update check history accurately

---

## Workflow Examples

### Example 1: Brand New Review

```
Day 1 - Initial Discovery:
You: assess review 967773
AI:  Creates review_967773.md (full assessment of PS1)

Day 2 - Quick Check:
You: check review 967773
AI:  ╔══════════════════════════════════╗
     ║ ✓ No changes since last check   ║
     ╚══════════════════════════════════╝

Day 3 - Author Uploaded PS2:
You: check review 967773
AI:  🔔 New patchset detected (PS2)
     💡 Run "check review 967773 latest only" to analyze

You: check review 967773 latest only
AI:  Creates review_967773_patchset_2.md
     Shows what changed from PS1 to PS2
```

### Example 2: Multi-Patchset Review (Full History)

```
Review already has PS1, PS2, PS3

You: check review 967773 create patchsets
AI:  Creates review_967773.md (dashboard)
     Creates review_967773_patchset_1.md
     Creates review_967773_patchset_2.md
     Creates review_967773_patchset_3.md
     
     Shows evolution timeline:
     PS1 → PS2: Fixed CSS syntax
     PS2 → PS3: Rebased on master

You: [Read patchsets in order to understand evolution]

Day 2 - Author Uploads PS4:
You: check review 967773 create patchsets
AI:  Detects existing PS1, PS2, PS3 assessments
     Skips those (already done)
     Creates review_967773_patchset_4.md only
     Updates dashboard
```

### Example 3: Fast-Moving Review (Latest Only)

```
Review has PS1, then author quickly uploads PS2, PS3, PS4, PS5

You: check review 967773 latest only
AI:  Skips PS2, PS3, PS4 (intermediate)
     Creates review_967773_patchset_5.md only
     Shows summary: PS1 → PS5 changes

Result: Quick assessment of final state without tracking every iteration
```

---

## Best Practices

### 1. **Start with Basic Check**
```
Morning routine:
check review 967773
check review 965215
check review 966349

Result: Quick visual boxes showing what (if anything) changed
```

### 2. **Use "Latest Only" for Fast Iteration**
```
When: Author is actively addressing feedback

You: check review 967773 latest only

Result: You always analyze the current state, skip intermediate attempts
```

### 3. **Use "Create Patchsets" for Complex Reviews**
```
When: Multiple patchsets, lots of feedback, need to understand evolution

You: check review 967773 create patchsets

Result: Complete historical record of how review evolved
```

### 4. **Combine Approaches**
```
Day 1: assess review 967773          # Initial full assessment
Day 2: check review 967773            # Quick status check
Day 3: check review 967773 latest    # New PS2, analyze latest only
Day 4: check review 967773            # No changes, visual box
Day 5: Author uploads PS3, PS4, PS5 rapidly
       check review 967773 latest    # Analyze only PS5
Day 6: Ready to give +2, want full context
       check review 967773 create patchsets  # Create full history
```

---

## Key Files

### Askme Keys (Command Definitions)
```
askme/keys/
├── review_assess.yaml              # Initial assessment
├── review_assess_with_master.yaml  # Assessment with master comparison
├── review_check.yaml               # Basic status check
├── review_check_latest.yaml        # Analyze latest patchset only
└── review_check_patchsets.yaml     # Create all patchset assessments
```

### Templates (Fill-in Patterns)
```
results/
├── review_template.md              # For initial assessment
├── review_dashboard_template.md    # For multi-patchset dashboard
└── review_patchset_template.md     # For individual patchset assessment
```

### Documentation
```
askme/
├── EXECUTE_KEYS_USAGE.md   # How to use execute keys
└── CHECK_FRAMEWORK.md      # This document
```

---

## Troubleshooting

### "No assessment found"

If you run `check review 967773` and no assessment exists:
- AI will automatically create initial assessment
- Equivalent to running `assess review 967773`

### "Already assessed this patchset"

If you run `check review 967773 create patchsets` and some patchsets already have assessments:
- AI skips those patchsets
- Only creates assessments for new patchsets
- Updates dashboard

### "Can't detect which patchset changed"

If metadata is unclear:
- AI will prompt you to clarify
- Or will analyze all patchsets to be safe

---

## Summary: Command Quick Reference

| Command | When to Use | What It Creates |
|---------|-------------|-----------------|
| `assess review 967773` | First time | Single `review_967773.md` |
| `check review 967773` | Quick status check | Updates existing, no new files |
| `check review 967773 latest` | New PS, only care about current | `review_967773_patchset_X.md` (latest) |
| `check review 967773 create patchsets` | Track evolution | Dashboard + all patchset files |

---

**Last Updated:** 2025-11-22  
**Version:** 1.0  
**Author:** AI Code Review Assistant

