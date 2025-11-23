# Workspace Project Integration

This document explains how to use the `mymcp` workspace with your personal project directory for storing work artifacts.

---

## Overview

**Purpose:** Keep `mymcp` clean and focused on tools/examples, while storing your actual work artifacts in a separate directory.

**Architecture:**
- **mymcp/** - Tools, scripts, documentation, examples (this repo)
- **workspace/\<your-project\>/** - Your actual work: reviews, analysis, spikes

---

## Flexibility: Choose Your Own Approach

You have **three options** for where to store your work:

### Option 1: Simple Directory (Quick Start)

Let the script create `workspace/myproject/` automatically:

```bash
cd <mymcp-repo-path>/workspace
./scripts/fetch-review.sh --with-assessment opendev <url>
```

**First run:** Script asks if you want to use default `myproject/` or specify custom name  
**Subsequent runs:** Script remembers your choice

### Option 2: Custom Named Directory

Use your own directory name:

```bash
./scripts/fetch-review.sh --myworkspace my_horizon_work --with-assessment opendev <url>
```

Creates: `workspace/my_horizon_work/results/` and `workspace/my_horizon_work/analysis/`

### Option 3: Git Repository (Recommended)

Clone your personal git repository and use it:

```bash
cd workspace
git clone https://gitlab.cee.redhat.com/yourusername/your-repo.git
cd ..

# Tell fetch-review.sh to use your repo
./scripts/fetch-review.sh --myworkspace your-repo --with-assessment opendev <url>
```

**Benefits:**
- ✅ Version control for your work
- ✅ Push to remote git server
- ✅ Separate from mymcp
- ✅ Can share with others

---

## Setup

### Quick Start (Option 1)

No setup needed! Just run:

```bash
cd <mymcp-repo-path>/workspace
./scripts/fetch-review.sh --with-assessment opendev <review-url>
```

**On first run**, the script will ask:

```
╔════════════════════════════════════════════════════════════╗
║  Workspace Project Setup                                    ║
╚════════════════════════════════════════════════════════════╝

No workspace project directory found.

Where would you like to store your work?

  1) workspace/myproject/     (default - simple directory)
  2) Custom directory name    (you choose the name)
  3) Git repository          (clone your repo first)

Choice [1]:
```

### Custom Directory (Option 2)

Use `--myworkspace` flag:

```bash
./scripts/fetch-review.sh --myworkspace my_custom_name --with-assessment opendev <url>
```

### Git Repository (Option 3 - Recommended)

```bash
# 1. Clone your repository
cd workspace
git clone https://gitlab.cee.redhat.com/yourusername/iproject.git

# 2. Use it with fetch-review.sh
cd ..
./scripts/fetch-review.sh --myworkspace iproject --with-assessment opendev <url>
```

**The script will remember your choice** in `workspace/.workspace-config`

---

## How It Works

### When You Run fetch-review.sh

```bash
cd <mymcp-repo-path>/workspace
./scripts/fetch-review.sh --with-assessment opendev <url>
```

**The script will:**
1. ✅ Check for `workspace/.workspace-config` (your saved preference)
2. ✅ If not found, ask you to choose workspace directory
3. ✅ Verify `workspace/<your-project>/results/` and `/analysis/` exist
4. ✅ Clone the review code to `workspace/<project>-XXXXX/`
5. ✅ Create assessment template in `<your-project>/results/review_XXXXX.md`
6. ✅ Tell you to ask Cursor to complete the analysis

### When You Ask Cursor to Analyze

```
You: "Please analyze review 967773"
```

**Cursor will:**
1. ✅ Find the assessment in `workspace/<your-project>/results/review_967773.md`
2. ✅ Read the code from `workspace/<project>-967773/`
3. ✅ Complete the full assessment
4. ✅ Save to `workspace/<your-project>/results/review_967773.md`

### When You Create Feature Analysis

```
You: "Full spike for OSPRH-12345"
```

**Cursor will:**
1. ✅ Create spike in `workspace/<your-project>/analysis/analysis_new_feature_osprh_12345/`
2. ✅ Create patchsets in the same location
3. ✅ Track WIP documents there as you work

---

## Directory Structure

```
<mymcp-repo-path>/
├── workspace/
│   ├── .workspace-config            # Your workspace preference (gitignored)
│   ├── myproject/                   # Your work (default name, gitignored)
│   │   ├── results/                 # Your review assessments
│   │   │   ├── review_967773.md
│   │   │   └── ...
│   │   └── analysis/                # Your feature analysis
│   │       ├── analysis_new_feature_osprh_XXXXX/
│   │       └── ...
│   ├── horizon-967773/              # Temporary code checkout (gitignored)
│   └── scripts/
│       └── fetch-review.sh          # Updated to support workspace projects
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

## What's in mymcp vs Your Workspace Project

### mymcp Repository (Public/Internal)

**Keep here:**
- ✅ Scripts (`workspace/scripts/fetch-review.sh`)
- ✅ Documentation (`README.md`, `HOW_TO_ASK.md`)
- ✅ **Example** assessments (`results/review_965215.md`)
- ✅ **Example** feature analysis (`analysis/analysis_new_feature_966349/`)
- ✅ Templates (`results/review_template.md`)
- ✅ Use case guides (`usecases/`)

**Purpose:** Help others learn your methodology

### Your Workspace Project (workspace/myproject/ or workspace/your-repo/)

**Keep here:**
- ✅ **All your actual work** assessments
- ✅ **All your actual** feature analysis
- ✅ **All your actual** spikes
- ✅ WIP documents
- ✅ Work-specific notes

**Purpose:** Your personal work directory (optionally a git repo)

---

## Committing Your Work

### If Using Git Repository (Option 3)

```bash
cd <mymcp-repo-path>/workspace/your-repo

# After Cursor completes an assessment
git add results/review_967773.md
git commit -m "Complete assessment for review 967773"
git push

# After creating feature analysis
git add analysis/analysis_new_feature_osprh_12345/
git commit -m "Add spike and patchsets for OSPRH-12345"
git push
```

### If Using Simple Directory (Options 1 & 2)

Your work is stored locally in `workspace/myproject/` or `workspace/your-custom-name/`.

**To add version control later:**

```bash
cd workspace/myproject
git init
git add .
git commit -m "Initial commit of my work"
git remote add origin https://gitlab.example.com/you/your-repo.git
git push -u origin main
```

### mymcp Workflow

```bash
cd <mymcp-repo-path>

# Only commit when you've created/updated examples or tools
git add workspace/scripts/fetch-review.sh
git commit -m "Update fetch-review.sh to support workspace projects"
git push
```

---

## Configuration: .workspace-config

The script stores your preference in `workspace/.workspace-config`:

```ini
# Workspace project configuration
# This file is created by fetch-review.sh on first run
WORKSPACE_PROJECT_DIR=myproject
```

**Manually edit** if you want to change:

```bash
# Switch to a different directory
echo "WORKSPACE_PROJECT_DIR=my_new_workspace" > workspace/.workspace-config
```

**Delete** to reset and be prompted again:

```bash
rm workspace/.workspace-config
```

---

## Command-Line Options

### --myworkspace <directory-name>

Specify workspace directory for this run (and save as default):

```bash
./scripts/fetch-review.sh --myworkspace iproject --with-assessment opendev <url>
```

**What this does:**
- Uses `workspace/iproject/` for this assessment
- Saves `iproject` to `.workspace-config` for future runs

### Examples

```bash
# Use default (myproject)
./scripts/fetch-review.sh --with-assessment opendev <url>

# Use custom directory
./scripts/fetch-review.sh --myworkspace horizon_reviews --with-assessment opendev <url>

# Use git repository
./scripts/fetch-review.sh --myworkspace iproject --with-assessment github <url>
```

---

## For Other Users of mymcp

If someone else uses your `mymcp` repository, they should:

1. **Clone mymcp:**
   ```bash
   git clone https://github.com/yourusername/mymcp.git
   cd mymcp/workspace
   ```

2. **Run fetch-review.sh:**
   ```bash
   ./scripts/fetch-review.sh --with-assessment opendev <url>
   ```

3. **Choose their workspace approach:**
   - Option 1: Accept default `myproject/`
   - Option 2: Use `--myworkspace their_custom_name`
   - Option 3: Clone their git repo and use `--myworkspace their-repo`

4. **Use the tools:**
   ```bash
   # Cursor completes assessment
   "Please analyze review XXXXX"
   ```

---

## Benefits

✅ **Flexibility:**
- Simple directory for quick start
- Custom names for organization
- Git repos for version control

✅ **Separation of Concerns:**
- mymcp = tools + examples
- Your workspace = your work

✅ **Clean Repository:**
- mymcp stays small and focused
- Easy for others to learn from

✅ **Version Control (Optional):**
- Use git if you want
- Or just use simple directories

✅ **Easy Sharing:**
- Share tools (mymcp) publicly
- Keep work (your workspace) private or share selectively

✅ **No Forced Structure:**
- You choose: simple dir, custom name, or git repo
- Script adapts to your preference

---

## Troubleshooting

### "Workspace project not found" Error

**Problem:** Script can't find your workspace directory

**Solution:**
```bash
# Check what's configured
cat workspace/.workspace-config

# Re-run with explicit directory
./scripts/fetch-review.sh --myworkspace myproject --with-assessment opendev <url>
```

### "Missing results/ or analysis/ directories"

**Problem:** Workspace exists but missing required directories

**Solution:**
```bash
cd workspace/myproject  # or your directory name
mkdir -p results analysis
```

The script will create these automatically on first run.

### Assessment not found

**Problem:** Cursor can't find the assessment file

**Solution:** Check the location
```bash
# Find your workspace config
cat workspace/.workspace-config

# Check if assessment exists
ls -la workspace/myproject/results/review_XXXXX.md
```

### Want to switch workspace directories

**Solution:**
```bash
# Option 1: Delete config and be prompted again
rm workspace/.workspace-config

# Option 2: Edit config manually
echo "WORKSPACE_PROJECT_DIR=new_directory_name" > workspace/.workspace-config

# Option 3: Use --myworkspace flag (will update config)
./scripts/fetch-review.sh --myworkspace new_directory --with-assessment opendev <url>
```

---

## Migration from iproject

If you previously used "iproject":

```bash
# Your existing setup still works!
# The script will find workspace/iproject/ and use it

# Or rename if you prefer
cd workspace
mv iproject myproject

# Update config
echo "WORKSPACE_PROJECT_DIR=myproject" > .workspace-config
```

---

## Quick Reference

| Task | Command |
|------|---------|
| First time setup | `./scripts/fetch-review.sh --with-assessment opendev <url>` |
| Use default (myproject) | `./scripts/fetch-review.sh --with-assessment opendev <url>` |
| Use custom directory | `./scripts/fetch-review.sh --myworkspace my_dir --with-assessment opendev <url>` |
| Use git repository | Clone first, then `--myworkspace repo-name` |
| Check current config | `cat workspace/.workspace-config` |
| Reset configuration | `rm workspace/.workspace-config` |
| Analyze review | "Please analyze review XXXXX" |
| Create spike | "Full spike for OSPRH-XXXXX" |

---

**Last Updated:** 2025-11-22  
**See Also:**
- [analysis/HOW_TO_ASK.md](analysis/HOW_TO_ASK.md) - How to request analysis
- [workspace/scripts/README.md](workspace/scripts/README.md) - Script documentation
- [results/README.md](results/README.md) - Assessment documentation

