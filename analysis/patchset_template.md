# Patchset N: [Patchset Name]

**Feature**: [JIRA-KEY] - [Feature name]  
**Patchset**: N of M  
**Story Points**: X-Y  
**Estimated Time**: X-Y days  
**Status**: 📋 **PLANNING** / 🔄 **IN PROGRESS** / ✅ **COMPLETE**

---

## 📋 Executive Summary

**Goal**: [One sentence: what this patchset achieves]

**Approach**: [One sentence: how it will be done]

**Files Affected**:
- **Modified**: X files
- **New**: Y files

**Expected Timeline**: X-Y days

**Dependencies**: [None or list dependencies]

---

## 🔧 Implementation Details

### Overview

This patchset implements [describe what's being implemented]:

1. [High-level step 1]
2. [High-level step 2]
3. [High-level step 3]

---

### Step 1: [First Change]

**File**: `path/to/file.py`

**Add/Modify**:

```python
# Code example
# Complete, copy-paste ready code
```

**Explanation**:
- [Why this change]
- [How it works]
- [What it affects]

**Reference**: [Link to similar code if applicable]

---

### Step 2: [Second Change]

**File**: `path/to/file.html`

**Add/Modify**:

```html
<!-- Code example -->
<!-- Complete, copy-paste ready code -->
```

**Explanation**:
- [Why this change]
- [How it works]
- [What it affects]

---

### Step N: [Final Change]

[Repeat structure for each step]

---

## ✅ Testing Checklist

### Happy Path Tests

- [ ] **1. [Test scenario name]**
  - [Step to test]
  - Expected: [Expected result]
  - Actual: [To be filled during testing]

- [ ] **2. [Test scenario name]**
  - [Step to test]
  - Expected: [Expected result]

### Validation Tests

- [ ] **3. [Validation test]**
  - [What to validate]
  - Expected: [Expected behavior]

### Error Cases

- [ ] **4. [Error scenario]**
  - [How to trigger error]
  - Expected: [Expected error handling]

### Integration Tests

- [ ] **5. [Integration test]**
  - [What integration to test]
  - Expected: [Expected behavior]

### Edge Cases

- [ ] **6. [Edge case]**
  - [Unusual scenario]
  - Expected: [How it's handled]

### Code Quality

- [ ] **7. PEP8 compliance**
  ```bash
  tox -e pep8
  ```
  - Expected: 0 violations

- [ ] **8. [Other quality check]**
  - [What to check]
  - Expected: [Expected result]

---

## 📝 Commit Message Template

```
[Subject Line: Brief description under 72 characters]

[Body: Detailed explanation of what and why]

[This change implements...]

[Key technical decisions:]
- [Decision 1]
- [Decision 2]

[Testing:]
- [Test summary]

[Reference implementation:]
- [Link to similar code if applicable]

[This change is part of...]

[Dependencies or Related work:]
- Depends-On: [Review URL if applicable]
- Related: [Related review/issue]

Change-Id: I<generated-by-git-review>
Signed-off-by: [Your Name] <[your.email@example.com]>
```

**Subject Line Guidelines**:
- Start with area: [Module]: or [Initiative]:
- Briefly describe what
- Keep under 72 characters

**Body Guidelines**:
- Explain user-facing benefit first
- Explain technical approach
- Reference similar implementations
- Mention initiative/epic if applicable
- Include `Depends-On` if needed

---

## ❓ Expected Reviewer Questions

### Q1: [Anticipated question]?

**A**: [Prepared answer]
- ✅ [Reason 1]
- ✅ [Reason 2]
- [Explanation]

### Q2: [Anticipated question]?

**A**: [Prepared answer]
- [Detailed reasoning]
- [Comparison to alternatives]

### Q3: [Anticipated question]?

**A**: [Prepared answer]
- [Technical justification]

[Add more Q&A as needed - typically 5-10 questions]

---

## 🔗 Reference Links

### Related Code

- **[Similar Implementation]**: [GitHub link]
- **[Pattern Source]**: [GitHub link]

### Related Reviews

- **[Related Feature]**: [Review link]
- **[Dependency]**: [Review link]

### Documentation

- [Link to framework docs]
- [Link to API docs]
- [Link to pattern guide]

---

## 🚀 Implementation Checklist

### Before You Start

- [ ] Development environment set up and running
- [ ] Source code checked out
- [ ] Feature branch created: `git checkout -b [branch-name]`
- [ ] Reference implementations available

### Implementation

- [ ] Step 1: [First change]
  - [ ] Code written
  - [ ] Code tested locally
  
- [ ] Step 2: [Second change]
  - [ ] Code written
  - [ ] Code tested locally

[Repeat for each step]

### Testing

- [ ] Manual testing (all scenarios from checklist)
- [ ] Code quality: `tox -e pep8`
- [ ] Unit tests (if applicable): `tox -e py39`
- [ ] Visual inspection in browser/UI

### Submission

- [ ] Prepare commit message (use template)
- [ ] Git add all changed files
- [ ] Git commit with message
- [ ] Ensure commit-msg hook installed (Change-Id)
- [ ] Submit: `git review -t [topic]`

---

**Patchset Status**: 📋 **READY FOR IMPLEMENTATION** / 🔄 **IN PROGRESS** / ✅ **COMPLETE**  
**Reference**: [Link to similar implementation]  
**Topic**: `[gerrit-topic]`  
**Estimated Effort**: X-Y days  
**Next Step**: [Next action]

---

*Document Version: 1.0*  
*Created: [Date]*  
*Based on: [Reference implementation]*  
*AI-assisted planning: mymcp framework*

