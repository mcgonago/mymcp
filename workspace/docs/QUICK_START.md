# Workspace Quick Start Guide

## TL;DR - Recommended Workflow

For comprehensive code review analysis with side-by-side comparison, experiment area, and automated assessment:

```bash
cd workspace
./fetch-review.sh --with-assessment --all <type> <url>
```

This gives you:
- ✅ The review/PR/MR to analyze
- ✅ Clean master branch for comparison
- ✅ Experiment directory for testing changes
- ✅ Review assessment document (review_XXXXX.md)

**Then ask Cursor:** "Please analyze review [NUMBER] and complete review_[NUMBER].md"

---

## Quick Examples

### OpenDev Review (with Assessment)
```bash
cd workspace
./fetch-review.sh --with-assessment --all opendev https://review.opendev.org/c/openstack/horizon/+/964897
```

Creates:
- `horizon-964897/` - The review
- `horizon-master/` - Master branch
- `horizon-964897-experiment/` - Experiment area
- `../results/review_964897.md` - Assessment document

Ask Cursor: "Please analyze review 964897 and complete results/review_964897.md"

### GitHub PR
```bash
cd workspace
./fetch-review.sh --all github https://github.com/openstack-k8s-operators/horizon-operator/pull/402
```

Creates:
- `horizon-operator-pr-402/` - The PR
- `horizon-operator-master/` - Master/main branch
- `horizon-operator-pr-402-experiment/` - Experiment area

### GitLab MR
```bash
cd workspace
./fetch-review.sh --all gitlab https://gitlab.cee.redhat.com/eng/openstack/python-django/-/merge_requests/123
```

---

## Common Tasks

### 1. Create and Complete Review Assessment
```bash
cd workspace
./fetch-review.sh --with-assessment opendev https://review.opendev.org/c/openstack/horizon/+/965216

# In Cursor, ask:
"Please analyze review 965216 and complete results/review_965216.md"
```

### 2. View the Changes
```bash
cd workspace/horizon-964897
git show HEAD
```

### 3. Run Linting
```bash
cd workspace/horizon-964897
tox -e pep8
```

### 4. Compare File with Master
```bash
cd workspace
diff -u horizon-master/path/to/file.py horizon-964897/path/to/file.py
```

### 5. Compare Entire Directories
```bash
cd workspace
meld horizon-master horizon-964897
# or
diff -qr horizon-master horizon-964897
```

### 6. Test Changes in Experiment Directory
```bash
cd workspace/horizon-964897-experiment
# Make your changes
vim openstack_dashboard/management/commands/migrate_settings.py
# Test them
tox -e pep8
# Commit if they work
git add .
git commit -m "Experiment: alternative approach"
```

### 7. Check if Review Works with Latest Master
```bash
cd workspace
./fetch-review.sh --rebase opendev https://review.opendev.org/c/openstack/horizon/+/964897
cd horizon-964897
tox -e pep8
```

### 8. Promote Assessment to Permanent Analysis
```bash
# After completing a thorough assessment
cp ../results/review_965216.md ../analysis/
cd /home/omcgonag/Work/mymcp
git add analysis/review_965216.md
git commit -m "Add assessment for review 965216"
```

---

## Options Reference

| Option | Description | Creates |
|--------|-------------|---------|
| _(none)_ | Basic fetch | Review only |
| `--with-master` | Add clean master | Review + Master |
| `--rebase` | Rebase on master | Review (rebased) + Master |
| `--experiment` | Add experiment dir | Review + Experiment |
| `--with-assessment` | Create assessment doc | Review + ../results/review_XXXXX.md |
| `--all` | Master + Experiment | Review + Master + Experiment |
| `--with-assessment --all` | Complete setup | All + ../results/review_XXXXX.md |

---

## Directory Layout

After `./fetch-review.sh --all opendev <url>`:

```
workspace/
├── horizon-964897/                  # The review (reference copy)
│   └── [detached HEAD or branch]
├── horizon-master/                  # Clean master branch
│   └── [master branch]
├── horizon-964897-experiment/       # Your workspace
│   └── [experiment-964897 branch]
├── fetch-review.sh
├── README.md
└── QUICK_START.md (this file)
```

---

## Tips

**Keep Master Updated:**
```bash
cd workspace/horizon-master
git pull origin master
```

**Clean Up After Review:**
```bash
cd workspace
rm -rf horizon-964897 horizon-964897-experiment
# Keep horizon-master for future reviews of same project
```

**Visual Diff Tools:**
```bash
# Meld (GUI)
meld horizon-master/file.py horizon-964897/file.py

# VS Code
code --diff horizon-master/file.py horizon-964897/file.py

# Vimdiff
vimdiff horizon-master/file.py horizon-964897/file.py
```

**Find All Changed Files:**
```bash
cd workspace/horizon-964897
git diff --name-only master..HEAD
```

**See Change Statistics:**
```bash
cd workspace/horizon-964897
git diff --stat master..HEAD
```

---

## Troubleshooting

**"Directory already exists":**
The script will prompt you to overwrite. Answer `y` to re-clone.

**"Rebase had conflicts":**
This means the review needs updating to work with current master. You can:
1. Fix the conflicts: `git status` → edit files → `git rebase --continue`
2. Or abort: `git rebase --abort`

**Wrong branch name (main vs master):**
The script auto-detects whether the project uses `main` or `master`.

---

## Advanced Usage

**Fetch specific patchset:**
Edit the URL or script to use different patchset numbers.
For OpenDev: `refs/changes/97/964897/2` (for patchset 2)

**Compare your experiment with the review:**
```bash
cd workspace
diff -u horizon-964897/file.py horizon-964897-experiment/file.py
```

**Create a patch file from experiment:**
```bash
cd workspace/horizon-964897-experiment
git diff HEAD^ > ~/my-suggestion.patch
```

**Apply someone else's suggestion:**
```bash
cd workspace/horizon-964897-experiment
git apply ~/their-suggestion.patch
tox -e pep8
```

---

For full documentation, see [README.md](../README.md)

