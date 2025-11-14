# Patchset 001-007: Initial Implementation - Custom JavaScript Approach

**Date**: November 5-6, 2025  
**Review**: [966349](https://review.opendev.org/c/openstack/horizon/+/966349)  
**Status**: Initial working implementation (superseded by Bootstrap approach)

---

## View Patchset Changes

### Compare with baseline (view all initial changes):
```bash
# View the complete initial implementation
cd /path/to/horizon
git review -d 966349,7

# View changes relative to master
git diff origin/master

# View file-by-file changes
git diff origin/master --stat
```

### View specific patchset:
```bash
# Fetch and checkout patchset 7
git fetch origin refs/changes/49/966349/7
git checkout FETCH_HEAD

# Or use git-review
git review -d 966349,7
```

### Compare patchsets online:
```
https://review.opendev.org/c/openstack/horizon/+/966349/1..7
```

---

## Executive Summary

**Goal**: Implement expandable rows in Key Pairs table to achieve feature parity with AngularJS version.

**Approach**: Custom jQuery-based solution with:
- Custom row rendering via `ExpandableKeyPairRow.render()`
- Chevron column for expand/collapse trigger
- jQuery `slideDown()`/`slideUp()` animations
- Accordion behavior (close others when opening one)

**Files Created**:
- `tables.py` - Custom row and column classes
- `_keypairs_table.html` - Custom table template  
- `expandable_row.html` - Detail row template
- `_chevron_column.html` - Chevron toggle template
- `keypairs.scss` - Chevron and detail row styles
- `keypairs.js` - Toggle functionality

**Result**: ✅ Working expandable rows, but feedback suggested using Bootstrap's native collapse instead of custom JavaScript.

---

## Implementation Details

### Problem Statement

The Python-based Key Pairs panel lacked the expandable row feature present in the AngularJS version. Users needed to click through to a detail page to view full key pair information (especially the public key).

**Missing Feature**:
- Chevron icons to indicate expandable rows
- Click to expand inline details
- Smooth animations when expanding/collapsing
- Accordion behavior (one row open at a time)

### Initial Approach: Custom JavaScript

#### Why Custom JavaScript Initially?

1. **Familiarity**: jQuery was already loaded in Horizon
2. **Flexibility**: Full control over animation timing and behavior
3. **Accordion Pattern**: Could easily implement "close others" behavior
4. **Unknown**: Didn't yet know Bootstrap collapse would work with table rows

#### Architecture

**Django Side**:
```python
class ExpandableKeyPairRow(tables.Row):
    """Custom row class that renders summary + detail rows."""
    
    def render(self):
        chevron_id = "%s_chevron_%s" % (self.table.name, self.creation_counter)
        return render_to_string("key_pairs/expandable_row.html",
                                {"row": self, "chevron_id": chevron_id})

class ExpandableKeyPairColumn(tables.Column):
    """Chevron column with click handler."""
    
    def get_data(self, datum):
        chevron_id = "%s_table_chevron%d" % (self.table.name, self.creation_counter)
        return render_to_string(
            "key_pairs/_chevron_column.html",
            {"chevron_id": chevron_id}
        )
```

**Template Structure**:
```django
{# Summary row #}
<tr class="keypair-summary-row">
  <td class="chevron-cell">
    <a href="#" class="chevron-toggle" data-target="#chevron_{{ keypair.name }}">
      <i class="fa fa-chevron-right"></i>
    </a>
  </td>
  <td>{{ keypair.name }}</td>
  <td>{{ keypair.type }}</td>
  <td>{{ keypair.fingerprint }}</td>
</tr>

{# Detail row #}
<tr class="detail-row" id="chevron_{{ keypair.name }}" style="display: none;">
  <td colspan="4">
    <dl class="dl-horizontal">
      <dt>Key Pair Name</dt>
      <dd>{{ keypair.name }}</dd>
      <!-- ... more details ... -->
    </dl>
  </td>
</tr>
```

**JavaScript Logic** (`keypairs.js`):
```javascript
horizon.addInitFunction(function() {
  // Chevron toggle handler
  $(document).on('click', '.chevron-toggle', function(e) {
    e.preventDefault();
    
    var chevronIcon = $(this).find('i');
    var targetId = $(this).data('target');
    var detailRow = $(targetId);
    var isExpanded = chevronIcon.hasClass('fa-chevron-down');
    
    if (isExpanded) {
      // Collapse
      detailRow.slideUp(200);
      chevronIcon.removeClass('fa-chevron-down').addClass('fa-chevron-right');
    } else {
      // Accordion: close all other details first
      $('.detail-row:visible').slideUp(200);
      $('.chevron-toggle i').removeClass('fa-chevron-down').addClass('fa-chevron-right');
      
      // Expand this row
      detailRow.slideDown(200);
      chevronIcon.removeClass('fa-chevron-right').addClass('fa-chevron-down');
    }
  });
});
```

**SCSS Styles** (`keypairs.scss`):
```scss
.chevron-toggle {
  color: #337ab7;
  cursor: pointer;
  text-decoration: none;
  
  i {
    transition: transform 0.2s;
  }
  
  &:hover {
    color: #23527c;
  }
}

.detail-row {
  background-color: #f9f9f9;
  
  td {
    padding: 15px;
    border-top: 1px solid #ddd;
  }
  
  dl {
    margin-bottom: 0;
  }
}
```

---

## Technical Decisions

### 1. Custom Row Class

**Decision**: Override `Row.render()` to output both summary and detail rows

**Reasoning**:
- Horizon's table system renders one `<tr>` per row by default
- Needed two `<tr>` elements (summary + detail)
- `render()` method allows custom HTML output

**Trade-off**:
- ✅ Full control over row structure
- ⚠️ More code than using standard table rendering

### 2. Chevron as Separate Column

**Decision**: Add `ExpandableKeyPairColumn` as first column

**Reasoning**:
- Clean separation (chevron logic isolated)
- Matches AngularJS implementation structure
- Easy to style and target with CSS

**Trade-off**:
- ✅ Clear visual indicator
- ⚠️ Adds extra column to table

### 3. jQuery Animations

**Decision**: Use `slideDown(200)` and `slideUp(200)`

**Reasoning**:
- Smooth, polished transitions
- Standard jQuery API (simple to use)
- 200ms duration feels responsive

**Trade-off**:
- ✅ Nice user experience
- ⚠️ Custom JavaScript to maintain

### 4. Accordion Behavior

**Decision**: Close other detail rows when opening one

**Reasoning**:
- Reduces visual clutter
- Matches common UI patterns
- Easier to scan table

**Trade-off**:
- ✅ Cleaner interface
- ⚠️ Users can't compare multiple key pairs side-by-side

---

## Issues Discovered

### Issue 1: Duplicate Chevron IDs (Critical)

**Problem**: All rows had the same `chevron_id`, so only the first row expanded.

**Root Cause**:
```python
chevron_id = "%s_table_chevron%d" % (self.table.name, self.creation_counter)
# self.creation_counter is the same for all rows!
```

**Impact**: ❌ **Blocking** - Feature completely broken for rows 2+

**Status**: Fixed in Phase 1 (next patchset)

### Issue 2: Duplicate ID Generation Logic

**Problem**: ID generation code duplicated in `ExpandableKeyPairRow` and `ExpandableKeyPairColumn`.

**Reviewer Feedback** (Radomir):
> "it looks like those two lines could be moved to a function, something like get_chevron_id, so that we don't accidentally introduce differences with how the id is generated in both cases"

**Impact**: ⚠️ Maintainability risk - could diverge over time

**Status**: Fixed in Phase 1 (next patchset)

### Issue 3: Bootstrap Not Utilized

**Problem**: Custom JavaScript for collapse, but Bootstrap has built-in collapse functionality.

**Reviewer Feedback** (Radomir):
> "See https://getbootstrap.com/docs/3.4/javascript/#collapse. Please study this comment and come up with a clean, crisp, solution where we changed the code to not use javascript to implement the expand and collapse of the row."

**Impact**: ⚠️ Code complexity - maintaining custom JS when framework solution exists

**Status**: Fixed in Phase 2 (later patchset)

---

## What Worked Well

### ✅ Core Concept

The expandable row architecture was sound:
- Summary + detail row pattern
- Chevron column for visual indication
- Click to expand inline
- Smooth animations

### ✅ Template Organization

Separate templates for different concerns:
- `_chevron_column.html` - Chevron toggle UI
- `expandable_row.html` - Summary + detail rows
- Clean, maintainable structure

### ✅ Visual Design

The UI matched the AngularJS version:
- Chevron icons (► → ▼)
- Gray background for detail rows
- Horizontal definition list layout
- Proper spacing and borders

### ✅ Functionality

Despite the bugs, the core functionality worked:
- Expand/collapse on click
- Smooth animations
- Accordion behavior
- All details visible when expanded

---

## Lessons Learned

### 1. Generate Unique IDs Per Row

**Lesson**: When rendering multiple rows, use row-specific data (like datum) for ID generation, not class-level attributes.

**Applied**: Next patchset uses `table.get_object_id(datum)` for unique IDs.

### 2. Check Framework First

**Lesson**: Before writing custom JavaScript, check if the framework (Bootstrap) has a built-in solution.

**Applied**: Next patchset switches to Bootstrap collapse, eliminating ~30 lines of custom JS.

### 3. Extract Duplicated Logic

**Lesson**: If the same logic appears in multiple places, extract it to a function immediately (don't wait for code review).

**Applied**: Next patchset adds `get_chevron_id(table, datum)` helper function.

### 4. Test with Multiple Rows

**Lesson**: Always test with 3+ items when implementing row-based features. Edge cases appear quickly.

**Applied**: Created test key pairs: test1, test2, test3 to verify all rows work.

---

## Review Feedback Summary

### Radomir Dopieralski (Project Maintainer)

**Comment 1: Duplicate ID Generation**
```
Location: tables.py, line 126
Issue: chevron_id generation duplicated in Row and Column classes
Suggestion: Extract to get_chevron_id(table, datum) function
```

**Comment 2: Use Bootstrap Collapse**
```
Location: General feedback on JavaScript approach
Issue: Custom JavaScript for something Bootstrap provides
Suggestion: Use data-toggle="collapse" and data-target attributes
Reference: https://getbootstrap.com/docs/3.4/javascript/#collapse
```

**Comment 3: Chevron ID Uniqueness**
```
Location: ExpandableKeyPairColumn.get_data()
Issue: self.creation_counter generates same ID for all rows
Suggestion: Use datum (row data) for unique per-row IDs
```

---

## Files Modified

| File | Type | Purpose | Lines |
|------|------|---------|-------|
| `tables.py` | Modified | Add custom row/column classes | +80 |
| `panel.py` | Modified | Register CSS file | +5 |
| `_keypairs_table.html` | Created | Custom table template | +20 |
| `expandable_row.html` | Created | Summary + detail rows | +35 |
| `_chevron_column.html` | Created | Chevron toggle cell | +10 |
| `keypairs.scss` | Created | Chevron and detail styles | +50 |
| `keypairs.js` | Created | Toggle functionality | +30 |
| **TOTAL** | | | **~230 lines** |

---

## Next Steps

Based on reviewer feedback, the next patchset will address:

1. **Fix Unique IDs** (Phase 1)
   - Create `get_chevron_id(table, datum)` helper function
   - Use `table.get_object_id(datum)` for row-specific IDs
   - Call helper from both Row and Column classes

2. **Switch to Bootstrap Collapse** (Phase 2)
   - Remove custom JavaScript (~30 lines)
   - Add `data-toggle="collapse"` to chevron links
   - Add `data-target="#chevron_xxx"` attributes
   - Move `id` from `<tr>` to inner `<div class="collapse">`

3. **Automatic Chevron Rotation** (Phase 3)
   - Add `.collapsed` class to chevron link
   - Use CSS to rotate based on `.collapsed` presence
   - Let Bootstrap manage class toggling

4. **PEP8 Compliance** (Phase 4)
   - Fix import ordering
   - Address any linting issues

---

## Source Documents

This patchset summary synthesizes:
- `analysis_osprh_12803_review_of_first_set_of_changes.md` - Technical review
- `analysis_osprh_12803_review_what_new_things_were_introduced.md` - Feature analysis
- `analysis_osprh_12803_Add_chevrons_to_the_key_pair_table.org` - Initial investigation

---

## Conclusion

**Status**: ✅ Working implementation with known issues

**Key Achievement**: Proved the expandable row concept works and provides value to users.

**Critical Issues**: 
- ❌ Duplicate IDs (blocking for multi-row tables)
- ⚠️ Custom JS where Bootstrap solution exists
- ⚠️ Duplicated ID generation logic

**Verdict**: Good proof of concept, but needs refinement based on maintainer feedback before merge.

**Next Action**: Implement Phase 1-4 improvements in subsequent patchsets.

