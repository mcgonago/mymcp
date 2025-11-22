#!/bin/bash
#
# Helper script to fetch OpenDev reviews, GitHub PRs, or GitLab MRs
# into the workspace directory for analysis
#
# Usage:
#   ./fetch-review.sh [options] <type> <url>
#
# Options:
#   --with-master      Also clone clean master branch for side-by-side comparison
#   --rebase           Rebase the review on top of latest master
#   --experiment       Create an experiment directory for testing changes
#   --with-assessment  Create a review assessment document (review_XXXXX.md)
#   --all              Equivalent to --with-master --experiment
#
# Types:
#   opendev - OpenDev/Gerrit review
#   github  - GitHub Pull Request
#   gitlab  - GitLab Merge Request
#
# Examples:
#   ./fetch-review.sh opendev https://review.opendev.org/c/openstack/horizon/+/964897
#   ./fetch-review.sh --with-master opendev https://review.opendev.org/c/openstack/horizon/+/964897
#   ./fetch-review.sh --rebase --experiment github https://github.com/org/repo/pull/402
#   ./fetch-review.sh --all opendev https://review.opendev.org/c/openstack/horizon/+/964897

set -e

# Remember where the script was called from (for cloning repos)
WORK_DIR="$(pwd)"

# Remember where the script is located (for finding results directory)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Options
WITH_MASTER=false
DO_REBASE=false
WITH_EXPERIMENT=false
WITH_ASSESSMENT=false

# Parse options
while [[ $# -gt 0 ]]; do
    case "$1" in
        --with-master)
            WITH_MASTER=true
            shift
            ;;
        --rebase)
            DO_REBASE=true
            WITH_MASTER=true  # Rebase requires master
            shift
            ;;
        --experiment)
            WITH_EXPERIMENT=true
            shift
            ;;
        --with-assessment)
            WITH_ASSESSMENT=true
            shift
            ;;
        --all)
            WITH_MASTER=true
            WITH_EXPERIMENT=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [options] <type> <url>"
            echo ""
            echo "Options:"
            echo "  --with-master      Also clone clean master branch for comparison"
            echo "  --rebase           Rebase the review on latest master (implies --with-master)"
            echo "  --experiment       Create an experiment directory for testing"
            echo "  --with-assessment  Create review assessment document (review_XXXXX.md)"
            echo "  --all              Equivalent to --with-master --experiment"
            echo ""
            echo "Types:"
            echo "  opendev - OpenDev/Gerrit review"
            echo "  github  - GitHub Pull Request"
            echo "  gitlab  - GitLab Merge Request"
            echo ""
            echo "Examples:"
            echo "  $0 opendev https://review.opendev.org/c/openstack/horizon/+/964897"
            echo "  $0 --with-master --with-assessment opendev https://review.opendev.org/.../964897"
            echo "  $0 --rebase github https://github.com/org/repo/pull/402"
            echo "  $0 --all opendev https://review.opendev.org/c/openstack/horizon/+/964897"
            exit 0
            ;;
        -*)
            echo -e "${RED}Error: Unknown option '$1'${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
        *)
            break
            ;;
    esac
done

if [ $# -ne 2 ]; then
    echo "Usage: $0 [options] <type> <url>"
    echo "Use --help for more information"
    exit 1
fi

TYPE="$1"
URL="$2"

prompt_overwrite() {
    local dir="$1"
    if [ -d "$dir" ]; then
        echo -e "${YELLOW}Directory $dir already exists!${NC}"
        read -p "Remove and re-clone? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$dir"
            return 0
        else
            return 1
        fi
    fi
    return 0
}

create_review_assessment() {
    local type="$1"
    local number="$2"
    local url="$3"
    local project="$4"
    local dir_name="$5"
    
    # Create results directory at repository root (mymcp/results/)
    local results_dir="$SCRIPT_DIR/../../results"
    mkdir -p "$results_dir"
    
    local assessment_file="$results_dir/review_${number}.md"
    local template_file="$results_dir/review_template.md"
    
    echo -e "${BLUE}Creating review assessment document: results/review_${number}.md${NC}"
    
    # Get basic info from the review (using WORK_DIR as base)
    cd "$WORK_DIR/$dir_name"
    local commit_subject=$(git log -1 --format="%s")
    local commit_author=$(git log -1 --format="%an <%ae>")
    local commit_date=$(git log -1 --format="%ad" --date=short)
    local files_changed=$(git show --name-only --format="" HEAD | wc -l)
    local insertions=$(git show --shortstat HEAD | grep -oP '\d+(?= insertion)')
    local deletions=$(git show --shortstat HEAD | grep -oP '\d+(?= deletion)')
    cd "$WORK_DIR"
    
    # Check if template exists, use it as base
    if [ -f "$template_file" ]; then
        cp "$template_file" "$assessment_file"
        echo -e "${GREEN}✓ Copied from results/review_template.md${NC}"
        echo -e "${YELLOW}✓ Ready for Cursor to complete full analysis${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠ Template not found at results/review_template.md, creating basic template${NC}"
    fi
    
    # Fallback: Create basic assessment template if review_template.md doesn't exist
    cat > "$assessment_file" << EOF
# Review Assessment: ${number} - ${commit_subject}

## Review Information

**Review URL:** ${url}
**Review Number:** ${number}
**Project:** ${project}
**Author:** ${commit_author}
**Status:** NEW / MERGED / ABANDONED (check in Gerrit)
**Branch:** master
**Created:** ${commit_date}
**Updated:** ${commit_date}
**Assessment Date:** $(date +%Y-%m-%d)

## Original Inquiry

**Query to Agent:**
\`\`\`
@opendev-reviewer-agent Analyze the review at ${url}
\`\`\`

## Executive Summary

**Purpose:** [What does this change do?]

**Scope:** 
- Files changed: ${files_changed}
- Lines added: +${insertions:-0}
- Lines deleted: -${deletions:-0}

**Recommendation:** ⏳ PENDING ANALYSIS

[Use Cursor to analyze the changes and provide initial assessment]

**Instructions:**
1. Review the changes in \`${dir_name}/\`
2. Run: \`cd ${dir_name} && git show HEAD\` to see the diff
3. Ask Cursor: "Please analyze this review and fill in the assessment sections"
4. Cursor will populate the remaining sections based on the code changes

## Change Overview

### What Changed

[To be populated by Cursor after analyzing git show HEAD]

### Why This Change

[To be populated - check commit message and code context]

### Impact

**Breaking Changes:** [YES / NO - to be determined]
**API Changes:** [YES / NO - to be determined]
**Configuration Changes:** [YES / NO - to be determined]
**Database Changes:** [YES / NO - to be determined]

## Code Quality Assessment

[To be populated by Cursor]

### ✅ Strengths

[Cursor will identify strengths after analysis]

### ⚠️ Concerns

[Cursor will identify concerns after analysis]

### 📋 Suggestions

[Cursor will provide suggestions after analysis]

## Technical Analysis

### Files Modified

[To be populated with list from: git show --name-status HEAD]

### Code Review

[To be populated by Cursor after examining the changes]

## Review Checklist

[To be completed during analysis]

### Code Quality
- [ ] Code follows project style guidelines
- [ ] No obvious bugs or logic errors
- [ ] Error handling is appropriate
- [ ] Code is readable and maintainable

### Testing
- [ ] Unit tests included/updated
- [ ] Integration tests considered
- [ ] Manual testing performed
- [ ] Edge cases covered

### Documentation
- [ ] Code comments are clear
- [ ] Docstrings updated
- [ ] README updated (if needed)
- [ ] Release notes added (if needed)

### Security
- [ ] No security vulnerabilities introduced
- [ ] Input validation appropriate
- [ ] Authentication/authorization correct
- [ ] Sensitive data handled properly

### Performance
- [ ] No obvious performance issues
- [ ] Database queries optimized
- [ ] Resource usage reasonable
- [ ] Scalability considered

### Backward Compatibility
- [ ] API compatibility maintained
- [ ] Database migrations safe
- [ ] Configuration backward compatible
- [ ] Deprecation warnings added (if needed)

## Testing Verification

### How to Test

\`\`\`bash
# Commands to test this change
cd ${dir_name}

# Run linting
tox -e pep8

# Run tests
tox -e py3

# View the changes
git show HEAD
\`\`\`

### Test Results

**Linting:** [To be tested]
**Unit Tests:** [To be tested]
**Integration Tests:** [To be tested]

## Comparison with Master

[To be populated if --with-master was used]

\`\`\`bash
# Compare with master
diff -u ${project}-master/[file] ${dir_name}/[file]
\`\`\`

## Related Work

### Related Reviews
[To be populated - search for related changes]

### Related Issues
[To be populated - check commit message for bug/feature references]

## Questions for Author

[To be populated after initial analysis]

## Recommendations

[To be populated after analysis]

### Before Merge

**Must Address:**
[To be populated]

**Should Consider:**
[To be populated]

## Verification Commands

\`\`\`bash
# Fetch the review (already done)
cd ${dir_name}

# View changes
git show HEAD

# View commit message
git log -1

# List changed files
git show --name-status HEAD

# Run linting
tox -e pep8

# Run tests  
tox -e py3
\`\`\`

## Decision

**Recommendation:** ⏳ PENDING ANALYSIS

**Next Steps:**
1. Ask Cursor to analyze the changes: "Please review ${dir_name} and fill in this assessment"
2. Run tests and linting
3. Update recommendation based on findings

---

**Status:** 🔄 In Progress
**Reviewer:** [Your Name]
**Assessment Date:** $(date +%Y-%m-%d)
**Last Updated:** $(date +%Y-%m-%d)
EOF
    
    echo -e "${GREEN}✓ Review assessment created: results/review_${number}.md${NC}"
    echo -e "${YELLOW}  Next: Ask Cursor to analyze and fill in the assessment${NC}"
    echo -e "${YELLOW}  Try: 'Please analyze review ${number} and complete results/review_${number}.md'${NC}"
}

case "$TYPE" in
    opendev)
        # Parse OpenDev URL: https://review.opendev.org/c/openstack/horizon/+/964897
        if [[ ! "$URL" =~ ^https://review\.opendev\.org/c/([^/]+)/([^/]+)/\+/([0-9]+) ]]; then
            echo -e "${RED}Error: Invalid OpenDev URL format${NC}"
            echo "Expected: https://review.opendev.org/c/<org>/<project>/+/<change-number>"
            exit 1
        fi
        
        ORG="${BASH_REMATCH[1]}"
        PROJECT="${BASH_REMATCH[2]}"
        CHANGE="${BASH_REMATCH[3]}"
        LAST_TWO="${CHANGE: -2}"
        DIR_NAME="${PROJECT}-${CHANGE}"
        MASTER_DIR="${PROJECT}-master"
        EXPERIMENT_DIR="${PROJECT}-${CHANGE}-experiment"
        CLONE_URL="https://github.com/${ORG}/${PROJECT}"
        REVIEW_URL="https://review.opendev.org/${ORG}/${PROJECT}"
        BRANCH="master"
        
        echo -e "${BLUE}Fetching OpenDev review ${CHANGE} for ${ORG}/${PROJECT}${NC}"
        
        # Change to the working directory where user ran the script
        cd "$WORK_DIR"
        
        # Clone the review
        if ! prompt_overwrite "$DIR_NAME"; then
            exit 1
        fi
        
        echo -e "${GREEN}[1/3] Cloning review repository...${NC}"
        git clone "$CLONE_URL" "$DIR_NAME"
        cd "$DIR_NAME"
        
        echo -e "${GREEN}[2/3] Fetching review patchset...${NC}"
        git fetch "$REVIEW_URL" "refs/changes/${LAST_TWO}/${CHANGE}/1"
        
        if [ "$DO_REBASE" = true ]; then
            echo -e "${GREEN}[3/3] Rebasing on latest master...${NC}"
            git checkout -b "ws-review-${CHANGE}" FETCH_HEAD
            git fetch origin master
            git rebase origin/master
            if [ $? -ne 0 ]; then
                echo -e "${RED}⚠ Rebase had conflicts. You are in the review directory.${NC}"
                echo -e "${YELLOW}Fix conflicts, then run: git rebase --continue${NC}"
            else
                echo -e "${GREEN}✓ Successfully rebased on master${NC}"
            fi
        else
            echo -e "${GREEN}[3/3] Checking out review and creating branch ws-review-${CHANGE}...${NC}"
            git checkout -b "ws-review-${CHANGE}" FETCH_HEAD
        fi
        
        cd "$WORK_DIR"
        
        # Clone master branch if requested
        if [ "$WITH_MASTER" = true ]; then
            if [ -d "$MASTER_DIR" ]; then
                echo -e "${BLUE}Using existing ${MASTER_DIR}/ for comparison${NC}"
            else
                echo -e "${BLUE}Cloning clean master branch for comparison...${NC}"
                git clone --branch "$BRANCH" --single-branch "$CLONE_URL" "$MASTER_DIR"
                echo -e "${GREEN}✓ Master branch cloned to: ${MASTER_DIR}${NC}"
            fi
        fi
        
        # Create experiment directory if requested
        if [ "$WITH_EXPERIMENT" = true ]; then
            if ! prompt_overwrite "$EXPERIMENT_DIR"; then
                echo -e "${YELLOW}Skipping experiment directory${NC}"
            else
                echo -e "${BLUE}Creating experiment directory...${NC}"
                cp -r "$DIR_NAME" "$EXPERIMENT_DIR"
                cd "$EXPERIMENT_DIR"
                # Switch from ws-review-* to ws-experiment-*
                git checkout -b "ws-experiment-${CHANGE}"
                cd "$WORK_DIR"
                echo -e "${GREEN}✓ Experiment directory created: ${EXPERIMENT_DIR}${NC}"
                echo -e "${YELLOW}  You can make changes here without affecting the review${NC}"
            fi
        fi
        
        # Create review assessment if requested
        if [ "$WITH_ASSESSMENT" = true ]; then
            create_review_assessment "opendev" "$CHANGE" "$URL" "$PROJECT" "$DIR_NAME"
            echo ""
        fi
        
        echo ""
        echo -e "${GREEN}✓ Successfully fetched review into: ${DIR_NAME}${NC}"
        echo -e "${BLUE}Directory structure:${NC}"
        echo -e "  ${DIR_NAME}/           - The review patchset"
        [ "$WITH_MASTER" = true ] && echo -e "  ${MASTER_DIR}/           - Clean master branch (for comparison)"
        [ "$WITH_EXPERIMENT" = true ] && echo -e "  ${EXPERIMENT_DIR}/ - Experiment area (for testing changes)"
        [ "$WITH_ASSESSMENT" = true ] && echo -e "  results/review_${CHANGE}.md  - Review assessment document"
        echo ""
        echo -e "${BLUE}Next steps:${NC}"
        echo -e "  cd ${DIR_NAME}                                     # Examine the review"
        echo -e "  git show HEAD                                         # View the changes"
        echo -e "  tox -e pep8                                           # Run linting"
        echo -e "  local_settings.py                                     # Update script to support local Horizon deployment"
        echo -e "  tox -e runserver -- 0.0.0.0:8080                      # Run tox"
        echo -e "  http://localhost:8080/auth/login                      # Connect Horizon to your local devstack"
        [ "$WITH_MASTER" = true ] && echo -e "  diff -ur ${MASTER_DIR}/<file> ${DIR_NAME}/<file>  # Compare with master"
        [ "$WITH_EXPERIMENT" = true ] && echo -e "  cd ${EXPERIMENT_DIR}                              # Make experimental changes"
        
        if [ "$WITH_ASSESSMENT" = true ]; then
            echo ""
            echo -e "${GREEN}📋 Assessment template ready: results/review_${CHANGE}.md${NC}"
            echo -e "${YELLOW}   → Ask Cursor to complete the analysis: 'Please analyze review ${CHANGE}'${NC}"
        fi
        ;;
        
    github)
        # Parse GitHub URL: https://github.com/openstack-k8s-operators/horizon-operator/pull/402
        if [[ ! "$URL" =~ ^https://github\.com/([^/]+)/([^/]+)/pull/([0-9]+) ]]; then
            echo -e "${RED}Error: Invalid GitHub URL format${NC}"
            echo "Expected: https://github.com/<org>/<repo>/pull/<number>"
            exit 1
        fi
        
        ORG="${BASH_REMATCH[1]}"
        REPO="${BASH_REMATCH[2]}"
        PR="${BASH_REMATCH[3]}"
        DIR_NAME="${REPO}-pr-${PR}"
        MASTER_DIR="${REPO}-master"
        EXPERIMENT_DIR="${REPO}-pr-${PR}-experiment"
        CLONE_URL="https://github.com/${ORG}/${REPO}"
        BRANCH="main"
        
        echo -e "${BLUE}Fetching GitHub PR ${PR} for ${ORG}/${REPO}${NC}"
        
        # Change to the working directory where user ran the script
        cd "$WORK_DIR"
        
        # Clone the PR
        if ! prompt_overwrite "$DIR_NAME"; then
            exit 1
        fi
        
        echo -e "${GREEN}[1/3] Cloning repository...${NC}"
        git clone "$CLONE_URL" "$DIR_NAME"
        cd "$DIR_NAME"
        
        # Try 'main' first, fall back to 'master'
        if ! git show-ref --verify --quiet refs/remotes/origin/main; then
            BRANCH="master"
        fi
        
        echo -e "${GREEN}[2/3] Fetching PR branch...${NC}"
        git fetch origin "pull/${PR}/head:pr-${PR}"
        
        if [ "$DO_REBASE" = true ]; then
            echo -e "${GREEN}[3/3] Rebasing on latest ${BRANCH}...${NC}"
            git checkout -b "ws-pr-${PR}" "pr-${PR}"
            git fetch origin "$BRANCH"
            git rebase "origin/${BRANCH}"
            if [ $? -ne 0 ]; then
                echo -e "${RED}⚠ Rebase had conflicts. You are in the PR directory.${NC}"
                echo -e "${YELLOW}Fix conflicts, then run: git rebase --continue${NC}"
            else
                echo -e "${GREEN}✓ Successfully rebased on ${BRANCH}${NC}"
            fi
        else
            echo -e "${GREEN}[3/3] Checking out PR and creating branch ws-pr-${PR}...${NC}"
            git checkout -b "ws-pr-${PR}" "pr-${PR}"
        fi
        
        cd "$WORK_DIR"
        
        # Clone master/main branch if requested
        if [ "$WITH_MASTER" = true ]; then
            if [ -d "$MASTER_DIR" ]; then
                echo -e "${BLUE}Using existing ${MASTER_DIR}/ for comparison${NC}"
            else
                echo -e "${BLUE}Cloning clean ${BRANCH} branch for comparison...${NC}"
                git clone --branch "$BRANCH" --single-branch "$CLONE_URL" "$MASTER_DIR"
                echo -e "${GREEN}✓ ${BRANCH} branch cloned to: ${MASTER_DIR}${NC}"
            fi
        fi
        
        # Create experiment directory if requested
        if [ "$WITH_EXPERIMENT" = true ]; then
            if ! prompt_overwrite "$EXPERIMENT_DIR"; then
                echo -e "${YELLOW}Skipping experiment directory${NC}"
            else
                echo -e "${BLUE}Creating experiment directory...${NC}"
                cp -r "$DIR_NAME" "$EXPERIMENT_DIR"
                cd "$EXPERIMENT_DIR"
                # Switch from ws-pr-* to ws-experiment-pr-*
                git checkout -b "ws-experiment-pr-${PR}"
                cd "$WORK_DIR"
                echo -e "${GREEN}✓ Experiment directory created: ${EXPERIMENT_DIR}${NC}"
            fi
        fi
        
        # Create review assessment if requested
        if [ "$WITH_ASSESSMENT" = true ]; then
            create_review_assessment "github" "$PR" "$URL" "$REPO" "$DIR_NAME"
            echo ""
        fi
        
        echo ""
        echo -e "${GREEN}✓ Successfully fetched PR into: ${DIR_NAME}${NC}"
        echo -e "${BLUE}Directory structure:${NC}"
        echo -e "  ${DIR_NAME}/           - The PR"
        [ "$WITH_MASTER" = true ] && echo -e "  ${MASTER_DIR}/           - Clean ${BRANCH} branch"
        [ "$WITH_EXPERIMENT" = true ] && echo -e "  ${EXPERIMENT_DIR}/ - Experiment area"
        [ "$WITH_ASSESSMENT" = true ] && echo -e "  results/review_pr_${PR}.md  - Review assessment document"
        echo ""
        echo -e "${BLUE}Next steps:${NC}"
        echo -e "  cd ${DIR_NAME}                                     # Examine the PR"
        echo -e "  git show HEAD                                         # View the changes"
        [ "$WITH_MASTER" = true ] && echo -e "  diff -ur ${MASTER_DIR}/<file> ${DIR_NAME}/<file>  # Compare with master"
        [ "$WITH_EXPERIMENT" = true ] && echo -e "  cd ${EXPERIMENT_DIR}                              # Make experimental changes"
        
        if [ "$WITH_ASSESSMENT" = true ]; then
            echo ""
            echo -e "${GREEN}📋 Assessment template ready: results/review_pr_${PR}.md${NC}"
            echo -e "${YELLOW}   → Ask Cursor to complete the analysis: 'Please analyze PR ${PR}'${NC}"
        fi
        ;;
        
    gitlab)
        # Parse GitLab URL: https://gitlab.cee.redhat.com/eng/openstack/python-django/-/merge_requests/123
        if [[ ! "$URL" =~ ^https://([^/]+)/(.+)/-/merge_requests/([0-9]+) ]]; then
            echo -e "${RED}Error: Invalid GitLab URL format${NC}"
            echo "Expected: https://<gitlab-host>/<group>/<project>/-/merge_requests/<number>"
            exit 1
        fi
        
        GITLAB_HOST="${BASH_REMATCH[1]}"
        PROJECT_PATH="${BASH_REMATCH[2]}"
        MR="${BASH_REMATCH[3]}"
        PROJECT_NAME=$(basename "$PROJECT_PATH")
        DIR_NAME="${PROJECT_NAME}-mr-${MR}"
        MASTER_DIR="${PROJECT_NAME}-master"
        EXPERIMENT_DIR="${PROJECT_NAME}-mr-${MR}-experiment"
        CLONE_URL="https://${GITLAB_HOST}/${PROJECT_PATH}.git"
        BRANCH="main"
        
        echo -e "${BLUE}Fetching GitLab MR ${MR} for ${PROJECT_PATH}${NC}"
        
        # Change to the working directory where user ran the script
        cd "$WORK_DIR"
        
        # Clone the MR
        if ! prompt_overwrite "$DIR_NAME"; then
            exit 1
        fi
        
        echo -e "${GREEN}[1/3] Cloning repository...${NC}"
        git clone "$CLONE_URL" "$DIR_NAME"
        cd "$DIR_NAME"
        
        # Try 'main' first, fall back to 'master'
        if ! git show-ref --verify --quiet refs/remotes/origin/main; then
            BRANCH="master"
        fi
        
        echo -e "${GREEN}[2/3] Fetching MR branch...${NC}"
        git fetch origin "merge-requests/${MR}/head:mr-${MR}"
        
        if [ "$DO_REBASE" = true ]; then
            echo -e "${GREEN}[3/3] Rebasing on latest ${BRANCH}...${NC}"
            git checkout -b "ws-mr-${MR}" "mr-${MR}"
            git fetch origin "$BRANCH"
            git rebase "origin/${BRANCH}"
            if [ $? -ne 0 ]; then
                echo -e "${RED}⚠ Rebase had conflicts. You are in the MR directory.${NC}"
                echo -e "${YELLOW}Fix conflicts, then run: git rebase --continue${NC}"
            else
                echo -e "${GREEN}✓ Successfully rebased on ${BRANCH}${NC}"
            fi
        else
            echo -e "${GREEN}[3/3] Checking out MR and creating branch ws-mr-${MR}...${NC}"
            git checkout -b "ws-mr-${MR}" "mr-${MR}"
        fi
        
        cd "$WORK_DIR"
        
        # Clone master/main branch if requested
        if [ "$WITH_MASTER" = true ]; then
            if [ -d "$MASTER_DIR" ]; then
                echo -e "${BLUE}Using existing ${MASTER_DIR}/ for comparison${NC}"
            else
                echo -e "${BLUE}Cloning clean ${BRANCH} branch for comparison...${NC}"
                git clone --branch "$BRANCH" --single-branch "$CLONE_URL" "$MASTER_DIR"
                echo -e "${GREEN}✓ ${BRANCH} branch cloned to: ${MASTER_DIR}${NC}"
            fi
        fi
        
        # Create experiment directory if requested
        if [ "$WITH_EXPERIMENT" = true ]; then
            if ! prompt_overwrite "$EXPERIMENT_DIR"; then
                echo -e "${YELLOW}Skipping experiment directory${NC}"
            else
                echo -e "${BLUE}Creating experiment directory...${NC}"
                cp -r "$DIR_NAME" "$EXPERIMENT_DIR"
                cd "$EXPERIMENT_DIR"
                # Switch from ws-mr-* to ws-experiment-mr-*
                git checkout -b "ws-experiment-mr-${MR}"
                cd "$WORK_DIR"
                echo -e "${GREEN}✓ Experiment directory created: ${EXPERIMENT_DIR}${NC}"
            fi
        fi
        
        # Create review assessment if requested
        if [ "$WITH_ASSESSMENT" = true ]; then
            create_review_assessment "gitlab" "$MR" "$URL" "$PROJECT_NAME" "$DIR_NAME"
            echo ""
        fi
        
        echo ""
        echo -e "${GREEN}✓ Successfully fetched MR into: ${DIR_NAME}${NC}"
        echo -e "${BLUE}Directory structure:${NC}"
        echo -e "  ${DIR_NAME}/           - The MR"
        [ "$WITH_MASTER" = true ] && echo -e "  ${MASTER_DIR}/           - Clean ${BRANCH} branch"
        [ "$WITH_EXPERIMENT" = true ] && echo -e "  ${EXPERIMENT_DIR}/ - Experiment area"
        [ "$WITH_ASSESSMENT" = true ] && echo -e "  results/review_mr_${MR}.md  - Review assessment document"
        echo ""
        echo -e "${BLUE}Next steps:${NC}"
        echo -e "  cd ${DIR_NAME}                                     # Examine the MR"
        echo -e "  git show HEAD                                         # View the changes"
        [ "$WITH_MASTER" = true ] && echo -e "  diff -ur ${MASTER_DIR}/<file> ${DIR_NAME}/<file>  # Compare with master"
        [ "$WITH_EXPERIMENT" = true ] && echo -e "  cd ${EXPERIMENT_DIR}                              # Make experimental changes"
        
        if [ "$WITH_ASSESSMENT" = true ]; then
            echo ""
            echo -e "${GREEN}📋 Assessment template ready: results/review_mr_${MR}.md${NC}"
            echo -e "${YELLOW}   → Ask Cursor to complete the analysis: 'Please analyze MR ${MR}'${NC}"
        fi
        ;;
        
    *)
        echo -e "${RED}Error: Unknown type '$TYPE'${NC}"
        echo "Valid types: opendev, github, gitlab"
        echo "Use --help for more information"
        exit 1
        ;;
esac
