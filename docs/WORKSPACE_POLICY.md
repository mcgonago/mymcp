# Workspace Policy: Where New Work Goes

**Created**: 2025-11-22  
**Purpose**: Define clear rules for where AI creates new analysis and review documents

---

## 🎯 Core Policy

### For ALL New Work

**Rule**: ALL new reviews and analysis go to `workspace/iproject/` (or user's configured workspace project)

**Never**: Create new work in `mymcp/results/` or `mymcp/analysis/`

---

## 📁 Directory Purposes

### `mymcp/results/` - Examples ONLY

**Purpose**: Provide example review assessments for mymcp users

**Content**:
- ✅ `review_template.md` - Template for all reviews
- ✅ `review_965215.md` - Example: complete assessment (referenced in docs)
- ✅ Other templates (dashboard, patchset)

**DO NOT ADD**:
- ❌ New review assessments (yours or anyone's actual work)
- ❌ Work-in-progress reviews

### `mymcp/analysis/` - Examples ONLY

**Purpose**: Provide example feature analyses for mymcp users

**Content**:
- ✅ `analysis_new_feature_966349/` - Example: complete, merged feature (Key Pairs)
- ✅ `analysis_new_feature_osprh_12802/` - Example: in-progress feature
- ✅ Templates (`spike_template.md`, `patchset_template.md`, `design_template.md`)
- ✅ Documentation (`HOW_TO_ASK.md`, `README.md`, `TEMPLATES_README.md`)

**DO NOT ADD**:
- ❌ New feature analysis (yours or anyone's actual work)
- ❌ Work-in-progress analysis
- ❌ Planning documents for features not yet started

### `workspace/iproject/results/` - YOUR Actual Work

**Purpose**: Store all YOUR review assessments

**Content**:
- ✅ `review_967773.md` - Your actual review work
- ✅ `review_pr_5232.md` - Your GitHub PR reviews
- ✅ Any other review assessments you create

**When to add**:
- ✅ When you run `assess review XXXXX`
- ✅ When `fetch-review.sh --with-assessment` is executed
- ✅ Any review assessment AI creates for you

### `workspace/iproject/analysis/` - YOUR Actual Work

**Purpose**: Store all YOUR feature planning and analysis

**Content**:
- ✅ `analysis_new_feature_osprh_16421/` - Your actual planning
- ✅ Any spike, patchset, or design documents AI creates for you

**When to add**:
- ✅ When you say "Full spike for OSPRH-XXXXX"
- ✅ When AI creates feature planning documents
- ✅ Work-in-progress analysis

---

## 🤖 AI Behavior Rules

### For Review Assessments

**When user says**: `assess review XXXXX`

**AI creates in**: `workspace/iproject/results/review_XXXXX.md`

**How AI knows location**:
1. Read `workspace/.workspace-config`
2. Get `WORKSPACE_PROJECT_DIR` (usually "iproject")
3. Create in `workspace/$WORKSPACE_PROJECT_DIR/results/`

**Script behavior**: `fetch-review.sh` does this correctly ✅

### For Feature Analysis

**When user says**: `Full spike for OSPRH-XXXXX`

**AI creates in**: `workspace/iproject/analysis/analysis_new_feature_osprh_xxxxx/`

**How AI knows location**:
1. Read `workspace/.workspace-config`
2. Get `WORKSPACE_PROJECT_DIR` (usually "iproject")
3. Create directory `workspace/$WORKSPACE_PROJECT_DIR/analysis/analysis_new_feature_osprh_xxxxx/`
4. Create all documents there (spike, patchsets, design, README)

**Script behavior**: No script for this yet - AI does it directly ✅

---

## 📋 Migration: Moving Old Work

### If Work is in Wrong Location

**Scenario**: AI created analysis in `mymcp/analysis/` instead of `workspace/iproject/analysis/`

**Action**:
1. User deletes files from `mymcp/analysis/analysis_new_feature_XXXXX/`
2. AI recreates in `workspace/iproject/analysis/analysis_new_feature_XXXXX/`
3. Confirm old directory is removed

**Example** (OSPRH-16421):
```bash
# User deleted (seen in deleted_files):
mymcp/analysis/analysis_new_feature_osprh_16421/spike.md
mymcp/analysis/analysis_new_feature_osprh_16421/patchset_*.md
mymcp/analysis/analysis_new_feature_osprh_16421/README.md

# AI recreated in correct location:
workspace/iproject/analysis/analysis_new_feature_osprh_16421/spike.md
workspace/iproject/analysis/analysis_new_feature_osprh_16421/patchset_*.md
workspace/iproject/analysis/analysis_new_feature_osprh_16421/README.md
```

---

## 🔄 Workflow: From Active Work to Example

### When a Feature is Complete and Merged

**Scenario**: You completed OSPRH-16421, it's merged upstream, you want to share as example

**Steps**:
1. **Verify it's merged**: Review is +2 approved and merged
2. **Copy to examples**:
   ```bash
   cp -r workspace/iproject/analysis/analysis_new_feature_osprh_16421/ \
        analysis/
   ```
3. **Update documentation**:
   - Add to `analysis/README.md` (list of examples)
   - Add to `usecases/analysis_new_feature/README.md` (success stories)
4. **Keep original**: Don't delete from `workspace/iproject/` (it's your work history)

### Criteria for Becoming an Example

**Should be**:
- ✅ Complete (all patchsets merged)
- ✅ Successful (+2 approval, merged upstream)
- ✅ Well-documented (spike, patchsets, design docs all present)
- ✅ Good reference for others (follows patterns, shows best practices)

**Don't make examples of**:
- ❌ Abandoned work
- ❌ Failed/rejected reviews
- ❌ Incomplete planning (spike only, no implementation)
- ❌ Work-in-progress

---

## 🔍 How to Check Compliance

### Verify AI is Following Policy

**Check review assessments**:
```bash
# Should be EMPTY (or only templates/examples):
ls -la mymcp/results/*.md

# Should contain YOUR work:
ls -la workspace/iproject/results/*.md
```

**Check feature analysis**:
```bash
# Should be EMPTY (or only examples):
ls -la mymcp/analysis/analysis_new_feature_osprh_*/

# Should contain YOUR work:
ls -la workspace/iproject/analysis/analysis_new_feature_osprh_*/
```

### What to Do if Policy is Violated

**If AI creates in wrong location**:
1. Tell AI: "This should be in workspace/iproject, not mymcp"
2. AI will move files to correct location
3. AI will update its behavior

**If you see old work in wrong location**:
1. Decide if it should be an example or deleted
2. If example: Keep it, document in `analysis/README.md`
3. If not example: Delete it

---

## 📖 Examples of Correct Structure

### Correct Review Structure

```
mymcp/
├── results/
│   ├── review_template.md                    ✅ Template
│   ├── review_dashboard_template.md          ✅ Template
│   ├── review_patchset_template.md           ✅ Template
│   ├── review_965215.md                      ✅ Example (referenced in docs)
│   └── README.md                             ✅ Documentation
└── workspace/
    └── iproject/
        └── results/
            ├── review_967773.md              ✅ Your actual work
            ├── review_pr_5232.md             ✅ Your actual work
            └── ...
```

### Correct Analysis Structure

```
mymcp/
├── analysis/
│   ├── analysis_new_feature_966349/          ✅ Example (complete, merged)
│   ├── analysis_new_feature_osprh_12802/     ✅ Example (in-progress reference)
│   ├── spike_template.md                     ✅ Template
│   ├── patchset_template.md                  ✅ Template
│   ├── design_template.md                    ✅ Template
│   ├── HOW_TO_ASK.md                         ✅ Documentation
│   ├── TEMPLATES_README.md                   ✅ Documentation
│   └── README.md                             ✅ Documentation
└── workspace/
    └── iproject/
        └── analysis/
            ├── analysis_new_feature_osprh_16421/  ✅ Your actual work
            ├── analysis_new_feature_osprh_16xxx/  ✅ Your future work
            └── ...
```

---

## ❓ FAQ

### Q: Where does "Full spike for OSPRH-XXXXX" create files?

**A**: `workspace/iproject/analysis/analysis_new_feature_osprh_xxxxx/`

### Q: Where does "assess review XXXXX" create files?

**A**: `workspace/iproject/results/review_xxxxx.md`

### Q: Can I have multiple workspace projects?

**A**: Yes! Change `workspace/.workspace-config`:
```bash
WORKSPACE_PROJECT_DIR=myproject
# or
WORKSPACE_PROJECT_DIR=customer-work
```

All new work goes to that configured directory.

### Q: What if I'm not using the workspace system?

**A**: You should be! But if not, AI will create in:
- Default: `workspace/iproject/` (creates if doesn't exist)
- All new work still goes to workspace, never to main `mymcp/`

### Q: When should something go in main `mymcp/analysis/` or `mymcp/results/`?

**A**: Only when it's meant to be an **example for other mymcp users**:
- Complete and merged work
- Referenced in documentation
- Demonstrates best practices
- Useful as reference for others

---

## 🔐 Git Ignore Rules

### What's Tracked in Git

**Main mymcp** (tracked):
```
mymcp/
├── results/
│   └── *.md                    # Templates and examples ONLY
└── analysis/
    └── */                      # Examples ONLY
```

**Workspace** (gitignored):
```
workspace/
├── iproject/                   # Gitignored (your personal work)
├── myproject/                  # Gitignored
└── .workspace-config           # Gitignored (your config)
```

### Why This Separation?

- ✅ **mymcp**: Clean, minimal, shareable examples
- ✅ **workspace**: Your actual work, not pushed to public repo
- ✅ **Flexibility**: Your work can go to different repos (e.g., GitLab iproject)

---

## 📝 Summary

### Simple Rules

1. **New reviews** → `workspace/iproject/results/`
2. **New analysis** → `workspace/iproject/analysis/`
3. **Templates/examples** → `mymcp/results/` or `mymcp/analysis/` (already there, don't add more)
4. **When complete** → Optionally copy to `mymcp/` as example

### AI Promises

When you say:
- ✅ "assess review XXXXX" → Creates in `workspace/iproject/results/`
- ✅ "Full spike for OSPRH-XXXXX" → Creates in `workspace/iproject/analysis/`
- ❌ Never creates new work in `mymcp/results/` or `mymcp/analysis/`

---

**Policy Version**: 1.0  
**Established**: 2025-11-22  
**Enforced by**: AI behavior + user vigilance  
**Updated**: When new patterns emerge

---

*Keep mymcp clean. Keep your work in workspace. Everyone's happy.* ✨

