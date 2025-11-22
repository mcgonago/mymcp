# Fetch Review Script

Helper script to fetch OpenDev reviews, GitHub PRs, or GitLab MRs into the workspace for analysis.

## Usage

```bash
./fetch-review.sh [options] <type> <url>
```

## Options

| Option | Description |
|--------|-------------|
| `--with-master` | Also clone clean master branch for side-by-side comparison |
| `--rebase` | Rebase the review on top of latest master (implies --with-master) |
| `--experiment` | Create an experiment directory for testing changes |
| `--with-assessment` | Create review assessment document template |
| `--all` | Equivalent to `--with-master --experiment` |

## Review Types

| Type | Description | Example URL |
|------|-------------|-------------|
| `opendev` | OpenDev/Gerrit review | `https://review.opendev.org/c/openstack/horizon/+/967773` |
| `github` | GitHub Pull Request | `https://github.com/org/repo/pull/5232` |
| `gitlab` | GitLab Merge Request | `https://gitlab.example.com/group/project/-/merge_requests/123` |

## Examples

### Basic: Fetch OpenDev Review

```bash
./fetch-review.sh opendev https://review.opendev.org/c/openstack/horizon/+/967773
```

Creates:
- `workspace/horizon-967773/` - Review code

### With Master Comparison

```bash
./fetch-review.sh --with-master opendev https://review.opendev.org/c/openstack/horizon/+/967773
```

Creates:
- `workspace/horizon-967773/` - Review code
- `workspace/horizon-master/` - Clean master branch

### With Assessment

```bash
./fetch-review.sh --with-master --with-assessment opendev \
  https://review.opendev.org/c/openstack/horizon/+/967773
```

Creates:
- `workspace/horizon-967773/` - Review code
- `workspace/horizon-master/` - Master branch
- `results/review_967773.md` - Assessment template (git-tracked)

### GitHub PR with Assessment

```bash
./fetch-review.sh --with-master --with-assessment github \
  https://github.com/RedHatInsights/rhsm-subscriptions/pull/5232
```

Creates:
- `workspace/rhsm-subscriptions-pr-5232/` - PR code
- `workspace/rhsm-subscriptions-master/` - Master branch
- `results/review_pr_5232.md` - Assessment template

### Full Setup with Experiment Directory

```bash
./fetch-review.sh --all --with-assessment opendev \
  https://review.opendev.org/c/openstack/horizon/+/967773
```

Creates:
- `workspace/horizon-967773/` - Review code (branch: `ws-review-967773`)
- `workspace/horizon-master/` - Master branch
- `workspace/horizon-967773-experiment/` - Experiment area (branch: `ws-experiment-967773`)
- `results/review_967773.md` - Assessment template

## Workflow Branches

The script creates descriptive branch names:

| Checkout Type | Branch Name | Purpose |
|---------------|-------------|---------|
| Review/PR/MR | `ws-review-XXXXX` | Working review branch |
| | `ws-pr-XXXXX` | GitHub PR branch |
| | `ws-mr-XXXXX` | GitLab MR branch |
| Experiment | `ws-experiment-XXXXX` | Safe testing area |

**Benefits:**
- ✅ No detached HEAD warnings
- ✅ Clear branch purpose
- ✅ Easy to track changes

## After Fetching

Once fetched, complete the assessment:

```bash
# 1. Review the code
cd horizon-967773
git show HEAD

# 2. Ask Cursor to complete the assessment
# In Cursor chat:
"Please analyze review 967773 and complete the assessment"

# 3. Cursor will fill in all sections:
#    - Executive Summary
#    - Code Quality Assessment
#    - Technical Analysis
#    - Recommendations
#    - Final Decision (+2/+1/0/-1)
```

## Directory Structure After Fetch

```
workspace/
├── horizon-967773/              # Review code
│   └── (on branch ws-review-967773)
├── horizon-master/              # Comparison baseline
├── horizon-967773-experiment/   # Experiment area (if --experiment)
└── scripts/
    └── fetch-review.sh

results/
├── review_967773.md            # Assessment (git-tracked)
└── review_template.md
```

## Related Documentation

- `../../results/README.md` - Results directory guide
- `../../analysis/HOW_TO_ASK.md` - How to request reviews and analysis

---

**Last Updated:** 2025-11-21
