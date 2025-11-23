# Spike: Add Chevrons to Images Table (OSPRH-16421)

**JIRA**: [OSPRH-16421](https://issues.redhat.com/browse/OSPRH-16421)  
**Summary**: Add chevrons to the Images table  
**Epic**: De-angularize Horizon  
**Created**: 2025-11-22  
**Status**: 🔍 **SPIKE - INVESTIGATION PHASE**

---

## Problem Statement

### What

Add collapsible chevron icons with expandable row details to the **Images table** in Horizon, matching the functionality that existed in the AngularJS version.

### Why

- **Feature Parity**: The AngularJS version of the Images view had collapsible chevrons showing more detailed information
- **User Experience**: Users need quick access to detailed image metadata without navigating to a separate detail page
- **De-angularization Initiative**: Part of the broader effort to remove Angular.js dependencies from Horizon

### Impact

- **Users**: Improved UX - view image details inline (OS type, architecture, disk format, size, visibility, etc.)
- **Timeline**: Critical path for de-angularization milestone
- **Scope**: Project → Compute → Images panel

---

## Current Implementation Analysis

### AngularJS Version (Being Replaced)

**Location**: `openstack_dashboard/dashboards/project/images/images/`

**Current Behavior**:
- Images table displays in grid/list view
- Chevron icons (▸) in leftmost column
- Click chevron to expand row
- Expanded row shows:
  - OS Type / Distribution
  - Architecture (x86_64, arm64, etc.)
  - Disk Format (qcow2, raw, iso, etc.)
  - Container Format
  - Image Size
  - Visibility (Public, Private, Shared, Community)
  - Protected status
  - Min Disk / Min RAM requirements
  - Created date
  - Updated date

**Current Architecture**:
- **Client-side**: AngularJS directives and controllers
- **State Management**: Browser-side
- **Rendering**: Angular templates
- **Dependencies**: angular.js, angular-bootstrap

### Python Version (Current State - Without Chevrons)

**Location**: `openstack_dashboard/dashboards/project/images/images/`

**Files**:
```
images/
├── tables.py          # ImagesTable, ImagesFilterAction
├── views.py           # IndexView, DetailView, CreateView, UpdateView
├── urls.py            # URL routing
├── forms.py           # Image create/update forms
├── templates/
│   └── images/
│       ├── index.html         # Main images page
│       ├── _detail_overview.html
│       └── _create.html
└── tests.py
```

**Current Table Structure** (`tables.py`):
```python
class ImagesTable(tables.DataTable):
    name = tables.Column("name", link="horizon:project:images:images:detail")
    image_type = tables.Column(get_image_type, verbose_name=_("Type"))
    status = tables.Column("status")
    visibility = tables.Column(get_visibility, verbose_name=_("Visibility"))
    protected = tables.Column("protected", verbose_name=_("Protected"))
    disk_format = tables.Column(get_format, verbose_name=_("Format"))
    size = tables.Column(get_size, verbose_name=_("Size"))
    
    class Meta(object):
        name = "images"
        verbose_name = _("Images")
        table_actions = (CreateImage, DeleteImage, ImagesFilterAction)
        row_actions = (LaunchImage, EditImage, UpdateMetadata, DeleteImage)
```

**Current Columns Displayed**:
- Name (with link to detail page)
- Type
- Status
- Visibility
- Protected
- Disk Format
- Size

**What's Missing**:
- ❌ No chevron column
- ❌ No expandable row capability
- ❌ No inline detail view
- ❌ Users must navigate to separate detail page

---

## Proposed Approach

### Architecture

**Pattern**: Replicate the successful Key Pairs expandable rows implementation (Review 966349)

**Components**:
1. **Custom Row Class** (`ExpandableImageRow`) - Renders two `<tr>` elements
2. **Chevron Column** (`ExpandableImageColumn`) - Displays chevron icon
3. **Templates**:
   - `expandable_row.html` - Summary + detail row structure
   - `_chevron_column.html` - Chevron icon with Bootstrap collapse
   - `_images_table.html` - Inline CSS styles
4. **Bootstrap Collapse** - Zero custom JavaScript needed

### Reference Implementation

**Source**: Key Pairs Expandable Rows (OSPRH-12803 / Review 966349)

**Files to Reference**:
- [`key_pairs/tables.py`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/key_pairs/tables.py)
- [`key_pairs/templates/key_pairs/expandable_row.html`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/templates/key_pairs/expandable_row.html)
- [`key_pairs/templates/key_pairs/_chevron_column.html`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/templates/key_pairs/_chevron_column.html)
- [`key_pairs/templates/key_pairs/_keypairs_table.html`](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/templates/key_pairs/_keypairs_table.html)

**Key Patterns to Adapt**:

1. **Unique ID Generation**:
```python
def get_chevron_id(datum):
    """Generate unique ID for each image row."""
    return "image_%s" % datum.id
```

2. **Custom Row Rendering**:
```python
class ExpandableImageRow(tables.Row):
    ajax = False
    
    def get_data(self, request, datum_id):
        return datum
    
    def render(self):
        template = "images/images/expandable_row.html"
        context = {
            "row": self,
            "chevron_id": get_chevron_id(self.datum),
        }
        return render_to_string(template, context)
```

3. **Bootstrap Collapse Integration**:
```html
<!-- Chevron -->
<a role="button" data-toggle="collapse" 
   href="#{{ chevron_id }}"
   aria-expanded="false">
  <i class="fa fa-chevron-right"></i>
</a>

<!-- Detail row -->
<tr class="collapse" id="{{ chevron_id }}">
  <td colspan="{{ columns|length }}">
    <div>
      <dl class="dl-horizontal">
        <!-- Image details -->
      </dl>
    </div>
  </td>
</tr>
```

4. **CSS-Driven Chevron Rotation**:
```css
.table-chevron .fa-chevron-right {
  transition: transform 0.2s;
}

.table-chevron [aria-expanded="true"] .fa-chevron-right {
  transform: rotate(90deg);
}
```

---

## Technical Decisions

### 1. Bootstrap Collapse vs Custom JavaScript

**Decision**: Use Bootstrap collapse

**Reasoning**:
- ✅ **Zero custom JavaScript** - Bootstrap handles all show/hide logic
- ✅ **Proven Pattern** - Successfully used in Key Pairs (Review 966349)
- ✅ **Maintainability** - Framework code, not custom code
- ✅ **Accessibility** - Built-in ARIA attributes
- ✅ **Reliability** - Well-tested library code

**Trade-offs**:
- ⚠️ Collapse class doesn't work directly on `<tr>` - Solution: Collapse `<div>` inside `<td>`
- ⚠️ Must use Bootstrap 3 syntax (Horizon's version)

### 2. Inline CSS vs External Stylesheet

**Decision**: Inline CSS in template

**Reasoning**:
- ✅ **Following Key Pairs Pattern** - Consistency across panels
- ✅ **Scoped Styles** - Specific to Images table, no global impact
- ✅ **Maintainability** - All styles in one place with the table
- ✅ **No Asset Pipeline Changes** - Simpler deployment

**Trade-offs**:
- ⚠️ ~30-40 lines of CSS in template
- ⚠️ Not reusable across other tables (but each table may have unique needs)

### 3. Two-Row Rendering Pattern

**Decision**: Custom `Row.render()` method to output summary + detail rows

**Reasoning**:
- ✅ **Standard Horizon Pattern** - Used in multiple panels
- ✅ **Clean Separation** - Summary and detail rows clearly defined
- ✅ **Template Control** - Full control over HTML structure
- ✅ **Bootstrap Compatible** - Works with collapse framework

**Trade-offs**:
- ⚠️ More code than default table rendering
- ⚠️ Must override `get_data()` method

### 4. Detail Content: What to Show

**Decision**: Show comprehensive image metadata in expandable detail

**Fields to Display**:
- **Basic Info**: Name, ID, Owner
- **OS Info**: OS Type, OS Distribution, OS Version
- **Architecture**: x86_64, arm64, ppc64le, etc.
- **Formats**: Disk Format, Container Format
- **Sizing**: Size (bytes), Min Disk, Min RAM
- **Visibility**: Public, Private, Shared, Community
- **Protection**: Protected (yes/no)
- **Timestamps**: Created, Updated
- **Advanced**: Checksum (MD5), Direct URL, Locations

**Reasoning**:
- ✅ **Feature Parity** - Matches AngularJS version
- ✅ **User Value** - All relevant metadata in one view
- ✅ **No Navigation** - Reduces clicks for power users

---

## Complexity Analysis

### Risk Factors (Multiplier: 1.5)

**API Integration** (0.3):
- ✅ No new API calls (data already fetched for table)
- ✅ Just formatting existing image object attributes

**State Management** (0.0):
- ✅ No state management needed (Bootstrap handles show/hide)

**Security** (0.2):
- ⚠️ Must properly escape image metadata (user-provided strings)
- ⚠️ Template auto-escaping should handle this

**UI/UX Changes** (1.0):
- ⚠️ Significant visual change to Images table
- ⚠️ Must match AngularJS behavior exactly
- ⚠️ Need to handle various image types and metadata edge cases

**Total Risk**: 1.5

### Knowledge Factors (Multiplier: 1.2)

**Framework Knowledge** (0.5):
- ✅ Have reference implementation (Key Pairs)
- ⚠️ Need to adapt pattern to Images-specific needs

**Domain Knowledge** (0.4):
- ⚠️ Need to understand Glance image attributes
- ⚠️ Multiple image types (snapshot, image, volume_snapshot)
- ⚠️ Various metadata fields and their meanings

**API Knowledge** (0.3):
- ✅ Glance API already integrated in Horizon
- ✅ Image object structure well-documented

**Total Knowledge**: 1.2

### Skill Factors (Multiplier: 1.2)

**Code Complexity** (0.5):
- ⚠️ Custom row rendering (moderate)
- ⚠️ Template logic for conditional display
- ✅ Direct adaptation from working example

**Testing Complexity** (0.4):
- ⚠️ Manual testing with multiple image types
- ⚠️ Edge cases (images with missing metadata)
- ⚠️ Different visibility levels

**Integration Complexity** (0.3):
- ✅ Isolated to Images panel
- ✅ No impact on other Horizon components
- ⚠️ Must work with existing image actions

**Total Skill**: 1.2

### Story Point Calculation

```
Base Story Points: 3 (small-to-medium feature)
× Risk Factor: 1.5
× Knowledge Factor: 1.2
× Skill Factor: 1.2
= 6.48 ≈ 6-8 story points

Timeline: 1-1.5 sprints (5-7 days)
```

**Interpretation**:
- **Small to Medium Complexity**: Mostly reference-driven implementation
- **Well-Understood Pattern**: 90% adaptation, 10% custom
- **Low Risk**: Framework-based approach, no custom JavaScript
- **Moderate Effort**: Template creation and testing

---

## Recommended Breakdown

### Patchset 1: Add Expandable Rows with Chevrons (5 days)

**Goal**: Implement complete expandable row functionality for Images table

**Scope**:
- Custom row and column classes
- Templates for expandable rows and chevrons
- Inline CSS for chevron rotation and detail styling
- Bootstrap collapse integration

**Files Modified**:
- `tables.py` - Add `ExpandableImageRow`, `ExpandableImageColumn`, `get_chevron_id()`
- `templates/images/images/expandable_row.html` (new)
- `templates/images/images/_chevron_column.html` (new)
- `templates/images/images/_images_table.html` (new)

**Testing**:
- ✅ Manual testing with various image types (images, snapshots, volume snapshots)
- ✅ Test with public, private, shared, community images
- ✅ Test expand/collapse behavior
- ✅ Test chevron rotation animation
- ✅ PEP8 compliance

**Story Points**: 6-8

**Dependencies**:
- None (standalone implementation)

**Expected Reviewer Questions**:
- Why inline CSS vs external stylesheet?
- Why not use JavaScript for toggles?
- How does this compare to Key Pairs implementation?
- What about images with missing metadata?

---

## Success Criteria

### Functional Requirements

✅ **Chevron Column**:
- [ ] Chevron icon (▸) appears as first column
- [ ] Chevron is clickable
- [ ] Chevron rotates 90° when expanded (▸ → ▾)
- [ ] Chevron rotates back when collapsed (▾ → ▸)

✅ **Expandable Row**:
- [ ] Detail row hidden by default
- [ ] Detail row shows when chevron clicked
- [ ] Detail row hides when chevron clicked again
- [ ] Each row expands/collapses independently
- [ ] Smooth animation (200ms)

✅ **Detail Content**:
- [ ] All relevant image metadata displayed
- [ ] Proper formatting (dl-horizontal)
- [ ] Handles missing metadata gracefully
- [ ] OS info shown (if available)
- [ ] Architecture shown (if available)
- [ ] Size, format, visibility displayed
- [ ] Timestamps formatted correctly

✅ **Integration**:
- [ ] Existing table actions still work (Launch, Edit, Delete)
- [ ] Image name link still navigates to detail page
- [ ] Table search/filtering works with expanded rows
- [ ] Pagination works correctly

### Non-Functional Requirements

✅ **Code Quality**:
- [ ] PEP8 compliant (0 violations)
- [ ] No custom JavaScript (Bootstrap only)
- [ ] Clean CSS (no `!important` flags if possible)
- [ ] Follows Horizon patterns

✅ **Performance**:
- [ ] No perceptible slowdown with 50+ images
- [ ] Expand/collapse feels instant (<200ms)

✅ **Accessibility**:
- [ ] ARIA attributes present (`aria-expanded`, `aria-controls`)
- [ ] Keyboard navigation works
- [ ] Screen reader friendly

✅ **Browser Compatibility**:
- [ ] Chrome/Chromium
- [ ] Firefox
- [ ] Safari (if possible to test)

✅ **Documentation**:
- [ ] Commit message explains what/why/how
- [ ] Code comments for non-obvious logic
- [ ] Links to related work (Key Pairs review)

---

## Implementation Strategy

### Phase 1: Investigation (Complete - This Document)

✅ Understand current Images table structure  
✅ Study Key Pairs expandable rows pattern  
✅ Identify files to create/modify  
✅ Define success criteria

### Phase 2: Implementation (5 days)

**Day 1-2**: Core Structure
- Set up development environment
- Create custom row and column classes
- Generate unique chevron IDs per image

**Day 3-4**: Templates and Styling
- Create expandable_row.html template
- Create _chevron_column.html template
- Create _images_table.html with inline CSS
- Implement Bootstrap collapse

**Day 5**: Testing and Refinement
- Manual testing with various image types
- Edge case handling (missing metadata)
- PEP8 validation
- Prepare commit message

### Phase 3: Review and Iteration (Variable)

- Submit to Gerrit with topic `de-angularize`
- Address reviewer feedback
- Iterate on patchsets as needed
- Final approval and merge

---

## Risks and Mitigation

### Risk 1: Different Image Metadata Structure

**Risk**: Images have more varied metadata than key pairs

**Mitigation**:
- Study Glance image schema thoroughly
- Handle missing fields gracefully (conditional display)
- Test with multiple image types
- Use `getattr(image, 'field', default)` pattern

### Risk 2: Performance with Large Image Lists

**Risk**: Rendering extra HTML for detail rows could slow down large tables

**Mitigation**:
- Detail rows are hidden by default (minimal initial render cost)
- Bootstrap collapse is efficient
- Pagination limits visible rows
- No JavaScript event handlers (just Bootstrap)

### Risk 3: Reviewer Preference for Different Approach

**Risk**: Maintainers might prefer external CSS or different structure

**Mitigation**:
- Reference successful Key Pairs implementation
- Explain rationale in commit message
- Be prepared to adapt to feedback
- Inline CSS is pattern already used in Horizon

### Risk 4: Edge Cases in Image Metadata

**Risk**: Some images might have unusual or missing metadata

**Mitigation**:
- Conditional rendering in templates
- Default values for missing fields
- Comprehensive manual testing
- Handle None/empty values gracefully

---

## Reference Documentation

### Horizon Patterns

- [Horizon Tables Documentation](https://docs.openstack.org/horizon/latest/)
- [Bootstrap 3 Collapse](https://getbootstrap.com/docs/3.4/javascript/#collapse)
- [Django Templates](https://docs.djangoproject.com/en/stable/topics/templates/)

### Related Reviews

- **Key Pairs Expandable Rows**: [Review 966349](https://review.opendev.org/c/openstack/horizon/+/966349) (OSPRH-12803)
- **De-angularization Epic**: OSPRH-12801

### Code References

- [Key Pairs tables.py](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/key_pairs/tables.py)
- [Key Pairs templates](https://github.com/openstack/horizon/tree/master/openstack_dashboard/dashboards/project/templates/key_pairs)
- [Images tables.py (current)](https://github.com/openstack/horizon/blob/master/openstack_dashboard/dashboards/project/images/images/tables.py)

---

## Next Steps

1. ✅ **Spike Complete** - This document
2. ⏭️ **Create Patchset Document** - Detailed implementation guide
3. ⏭️ **Set Up Development Environment** - DevStack or local Horizon
4. ⏭️ **Implement Code** - Follow patchset guide
5. ⏭️ **Test Locally** - Verify all success criteria
6. ⏭️ **Submit Review** - Push to Gerrit with topic `de-angularize`
7. ⏭️ **Iterate** - Address reviewer feedback

---

## Appendix: Comparison with Key Pairs

| Aspect | Key Pairs | Images | Notes |
|--------|-----------|--------|-------|
| **Complexity** | Medium | Medium | Similar scope |
| **Reference Code** | volumes/, networks/ | **Key Pairs!** | Direct reference available |
| **Metadata Fields** | ~5 fields | ~15 fields | Images more complex |
| **JavaScript** | 0 lines | 0 lines (goal) | Bootstrap only |
| **CSS** | ~30 lines inline | ~40 lines inline (est.) | More detail content |
| **Review Iterations** | 20 patchsets | 5-10 patchsets (est.) | Have reference now |
| **Story Points** | N/A | 6-8 | ~1-1.5 sprints |

---

**Spike Status**: ✅ **COMPLETE**  
**Next Document**: `patchset_1_add_expandable_rows.md`  
**Estimated Start Date**: TBD  
**Estimated Completion**: 5-7 days after start

---

*Document Version: 1.0*  
*Created: 2025-11-22*  
*Author: AI-assisted feature planning (mymcp framework)*  
*Based on: Key Pairs expandable rows pattern (Review 966349)*

