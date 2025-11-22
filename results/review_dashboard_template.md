# Review Dashboard: [Review Number] - [Title]

## Current Status

| Property | Value |
|----------|-------|
| **Review URL** | [URL] |
| **Review Number** | [Number] |
| **Project** | [Project Name] |
| **Author** | [Author Name] <email> |
| **Current Status** | [NEW/MERGED/ABANDONED] |
| **Branch** | [master/stable/...] |
| **Current Patchset** | [X] |
| **Total Patchsets** | [Y] |
| **Created** | [Date] |
| **Last Updated** | [Date] |
| **Last Checked** | [Date] |

## Quick Summary

**What this review does:** [1-2 sentence summary]

**Current recommendation:** ✅ +2 / ⚠️ +1 / 🔄 0 / ❌ -1

**Next action:** [What should happen next]

---

## Check History

### Check #[N] - [Date/Time]

**Status:** [No changes / New patchset / New comments / Status changed]

**Changes detected:**
- [Change 1]
- [Change 2]

**Action taken:**
- [What was done, e.g., "Created patchset 2 assessment"]

**Next steps:**
- [Recommendations]

---

### Check #[N-1] - [Date/Time]

[Previous check...]

---

## Patchset Evolution

### Patchset [X] - [Date] (CURRENT)

**File:** [`review_[number]_patchset_[X].md`](review_[number]_patchset_[X].md)

**Summary:** [What changed in this patchset]

**Status:** [In review / Waiting for author / Ready to merge]

**Comments during this patchset:**
- [Author Name]: [Comment summary]
- [Reviewer Name]: [Comment summary]

**Votes:**
- ✅ +2: [names]
- ✅ +1: [names]
- 🔄 0: [names]
- ❌ -1: [names]

---

### Patchset [X-1] - [Date]

**File:** [`review_[number]_patchset_[X-1].md`](review_[number]_patchset_[X-1].md)

**Summary:** [What changed in this patchset]

**Status:** [Superseded by PS[X]]

**What changed from PS[X-2] to PS[X-1]:**
- [Change 1]
- [Change 2]

**Comments during this patchset:**
- [Author Name]: [Comment summary]
- [Reviewer Name]: [Comment summary]

**Why this patchset was updated:**
[Reason for creating next patchset]

---

### Patchset 1 - [Date]

**File:** [`review_[number]_patchset_1.md`](review_[number]_patchset_1.md)

**Summary:** [Initial submission - what it did]

**Status:** [Superseded by PS2]

**Initial approach:**
[Description of initial implementation]

**Comments during this patchset:**
- [Reviewer Name]: [Comment summary]

**What needed to change:**
[What feedback led to PS2]

---

## Review Timeline

```
[Date1] PS1 uploaded    → Initial submission
        ├─ [Date2] Comment from [Reviewer]: [Summary]
        └─ [Date3] Comment from [You]: [Summary]

[Date4] PS2 uploaded    → [What changed]
        ├─ [Date5] Comment from [Reviewer]: [Summary]
        └─ [Date6] Vote: +1 from [Reviewer]

[Date7] PS3 uploaded    → [What changed]
        └─ [Date8] Status: Ready for +2

[Date9] Check #1        → No changes
[Date10] Check #2       → New comment detected
[Date11] Check #3       → Merged to master
```

---

## Comment Thread Summary

### General Comments

**[Reviewer Name] - [Date]:**
> [Comment text or summary]

**Your Response - [Date]:**
> [Your response or planned response]

---

### File-Specific Comments

#### File: `[path/to/file.py]`

**[Reviewer Name] - [Date] (PS[X]):**
> Line [Y]: [Comment]

**Author Response - [Date] (PS[X+1]):**
> [How they addressed it]

---

## Related Work

### Depends On
- Review [XXXXXX](link) - [Description] - Status: [MERGED/NEW/etc.]

### Required By
- Review [YYYYYY](link) - [Description] - Status: [BLOCKED/WAITING/etc.]

### Related Issues
- Bug [#XXXX](link) - [Description]
- Feature [#YYYY](link) - [Description]

### Related Reviews
- Review [ZZZZZZ](link) - [Description] (similar work)

---

## Overall Assessment

### Strengths
1. [Strength across all patchsets]
2. [Author responsiveness to feedback]
3. [Code quality]

### Evolution Notes
[How the review improved from PS1 to PSX]

### Current State
[Assessment of the current patchset]

### Recommendation

**Final vote:** ✅ +2 / ⚠️ +1 / 🔄 0 / ❌ -1

**Reasoning:**
[Why this vote]

**Conditions for approval:**
[Any remaining items needed]

---

## Files for This Review

### Dashboard (This File)
- `review_[number].md` - Review dashboard with links and history

### Patchset Assessments
- [`review_[number]_patchset_1.md`](review_[number]_patchset_1.md) - Initial submission
- [`review_[number]_patchset_2.md`](review_[number]_patchset_2.md) - First revision
- [`review_[number]_patchset_3.md`](review_[number]_patchset_3.md) - Current state
- [Add more as patchsets are created]

### Code Location
- `workspace/[project]-[review-number]/` - Checked out code (current patchset)
- `workspace/[project]-master/` - Master branch for comparison

---

## Quick Actions

### To check for updates:
```
check review [number]
```

### To analyze new patchset:
```
check review [number] latest only           # Analyze just the latest
check review [number] create patchsets      # Create assessment for all new patchsets
```

### To update your vote:
```
Visit: [review URL]
Post your updated vote and comments
```

### To compare patchsets:
```bash
cd workspace
diff -u [project]-[review]/patchset1/ [project]-[review]/patchset2/
```

---

**Dashboard Created:** [Date]  
**Last Updated:** [Date]  
**Maintained By:** [Your Name]  

---

## Metadata (for AI tracking)

```yaml
review_metadata:
  review_number: [number]
  project: [project]
  current_patchset: [X]
  total_patchsets: [Y]
  status: [NEW/MERGED/ABANDONED]
  last_check_date: [ISO 8601 date]
  last_check_patchset: [X]
  patchset_files_created:
    - patchset_1
    - patchset_2
    - patchset_3
  check_count: [N]
  assessment_type: "dashboard"
```

