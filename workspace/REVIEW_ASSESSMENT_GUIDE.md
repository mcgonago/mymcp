# Review Assessment Workflow Guide

## Overview

The workspace now supports automated creation of review assessment documents. When you fetch a review using `--with-assessment`, it automatically creates a `review_XXXXX.md` file pre-populated with metadata and ready for Cursor to complete.

---

## Quick Start

```bash
# Fetch review with assessment document
cd /home/omcgonag/Work/mymcp/workspace
./fetch-review.sh --with-assessment opendev https://review.opendev.org/c/openstack/horizon/+/965216

# Ask Cursor to analyze and complete the assessment
# In Cursor prompt:
"Please analyze review 965216 in horizon-965216 and complete results/review_965216.md"
```

---

## Workflow

###Step 1: Fetch Review with Assessment

```bash
./fetch-review.sh --with-assessment opendev [review-url]
```

**What happens:**
1. Script fetches the review code
2. Extracts metadata (author, files changed, commit message)
3. Creates `review_XXXXX.md` from template
4. Pre-fills basic information
5. Marks sections with `[To be populated by Cursor]`

### Step 2: Review is Ready

The script outputs:
```
✓ Review assessment created: results/review_965216.md
  Next: Ask Cursor to analyze and fill in the assessment
  Try: 'Please analyze review 965216 and complete results/review_965216.md'
```

### Step 3: Ask Cursor to Complete Assessment

**In Cursor prompt:**
```
Please analyze review 965216 and complete results/review_965216.md
```

**Cursor will:**
1. Read the code in `horizon-965216/`
2. Run `git show HEAD` to see changes
3. Analyze the modifications
4. Fill in all assessment sections:
   - Executive summary
   - Code quality assessment
   - Technical analysis
   - Test recommendations
   - Security review
   - Performance considerations
   - Final recommendation

### Step 4: Review and Refine

Review Cursor's assessment and:
- Add your own observations
- Run suggested tests
- Update recommendations
- Post comments to Gerrit

---

## Assessment Document Structure

The generated `review_XXXXX.md` includes:

### Pre-filled Sections (Auto)
- ✅ Review number and URL
- ✅ Author and date
- ✅ Files changed count
- ✅ Lines added/deleted
- ✅ Commit subject

### To Be Filled (Cursor)
- [ ] Executive summary
- [ ] What changed (detailed)
- [ ] Code quality assessment
- [ ] Technical analysis
- [ ] Review checklist
- [ ] Testing verification
- [ ] Recommendations
- [ ] Final decision

---

## Examples

### Example 1: Simple Bug Fix

```bash
./fetch-review.sh --with-assessment opendev https://review.opendev.org/c/openstack/horizon/+/964897

# Cursor analyzes and finds:
# - Simple 2-line change
# - Removes invalid parameter
# - Fixes linter error
# - Recommendation: +2 Approve
```

### Example 2: Feature Addition with Master Comparison

```bash
./fetch-review.sh --with-assessment --with-master opendev https://review.opendev.org/c/openstack/horizon/+/965216

# Cursor analyzes and compares with master:
# - Multiple files changed
# - New feature implementation
# - Configuration updates needed
# - Recommendation: +1 (with suggestions)
```

### Example 3: Comprehensive Review

```bash
./fetch-review.sh --with-assessment --all opendev https://review.opendev.org/c/openstack/horizon/+/960204

# Creates:
# - horizon-960204/ (review)
# - horizon-master/ (for comparison)
# - horizon-960204-experiment/ (for testing)
# - review_960204.md (assessment)

# Cursor performs comprehensive analysis with all context
```

---

## Advanced Usage

### Combine with All Options

```bash
./fetch-review.sh --with-assessment --with-master --experiment opendev [url]
```

This creates:
- Review code
- Master branch for comparison
- Experiment directory for testing
- Assessment document

**Best for:** Complex reviews requiring thorough analysis

### Multiple Reviews

```bash
# Review multiple related changes
./fetch-review.sh --with-assessment opendev [url-1]
./fetch-review.sh --with-assessment opendev [url-2]
./fetch-review.sh --with-assessment opendev [url-3]

# Cross-reference in assessments
```

### Batch Processing

```bash
# Create a script to process multiple reviews
for review in 965216 965217 965218; do
  ./fetch-review.sh --with-assessment opendev \
    https://review.opendev.org/c/openstack/horizon/+/$review
  
  # Ask Cursor to analyze each
  echo "Please analyze review $review and complete review_${review}.md"
done
```

---

## Assessment Template Sections

### Review Information
- Metadata about the review
- URLs and identifiers
- Author and dates

### Executive Summary
- **Purpose:** What does this change do?
- **Scope:** Files and lines changed
- **Recommendation:** Approve/needs work/reject

### Change Overview
- **What Changed:** Detailed description
- **Why This Change:** Rationale
- **Impact:** Breaking changes, API changes, etc.

### Code Quality Assessment
- **Strengths:** What's good about the code
- **Concerns:** Potential issues
- **Suggestions:** Improvements

### Technical Analysis
- **Files Modified:** List with analysis
- **Code Review:** Detailed examination
- **Issues:** Specific problems to address

### Review Checklist
Comprehensive checklist covering:
- Code quality
- Testing
- Documentation
- Security
- Performance
- Backward compatibility

### Testing Verification
- **How to Test:** Commands and procedures
- **Test Results:** Pass/fail status
- **Notes:** Any issues found

### Recommendations
- **Must Address:** Critical issues
- **Should Consider:** Important improvements
- **Nice to Have:** Optional enhancements

### Decision
- **Recommendation:** +2/+1/0/-1 vote
- **Reasoning:** Why this recommendation
- **Conditions:** Any requirements for approval

---

## Tips for Effective Reviews

### 1. Use Descriptive Prompts

**Good:**
```
Please analyze review 965216 and complete the assessment in review_965216.md.
Focus on security implications and backward compatibility.
```

**Not as good:**
```
Review this code.
```

### 2. Iterate on the Analysis

```
# First pass: Basic analysis
"Please analyze review 965216"

# Second pass: Specific focus
"Now examine the security aspects of review 965216"

# Third pass: Performance
"Check for performance implications in review 965216"
```

### 3. Reference Related Reviews

```
Please analyze review 965216 and compare it with the changes in review 960204
which we previously analyzed in review_960204.md
```

### 4. Ask for Specific Checks

```
Please analyze review 965216 and specifically check:
1. Are there any database migration issues?
2. Does this maintain backward compatibility?
3. Are the tests comprehensive?
```

---

## Integration with Analysis Directory

Review assessments in `workspace/` are temporary. For permanent documentation:

```bash
# After completing assessment
cp workspace/review_965216.md analysis/review_965216.md

# Add to git for permanent record
cd /home/omcgonag/Work/mymcp
git add analysis/review_965216.md
git commit -m "Add assessment for review 965216"
```

**When to promote to analysis/:**
- Significant architectural changes
- Security-related reviews
- Performance optimizations
- Breaking changes
- Reference material for team

---

## Troubleshooting

### Assessment File Not Created

**Problem:** `--with-assessment` doesn't create file

**Solution:** Check script ran successfully:
```bash
./fetch-review.sh --with-assessment opendev [url] 2>&1 | grep "assessment"
```

### Cursor Can't Find Assessment

**Problem:** Cursor says it can't find the review file

**Solution:** Use absolute path:
```
Please analyze /home/omcgonag/Work/mymcp/workspace/review_965216.md
```

### Incomplete Analysis

**Problem:** Cursor only fills in some sections

**Solution:** Be more specific:
```
Please complete ALL sections in review_965216.md, including:
- Technical Analysis
- Review Checklist
- Testing Verification
- Final Recommendation
```

---

## Files and Templates

### Template Files
- `review_template.md` - Full template with all sections
- Used automatically by `--with-assessment`

### Generated Files
- `review_XXXXX.md` - Generated assessment document
- Located in `workspace/` directory
- Git-ignored (temporary)

### Cleanup

```bash
# Remove old reviews and assessments
cd workspace
rm -rf horizon-* review_*.md

# Keep only recent assessments
find . -name "review_*.md" -mtime +30 -delete
```

---

## Quick Reference

```bash
# Basic assessment
./fetch-review.sh --with-assessment opendev [url]

# With master comparison
./fetch-review.sh --with-assessment --with-master opendev [url]

# Full setup
./fetch-review.sh --with-assessment --all opendev [url]

# Ask Cursor to analyze
"Please analyze review [NUMBER] and complete review_[NUMBER].md"

# Specific focus
"Please analyze review [NUMBER] focusing on [ASPECT]"

# Promote to permanent analysis
cp workspace/review_[NUMBER].md analysis/
```

---

## Benefits

✅ **Automated Setup** - No manual template copying
✅ **Pre-filled Metadata** - Author, files, dates auto-populated
✅ **Structured Analysis** - Consistent review format
✅ **Comprehensive Checklists** - Nothing gets missed
✅ **Cursor-Ready** - Optimized for Cursor to complete
✅ **Reproducible** - Same process every time
✅ **Trackable** - Can be committed to git

---

**The review assessment workflow makes code review systematic, thorough, and efficient!**

