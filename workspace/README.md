# Review Workspace

> **📝 For AI Assistants:** When user asks to "analyze review [URL]", follow the complete 5-step workflow in [README.md](../README.md#ai-assistant-instructions). Run fetch-review.sh, query MCP agent, read code, complete assessment, report findings.

This directory is for temporary code checkouts when analyzing OpenDev reviews, GitHub PRs, GitLab MRs, etc.

## Purpose

When using the MCP agents to analyze code reviews, you often need to:
1. Clone the repository
2. Fetch the specific review/PR
3. Examine the code changes in detail

This workspace keeps all temporary checkouts organized and separate from the MCP agent code.

## Usage

The `fetch-review.sh` script supports multiple options for different workflows:

```bash
./fetch-review.sh [options] <type> <url>

Options:
  --with-master      Also clone clean master branch for side-by-side comparison
  --rebase           Rebase the review on latest master (implies --with-master)
  --experiment       Create an experiment directory for testing changes
  --with-assessment  Create review assessment document (review_XXXXX.md)
  --all              Equivalent to --with-master --experiment
```

### Basic Usage (Review Only)

```bash
cd workspace
./fetch-review.sh opendev https://review.opendev.org/c/openstack/horizon/+/964897
```

This creates:
- `horizon-964897/` - The review patchset

### With Review Assessment (NEW!)

```bash
cd workspace
./fetch-review.sh --with-assessment opendev https://review.opendev.org/c/openstack/horizon/+/965216
```

This creates:
- `horizon-965216/` - The review patchset (in workspace/)
- `../results/review_965216.md` - Assessment document ready for Cursor to analyze

**Workflow:**
1. Script fetches review and creates assessment template in `results/`
2. Template is pre-filled with metadata (author, files changed, etc.)
3. Ask Cursor: "Please analyze review 965216 and complete results/review_965216.md"
4. Cursor examines the code and fills in all assessment sections

### Side-by-Side Comparison (with Master)

```bash
cd workspace
./fetch-review.sh --with-master opendev https://review.opendev.org/c/openstack/horizon/+/964897
```

This creates:
- `horizon-964897/` - The review patchset
- `horizon-master/` - Clean master branch for comparison

**Useful for:**
```bash
# Compare a file between review and master
diff -u horizon-master/path/to/file.py horizon-964897/path/to/file.py

# Or use a visual diff tool
meld horizon-master horizon-964897

# Check what changed across the entire project
git -C horizon-964897 diff master..HEAD
```

### With Rebase on Latest Master

```bash
cd workspace
./fetch-review.sh --rebase opendev https://review.opendev.org/c/openstack/horizon/+/964897
```

This creates:
- `horizon-964897/` - The review rebased on latest master
- `horizon-master/` - Clean master branch

**Useful for:**
- Ensuring the review still works with latest master
- Finding conflicts before they hit CI
- Testing against cutting-edge code

### With Experiment Directory

```bash
cd workspace
./fetch-review.sh --experiment opendev https://review.opendev.org/c/openstack/horizon/+/964897
```

This creates:
- `horizon-964897/` - The original review (read-only reference)
- `horizon-964897-experiment/` - Writable copy for testing changes

**Useful for:**
- Testing modifications to the review
- Trying alternative approaches
- Adding debug statements without affecting the original

### Full Setup (All Options)

```bash
cd workspace
./fetch-review.sh --all opendev https://review.opendev.org/c/openstack/horizon/+/964897
```

This creates:
- `horizon-964897/` - The review patchset
- `horizon-master/` - Clean master branch
- `horizon-964897-experiment/` - Experiment area

**Perfect for comprehensive review analysis!**

### OpenDev Reviews (Manual Method)

If you prefer manual git commands:

```bash
cd workspace
git clone https://github.com/openstack/<project> <project>-<change-number>
cd <project>-<change-number>
git fetch https://review.opendev.org/openstack/<project> refs/changes/<last-2-digits>/<change-number>/<patchset> && git checkout FETCH_HEAD
```

**Example** (for review 964897):
```bash
cd workspace
git clone https://github.com/openstack/horizon horizon-964897
cd horizon-964897
git fetch https://review.opendev.org/openstack/horizon refs/changes/97/964897/1 && git checkout FETCH_HEAD
```

### GitHub Pull Requests

```bash
# Basic
./fetch-review.sh github https://github.com/openstack-k8s-operators/horizon-operator/pull/402

# With master for comparison
./fetch-review.sh --with-master github https://github.com/openstack-k8s-operators/horizon-operator/pull/402

# Rebased on latest main/master
./fetch-review.sh --rebase github https://github.com/openstack-k8s-operators/horizon-operator/pull/402

# Full setup
./fetch-review.sh --all github https://github.com/openstack-k8s-operators/horizon-operator/pull/402
```

**Manual method:**
```bash
cd workspace
git clone https://github.com/<org>/<repo> <repo>-pr-<number>
cd <repo>-pr-<number>
git fetch origin pull/<number>/head:pr-<number>
git checkout pr-<number>
```

### GitLab Merge Requests

```bash
# Basic
./fetch-review.sh gitlab https://gitlab.cee.redhat.com/eng/openstack/python-django/-/merge_requests/123

# With master for comparison
./fetch-review.sh --with-master gitlab https://gitlab.cee.redhat.com/eng/openstack/python-django/-/merge_requests/123

# Rebased on latest main/master
./fetch-review.sh --rebase gitlab https://gitlab.cee.redhat.com/eng/openstack/python-django/-/merge_requests/123

# Full setup
./fetch-review.sh --all gitlab https://gitlab.cee.redhat.com/eng/openstack/python-django/-/merge_requests/123
```

**Manual method:**
```bash
cd workspace
git clone <gitlab-url>/<group>/<project> <project>-mr-<number>
cd <project>-mr-<number>
git fetch origin merge-requests/<number>/head:mr-<number>
git checkout mr-<number>
```

## Organization

The script creates directories following this naming convention:

**Review/PR/MR directories:**
- OpenDev: `<project>-<change-number>/` (e.g., `horizon-964897/`)
- GitHub: `<repo>-pr-<number>/` (e.g., `horizon-operator-pr-402/`)
- GitLab: `<project>-mr-<number>/` (e.g., `python-django-mr-123/`)

**Master/Main branch directories (with `--with-master` or `--rebase`):**
- `<project>-master/` (e.g., `horizon-master/`)
- Contains clean master/main branch for comparison

**Experiment directories (with `--experiment` or `--all`):**
- `<project>-<change-number>-experiment/` (e.g., `horizon-964897-experiment/`)
- Writable copy on its own branch for testing changes

**Example layout after `--all`:**
```
workspace/
├── horizon-964897/              # The review (reference)
├── horizon-master/              # Clean master branch
├── horizon-964897-experiment/   # Your experiment area
└── fetch-review.sh
```

## Comparison Workflows

### Side-by-Side File Comparison

Compare a specific file between the review and master:

```bash
# Using diff
diff -u horizon-master/openstack_dashboard/management/commands/migrate_settings.py \
        horizon-964897/openstack_dashboard/management/commands/migrate_settings.py

# Using diff with color
diff -u --color=always horizon-master/path/to/file.py horizon-964897/path/to/file.py

# Using a visual diff tool (meld, vimdiff, etc.)
meld horizon-master/path/to/file.py horizon-964897/path/to/file.py

# Using VS Code
code --diff horizon-master/path/to/file.py horizon-964897/path/to/file.py
```

### Directory Comparison

Compare entire directories:

```bash
# Compare entire projects
meld horizon-master horizon-964897

# Or use diff recursively
diff -r horizon-master horizon-964897

# Find modified files only
diff -qr horizon-master horizon-964897
```

### Git-Based Comparison

Using git within the review directory:

```bash
cd horizon-964897

# Show what changed in the review
git show HEAD

# Compare review against current master
git diff master..HEAD

# See the commit log
git log master..HEAD --oneline

# Show files changed
git diff --name-only master..HEAD

# Show statistics
git diff --stat master..HEAD
```

### Experiment Workflow

The experiment directory lets you test changes safely:

```bash
cd horizon-964897-experiment

# Make experimental changes
vim openstack_dashboard/management/commands/migrate_settings.py

# Test your changes
tox -e pep8

# Commit your experiment
git add .
git commit -m "Experiment: trying alternative approach"

# Compare your experiment with the original review
cd ..
diff -u horizon-964897/path/to/file.py \
        horizon-964897-experiment/path/to/file.py

# If experiment works, you can suggest it in the review comments
# If not, just delete the experiment directory
```

### Rebase Workflow

Check if the review still works with latest master:

```bash
# Fetch with rebase
./fetch-review.sh --rebase opendev https://review.opendev.org/c/openstack/horizon/+/964897

cd horizon-964897

# If rebase had conflicts, you'll see:
git status

# View the conflict
cat path/to/conflicted/file.py

# After resolving (if needed), test
tox -e pep8

# This tells you if the review needs updating before it can merge
```

## Important Note: Linter Behavior Can Vary

**Why you might not see errors in master:**

Linters like pylint may not catch all errors consistently due to:
- Different pylint versions
- Python version differences
- Type inference limitations
- Configuration variations

**Example:** Review 964897 fixes `os.path.exists(path, encoding="utf-8")` which causes a runtime `TypeError`, but current pylint 3.3.1 doesn't flag it. The author saw the error (E1123) when they created the review.

**Best practice:** Always:
1. ✅ Compare the actual code changes (`git show HEAD` or `diff`)
2. ✅ Test for runtime errors if suspicious
3. ✅ Run linting on both master and review
4. ✅ Trust the review's commit message about what error they saw

## Running Linters and Tests

Most OpenStack projects use `tox` for running linters and tests. After fetching a review:

### Check Available Tox Environments

```bash
cd workspace/<project-name>
tox -l
```

Common environments:
- `pep8` - Run all linting (flake8, pylint, etc.)
- `py3` or `py313` - Run unit tests
- `docs` - Build documentation
- `releasenotes` - Build release notes

### Run Linting

```bash
cd workspace/horizon-964897
tox -e pep8
```

This will:
- Install all required dependencies in an isolated environment
- Run flake8, pylint, and other project-specific linters
- Show a rating (e.g., "Your code has been rated at 10.00/10")

### Run Specific Linter Only

If you want to run just pylint on a specific file:

```bash
cd workspace/horizon-964897
source .tox/pep8/bin/activate  # After running tox -e pep8 once
pylint openstack_dashboard/management/commands/migrate_settings.py
```

### Quick Verification

To quickly verify the change doesn't break anything:

```bash
cd workspace/<project>
git show HEAD              # View the change
tox -e pep8               # Run linting
tox -e py3                # Run tests (optional, can be slow)
```

## Cleanup

This directory is gitignored. You can safely:
- Clone repositories here
- Make local changes for testing
- Delete directories when done

```bash
# Remove a specific review
rm -rf workspace/horizon-964897

# Clean up all old reviews
rm -rf workspace/*
```

## Benefits

✅ **Organized**: All review checkouts in one place  
✅ **Isolated**: Separate from MCP agent code  
✅ **Gitignored**: Won't clutter your repository  
✅ **Persistent**: Available across Cursor sessions  
✅ **Searchable**: Can use codebase_search across review code  
✅ **Context**: Full repository context for better analysis

