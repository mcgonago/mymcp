# AngularJS De-Angularization Tickets

This document tracks all Jira tickets related to the ongoing effort to remove AngularJS dependencies from OpenStack Horizon and convert panels to use pure Python implementations.

## Overview

The de-angularization initiative aims to modernize the Horizon dashboard by replacing AngularJS-based panels with Django template-based Python implementations. This improves maintainability, reduces technical debt, and aligns with current web development best practices.

## Related Epic

- [OSPRH-12801: Remove angular.js from Horizon](https://issues.redhat.com/browse/OSPRH-12801)

## Ticket Summary

| Ticket | Description | Code Areas of Concern | Status | Spike Doc |
|--------|-------------|------------------------|--------|-----------|
| [OSPRH-15422](https://issues.redhat.com/browse/OSPRH-15422) | Explore the potential DFG:UI contribution for this effort | • Research phase<br>• Documentation<br>• Stakeholder coordination | 📋 Planning | [spike.md](../analysis_new_feature_osprh_15422/spike.md) |
| [OSPRH-12802](https://issues.redhat.com/browse/OSPRH-12802) | Implement key pair create form in Python | • `openstack_dashboard/dashboards/project/key_pairs/forms.py`<br>• `openstack_dashboard/dashboards/project/key_pairs/views.py`<br>• `openstack_dashboard/dashboards/project/key_pairs/templates/key_pairs/create.html`<br>• Form validation logic<br>• Nova client integration | 📋 Planning | [spike.md](../analysis_new_feature_osprh_12802/spike.md) |
| [OSPRH-16421](https://issues.redhat.com/browse/OSPRH-16421) | Add chevrons to the Images table | • `openstack_dashboard/dashboards/project/images/images/tables.py`<br>• `openstack_dashboard/dashboards/project/images/images/templates/images/_images_table.html`<br>• `openstack_dashboard/static/dashboard/project/images/images.js`<br>• `openstack_dashboard/static/dashboard/project/images/images.scss`<br>• Panel registration (`panel.py`)<br>• Bootstrap collapse integration<br>• Font Awesome icons | 📋 Planning | [spike.md](../analysis_new_feature_osprh_16421/spike.md) |
| [OSPRH-16422](https://issues.redhat.com/browse/OSPRH-16422) | Update filtering in the Images table | • `openstack_dashboard/dashboards/project/images/images/tables.py`<br>• Filter action classes<br>• Search functionality<br>• Client-side vs server-side filtering<br>• UI/UX consistency with Angular version | 📋 Planning | [spike.md](../analysis_new_feature_osprh_16422/spike.md) |
| [OSPRH-16423](https://issues.redhat.com/browse/OSPRH-16423) | Add missing fields to the Image Create/Edit form | • `openstack_dashboard/dashboards/project/images/images/forms.py`<br>• Kernel field (`kernel_id`)<br>• Ramdisk field (`ramdisk_id`)<br>• Form validation<br>• Glance API integration<br>• Template updates (`create.html`, `update.html`) | 📋 Planning | [spike.md](../analysis_new_feature_osprh_16423/spike.md) |
| [OSPRH-16424](https://issues.redhat.com/browse/OSPRH-16424) | Update visibility settings in the Image Create/Edit form | • `openstack_dashboard/dashboards/project/images/images/forms.py`<br>• Visibility field options (public, private, shared, community)<br>• Policy-based field rendering<br>• Permissions/RBAC integration<br>• Form templates | 📋 Planning | [spike.md](../analysis_new_feature_osprh_16424/spike.md) |
| [OSPRH-16426](https://issues.redhat.com/browse/OSPRH-16426) | Add activate/deactivate actions to the Images view | • `openstack_dashboard/dashboards/project/images/images/tables.py`<br>• `ActivateImage` action class<br>• `DeactivateImage` action class<br>• Policy checks<br>• Glance API calls (`image.deactivate()`, `image.reactivate()`)<br>• Success/error messages | 📋 Planning | [spike.md](../analysis_new_feature_osprh_16426/spike.md) |
| [OSPRH-16429](https://issues.redhat.com/browse/OSPRH-16429) | Add search/filter to the Roles panel | • `openstack_dashboard/dashboards/identity/roles/tables.py`<br>• `RolesFilterAction` class<br>• Search functionality<br>• Filter implementation<br>• Keystone client integration<br>• UI consistency | 📋 Planning | [spike.md](../analysis_new_feature_osprh_16429/spike.md) |
| [OSPRH-16644](https://issues.redhat.com/browse/OSPRH-16644) | Deprecate and remove angular.js versions of the panels | • `horizon/openstack_dashboard/defaults.py` (ANGULAR_FEATURES)<br>• All Angular JavaScript files<br>• Migration documentation<br>• Deprecation warnings<br>• Release notes<br>• Complete removal of:<br>  - `openstack_dashboard/static/app/core/keypairs/`<br>  - `openstack_dashboard/static/app/core/images/`<br>  - Other Angular panel directories | 📋 Planning | [spike.md](../analysis_new_feature_osprh_16644/spike.md) |

## Status Legend

- 📋 **Planning** - Spike document created, implementation not started
- 🚧 **In Progress** - Active development
- ✅ **Complete** - Merged upstream
- ⏸️ **Blocked** - Waiting on dependencies

## Completed Work

### Review 966349: Key Pairs Expandable Rows (OSPRH-12803)

**Status**: ✅ Merged (+2 approval, Nov 2025)

**Feature**: De-angularized the Key Pairs table by implementing a Bootstrap-based expandable row system that displays detailed key pair information (fingerprint, type, creation date) on demand. This feature replaced the AngularJS implementation with Django templates and CSS-driven interactions.

**Documentation**: [analysis/analysis_new_feature_966349](../analysis_new_feature_966349/)

**Upstream Review**: [https://review.opendev.org/c/openstack/horizon/+/966349](https://review.opendev.org/c/openstack/horizon/+/966349)

---

## Dependencies

### Inter-ticket Dependencies

```
OSPRH-15422 (Research)
    │
    ├─> OSPRH-16421 (Images chevrons)
    ├─> OSPRH-16422 (Images filtering)
    ├─> OSPRH-16423 (Images form fields)
    ├─> OSPRH-16424 (Images visibility)
    ├─> OSPRH-16426 (Images actions)
    ├─> OSPRH-16429 (Roles search)
    └─> OSPRH-12802 (Key pairs create form)
         │
         └─> OSPRH-16644 (Final cleanup & removal)
```

### External Dependencies

- **Bootstrap 3.4**: For UI components and collapse functionality
- **Font Awesome**: For icon support (chevrons, etc.)
- **Django Templates**: For server-side rendering
- **Horizon DataTable Framework**: For table extensibility
- **OpenStack APIs**: Nova, Glance, Keystone clients

---

## Common Patterns Across Tickets

Based on the successfully completed Key Pairs de-angularization (Review 966349), these patterns apply to most tickets:

### 1. Expandable Table Rows (OSPRH-16421)

**Files Modified**:
1. `tables.py` - Add custom `Row` class
2. `expandable_row.html` - Two-row template (summary + detail)
3. `panel.py` - Register CSS/JS files
4. `keypairs.js` - Toggle logic
5. `keypairs.scss` - Styling and animations

### 2. Form Field Additions (OSPRH-16423, OSPRH-16424, OSPRH-12802)

**Files Modified**:
1. `forms.py` - Add form fields, validation
2. `create.html` / `update.html` - Template updates
3. Views if needed (`views.py`)

### 3. Action Additions (OSPRH-16426)

**Files Modified**:
1. `tables.py` - Add action classes
2. Policy checks
3. API integration

### 4. Filter/Search (OSPRH-16422, OSPRH-16429)

**Files Modified**:
1. `tables.py` - Add filter action class
2. Search implementation
3. UI updates

---

## Development Guidelines

### Before Starting Implementation

1. **Review the spike document** for the ticket
2. **Study Review 966349** as a reference implementation: [analysis_new_feature_966349](../analysis_new_feature_966349/)
3. **Review best practices**: [BEST_PRACTICES_FEATURE_DEV.md](BEST_PRACTICES_FEATURE_DEV.md)
4. **Set up dev environment**: [HOWTO_install_devstack_on_psi.org](../analysis_new_feature_966349/HOWTO_install_devstack_on_psi.org) or [HOWTO_install_devstack_on_laptop.org](../analysis_new_feature_966349/HOWTO_install_devstack_on_laptop.org)

### During Implementation

1. **Follow the spike plan** but iterate based on reviewer feedback
2. **Document your work** in `analysis_new_feature_osprh_XXXXX_wip/`
3. **Use consistent Gerrit topic**: `de-angularize`
4. **Test with multiple data items** (3+ rows/objects)
5. **Ensure PEP8 compliance** before submitting each patchset

### After Implementation

1. **Consolidate WIP docs** into polished `analysis_new_feature_osprh_XXXXX/` structure
2. **Update this table** with links to your documentation
3. **Update best practices** if you discover new patterns
4. **Share lessons learned** with the team

---

## Resources

### Documentation

- [Feature Development Workflow Guide](../../usecases/analysis_new_feature/README.md)
- [Best Practices for Feature Development](BEST_PRACTICES_FEATURE_DEV.md)
- [Review 966349 Complete Documentation](../analysis_new_feature_966349/)

### External Resources

- [Bootstrap 3.4 Collapse Component](https://getbootstrap.com/docs/3.4/javascript/#collapse)
- [Django Templates Documentation](https://docs.djangoproject.com/en/5.2/topics/templates/)
- [Horizon DataTables Documentation](https://docs.openstack.org/horizon/latest/contributor/topics/tables.html)
- [OpenDev Gerrit](https://review.opendev.org/)

### MCP Agents

- `@opendev-reviewer-agent` - For Gerrit reviews
- `@jira-agent` - For Jira ticket queries

---

**Total Tickets**: 9  
**Completed**: 1 (OSPRH-12803)  
**In Progress**: 0  
**Planning**: 8  
**Last Updated**: November 15, 2025

