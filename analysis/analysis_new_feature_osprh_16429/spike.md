# Spike: OSPRH-16429 - Add Search/Filter to Roles Panel

**Jira**: [OSPRH-16429](https://issues.redhat.com/browse/OSPRH-16429)  
**Epic**: [OSPRH-12801](https://issues.redhat.com/browse/OSPRH-12801) - Remove angular.js from Horizon  
**Type**: Feature Enhancement  
**Estimated Complexity**: Low  
**Date Created**: November 15, 2025

---

## Overview

Add search/filter functionality to the Roles panel to match the capabilities available in the AngularJS version. This improves usability, especially in environments with many roles.

## Problem Statement

The Angular version of the Roles panel includes search/filter functionality that helps users quickly find specific roles. The Python version lacks this feature, making it difficult to locate roles in large deployments.

### Current State (Angular)
- ✅ Search/filter functionality
- ✅ Real-time filtering as user types
- ✅ Clear visual feedback

### Current State (Python)
- ❌ No search/filter
- Must manually scan the table
- Difficult with many roles

### Desired State
- Search/filter functionality added
- Filters by role name
- Clear UI/UX
- Consistent with other Horizon panels

## Success Criteria

- [ ] Search/filter field added to Roles table
- [ ] Filters by role name (case-insensitive)
- [ ] Optional: filters by role description
- [ ] Works with pagination
- [ ] Clear visual feedback
- [ ] PEP8 compliant
- [ ] Tested with 10+ roles
- [ ] Upstream review submitted with topic: `de-angularize`

## Key Technical Areas

### 1. Horizon FilterAction

Horizon's DataTable framework provides `FilterAction` class for adding search/filter to tables.

```python
class RolesFilterAction(tables.FilterAction):
    name = "roles_filter"
    filter_type = "server"  # or "client"
    filter_choices = (('name', _("Role Name ="), True),)
```

### 2. Keystone Roles API

```python
# List roles
keystone.roles.list()

# List roles with filter (if API supports)
keystone.roles.list(name__contains='admin')
```

**Question**: Does Keystone API support filtering? If not, must use client-side filtering.

### 3. Implementation Strategies

**Option A: Server-Side Filtering**
- Pros: Better performance with many roles
- Cons: Requires Keystone API support (may not exist)

**Option B: Client-Side Filtering**
- Pros: Works regardless of API support
- Cons: Less efficient with many roles (but roles are typically < 100)

**Decision**: Start with client-side (simpler, roles list is typically small).

## Investigation Plan

### Phase 1: Angular Analysis (1 day)
1. Document Angular filter implementation
   - Where is the filter field located?
   - What can be filtered? (name, description, ID?)
   - Is it case-sensitive?
   - How is it styled?

2. Test Angular filtering
   - Filter by role name
   - Filter by partial name
   - Test with special characters
   - Clear filter

3. Check Keystone API
   - Does Keystone support role filtering?
   - What query parameters are available?

### Phase 2: Implementation (2 days)

#### Step 1: Add FilterAction to `tables.py`

```python
# openstack_dashboard/dashboards/identity/roles/tables.py

class RolesFilterAction(tables.FilterAction):
    name = "roles_filter"
    filter_type = "client"  # Client-side filtering
    filter_choices = (('name', _("Role Name"), True),)
    
    def filter(self, table, roles, filter_string):
        """Filter roles by name (case-insensitive)."""
        query = filter_string.lower()
        return [role for role in roles if query in role.name.lower()]


class RolesTable(tables.DataTable):
    name = tables.Column('name', verbose_name=_('Role Name'))
    id = tables.Column('id', verbose_name=_('Role ID'))
    
    class Meta(object):
        name = "roles"
        verbose_name = _("Roles")
        table_actions = (CreateRole, RolesFilterAction, DeleteRole)  # ADD RolesFilterAction
        row_actions = (EditRole, DeleteRole)
```

#### Step 2: Test Basic Filtering

```python
# Should work out of the box with Horizon's FilterAction
# Test in browser:
# 1. Navigate to Identity → Roles
# 2. Type in filter field
# 3. Verify roles filtered by name
```

#### Step 3: Optional Enhancements

**Enhanced filtering** (if needed):
```python
class RolesFilterAction(tables.FilterAction):
    name = "roles_filter"
    filter_type = "client"
    filter_choices = (
        ('name', _("Role Name"), True),
        ('id', _("Role ID"), False),
    )
    
    def filter(self, table, roles, filter_string):
        """Filter roles by name or ID."""
        query = filter_string.lower()
        
        # Filter by the selected field
        filter_field = self.get_filter_field()
        
        if filter_field == 'name':
            return [role for role in roles if query in role.name.lower()]
        elif filter_field == 'id':
            return [role for role in roles if query in role.id.lower()]
        else:
            # Default: search both
            return [role for role in roles 
                    if query in role.name.lower() or query in role.id.lower()]
```

**Server-side filtering** (if Keystone API supports):
```python
class RolesFilterAction(tables.FilterAction):
    name = "roles_filter"
    filter_type = "server"
    filter_choices = (('name', _("Role Name"), True),)

# Then update the view to pass filter to API:
class IndexView(tables.DataTableView):
    table_class = project_tables.RolesTable
    template_name = 'identity/roles/index.html'
    page_title = _("Roles")
    
    def get_data(self):
        filter_string = self.table.get_filter_string()
        if filter_string:
            # If Keystone supports filtering
            roles = api.keystone.role_list(self.request, name=filter_string)
        else:
            roles = api.keystone.role_list(self.request)
        return roles
```

### Phase 3: Testing (1 day)
1. **Functional Testing**
   - [ ] Filter field appears
   - [ ] Type "admin" → only admin roles shown
   - [ ] Type "member" → only member roles shown
   - [ ] Type partial name → substring match works
   - [ ] Clear filter → all roles shown

2. **Edge Cases**
   - [ ] Empty filter (all roles)
   - [ ] No matches (empty table with message)
   - [ ] Special characters in filter
   - [ ] Case insensitivity (Admin = admin)

3. **Performance**
   - [ ] Test with 10 roles
   - [ ] Test with 50 roles (if possible)
   - [ ] Test with 100+ roles (if possible)

4. **Pagination**
   - [ ] If table is paginated, filter works across pages

### Phase 4: Documentation (1 day)

**Total Estimated Time**: 5 days (1 sprint)

## Code Areas of Concern

```
openstack_dashboard/dashboards/identity/roles/
├── tables.py                          # MODIFY: Add RolesFilterAction
├── views.py                           # MODIFY (optional): Server-side filtering
└── tests/
    └── test_tables.py                 # MODIFY: Add test cases
```

## Proposed Work Items

### Patchset 1: Add Client-Side Filter
- Add `RolesFilterAction` to `tables.py`
- Register in `RolesTable.Meta.table_actions`
- Basic name filtering

**Commit**: "Add search/filter to Roles table"

### Patchset 2: Enhancements (Optional)
- Add filter by ID
- Add filter by multiple fields
- Optimize for large datasets

**Commit**: "Enhance Roles table filtering"

### Patchset 3: Tests & Polish
- Unit tests for FilterAction
- Browser testing
- PEP8 compliance

**Commit**: "Add tests for Roles table filtering"

## Dependencies

### Upstream Dependencies
- None (can start immediately)

### Downstream Dependencies
- None

## Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Keystone API lacks filtering support | Low | High | Use client-side filtering (acceptable for roles) |
| Performance with many roles | Low | Low | Roles list typically small (<100), pagination available |
| Filter UI inconsistency | Low | Low | Follow Horizon FilterAction patterns |

## Testing Checklist

### Setup
```bash
# Create test roles (if needed)
openstack role create test-role-1
openstack role create test-role-2
openstack role create admin-role
openstack role create member-role
openstack role create reader-role
```

### Test Cases
- [ ] Navigate to Identity → Roles
- [ ] Filter field visible
- [ ] Type "admin" → only "admin-role" shown
- [ ] Type "test" → "test-role-1" and "test-role-2" shown
- [ ] Type "xyz" (no matches) → empty table with message
- [ ] Clear filter → all roles shown
- [ ] Filter is case-insensitive ("ADMIN" = "admin")

### Performance
- [ ] Filter with 10 roles (instant)
- [ ] Filter with 50 roles (if available)
- [ ] No noticeable lag

## References

- [Horizon FilterAction Documentation](https://docs.openstack.org/horizon/latest/contributor/topics/tables.html#filter-actions)
- [Keystone Roles API](https://docs.openstack.org/api-ref/identity/v3/#roles)
- [Review 966349: Pattern for table enhancements](https://review.opendev.org/c/openstack/horizon/+/966349)
- [AngularJS Tickets Overview](../docs/ANGULAR_JS_TICKETS.md)

---

**Status**: 📋 Planning  
**Assigned To**: TBD  
**Target Completion**: TBD  
**Estimated Effort**: 5 days (1 sprint)

