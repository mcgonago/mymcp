# Spike: OSPRH-16422 - Update Filtering in the Images Table

**Jira**: [OSPRH-16422](https://issues.redhat.com/browse/OSPRH-16422)  
**Epic**: [OSPRH-12801](https://issues.redhat.com/browse/OSPRH-12801) - Remove angular.js from Horizon  
**Related**: OSPRH-16421 (Images chevrons)  
**Type**: Feature Enhancement  
**Estimated Complexity**: Medium  
**Date Created**: November 15, 2025

---

## Overview

Update the filtering functionality in the Images table to match the AngularJS version's capabilities. The Python version has basic filtering, but the Angular version provides a more sophisticated and user-friendly filtering experience.

## Problem Statement

The Angular version of the Images table has enhanced filtering that differs significantly from the Python version. Users expect consistent filtering UX across all panels.

### Current State (Angular)
- Advanced filter options
- Multiple filter criteria
- Real-time client-side filtering
- Better UX and visual feedback

### Current State (Python)
- Basic server-side filtering
- Limited filter options
- Less intuitive interface

### Desired State
- Match Angular filtering capabilities
- Maintain or improve performance
- Consistent UX with other panels

## Success Criteria

- [ ] Filter functionality matches Angular version
- [ ] All filter options implemented
- [ ] Client-side and/or server-side filtering optimized
- [ ] Clear visual feedback for active filters
- [ ] Filter persistence (if applicable)
- [ ] PEP8 compliant
- [ ] Tested with various filter combinations
- [ ] Upstream review submitted with topic: `de-angularize`

## Key Questions to Answer

### UX Questions
1. What specific filter options does Angular provide?
2. How are filters displayed to the user?
3. Is there a filter dropdown or inline fields?
4. Can multiple filters be combined?
5. How are filters cleared?

### Technical Questions
1. Client-side or server-side filtering?
2. Does Glance API support all needed filters?
3. What's the performance impact with many images?
4. Should filters persist across page refreshes?

## Investigation Plan

### Phase 1: Angular Implementation Analysis (2 days)
1. **Document Angular Filtering Behavior**
   - Screenshot all filter UI elements
   - List all available filter options
   - Test filter combinations
   - Document clear/reset behavior

2. **Identify Filter Criteria**
   - Name (text search)
   - Status (active, deactivated, queued, etc.)
   - Visibility (public, private, shared, community)
   - Disk format (qcow2, raw, vmdk, etc.)
   - Container format (bare, ovf, etc.)
   - Protected (yes/no)
   - Size range?
   - Date range?

3. **Map to Glance API**
   - Which filters supported by API?
   - Which need client-side implementation?
   - Performance implications

### Phase 2: Python Implementation (4 days)

**Approach 1: Server-Side Filtering (Preferred)**
```python
# tables.py
class ImagesFilterAction(tables.FilterAction):
    name = "images_filter"
    filter_type = "server"  # Use Glance API filtering
    filter_choices = (
        ('name', _("Name ="), True),
        ('status', _("Status ="), True),
        ('visibility', _("Visibility ="), True),
        ('disk_format', _("Disk Format ="), True),
    )
    
    def filter(self, table, images, filter_string):
        """Filter images based on user input."""
        # Implementation depends on Glance API capabilities
        pass
```

**Approach 2: Client-Side Filtering (If Needed)**
```javascript
// images.js
horizon.images = {
    filterTable: function(criteria) {
        var $table = $('.images-table');
        var $rows = $table.find('tbody tr');
        
        $rows.each(function() {
            var $row = $(this);
            var matches = true;
            
            // Check each filter criterion
            if (criteria.name && !$row.data('name').includes(criteria.name)) {
                matches = false;
            }
            // ... more criteria ...
            
            $row.toggle(matches);
        });
    }
};
```

### Phase 3: Testing (2 days)
1. Test each filter individually
2. Test filter combinations
3. Test with large dataset (100+ images)
4. Test filter clear/reset
5. Test edge cases (no results, special characters)

### Phase 4: Documentation (1 day)

**Total Estimated Time**: 9 days (2 sprints)

## Code Areas of Concern

```
openstack_dashboard/dashboards/project/images/images/
├── tables.py                      # MODIFY: Add/enhance ImagesFilterAction
├── views.py                       # MODIFY: Handle filter parameters
├── templates/
│   └── images/
│       └── images/
│           └── _filter_form.html  # CREATE: Custom filter UI (if needed)
└── static/
    └── dashboard/
        └── project/
            └── images/
                └── images/
                    ├── images.js  # MODIFY: Add client-side filtering
                    └── images.scss # MODIFY: Style filter UI
```

## Glance API Filter Capabilities

| Filter | Glance API Support | Implementation |
|--------|-------------------|----------------|
| name | ✅ Partial (exact match) | Client-side substring search |
| status | ✅ Yes | Server-side |
| visibility | ✅ Yes | Server-side |
| disk_format | ✅ Yes | Server-side |
| container_format | ✅ Yes | Server-side |
| protected | ✅ Yes | Server-side |
| size (range) | ❌ No | Client-side |
| created_at (range) | ❌ No | Client-side |

**Strategy**: Use server-side for supported filters, add client-side enhancement for name substring and ranges.

## Proposed Work Items

### Patchset 1: Enhanced Filter Action
- Add comprehensive `ImagesFilterAction` to `tables.py`
- Support basic filters (status, visibility, disk_format)
- Server-side implementation

**Commit**: "Add enhanced filtering to Images table"

### Patchset 2: Client-Side Enhancements
- Add JavaScript for name substring filtering
- Add size range filtering (client-side)
- Improve filter UI/UX

**Commit**: "Add client-side filter enhancements for Images"

### Patchset 3: Visual Improvements
- Style filter controls
- Add filter badges/tags to show active filters
- Add clear filters button

**Commit**: "Improve Images filter UI and visual feedback"

### Patchset 4: Performance & Polish
- Optimize for large datasets
- Add filter persistence (local storage?)
- Address reviewer feedback

**Commit**: "Optimize Images filtering performance"

## Dependencies

### Upstream Dependencies
- OSPRH-16421 (Images chevrons) - can proceed in parallel

### Downstream Dependencies
- None

## Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Glance API limitations | High | High | Hybrid server/client approach |
| Performance with many images | Medium | Medium | Pagination + client-side optimization |
| Complex filter UI | Low | Low | Iterative design with user feedback |
| Filter persistence complexity | Low | Low | Start simple (session-only), add later if needed |

## References

- [Glance API Filtering](https://docs.openstack.org/api-ref/image/v2/#list-images)
- [Horizon FilterAction Documentation](https://docs.openstack.org/horizon/latest/contributor/topics/tables.html#filter-actions)
- [AngularJS Tickets Overview](../docs/ANGULAR_JS_TICKETS.md)

---

**Status**: 📋 Planning  
**Assigned To**: TBD  
**Target Completion**: TBD  
**Estimated Effort**: 9 days (2 sprints)

