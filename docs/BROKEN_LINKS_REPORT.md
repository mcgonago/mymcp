# Broken Links Report

Generated: November 14, 2025

Total broken links found: **42**

---

## Summary

Most broken links fall into three categories:

1. **Template files** (16 links) - These are expected placeholders in template files
2. **Old workspace references** (20 links) - Historical references to workspace directories that no longer exist
3. **Missing documentation** (6 links) - Links to documentation that was never created or has been moved

---

## Links That Need Fixing

### 1. `analysis/analysis_direct_mode.md` (2 broken links)

**Line ~25:**
```text
\[analysis_cors_security.md\](analysis_cors_security.md)
```
- **Expected file**: `<mymcp-repo-path>/analysis/analysis_cors_security.md`
- **Status**: File doesn't exist
- **Action**: Either create this analysis file or remove the link

**Line ~30:**
```text
\[analysis_large_file_uploads.md\](analysis_large_file_uploads.md)
```
- **Expected file**: `<mymcp-repo-path>/analysis/analysis_large_file_uploads.md`
- **Status**: File doesn't exist
- **Action**: Either create this analysis file or remove the link

---

### 2. `analysis/analysis_new_feature_966349_wip/PHASE_1_TO_4_COMPLETE_SUMMARY.md` (23 broken links)

This WIP document has many references to old workspace directories and files:

**Workspace code references (12 links):**

| Link Text | Target Path |
|-----------|-------------|
| `tables.py` | `../workspace/horizon-osprh-12803-working/.../tables.py` |
| `_chevron_column.html` | `../workspace/horizon-osprh-12803-working/.../_chevron_column.html` |
| `expandable_row.html` | `../workspace/horizon-osprh-12803-working/.../expandable_row.html` |

- **Expected**: Files in `workspace/horizon-osprh-12803-working/`
- **Status**: This workspace directory no longer exists (was temporary)
- **Action**: These are historical references. Options:
  1. Keep them as-is (broken links in WIP docs are acceptable for history)
  2. Remove the links but keep the file names as plain text
  3. Update to point to the actual merged code in upstream Horizon repo

**Phase summary references (4 links):**

| Link Text | Target Path |
|-----------|-------------|
| `REFACTOR_SUMMARY_PHASE1.md` | `../workspace/REFACTOR_SUMMARY_PHASE1.md` |
| `REFACTOR_SUMMARY_PHASE2.md` | `../workspace/REFACTOR_SUMMARY_PHASE2.md` |
| `REFACTOR_SUMMARY_PHASE3.md` | `../workspace/REFACTOR_SUMMARY_PHASE3.md` |
| `CLEANUP_SUMMARY_PHASE4.md` | `../workspace/CLEANUP_SUMMARY_PHASE4.md` |

- **Expected**: Files in `workspace/`
- **Status**: These temporary summary files don't exist
- **Action**: Remove these links or note they were temporary working documents

**Other WIP directory references (7 links):**

| Link Text | Target Path |
|-----------|-------------|
| `Workspace README` | `../workspace/README.md` |
| `analysis_peer_review_day_1.md` | `./analysis_peer_review_day_1.md` |
| `analysis_peer_review_day_1_phase_1.md` | `./analysis_peer_review_day_1_phase_1.md` |
| `analysis_template.md` | `./analysis_template.md` |
| `analysis_random_topics.md` | `./analysis_random_topics.md` |
| `analysis_review_966349_patchset_1.org` | `./analysis_review_966349_patchset_1.org` |
| `results/README.md` | `../results/README.md` |

- **Expected**: Files in `analysis_new_feature_966349_wip/` or `../workspace/`
- **Status**: Most of these files are in parent directory, not WIP directory
- **Action**: Update relative paths or remove links to non-existent files

---

### 3. `opendev-review-agent/README.md` (1 broken link)

**Line ~35:**
```text
\[OpenDev MCP Agent Setup Guide\](opendev-mcp-agent-setup.org)
```
- **Expected file**: `<mymcp-repo-path>/opendev-review-agent/opendev-mcp-agent-setup.org`
- **Status**: File doesn't exist
- **Action**: Either create this setup guide or remove the link

---

## Template Files (Expected Broken Links)

These files are templates with placeholder links - **no action needed**:

### `analysis/analysis_template.md` (7 placeholder links)
- `analysis_other_topic.md` (2 occurrences)
- `link` (placeholder for PR #XXX, PR #YYY, etc.) (5 occurrences)

### `analysis/analysis_template_random_topics.md` (6 placeholder links)
- `analysis_other_topic.md`
- `link` (placeholder for PR #XXX, Review XXXXXX, etc.) (5 occurrences)

### `workspace/docs/review_template.md` (4 placeholder links)
- `link` (placeholder for review/issue numbers) (4 occurrences)

---

## Recommendations

### Priority 1: High Priority Fixes

1. **`analysis/analysis_direct_mode.md`**
   - Remove links to non-existent CORS and large file upload analysis files
   - Or create stub files for these topics

2. **`opendev-review-agent/README.md`**
   - Remove link to non-existent setup guide
   - Or create the referenced setup guide

### Priority 2: Medium Priority (WIP Directory)

3. **`analysis/analysis_new_feature_966349_wip/PHASE_1_TO_4_COMPLETE_SUMMARY.md`**
   - This is a WIP document with historical references
   - Options:
     - **Option A** (Recommended): Keep as-is - it's archived WIP, broken links are acceptable
     - **Option B**: Convert broken file links to plain text (remove markdown link syntax)
     - **Option C**: Add note at top explaining links may be broken due to cleaned workspace

### Priority 3: No Action Needed

4. **Template files** - These are meant to have placeholder links

---

## Quick Fix Commands

### Fix analysis/analysis_direct_mode.md

```bash
# Open file and manually remove or fix the two broken links
vim <mymcp-repo-path>/analysis/analysis_direct_mode.md
# Search for: analysis_cors_security.md
# Search for: analysis_large_file_uploads.md
```

### Fix opendev-review-agent/README.md

```bash
# Open file and manually remove or fix the broken link
vim <mymcp-repo-path>/opendev-review-agent/README.md
# Search for: opendev-mcp-agent-setup.org
```

### Add note to PHASE_1_TO_4_COMPLETE_SUMMARY.md (Optional)

```bash
# Add note at top of file explaining historical nature
vim <mymcp-repo-path>/analysis/analysis_new_feature_966349_wip/PHASE_1_TO_4_COMPLETE_SUMMARY.md
```

Add this note at the top:

> **Note**: This is an archived work-in-progress document. Some links reference temporary workspace directories and files that no longer exist. This is expected and preserved for historical context.

---

## Files to Verify

After making fixes, re-run the link checker:

```bash
python3 <mymcp-repo-path>/scripts/check-links.py
```

---

## Summary of Action Items

| File | Broken Links | Priority | Action |
|------|--------------|----------|--------|
| `analysis/analysis_direct_mode.md` | 2 | High | Remove or fix links |
| `opendev-review-agent/README.md` | 1 | High | Remove or create referenced file |
| `analysis/analysis_new_feature_966349_wip/PHASE_1_TO_4_COMPLETE_SUMMARY.md` | 23 | Medium | Add note or keep as-is |
| Template files (3 files) | 16 | None | Expected placeholders |

**Total requiring action: 26 links across 3 files**  
**Total that are acceptable: 16 links in template files**

---

**Generated by**: `scripts/check-links.py`  
**Date**: November 14, 2025
