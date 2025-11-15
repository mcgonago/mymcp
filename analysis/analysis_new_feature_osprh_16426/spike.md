# Spike: OSPRH-16426 - Add Activate/Deactivate Actions to Images View

**Jira**: [OSPRH-16426](https://issues.redhat.com/browse/OSPRH-16426)  
**Epic**: [OSPRH-12801](https://issues.redhat.com/browse/OSPRH-12801) - Remove angular.js from Horizon  
**Type**: Feature Enhancement  
**Estimated Complexity**: Low-Medium  
**Date Created**: November 15, 2025

---

## Overview

Add activate and deactivate actions to the Images table to match the functionality available in the AngularJS version. These actions allow administrators to temporarily disable images without deleting them.

## Problem Statement

The Angular version allows users (typically admins) to activate/deactivate images, which changes their status and prevents instances from being launched with deactivated images. The Python version lacks this functionality.

### Current State (Angular)
- ✅ Activate action (changes status: deactivated → active)
- ✅ Deactivate action (changes status: active → deactivated)
- ✅ Actions shown based on current image status
- ✅ Policy-based permissions

### Current State (Python)
- ❌ No activate action
- ❌ No deactivate action
- Must use CLI or API to activate/deactivate

### Desired State
- Activate action available for deactivated images
- Deactivate action available for active images
- Policy checks enforce permissions
- Clear success/error messages

## Success Criteria

- [ ] Activate action added to Images table
- [ ] Deactivate action added to Images table
- [ ] Actions shown/hidden based on image status
- [ ] Policy checks implemented
- [ ] Success/error messages displayed
- [ ] Actions work for single images
- [ ] Batch actions supported (optional)
- [ ] PEP8 compliant
- [ ] Tested with various image statuses
- [ ] Upstream review submitted with topic: `de-angularize`

## Key Technical Areas

### 1. Glance Image Status

Glance images have several status values:
- `active` - Image is ready to use
- `deactivated` - Image is disabled (cannot launch instances)
- `queued` - Image metadata created, data not uploaded
- `saving` - Image data being uploaded
- `deleted` - Image is deleted
- Other statuses (killed, pending_delete, etc.)

**Relevant actions**:
- `deactivate()` - Changes `active` → `deactivated`
- `reactivate()` - Changes `deactivated` → `active`

### 2. Glance API

```python
# Deactivate an image
glance.images.deactivate(image_id)

# Reactivate an image
glance.images.reactivate(image_id)
```

### 3. Horizon Action Pattern

```python
class DeactivateImage(tables.Action):
    name = "deactivate"
    
    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            "Deactivate Image",
            "Deactivate Images",
            count
        )
    
    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            "Deactivated Image",
            "Deactivated Images",
            count
        )
    
    def allowed(self, request, image=None):
        # Only show for active images
        # Only show if user has permission
        pass
    
    def action(self, request, obj_id):
        # Call Glance API to deactivate
        pass
```

## Investigation Plan

### Phase 1: Angular Analysis (1 day)
1. Document Angular implementation
   - Where are actions located? (row actions? batch actions?)
   - When are they shown/hidden?
   - What confirmation dialogs appear?
   - What success/error messages?

2. Test Angular actions
   - Deactivate an active image
   - Try to launch instance with deactivated image (should fail)
   - Reactivate a deactivated image
   - Try actions on images with different statuses

3. Document policy requirements
   - What policy rules gate these actions?
   - Different behavior for admins vs. regular users?

### Phase 2: Implementation (2 days)

#### Step 1: Add Actions to `tables.py`

```python
# tables.py
from openstack_dashboard import api
from openstack_dashboard import policy

class DeactivateImage(policy.PolicyTargetMixin, tables.Action):
    name = "deactivate"
    policy_rules = (("image", "deactivate"),)
    
    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            "Deactivate Image",
            "Deactivate Images",
            count
        )
    
    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            "Deactivated Image",
            "Deactivated Images",
            count
        )
    
    def allowed(self, request, image=None):
        """Only allow for active images."""
        if image:
            return image.status == 'active'
        return False
    
    def action(self, request, obj_id):
        try:
            api.glance.image_deactivate(request, obj_id)
            messages.success(request, _("Image deactivated successfully."))
        except Exception as e:
            messages.error(request, _("Failed to deactivate image: %s") % e)


class ActivateImage(policy.PolicyTargetMixin, tables.Action):
    name = "activate"
    policy_rules = (("image", "reactivate"),)
    
    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            "Activate Image",
            "Activate Images",
            count
        )
    
    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            "Activated Image",
            "Activated Images",
            count
        )
    
    def allowed(self, request, image=None):
        """Only allow for deactivated images."""
        if image:
            return image.status == 'deactivated'
        return False
    
    def action(self, request, obj_id):
        try:
            api.glance.image_reactivate(request, obj_id)
            messages.success(request, _("Image activated successfully."))
        except Exception as e:
            messages.error(request, _("Failed to activate image: %s") % e)


class ImagesTable(tables.DataTable):
    # ... existing columns ...
    
    class Meta(object):
        name = "images"
        verbose_name = _("Images")
        # ... existing meta ...
        row_actions = (
            # ... existing actions ...
            DeactivateImage,
            ActivateImage,
            # ... existing actions ...
        )
```

#### Step 2: Add API Methods (if missing)

```python
# openstack_dashboard/api/glance.py
def image_deactivate(request, image_id):
    """Deactivate an image."""
    image = glanceclient(request).images.deactivate(image_id)
    return image

def image_reactivate(request, image_id):
    """Reactivate an image."""
    image = glanceclient(request).images.reactivate(image_id)
    return image
```

#### Step 3: Verify Policy Rules

Check `openstack_dashboard/conf/glance_policy.yaml` (or default policy):
```yaml
"deactivate": "rule:admin_or_owner"
"reactivate": "rule:admin_or_owner"
```

### Phase 3: Testing (2 days)
1. **Functional Testing**
   - [ ] Deactivate an active image
   - [ ] Verify image status changed to `deactivated`
   - [ ] Verify action no longer appears for deactivated image
   - [ ] Verify activate action now appears
   - [ ] Activate the deactivated image
   - [ ] Verify image status changed to `active`
   - [ ] Try to launch instance with deactivated image (should fail in Nova)

2. **Policy Testing**
   - [ ] Admin user can deactivate/activate images
   - [ ] Image owner can deactivate/activate own images
   - [ ] Regular user cannot deactivate/activate others' images

3. **Edge Cases**
   - [ ] Try to deactivate already deactivated image (action hidden)
   - [ ] Try to activate already active image (action hidden)
   - [ ] Try actions on images with other statuses (queued, saving, etc.)
   - [ ] API failure handling

4. **Verification Commands**
   ```bash
   # Check image status
   openstack image show <image-id> -f value -c status
   
   # Should show "deactivated" after deactivate action
   # Should show "active" after activate action
   
   # Try to launch instance with deactivated image (should fail)
   openstack server create --image <deactivated-image-id> --flavor m1.small test-vm
   ```

### Phase 4: Documentation (1 day)

**Total Estimated Time**: 6 days (1+ sprint)

## Code Areas of Concern

```
openstack_dashboard/
├── dashboards/
│   └── project/
│       └── images/
│           └── images/
│               ├── tables.py              # MODIFY: Add action classes
│               └── tests/
│                   └── test_tables.py     # MODIFY: Add test cases
└── api/
    └── glance.py                          # MODIFY: Add deactivate/reactivate methods (if missing)
```

## Proposed Work Items

### Patchset 1: Add Actions
- Add `DeactivateImage` action class
- Add `ActivateImage` action class
- Register actions in `ImagesTable.Meta.row_actions`
- Basic policy checks

**Commit**: "Add activate/deactivate actions to Images table"

### Patchset 2: API Integration
- Add `image_deactivate()` to `api/glance.py` (if missing)
- Add `image_reactivate()` to `api/glance.py` (if missing)
- Error handling
- Success messages

**Commit**: "Add Glance API methods for image activation"

### Patchset 3: Testing & Polish
- Unit tests for actions
- Unit tests for `allowed()` method
- Integration testing
- PEP8 compliance

**Commit**: "Add tests for image activate/deactivate actions"

## Dependencies

### Upstream Dependencies
- None (can start immediately)

### Downstream Dependencies
- None

## Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Glance API version differences | Medium | Low | Check glanceclient version, add version check if needed |
| Policy rules missing/incorrect | High | Low | Test with multiple user roles, verify policy files |
| User confusion about deactivate vs. delete | Medium | Medium | Clear action names, confirmation dialogs, help text |

## Testing Checklist

### Setup
```bash
# Create a test image
openstack image create \
  --disk-format qcow2 \
  --container-format bare \
  --file cirros.qcow2 \
  test-activation-image
```

### Test Cases
- [ ] Deactivate action appears for active image
- [ ] Click deactivate action
- [ ] Success message displayed
- [ ] Image status is now `deactivated`
- [ ] Deactivate action no longer appears
- [ ] Activate action now appears
- [ ] Click activate action
- [ ] Success message displayed
- [ ] Image status is now `active`
- [ ] Deactivate action appears again

### Policy Tests
- [ ] Admin can deactivate any image
- [ ] Image owner can deactivate own image
- [ ] Non-owner cannot deactivate others' image
- [ ] Actions hidden when user lacks permission

### Nova Integration Test
- [ ] Create VM with active image (success)
- [ ] Deactivate image
- [ ] Try to create VM with deactivated image (should fail with clear error)
- [ ] Reactivate image
- [ ] Create VM with reactivated image (success)

## References

- [Glance Image Deactivation](https://docs.openstack.org/glance/latest/admin/image-deactivation.html)
- [Glance Images API - Deactivate](https://docs.openstack.org/api-ref/image/v2/#deactivate-image)
- [Glance Images API - Reactivate](https://docs.openstack.org/api-ref/image/v2/#reactivate-image)
- [Horizon Actions Documentation](https://docs.openstack.org/horizon/latest/contributor/topics/tables.html#table-actions)
- [AngularJS Tickets Overview](../docs/ANGULAR_JS_TICKETS.md)

---

**Status**: 📋 Planning  
**Assigned To**: TBD  
**Target Completion**: TBD  
**Estimated Effort**: 6 days (1+ sprint)

