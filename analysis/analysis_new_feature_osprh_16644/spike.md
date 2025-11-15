# Spike: OSPRH-16644 - Deprecate and Remove AngularJS Versions of Panels

**Jira**: [OSPRH-16644](https://issues.redhat.com/browse/OSPRH-16644)  
**Epic**: [OSPRH-12801](https://issues.redhat.com/browse/OSPRH-12801) - Remove angular.js from Horizon  
**Type**: Cleanup/Deprecation  
**Estimated Complexity**: High  
**Date Created**: November 15, 2025

---

## Overview

Final step in the de-angularization initiative: deprecate the `ANGULAR_FEATURES` setting, make Python versions of all panels the default, and remove the AngularJS panel code from Horizon.

## Problem Statement

Once all panels have been successfully de-angularized (OSPRH-12802 through OSPRH-16429 complete), we need to:
1. Deprecate the `ANGULAR_FEATURES` configuration setting
2. Remove all AngularJS panel implementations
3. Clean up related configuration and documentation
4. Ensure smooth migration path for deployers

### Current State
```python
# horizon/openstack_dashboard/defaults.py
ANGULAR_FEATURES = {
    'images_panel': True,        # Still using Angular
    'key_pairs_panel': False,    # ✅ Python complete (Review 966349)
    'flavors_panel': False,
    'domains_panel': False,
    'users_panel': False,
    'groups_panel': False,
    'roles_panel': True          # Still using Angular
}
```

### Desired State
- `ANGULAR_FEATURES` setting removed
- All panels use Python implementations
- All Angular JavaScript code removed
- Migration guide published
- Release notes updated

## Success Criteria

- [ ] All dependent tickets complete (OSPRH-12802-16429)
- [ ] Deprecation warnings added (one release cycle)
- [ ] `ANGULAR_FEATURES` setting removed
- [ ] All Angular panel directories deleted
- [ ] All Angular-related imports removed
- [ ] Tests updated/removed
- [ ] Documentation updated
- [ ] Migration guide published
- [ ] Release notes comprehensive
- [ ] No regressions in functionality
- [ ] PEP8 compliant
- [ ] Upstream review submitted with topic: `de-angularize`

## Prerequisites (Blocking Dependencies)

**MUST BE COMPLETE BEFORE THIS TICKET**:

| Ticket | Feature | Status |
|--------|---------|--------|
| OSPRH-12803 | Key Pairs expandable rows | ✅ Complete (Review 966349) |
| OSPRH-12802 | Key Pairs create form | 📋 Planning |
| OSPRH-16421 | Images chevrons | 📋 Planning |
| OSPRH-16422 | Images filtering | 📋 Planning |
| OSPRH-16423 | Images form fields | 📋 Planning |
| OSPRH-16424 | Images visibility | 📋 Planning |
| OSPRH-16426 | Images activate/deactivate | 📋 Planning |
| OSPRH-16429 | Roles search/filter | 📋 Planning |

**THIS TICKET CANNOT START UNTIL ALL ABOVE ARE COMPLETE AND MERGED**

## Investigation Plan

### Phase 1: Dependency Verification (1 day)
1. **Verify all panels complete**
   - Check each ticket is merged upstream
   - Manual testing of each panel
   - Verify no regressions

2. **Document current Angular code locations**
   - List all Angular panel directories
   - List all Angular-related files
   - Identify shared Angular code vs. panel-specific

3. **Identify remaining Angular usage**
   - Search for Angular imports
   - Search for `ANGULAR_FEATURES` references
   - Search for Angular templates

### Phase 2: Deprecation (1 release cycle, ~6 months)

**In Release N** (e.g., 2026.1):

#### Step 1: Add Deprecation Warnings

```python
# horizon/openstack_dashboard/defaults.py
import warnings

# Deprecated: Will be removed in 2026.2
ANGULAR_FEATURES = {
    'images_panel': False,       # Python version is default
    'key_pairs_panel': False,    # Python version is default
    'flavors_panel': False,
    'domains_panel': False,
    'users_panel': False,
    'groups_panel': False,
    'roles_panel': False         # Python version is default
}

def check_angular_features_setting():
    """Warn if ANGULAR_FEATURES is being used."""
    if hasattr(settings, 'ANGULAR_FEATURES'):
        warnings.warn(
            "ANGULAR_FEATURES is deprecated and will be removed in 2026.2. "
            "All panels now use Python implementations. "
            "Please remove ANGULAR_FEATURES from your local_settings.py.",
            DeprecationWarning,
            stacklevel=2
        )

# Call on module load
check_angular_features_setting()
```

#### Step 2: Update Documentation

1. **Add deprecation notice to docs**
   ```markdown
   # Deprecated Settings
   
   ## ANGULAR_FEATURES (Deprecated in 2026.1, removed in 2026.2)
   
   The `ANGULAR_FEATURES` setting is deprecated. All panels now use Python
   implementations. Remove this setting from your `local_settings.py`.
   
   **Migration**: Simply remove the `ANGULAR_FEATURES` dictionary from your
   configuration. All panels will use Python versions automatically.
   ```

2. **Update release notes**
   - Announce deprecation
   - List all completed panel migrations
   - Provide migration guidance

#### Step 3: Log Warnings

```python
# In horizon settings initialization
if getattr(settings, 'ANGULAR_FEATURES', None):
    logger.warning(
        "ANGULAR_FEATURES setting is deprecated and will be removed in 2026.2. "
        "All panels now use Python implementations."
    )
```

### Phase 3: Removal (Next release, Release N+1)

**In Release N+1** (e.g., 2026.2):

#### Step 1: Remove ANGULAR_FEATURES Setting

```bash
# Remove from defaults.py
sed -i '/ANGULAR_FEATURES/,/^}/d' horizon/openstack_dashboard/defaults.py

# Remove from documentation
find docs/ -name "*.rst" -o -name "*.md" | xargs sed -i '/ANGULAR_FEATURES/d'
```

#### Step 2: Remove Angular Panel Code

**Directories to remove**:
```
openstack_dashboard/static/app/core/images/
openstack_dashboard/static/app/core/keypairs/
openstack_dashboard/static/app/core/flavors/
openstack_dashboard/static/app/core/users/
openstack_dashboard/static/app/core/groups/
openstack_dashboard/static/app/core/roles/
```

**Command**:
```bash
cd openstack_dashboard
rm -rf static/app/core/images
rm -rf static/app/core/keypairs
rm -rf static/app/core/flavors
rm -rf static/app/core/users
rm -rf static/app/core/groups
rm -rf static/app/core/roles
```

#### Step 3: Remove Angular-Related Imports and References

```bash
# Find all files referencing ANGULAR_FEATURES
git grep -l "ANGULAR_FEATURES"

# Remove or update each file
# Examples:
# - Remove feature toggles in panel views
# - Remove Angular template selection logic
# - Update tests to remove Angular code paths
```

#### Step 4: Update Tests

```bash
# Find tests that reference Angular features
git grep -l "ANGULAR_FEATURES" openstack_dashboard/test/

# Remove or update tests:
# - Remove tests for Angular panel behavior
# - Keep tests for Python panel behavior
# - Update mocks/fixtures
```

#### Step 5: Clean Up Dependencies

```python
# Check if any Angular-specific dependencies can be removed
# Review:
# - requirements.txt
# - package.json (if Angular-specific npm packages exist)
```

### Phase 4: Documentation & Migration Guide (1 week)

#### Migration Guide

```markdown
# Migrating from AngularJS Panels to Python Panels

## Overview

As of Horizon 2026.2, all panels use Python/Django implementations. The
AngularJS versions have been removed.

## What Changed

### Removed
- `ANGULAR_FEATURES` setting
- `openstack_dashboard/static/app/core/*/` directories
- Angular panel templates and controllers

### No Action Required
All Python implementations provide equivalent functionality. No configuration
changes needed.

## For Deployers

### If you have ANGULAR_FEATURES in local_settings.py

**Before** (local_settings.py):
```python
ANGULAR_FEATURES = {
    'images_panel': True,
    'key_pairs_panel': False,
    # ...
}
```

**After** (local_settings.py):
```python
# Remove ANGULAR_FEATURES entirely
# (or comment it out - it will be ignored)
```

### Testing Your Deployment

After upgrading:

1. Test each panel:
   - Navigate to panel
   - Create/edit/delete operations
   - Search/filter functionality
   - Expandable rows (Images, Key Pairs)

2. Verify functionality:
   - Images: chevrons, filtering, visibility, activate/deactivate
   - Key Pairs: chevrons, create form, import form
   - Roles: search/filter

## For Downstream Distributions

If your distribution has patches to Angular panel code:

1. **Review patches**: Determine if still needed
2. **Port to Python**: Reimplement features in Python panels
3. **Test thoroughly**: Ensure no functionality lost
4. **Update documentation**: Reflect Python implementations

## Troubleshooting

### Issue: Panel looks different
**Solution**: This is expected. Python panels use Django templates with Bootstrap styling. Functionality is equivalent but appearance may differ slightly.

### Issue: Missing feature
**Solution**: Report as bug. All Angular features should have Python equivalents.

### Issue: ANGULAR_FEATURES warning in logs
**Solution**: Remove `ANGULAR_FEATURES` from your `local_settings.py`.

## Support

- Upstream bugs: https://bugs.launchpad.net/horizon
- Documentation: https://docs.openstack.org/horizon/latest/
- Community: openstack-discuss@lists.openstack.org
```

#### Release Notes

```markdown
# Horizon 2026.2 Release Notes

## AngularJS Removal (Major Change)

### Summary
All AngularJS panel implementations have been removed from Horizon. All
panels now use Python/Django implementations.

### Impact
- **Deployers**: Remove `ANGULAR_FEATURES` from configuration
- **Developers**: All panel development uses Python/Django/Bootstrap
- **Users**: No visible change (functionality equivalent)

### Completed Panels
- Images: Chevrons, filtering, form fields, visibility, activate/deactivate
- Key Pairs: Chevrons, create form, import form
- Roles: Search/filter functionality

### Migration
See [Migration Guide](migrating-from-angular.html) for details.

### Benefits
- Reduced technical debt
- Improved maintainability
- Consistent codebase
- Better performance (no client-side framework overhead)
```

### Phase 5: Testing & Validation (1 week)
1. **Full regression testing**
   - Test every panel
   - Test all CRUD operations
   - Test all special features

2. **Performance testing**
   - Compare before/after performance
   - Verify no regressions

3. **Upgrade testing**
   - Test upgrade from previous release
   - Verify deprecation warnings (Release N)
   - Verify clean removal (Release N+1)

**Total Estimated Time**: 
- Release N: 2 weeks (deprecation)
- Release N+1: 2-3 weeks (removal)

## Code Areas of Concern

### Files to Modify/Remove

```
horizon/
├── openstack_dashboard/
│   ├── defaults.py                               # MODIFY: Remove ANGULAR_FEATURES
│   ├── dashboards/
│   │   ├── project/
│   │   │   ├── images/
│   │   │   │   └── views.py                      # MODIFY: Remove Angular toggle
│   │   │   ├── key_pairs/
│   │   │   │   └── views.py                      # MODIFY: Remove Angular toggle
│   │   │   └── ...
│   │   └── identity/
│   │       └── roles/
│   │           └── views.py                      # MODIFY: Remove Angular toggle
│   ├── static/
│   │   └── app/
│   │       └── core/
│   │           ├── images/                       # DELETE entire directory
│   │           ├── keypairs/                     # DELETE entire directory
│   │           ├── flavors/                      # DELETE entire directory
│   │           ├── users/                        # DELETE entire directory
│   │           ├── groups/                       # DELETE entire directory
│   │           └── roles/                        # DELETE entire directory
│   └── test/
│       └── **/test_*.py                          # MODIFY: Remove Angular tests
└── doc/
    └── source/
        ├── configuration/
        │   └── settings.rst                      # MODIFY: Remove ANGULAR_FEATURES
        └── admin/
            └── manage-panels.rst                 # MODIFY: Update panel docs
```

## Proposed Work Items

### Release N (Deprecation)

#### Patchset 1: Add Deprecation Warnings
- Add warnings to `defaults.py`
- Add log messages
- Set all features to `False` (Python versions default)

**Commit**: "Deprecate ANGULAR_FEATURES setting"

#### Patchset 2: Documentation Updates
- Add deprecation notices to docs
- Update release notes
- Create migration guide

**Commit**: "Document ANGULAR_FEATURES deprecation"

### Release N+1 (Removal)

#### Patchset 1: Remove Setting
- Remove `ANGULAR_FEATURES` from `defaults.py`
- Remove feature toggles from panel views
- Update configuration documentation

**Commit**: "Remove deprecated ANGULAR_FEATURES setting"

#### Patchset 2: Remove Angular Code
- Delete Angular panel directories
- Remove Angular template references
- Clean up imports

**Commit**: "Remove AngularJS panel implementations"

#### Patchset 3: Update Tests
- Remove Angular panel tests
- Update mocks/fixtures
- Ensure Python tests comprehensive

**Commit**: "Update tests after AngularJS removal"

#### Patchset 4: Final Documentation
- Update all docs to remove Angular references
- Finalize migration guide
- Update release notes

**Commit**: "Update documentation after AngularJS removal"

## Dependencies

### Upstream Dependencies (MUST BE COMPLETE)
- ✅ OSPRH-12803 (Key Pairs chevrons)
- 📋 OSPRH-12802 (Key Pairs create form)
- 📋 OSPRH-16421 (Images chevrons)
- 📋 OSPRH-16422 (Images filtering)
- 📋 OSPRH-16423 (Images form fields)
- 📋 OSPRH-16424 (Images visibility)
- 📋 OSPRH-16426 (Images actions)
- 📋 OSPRH-16429 (Roles search)

### Downstream Dependencies
- None (this is the final ticket)

## Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Incomplete panel migrations | Critical | Medium | Thorough verification, blocking on all deps |
| Breaking changes for deployers | High | Medium | One release deprecation period, clear migration guide |
| Downstream distribution patches break | High | Medium | Early communication, comprehensive migration guide |
| Hidden Angular dependencies | Medium | Low | Thorough code search, comprehensive testing |
| Performance regressions | Medium | Low | Performance testing before/after |

## Testing Checklist

### Pre-Removal Verification (Release N)
- [ ] All dependent tickets merged
- [ ] Manual testing of all panels complete
- [ ] No regressions identified
- [ ] Deprecation warnings working
- [ ] Documentation published

### Post-Removal Verification (Release N+1)
- [ ] All Angular code removed
- [ ] No references to ANGULAR_FEATURES remain
- [ ] All tests pass
- [ ] No import errors
- [ ] Full regression test suite passes
- [ ] Performance equivalent or better

### Upgrade Testing
- [ ] Upgrade from Release N-1 (before deprecation)
- [ ] Upgrade from Release N (with deprecation)
- [ ] Verify warnings in Release N
- [ ] Verify clean removal in Release N+1

## Communication Plan

### Timeline

**6 Months Before Removal (Release N-1)**:
- Announce plan on openstack-discuss mailing list
- Update project roadmap
- Notify downstream distributions

**Release N (Deprecation)**:
- Release notes prominently feature deprecation
- Warnings in Horizon logs
- Migration guide published
- Announcement email to openstack-discuss

**3 Months Before Removal**:
- Reminder email to openstack-discuss
- Check-in with downstream distributions
- Final call for concerns

**Release N+1 (Removal)**:
- Release notes document removal
- Migration guide updated
- Support available for issues

## References

- [Horizon Deprecation Policy](https://docs.openstack.org/horizon/latest/contributor/topics/deprecation.html)
- [OpenStack Release Schedule](https://releases.openstack.org/)
- [Review 966349: First De-Angularization Complete](https://review.opendev.org/c/openstack/horizon/+/966349)
- [Complete Feature Documentation](../analysis_new_feature_966349/)
- [AngularJS Tickets Overview](../docs/ANGULAR_JS_TICKETS.md)

---

**Status**: 📋 Planning (BLOCKED on dependencies)  
**Assigned To**: TBD  
**Target Completion**: TBD (Release N+1, after all deps complete)  
**Estimated Effort**: 4-5 weeks across two release cycles

