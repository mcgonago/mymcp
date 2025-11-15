# Automating Reviews Using fetch_review.sh

## Overview

This use case demonstrates how to use `fetch_review.sh` to automate the review process for code changes across multiple platforms (OpenDev Gerrit, GitHub, GitLab). The workflow combines automated code fetching, MCP agent analysis, and structured assessment document creation.

## When to Use This

**User asks to analyze a review with any of these commands:**
- "Analyze review [URL]"
- "Analyze OpenDev review [NUMBER]"
- "Fetch and analyze review [URL] with full assessment"
- "Please review https://review.opendev.org/c/openstack/horizon/+/965215"

## Complete Workflow

### Step 1: Fetch the Review Code

```bash
cd /home/omcgonag/Work/mymcp/workspace
./fetch-review.sh --with-assessment opendev https://review.opendev.org/c/openstack/horizon/+/965215
```

This creates:
- `workspace/openstack-965215/` - the review (checked out) code
- `results/review_965215.md`    - review assessment

Here is a checked-in example: [`results/review_965215.md`](../../results/review_965215.md)

### Step 2: Query the MCP Agent (manual)

```
@opendev-reviewer-agent Analyze the review at https://review.opendev.org/c/openstack/horizon/+/965215
```

This fetches:
- Review metadata (author, status, commit message)
- File changes and statistics
- Comments and review history

### Step 3: What the Assessment Contains

The generated assessment document includes:
- **Executive Summary** - What this review does and your recommendation
- **Code Quality Assessment** - Strengths, concerns, suggestions
- **Technical Analysis** - File-by-file analysis
- **Review Checklist** - Code quality, testing, security, performance
- **Testing Verification** - How to test this change
- **Recommendations** - What should be addressed before merge
- **Decision** - Final recommendation (+2/+1/0/-1)

## Workspace for Code Review Analysis

The `workspace/` directory provides a dedicated space for cloning and analyzing code from reviews, PRs, and MRs:

**Quick Start (with automated assessment):**
```bash
# Fetch an OpenDev review with assessment document
cd workspace
./fetch-review.sh --with-assessment opendev https://review.opendev.org/c/openstack/horizon/+/965216

# Ask Cursor to complete the assessment
"Please analyze review 965216 and complete results/review_965216.md"
```

**Traditional workflow:**
```bash
# Fetch a GitHub PR
./fetch-review.sh github https://github.com/openstack-k8s-operators/horizon-operator/pull/402

# Fetch a GitLab MR
./fetch-review.sh gitlab https://gitlab.cee.redhat.com/eng/openstack/python-django/-/merge_requests/123
```

**Benefits:**
- ✅ Organized workspace separate from agent code
- ✅ **NEW:** Automated review assessment document creation
- ✅ Full repository context for deeper analysis
- ✅ Use Cursor's `codebase_search` across review code
- ✅ Git-ignored to avoid cluttering the repo
- ✅ Persistent across sessions

See [`workspace/README.md`](../../workspace/README.md) and [`workspace/docs/REVIEW_ASSESSMENT_GUIDE.md`](../../workspace/docs/REVIEW_ASSESSMENT_GUIDE.md) for detailed usage instructions.

## Platform-Specific Examples

### Example 1: OpenDev Review

```
User wants to: "Analyze review https://review.opendev.org/c/openstack/horizon/+/965215"

1. cd workspace && ./fetch-review.sh --with-assessment opendev https://review.opendev.org/c/openstack/horizon/+/965215
2. which runs @opendev-reviewer-agent Analyze the review at https://review.opendev.org/c/openstack/horizon/+/965215
3. full assessment at results/review_965215.md"
```

### Example 2: GitHub PR

```
User wants to: "Review PR https://github.com/openstack-k8s-operators/horizon-operator/pull/402"

1. cd workspace && ./fetch-review.sh --with-assessment github https://github.com/openstack-k8s-operators/horizon-operator/pull/402
2. Which runs @github-reviewer-agent Analyze PR https://github.com/openstack-k8s-operators/horizon-operator/pull/402
3. full assessment at results/review_pr_402.md
```

### Example 3: GitLab MR

```
User wants to: "Analyze GitLab MR https://gitlab.cee.redhat.com/eng/openstack/python-django/-/merge_requests/123"

1. cd workspace && ./fetch-review.sh --with-assessment gitlab https://gitlab.cee.redhat.com/eng/openstack/python-django/-/merge_requests/123
2. which runs @gitlab-cee-agent Analyze the merge request at https://gitlab.cee.redhat.com/eng/openstack/python-django/-/merge_requests/123
3. full assessment at results/review_mr_123.md
```

## Available MCP Agents

- `@opendev-reviewer-agent` - For review.opendev.org (Gerrit)
- `@github-reviewer-agent` - For github.com Pull Requests
- `@gitlab-cee-agent` - For gitlab.cee.redhat.com (internal Red Hat)
- `@jiraMcp` - For Jira issues

## Directory Structure

```
/home/omcgonag/Work/mymcp/
├── workspace/              # Run fetch-review.sh here (gitignored)
├── results/                # Assessment documents go here (can commit)
├── analysis/               # Permanent research (always commit)
└── README.md               # Main repository documentation
```

## Error Handling

**If fetch-review.sh fails:**
- Check the URL format
- Try manual git clone and fetch

**If MCP agent fails:**
- Continue anyway using git show HEAD
- Note in assessment that MCP data unavailable

**If review is very large:**
- Focus on changed files only
- Summarize rather than detail every file

## Quick Reference Commands

```bash
# Fetch review with assessment
cd /home/omcgonag/Work/mymcp/workspace
./fetch-review.sh --with-assessment opendev [URL]

# View changes
cd [project]-[number]
git show HEAD
git log -1

# Run tests
tox -e pep8

# Complete assessment location
/home/omcgonag/Work/mymcp/results/review_[number].md
```

## Additional Resources

- [Workspace README](../../workspace/README.md) - Detailed workspace usage
- [Review Assessment Guide](../../workspace/docs/REVIEW_ASSESSMENT_GUIDE.md) - Comprehensive assessment feature guide
- [Quick Start](../../workspace/docs/QUICK_START.md) - Quick reference commands
- [Main README](../../README.md) - Repository overview

## See Also

- [OpenDev Review Agent Setup](../../opendev-review-agent/README.md)
- [GitHub Review Agent Setup](../../github-agent/README.md)
- [GitLab Agent Setup](../../gitlab-rh-agent/README.md)

