# Horizon OSPRH-12803 Patchset Analysis

**Review URL:** https://review.opendev.org/c/openstack/horizon/+/966349  
**Title:** de-angularize Key Pairs  
**Author:** Owen McGonagle (omcgonag@redhat.com)  
**Project:** openstack/horizon  
**Branch:** master  
**Status:** NEW  
**Topic:** keypairs  

---

## Section 1: Patchset Overview and File Changes

### Patchset 1
**Created:** 2025-11-06 20:30:04  
**Commit:** 0725b0bee46a3e1fe3ae02fab6b4dff4bc77d5d5  
**Author:** Owen McGonagle  
**Committer:** Owen McGonagle  

**Files Changed:**
- `openstack_dashboard/dashboards/project/key_pairs/tables.py`
  - Lines: +8/-1 (net: +7)
  - Size delta: +351 bytes
  - Final size: 5,035 bytes
  
- `openstack_dashboard/dashboards/project/templates/key_pairs/expandable_row.html` (NEW)
  - Lines: +4/0
  - Size delta: +141 bytes
  - Final size: 141 bytes
  
- `openstack_dashboard/dashboards/project/templates/key_pairs/expandable_row.html~` (NEW - backup file)
  - Lines: +4/0
  - Size delta: +141 bytes
  - Final size: 141 bytes

**Total Changes:** 3 files, +16 lines, -1 lines

---

### Patchset 2
**Created:** 2025-11-06 20:32:31  
**Commit:** 76a7af68fd0273b04f66ddd6661ca69b09dea85c  
**Author:** Owen McGonagle  
**Committer:** Owen McGonagle  

**Files Changed:**
- `.gitignore` (MODIFIED)
  - Lines: +6/0
  - Size delta: +37 bytes
  - Final size: 982 bytes
  
- `openstack_dashboard/dashboards/project/key_pairs/tables.py`
  - Lines: +8/-1 (net: +7)
  - Size delta: +351 bytes
  - Final size: 5,035 bytes
  
- `openstack_dashboard/dashboards/project/templates/key_pairs/expandable_row.html` (NEW)
  - Lines: +4/0
  - Size delta: +141 bytes
  - Final size: 141 bytes

**Total Changes:** 3 files, +18 lines, -1 lines

**Changes from Patchset 1 to Patchset 2:**
- ✅ Added `.gitignore` modifications
- ❌ Removed `expandable_row.html~` (backup file)
- ⚠️ Same changes to `tables.py` and `expandable_row.html`

---

### Patchset 3
**Created:** 2025-11-07 02:39:51  
**Commit:** 6737fdbfb9ef084479c3787e3b32ed68f9b5a972  
**Author:** Owen McGonagle  
**Committer:** Owen McGonagle  

**Files Changed:**
- `.gitignore` (MODIFIED)
  - Lines: +6/0
  - Size delta: +37 bytes
  - Final size: 982 bytes
  
- `openstack_dashboard/dashboards/project/key_pairs/tables.py`
  - Lines: +8/-1 (net: +7)
  - Size delta: +351 bytes
  - Final size: 5,035 bytes
  
- `openstack_dashboard/dashboards/project/templates/key_pairs/expandable_row.html` (NEW)
  - Lines: +32/0
  - Size delta: +1,126 bytes
  - Final size: 1,126 bytes

**Total Changes:** 3 files, +46 lines, -1 lines

**Changes from Patchset 2 to Patchset 3:**
- ⚠️ Same `.gitignore` changes
- ⚠️ Same `tables.py` changes
- 🔄 **MAJOR UPDATE to `expandable_row.html`**: Expanded from 4 lines (141 bytes) to 32 lines (1,126 bytes)
  - Size increased by 985 bytes
  - Lines increased by 28 lines

---

### Patchset 4
**Created:** 2025-11-07 17:04:44  
**Commit:** 365530300f2e22f103a21c5f08654697c2a1773d  
**Author:** Owen McGonagle  
**Committer:** Radomir Dopieralski (thesheep)  

**Files Changed:**
- `.gitignore` (MODIFIED)
  - Lines: +6/0
  - Size delta: +37 bytes
  - Final size: 982 bytes
  
- `openstack_dashboard/dashboards/project/key_pairs/tables.py`
  - Lines: +24/-1 (net: +23)
  - Size delta: +896 bytes
  - Final size: 5,580 bytes
  
- `openstack_dashboard/dashboards/project/templates/key_pairs/expandable_row.html` (NEW)
  - Lines: +23/0
  - Size delta: +730 bytes
  - Final size: 730 bytes

**Total Changes:** 3 files, +53 lines, -1 lines

**Changes from Patchset 3 to Patchset 4:**
- ⚠️ Same `.gitignore` changes
- 🔄 **MAJOR UPDATE to `tables.py`**: Expanded from +8 lines to +24 lines (net +16 additional lines)
  - Size increased from 5,035 bytes to 5,580 bytes (+545 bytes)
  - Likely added more functionality to the ExpandableKeyPairRow class
- 🔄 **UPDATE to `expandable_row.html`**: Reduced from 32 lines (1,126 bytes) to 23 lines (730 bytes)
  - Size decreased by 396 bytes
  - Lines decreased by 9 lines
  - Likely refactoring/cleanup of the HTML template

---

### Patchset 5
**Created:** 2025-11-07 17:06:59  
**Commit:** 565d6d69d69d7ffd00ce5fc28a9e88dfa183b2f5  
**Author:** Owen McGonagle  
**Committer:** Radomir Dopieralski (thesheep)  
**Note:** "New patch set was added with same tree, parent tree, and commit message as Patch Set 4."

**Files Changed:**
- `.gitignore` (MODIFIED)
  - Lines: +6/0
  - Size delta: +37 bytes
  - Final size: 982 bytes
  
- `openstack_dashboard/dashboards/project/key_pairs/tables.py`
  - Lines: +24/-1 (net: +23)
  - Size delta: +896 bytes
  - Final size: 5,580 bytes
  
- `openstack_dashboard/dashboards/project/templates/key_pairs/expandable_row.html` (NEW)
  - Lines: +23/0
  - Size delta: +730 bytes
  - Final size: 730 bytes

**Total Changes:** 3 files, +53 lines, -1 lines

**Changes from Patchset 4 to Patchset 5:**
- ✅ **NO CODE CHANGES** - This is a trivial rebase/re-upload
- Kind: NO_CHANGE (as marked in Gerrit)
- Same tree, parent tree, and commit message as Patch Set 4

---

## Summary of File Evolution Across Patchsets

### `.gitignore`
- **Patchset 1:** Not modified
- **Patchset 2:** Added (+6 lines)
- **Patchset 3:** Same as Patchset 2
- **Patchset 4:** Same as Patchset 2
- **Patchset 5:** Same as Patchset 2

### `tables.py`
- **Patchset 1:** +8/-1 lines (351 bytes added) → 5,035 bytes
- **Patchset 2:** Same as Patchset 1
- **Patchset 3:** Same as Patchset 1
- **Patchset 4:** +24/-1 lines (896 bytes added) → 5,580 bytes ⚠️ **Significant expansion**
- **Patchset 5:** Same as Patchset 4

### `expandable_row.html`
- **Patchset 1:** +4 lines → 141 bytes (NEW)
- **Patchset 2:** Same as Patchset 1
- **Patchset 3:** +32 lines → 1,126 bytes ⚠️ **Major expansion**
- **Patchset 4:** +23 lines → 730 bytes ⚠️ **Refactored/reduced**
- **Patchset 5:** Same as Patchset 4

---

## Build Status Summary

### Patchset 2
- **Status:** Verified -1 (Build Failed)
- **Failed Jobs:**
  - `horizon-tox-python3-django52` (non-voting)
  - `openstack-tox-pep8` ❌

### Patchset 3
- **Status:** Verified -1 (Build Failed)
- **Workflow:** -1 (Work in progress)
- **Failed Jobs:**
  - `horizon-tox-python3-django52` (non-voting)
  - `openstack-tox-pep8` ❌

### Patchset 5 (Current)
- **Status:** Verified -1 (Build Failed)
- **Failed Jobs:**
  - `horizon-tox-python3-django52` (non-voting)
  - `openstack-tox-pep8` ❌
  - `horizon-tox-bandit-baseline` ❌

---

## Additional Sections (To Be Updated)

### Section 2: [Reserved for future analysis]

### Section 3: [Reserved for future analysis]

### Section 4: [Reserved for future analysis]

### Section 5: [Reserved for future analysis]

---

*Document created: 2025-11-10*  
*Last updated: 2025-11-10*



