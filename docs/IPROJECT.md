# iProject Integration

This document explains how to use the `mymcp` workspace with your personal `iproject` repository for storing work artifacts.

---

## Overview

**Purpose:** Keep `mymcp` clean and focused on tools/examples, while storing your actual work artifacts in a separate repository (`iproject`).

**Architecture:**
- **mymcp/** - Tools, scripts, documentation, examples (public or internal repo)
- **iproject/** - Your personal work: reviews, analysis, spikes (private GitLab repo)

---

## Setup

### 1. Clone Your iProject Repository

```bash
cd /home/omcgonag/Work/mymcp/workspace
git clone https://gitlab.cee.redhat.com/omcgonag/iproject.git
```

### 2. Create Required Directories

```bash
cd iproject
mkdir -p results analysis
git add results/.gitkeep analysis/.gitkeep
git commit -m "Initialize results and analysis directories"
git push
```

### 3. Set Environment Variable

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
export WORKSPACE_IPROJECT_REPO="https://gitlab.cee.redhat.com/omcgonag/iproject.git"
```

Then reload:
```bash
source ~/.bashrc
```

**What this does:**
- `fetch-review.sh` will verify iproject exists
- Assessments will be saved to `workspace/iproject/results/`
- Analysis documents will be suggested for `workspace/iproject/analysis/`

---

## How It Works

### When You Run fetch-review.sh

```bash
cd /home/omcgonag/Work/mymcp/workspace
./scripts/fetch-review.sh --with-assessment opendev <url>
```

**The script will:**
1. ✅ Check if `workspace/iproject/` exists
2. ✅ Verify `iproject/results/` and `iproject/analysis/` directories exist
3. ✅ Clone the review code to `workspace/horizon-XXXXX/`
4. ✅ Create assessment template in `iproject/results/review_XXXXX.md`
5. ✅ Tell you to ask Cursor to complete the analysis

### When You Ask Cursor to Analyze

```
You: "Please analyze review 967773"
```

**Cursor will:**
1. ✅ Find the assessment in `workspace/iproject/results/review_967773.md`
2. ✅ Read the code from `workspace/horizon-967773/`
3. ✅ Complete the full assessment
4. ✅ Save to `workspace/iproject/results/review_967773.md`

### When You Create Feature Analysis

```
You: "Full spike for OSPRH-12345"
```

**Cursor will:**
1. ✅ Create spike in `workspace/iproject/analysis/analysis_new_feature_osprh_12345/`
2. ✅ Create patchsets in the same location
3. ✅ Track WIP documents there as you work

---

## Directory Structure

```
/home/omcgonag/Work/mymcp/
├── workspace/
│   ├── iproject/                    # Your personal work (gitignored in mymcp)
│   │   ├── .git/                    # Separate git repository
│   │   ├── results/                 # Your review assessments
│   │   │   ├── review_967773.md
│   │   │   ├── review_pr_5192.md
│   │   │   └── ...
│   │   └── analysis/                # Your feature analysis
│   │       ├── analysis_new_feature_osprh_XXXXX/
│   │       └── ...
│   ├── horizon-967773/              # Temporary code checkout (gitignored)
│   └── scripts/
│       └── fetch-review.sh          # Updated to use iproject
├── results/                         # Examples only (for mymcp users)
│   ├── review_template.md
│   ├── review_965215.md             # Example assessment
│   └── README.md
└── analysis/                        # Examples only (for mymcp users)
    ├── analysis_new_feature_966349/ # Example: successful feature
    ├── analysis_new_feature_osprh_12802/  # Example: in-progress feature
    └── HOW_TO_ASK.md
```

---

## What's in mymcp vs iproject

### mymcp Repository (Public/Internal)

**Keep here:**
- ✅ Scripts (`workspace/scripts/fetch-review.sh`)
- ✅ Documentation (`README.md`, `HOW_TO_ASK.md`)
- ✅ **Example** assessments (`results/review_965215.md`)
- ✅ **Example** feature analysis (`analysis/analysis_new_feature_966349/`)
- ✅ Templates (`results/review_template.md`)
- ✅ Use case guides (`usecases/`)

**Purpose:** Help others learn your methodology

### iproject Repository (Private GitLab)

**Keep here:**
- ✅ **All your actual work** assessments
- ✅ **All your actual** feature analysis
- ✅ **All your actual** spikes
- ✅ WIP documents
- ✅ Work-specific notes

**Purpose:** Your personal work repository

---

## Committing Your Work

### iproject Workflow

```bash
cd /home/omcgonag/Work/mymcp/workspace/iproject

# After Cursor completes an assessment
git add results/review_967773.md
git commit -m "Complete assessment for review 967773"
git push

# After creating feature analysis
git add analysis/analysis_new_feature_osprh_12345/
git commit -m "Add spike and patchsets for OSPRH-12345"
git push
```

### mymcp Workflow

```bash
cd /home/omcgonag/Work/mymcp

# Only commit when you've created/updated examples or tools
git add workspace/scripts/fetch-review.sh
git commit -m "Update fetch-review.sh to support iproject"
git push
```

---

## Environment Variable: WORKSPACE_IPROJECT_REPO

### Purpose

Tells `fetch-review.sh` where your iproject repository lives.

### Configuration

**Option 1: In your shell config (~/.bashrc)**
```bash
export WORKSPACE_IPROJECT_REPO="https://gitlab.cee.redhat.com/omcgonag/iproject.git"
```

**Option 2: In .env file (workspace/.env)**
```bash
# Create workspace/.env
echo 'WORKSPACE_IPROJECT_REPO="https://gitlab.cee.redhat.com/omcgonag/iproject.git"' > workspace/.env
```

**Option 3: Per-session**
```bash
export WORKSPACE_IPROJECT_REPO="https://gitlab.cee.redhat.com/omcgonag/iproject.git"
./scripts/fetch-review.sh --with-assessment opendev <url>
```

### Verification

```bash
# Check if set
echo $WORKSPACE_IPROJECT_REPO

# Should output:
# https://gitlab.cee.redhat.com/omcgonag/iproject.git
```

### What Happens If Not Set?

If `WORKSPACE_IPROJECT_REPO` is not set:
- ✅ `fetch-review.sh` falls back to checking for `workspace/iproject/`
- ⚠️ If `workspace/iproject/` doesn't exist, script warns you to clone it
- ❌ If neither exists, script fails with helpful error message

---

## For Other Users of mymcp

If someone else uses your `mymcp` repository, they should:

1. **Fork or clone mymcp:**
   ```bash
   git clone https://github.com/yourusername/mymcp.git
   cd mymcp/workspace
   ```

2. **Create their own iproject:**
   ```bash
   # On GitLab/GitHub, create their personal repository
   git clone https://gitlab.example.com/theirname/their-iproject.git iproject
   cd iproject
   mkdir -p results analysis
   git add .
   git commit -m "Initialize"
   git push
   ```

3. **Set their environment variable:**
   ```bash
   export WORKSPACE_IPROJECT_REPO="https://gitlab.example.com/theirname/their-iproject.git"
   ```

4. **Use the tools:**
   ```bash
   ./scripts/fetch-review.sh --with-assessment opendev <url>
   ```

---

## Benefits

✅ **Separation of Concerns:**
- mymcp = tools + examples
- iproject = your work

✅ **Clean Repository:**
- mymcp stays small and focused
- Easy for others to learn from

✅ **Version Control:**
- Your work is versioned in iproject
- Tools are versioned in mymcp
- No mixing

✅ **Easy Sharing:**
- Share tools (mymcp) publicly
- Keep work (iproject) private
- Share specific assessments by cherry-picking from iproject

✅ **Gitignore Simplicity:**
- No complex gitignore patterns
- iproject is a separate repo
- workspace/iproject/ is gitignored in mymcp

---

## Troubleshooting

### "iproject not found" Error

**Problem:** `fetch-review.sh` can't find `workspace/iproject/`

**Solution:**
```bash
cd /home/omcgonag/Work/mymcp/workspace
git clone https://gitlab.cee.redhat.com/omcgonag/iproject.git
```

### "Missing results/ or analysis/ directories"

**Problem:** iproject exists but missing required directories

**Solution:**
```bash
cd /home/omcgonag/Work/mymcp/workspace/iproject
mkdir -p results analysis
git add results/.gitkeep analysis/.gitkeep
git commit -m "Add required directories"
git push
```

### "Assessment not found"

**Problem:** Cursor can't find the assessment file

**Solution:** Check the location
```bash
ls -la workspace/iproject/results/review_XXXXX.md
```

If not there, re-run fetch-review.sh:
```bash
./scripts/fetch-review.sh --with-assessment opendev <url>
```

---

## Migration Guide

If you have existing work in `mymcp/results/` or `mymcp/analysis/`:

### Move to iproject

```bash
# Move actual work to iproject
cd /home/omcgonag/Work/mymcp
mv results/review_967773.md workspace/iproject/results/
mv analysis/analysis_new_feature_osprh_XXXXX/ workspace/iproject/analysis/

# Commit in iproject
cd workspace/iproject
git add results/ analysis/
git commit -m "Migrate work from mymcp"
git push
```

### Keep examples in mymcp

```bash
# Keep examples for documentation
# results/review_965215.md - referenced in usecases/
# results/review_template.md - template
# analysis/analysis_new_feature_966349/ - complete example
# analysis/analysis_new_feature_osprh_12802/ - in-progress example
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Setup iproject | `cd workspace && git clone <repo> iproject` |
| Set env var | `export WORKSPACE_IPROJECT_REPO="<repo-url>"` |
| Fetch review | `./scripts/fetch-review.sh --with-assessment opendev <url>` |
| Analyze review | "Please analyze review XXXXX" |
| Commit work | `cd workspace/iproject && git add . && git commit && git push` |
| Create spike | "Full spike for OSPRH-XXXXX" |

---

**Last Updated:** 2025-11-22  
**See Also:**
- [HOW_TO_ASK.md](analysis/HOW_TO_ASK.md) - How to request analysis
- [workspace/scripts/README.md](workspace/scripts/README.md) - Script documentation
- [results/README.md](results/README.md) - Assessment documentation

