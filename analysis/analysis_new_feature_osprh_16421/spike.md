# Spike: OSPRH-16421 - Add Chevrons to the Images Table

**Jira**: [OSPRH-16421](https://issues.redhat.com/browse/OSPRH-16421)  
**Epic**: [OSPRH-12801](https://issues.redhat.com/browse/OSPRH-12801) - Remove angular.js from Horizon  
**Reference**: OSPRH-12803 (Key Pairs chevrons - ✅ Complete, Review 966349)  
**Type**: Feature Implementation  
**Estimated Complexity**: Medium  
**Date Created**: November 15, 2025

---

## Overview

Add expandable chevron functionality to the Images table, allowing users to click a chevron icon to expand/collapse inline image details without navigating to a separate page. This directly mirrors the work completed for Key Pairs in Review 966349.

## Problem Statement

The Angular version of the Images table has collapsible chevrons that display additional image information inline. The Python version lacks this functionality, requiring users to navigate to a detail page to see full image information.

### Current State (Angular)
- Chevron icons in first column
- Click chevron → row expands with detailed info
- Click again → row collapses
- Information displayed: Size, Status, Visibility, Protected, Disk Format, Container Format

### Current State (Python)
- No chevrons
- Must click image name to go to detail page
- Less efficient user experience

### Desired State
- Match Angular UX exactly
- Expandable rows with chevron toggle
- Preserve name click → detail page functionality
- Use Bootstrap collapse (native CSS if possible)

## Success Criteria

- [ ] Chevrons added to Images table
- [ ] Click chevron expands/collapses row
- [ ] Detail row shows all relevant image information
- [ ] Chevron rotates on expand/collapse
- [ ] Only one row expanded at a time (accordion behavior)
- [ ] Name link still navigates to detail page
- [ ] PEP8 compliant
- [ ] Tested with 3+ images
- [ ] Upstream review submitted with topic: `de-angularize`

## Key Technical Decisions

Based on the successful implementation in Review 966349:

### Use Bootstrap Native Collapse?
**Decision**: Start with Bootstrap native, fall back to custom JS only if needed.

**From Review 966349**: Initial implementation used custom jQuery, but Phase 2 refactored to Bootstrap's native `data-toggle="collapse"` with CSS-driven chevron rotation. This was simpler and more maintainable.

### CSS Specificity vs. `!important`?
**Decision**: Always use CSS specificity.

**From Review 966349**: Reviewer feedback emphasized avoiding `!important`. Use more specific selectors instead:
```css
/* Good */
.table .chevron-icon.collapsed {
    transform: rotate(0deg);
}

/* Bad */
.chevron-icon {
    transform: rotate(0deg) !important;
}
```

### Unique IDs for Multiple Rows?
**Decision**: Use datum-based unique IDs.

**From Review 966349**: Must generate unique IDs for each expandable row. Use a helper function:
```python
def get_chevron_id(self):
    return f"image-detail-{self.datum.id}"
```

## Code Areas of Concern

### Files to Create/Modify

```
openstack_dashboard/dashboards/project/images/images/
├── tables.py                              # MODIFY: Add ExpandableImageRow class
├── panel.py                               # MODIFY: Register CSS/JS files
├── templates/
│   └── images/
│       └── images/
│           ├── _images_table.html         # CREATE: Custom table template (if needed)
│           └── _expandable_row.html       # CREATE: Two-row template (summary + detail)
└── static/
    └── dashboard/
        └── project/
            └── images/
                └── images/
                    ├── images.js          # MODIFY: Add toggle logic
                    └── images.scss        # MODIFY: Add chevron styling
```

### Integration Points

1. **Glance Client** (`glanceclient.v2.images`)
   - Image object properties available in templates
   - Fields: id, name, size, status, visibility, protected, disk_format, container_format, created_at, updated_at

2. **Horizon DataTable Framework**
   - Custom `Row` class pattern (from `horizon.tables.base.Row`)
   - Custom template rendering
   - Table `Meta.row_class` attribute

3. **Bootstrap Collapse**
   - Native collapse component
   - Data attributes: `data-toggle`, `data-target`
   - CSS classes: `.collapse`, `.collapsed`

## Investigation Plan

### Phase 1: Study Review 966349 (1 day)
1. Read all documentation:
   - `analysis/analysis_new_feature_966349/spike.md`
   - `analysis/analysis_new_feature_966349/patchset_001_initial_implementation.md`
   - `analysis/analysis_new_feature_966349/patchset_008_bootstrap_refactor_phases_1to4.md`
   - `analysis/analysis_new_feature_966349/patchset_018_css_refinement.md`

2. Identify reusable patterns:
   - `ExpandableKeyPairRow` → `ExpandableImageRow`
   - Template structure
   - CSS/JS patterns
   - Helper functions

3. Note Key Pairs-specific code vs. generalizable patterns

### Phase 2: Images-Specific Analysis (1 day)
1. Review current Images table implementation
   - `openstack_dashboard/dashboards/project/images/images/tables.py`
   - Identify all image fields to display in detail row

2. Compare with Angular version
   - Document exact fields shown
   - Document layout and formatting
   - Note any special handling (e.g., size formatting, status icons)

3. Plan detail row layout
   - Which fields in detail row?
   - How to format size (bytes → GB)?
   - How to display booleans (protected, etc.)?

### Phase 3: Implementation (4 days)

#### Patchset 1: Basic Expandable Rows
**Goal**: Two-row template with always-visible detail row

```python
# tables.py
class ExpandableImageRow(tables.Row):
    """Custom row class for expandable image details."""
    
    def render(self):
        return render_to_string(
            "project/images/images/_expandable_row.html",
            {"row": self}
        )

class ImagesTable(tables.DataTable):
    # ... existing columns ...
    
    class Meta(object):
        name = "images"
        row_class = ExpandableImageRow  # NEW
        # ... existing meta ...
```

```django
{# _expandable_row.html #}
{% load i18n %}

{# Summary row #}
{% include "horizon/common/_data_table_row.html" %}

{# Detail row (always visible in patchset 1) #}
<tr class="image-detail-row">
  <td colspan="{{ row.cells|length }}">
    <dl class="dl-horizontal">
      <dt>{% trans "ID" %}</dt>
      <dd>{{ row.datum.id }}</dd>
      
      <dt>{% trans "Size" %}</dt>
      <dd>{{ row.datum.size|filesizeformat }}</dd>
      
      {# ... more fields ... #}
    </dl>
  </td>
</tr>
```

**Commit**: "Add expandable row template for Images table"

#### Patchset 2: Bootstrap Native Collapse
**Goal**: Hide detail rows by default, use Bootstrap collapse

```django
{# _expandable_row.html - updated #}
{# Summary row - add data attributes #}
<tr class="image-summary-row">
  <td>
    <a data-toggle="collapse" 
       data-target="#image-detail-{{ row.datum.id }}"
       class="chevron-toggle collapsed">
      <i class="fa fa-chevron-right chevron-icon"></i>
    </a>
  </td>
  {# ... other cells ... #}
</tr>

{# Detail row - add collapse classes #}
<tr id="image-detail-{{ row.datum.id }}" class="image-detail-row collapse">
  <td colspan="{{ row.cells|length }}">
    {# ... content ... #}
  </td>
</tr>
```

**Commit**: "Add Bootstrap collapse functionality to Images table"

#### Patchset 3: CSS-Driven Chevron Rotation
**Goal**: Chevron rotates automatically via CSS

```scss
// images.scss
.images-table {
  .chevron-icon {
    transition: transform 0.3s ease;
  }
  
  .collapsed .chevron-icon {
    transform: rotate(0deg);
  }
  
  .chevron-toggle:not(.collapsed) .chevron-icon {
    transform: rotate(90deg);
  }
  
  .image-detail-row {
    background-color: #f9f9f9;
    
    .dl-horizontal {
      margin: 15px 0;
      
      dt {
        width: 120px;
        text-align: right;
      }
      
      dd {
        margin-left: 140px;
      }
    }
  }
}
```

```python
# panel.py - register CSS
class Images(horizon.Panel):
    name = _("Images")
    slug = 'images'
    # ... existing ...
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not hasattr(self, 'stylesheets'):
            self.stylesheets = []
        self.stylesheets.append('dashboard/project/images/images/images.css')
```

**Commit**: "Add CSS styling for Images table chevrons"

#### Patchset 4: Polish & PEP8
**Goal**: Refinements based on testing

- Handle edge cases (no images, very long names)
- Improve detail row layout
- Format sizes correctly
- Add appropriate icons for status
- Ensure PEP8 compliance

**Commit**: "Polish Images table expandable rows UI"

### Phase 4: Testing (2 days)
1. **Unit Tests**: Not strictly required for UI-only changes, but consider
2. **Manual Testing**:
   - [ ] Create 3+ test images (different sizes, formats, statuses)
   - [ ] Test chevron click → expands
   - [ ] Test chevron click again → collapses
   - [ ] Test clicking name still goes to detail page
   - [ ] Test with no images (empty table)
   - [ ] Test with 10+ images (performance)
   - [ ] Test browser compatibility (Chrome, Firefox)
   - [ ] Test responsive behavior (narrow screens)

### Phase 5: Documentation (1 day)
1. Create WIP analysis document
2. Document decisions and iterations
3. Take screenshots for analysis
4. Update commit messages

**Total Estimated Time**: 9 days (2 sprints)

## Proposed Work Items Summary

1. **Patchset 1**: Basic expandable rows (always visible)
2. **Patchset 2**: Bootstrap collapse (hide/show)
3. **Patchset 3**: CSS chevron rotation + styling
4. **Patchset 4**: Polish and refinements

**Pattern**: Exactly mirrors Review 966349's approach - incremental, testable changes.

## Image-Specific Detail Row Fields

Based on Glance image properties:

| Field | Display Name | Format | Notes |
|-------|--------------|--------|-------|
| id | ID | UUID | Monospace font |
| size | Size | Human-readable (MB/GB) | Use `filesizeformat` filter |
| status | Status | String | Add status icon/color |
| visibility | Visibility | String | public/private/shared/community |
| protected | Protected | Boolean | Yes/No or icon |
| disk_format | Disk Format | String | qcow2, raw, vmdk, etc. |
| container_format | Container Format | String | bare, ovf, etc. |
| created_at | Created | DateTime | Use `timesince` filter |
| updated_at | Updated | DateTime | Use `timesince` filter |

Layout (two columns for efficiency):

```
┌────────────────────────────────────────────────────┐
│ ID:                 abc123-def456-...               │
│ Size:               2.5 GB                          │
│ Status:             active  [icon]                  │
│ Visibility:         public                          │
│ Protected:          No                              │
│ Disk Format:        qcow2                           │
│ Container Format:   bare                            │
│ Created:            2 days ago                      │
│ Updated:            1 hour ago                      │
└────────────────────────────────────────────────────┘
```

## Dependencies

### Upstream Dependencies
- None (can start immediately)

### Downstream Dependencies
- OSPRH-16422 (Images filtering) - can proceed in parallel
- OSPRH-16423 (Images form fields) - can proceed in parallel
- OSPRH-16424 (Images visibility) - can proceed in parallel
- OSPRH-16426 (Images actions) - can proceed in parallel

## Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Bootstrap version differences | Medium | Low | Check Horizon's Bootstrap version, test thoroughly |
| Many image properties (complex layout) | Low | Medium | Prioritize most important fields, use two-column layout |
| Performance with many images (100+) | Medium | Medium | Test with large datasets, consider pagination |
| Unique ID collisions | High | Low | Use image UUID for IDs (guaranteed unique) |

## Lessons from Review 966349 (Directly Applicable)

### Phase-by-Phase Development
1. ✅ Always-visible detail rows first (validate template)
2. ✅ Add collapse functionality second (validate Bootstrap)
3. ✅ Add CSS styling third (validate animations)
4. ✅ Polish fourth (address feedback)

### Technical Patterns to Reuse
1. ✅ Use `render_to_string()` in custom Row class
2. ✅ Use Bootstrap's `data-toggle="collapse"`
3. ✅ Use CSS transitions for animations
4. ✅ Use `.collapsed` class for chevron state
5. ✅ Use `dl-horizontal` for detail layout

### Code Quality
1. ✅ Ensure PEP8 from start
2. ✅ Test with 3+ data items
3. ✅ Handle empty state gracefully
4. ✅ Respond quickly to reviewer feedback

## Next Steps After Spike

1. Review all Review 966349 documentation thoroughly
2. Set up dev environment with Images panel
3. Create test images (various formats, sizes, statuses)
4. Implement Patchset 1 (basic template)
5. Submit for review with topic: `de-angularize`
6. Iterate through patchsets 2-4 based on feedback

---

## References

- [OSPRH-12803: Key Pairs Chevrons (Complete)](https://issues.redhat.com/browse/OSPRH-12803)
- [Review 966349: Key Pairs Implementation](https://review.opendev.org/c/openstack/horizon/+/966349)
- [Complete Documentation: Review 966349](../analysis_new_feature_966349/)
- [Glance API Documentation](https://docs.openstack.org/api-ref/image/)
- [Bootstrap 3.4 Collapse](https://getbootstrap.com/docs/3.4/javascript/#collapse)
- [Best Practices for Feature Development](../docs/BEST_PRACTICES_FEATURE_DEV.md)
- [AngularJS Tickets Overview](../docs/ANGULAR_JS_TICKETS.md)

---

**Status**: 📋 Planning  
**Assigned To**: TBD  
**Target Completion**: TBD  
**Estimated Effort**: 9 days (2 sprints)

