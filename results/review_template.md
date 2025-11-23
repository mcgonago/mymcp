# Review Assessment: [Review Number] - [Title]

## Patchset Information

**Patchset Number:** [X] (analyzing patchset [X] of this review)  
**Previous Patchsets:** [Links to other patchset assessments, if any]

## Review Information

**Review URL:** [URL]  
**Review Number:** [Number]  
**Project:** [Project Name]  
**Author:** [Author Name] <email>  
**Status:** [NEW/MERGED/ABANDONED]  
**Branch:** [master/stable/...]  
**Created:** [Date]  
**Updated:** [Date]  
**Assessment Date:** [Date]  

## Original Inquiry

**Query to Agent:**
```
@opendev-reviewer-agent Analyze the review at [URL]
```

## Executive Summary

**Purpose:** [What does this change do?]

**Scope:** 
- Files changed: [X]
- Lines added: [+X]
- Lines deleted: [-X]

**Recommendation:** ✅ APPROVE / ⚠️ NEEDS WORK / ❌ REJECT

[2-3 sentences summarizing the change and your recommendation]

## Decision

**Recommendation:** ✅ +2 APPROVE / ⚠️ +1 LOOKS GOOD (minor comments) / 🔄 0 NEEDS WORK / ❌ -1 DO NOT MERGE

**Reasoning:**
[Explain your recommendation]

**Conditions:**
[Any conditions for approval, e.g., "Approve after addressing [X]"]

## 📋 Assessment Summary

**Review:** xxxxx
**Recommendation:** ⚠️ xxxx
**Assessment File:** `xxxxxx.md` (xxxx lines)

---

## 🔍 Key Findings

### Why This Matters

## 👥 Reviewer Comments Analysis

**Ivan Anfimov:** "LGTM, trivial"  
→ ⚠️ **Premature approval** - CSS error was missed

**Owen McGonagle:** Recommended `border-top: 1px solid #ddd;`  
→ ✅ **Correct catch!** - Identified the CSS syntax issue

---

## 📝 What Needs to Happen

---

## Change Overview

### What Changed

[Describe what files were modified and what the changes accomplish]

### Why This Change

[Context for why this change was needed - bug fix, feature, cleanup, etc.]

### Impact

**Breaking Changes:** YES / NO  
**API Changes:** YES / NO  
**Configuration Changes:** YES / NO  
**Database Changes:** YES / NO  

## Code Quality Assessment

### ✅ Strengths

1. [Strength 1]
2. [Strength 2]
3. [Strength 3]

### ⚠️ Concerns

1. [Concern 1]
2. [Concern 2]
3. [Concern 3]

### 📋 Suggestions

1. [Suggestion 1]
2. [Suggestion 2]

## Technical Analysis

### Files Modified

| File | Changes | Notes |
|------|---------|-------|
| `path/to/file1.py` | +X/-Y | [What changed] |
| `path/to/file2.py` | +X/-Y | [What changed] |

### Code Review

#### File: [filename]

**Changes:**
```python
# Show key changes or explain them
```

**Analysis:**
[Your analysis of this change]

**Issues:**
- [ ] Issue 1
- [ ] Issue 2

## Review Checklist

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

```bash
# Commands to test this change
cd workspace/[project]-[review-number]

# Run linting
tox -e pep8

# Run tests
tox -e py3

# Manual testing steps
[specific test commands]
```

### Test Results

**Linting:** ✅ PASS / ❌ FAIL  
**Unit Tests:** ✅ PASS / ❌ FAIL  
**Integration Tests:** ✅ PASS / ❌ FAIL  

**Notes:**
[Any test failures or concerns]

## Comparison with Master

### Diff Summary

```bash
# Commands run
cd workspace
diff -u [project]-master/[file] [project]-[review]/[file]
```

**Key Differences:**
1. [Difference 1]
2. [Difference 2]

### Conflicts Check

**Files modified since original base:** [X files]

**Potential conflicts:** YES / NO

[Details if any]

## Related Work

### Related Reviews
- Review [XXXXXX](link) - [Description]
- Review [YYYYYY](link) - [Description]

### Related Issues
- Bug [#XXXX](link) - [Description]
- Feature [#YYYY](link) - [Description]

### Dependencies
- Depends on: [Review/PR numbers]
- Required by: [Review/PR numbers]

## Questions for Author

1. [Question 1]
2. [Question 2]
3. [Question 3]

## Recommendations

### Before Merge

**Must Address:**
- [ ] Critical issue 1
- [ ] Critical issue 2

**Should Consider:**
- [ ] Improvement suggestion 1
- [ ] Improvement suggestion 2

**Nice to Have:**
- [ ] Enhancement 1
- [ ] Enhancement 2

### Comments to Post

**Comment on [filename:line]:**
```
[Your comment suggesting improvement]
```

**General comment:**
```
[Overall feedback for the author]
```

## Verification Commands

```bash
# Fetch the review
cd <mymcp-repo-path>/workspace
./fetch-review.sh --with-master opendev [review-url]

# View changes
cd [project]-[review]
git show HEAD

# Compare with master
cd ..
diff -u [project]-master/[file] [project]-[review]/[file]

# Run tests
cd [project]-[review]
tox -e pep8
tox -e py3
```

---

**Status:** 🔄 In Progress / ✅ Complete  
**Reviewer:** [Your Name]  
**Assessment Date:** [Date]  
**Last Updated:** [Date]

