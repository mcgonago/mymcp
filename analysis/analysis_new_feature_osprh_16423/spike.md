# Spike: OSPRH-16423 - Add Missing Fields to Image Create/Edit Form

**Jira**: [OSPRH-16423](https://issues.redhat.com/browse/OSPRH-16423)  
**Epic**: [OSPRH-12801](https://issues.redhat.com/browse/OSPRH-12801) - Remove angular.js from Horizon  
**Type**: Feature Enhancement  
**Estimated Complexity**: Low-Medium  
**Date Created**: November 15, 2025

---

## Overview

Add missing **Kernel** and **Ramdisk** fields to the Image Create and Edit forms in the Python version to match the AngularJS implementation.

## Problem Statement

The Angular versions of the Image Create and Edit forms include Kernel and Ramdisk fields that are missing from the Python version. These fields are important for certain image types (particularly machine images that boot with specific kernels).

### Current State (Angular)
- ✅ Kernel field (dropdown or UUID input)
- ✅ Ramdisk field (dropdown or UUID input)
- ✅ Fields appear when relevant

### Current State (Python)
- ❌ No Kernel field
- ❌ No Ramdisk field
- Users cannot specify kernel/ramdisk on create/edit

### Desired State
- Kernel field added
- Ramdisk field added
- Fields populated with available kernel/ramdisk images
- Form validation ensures valid UUIDs

## Success Criteria

- [ ] Kernel field added to Create form
- [ ] Kernel field added to Edit/Update form
- [ ] Ramdisk field added to Create form
- [ ] Ramdisk field added to Edit/Update form
- [ ] Fields populated with appropriate image choices
- [ ] Form validation for UUIDs
- [ ] Fields conditionally shown (if applicable)
- [ ] PEP8 compliant
- [ ] Tested with kernel/ramdisk images
- [ ] Upstream review submitted with topic: `de-angularize`

## Key Technical Areas

### 1. Understanding Kernel/Ramdisk Images

In OpenStack Glance:
- **Kernel images**: Images with `disk_format = aki` (Amazon Kernel Image)
- **Ramdisk images**: Images with `disk_format = ari` (Amazon Ramdisk Image)
- **Machine images**: Images that reference a kernel and/or ramdisk

**Use case**: Some machine images (especially older AMI-style images) require a separate kernel and ramdisk to boot.

### 2. Glance API Properties

| Property | Type | Description |
|----------|------|-------------|
| `kernel_id` | UUID (optional) | ID of kernel image to use |
| `ramdisk_id` | UUID (optional) | ID of ramdisk image to use |

### 3. Form Implementation Strategy

**Option A: Dropdown (Preferred)**
- Query Glance for images with `disk_format=aki` (kernels)
- Query Glance for images with `disk_format=ari` (ramdisks)
- Populate dropdown with names and IDs
- Better UX (user doesn't need to know UUIDs)

**Option B: Text Input**
- User enters kernel UUID manually
- User enters ramdisk UUID manually
- Simpler implementation but worse UX

**Decision**: Option A (dropdown) for better UX

## Investigation Plan

### Phase 1: Angular Analysis (1 day)
1. Document how Angular implements these fields
   - Field types (dropdown vs. text)
   - When fields are shown
   - How choices are populated
   - Validation behavior

2. Test Angular form behavior
   - Create image with kernel/ramdisk
   - Edit image to change kernel/ramdisk
   - Remove kernel/ramdisk
   - Edge cases (no kernels available, invalid UUIDs)

### Phase 2: Implementation (3 days)

#### Step 1: Update Forms (`forms.py`)

```python
# forms.py
class CreateImageForm(forms.SelfHandlingForm):
    # ... existing fields ...
    
    kernel = forms.ChoiceField(
        label=_("Kernel"),
        required=False,
        help_text=_("Optional: Kernel image to use for booting")
    )
    
    ramdisk = forms.ChoiceField(
        label=_("Ramdisk"),
        required=False,
        help_text=_("Optional: Ramdisk image to use for booting")
    )
    
    def __init__(self, request, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        
        # Populate kernel choices
        try:
            kernels = api.glance.image_list_detailed(
                request, filters={'disk_format': 'aki'}
            )[0]
            kernel_choices = [('', _("No kernel"))]
            kernel_choices.extend([
                (kernel.id, kernel.name or kernel.id)
                for kernel in kernels
            ])
            self.fields['kernel'].choices = kernel_choices
        except Exception:
            self.fields['kernel'].choices = [('', _("No kernels available"))]
        
        # Populate ramdisk choices
        try:
            ramdisks = api.glance.image_list_detailed(
                request, filters={'disk_format': 'ari'}
            )[0]
            ramdisk_choices = [('', _("No ramdisk"))]
            ramdisk_choices.extend([
                (ramdisk.id, ramdisk.name or ramdisk.id)
                for ramdisk in ramdisks
            ])
            self.fields['ramdisk'].choices = ramdisk_choices
        except Exception:
            self.fields['ramdisk'].choices = [('', _("No ramdisks available"))]
    
    def handle(self, request, data):
        # ... existing code ...
        
        # Add kernel_id and ramdisk_id to image properties
        if data.get('kernel'):
            properties['kernel_id'] = data['kernel']
        if data.get('ramdisk'):
            properties['ramdisk_id'] = data['ramdisk']
        
        # ... rest of handle logic ...
```

#### Step 2: Update Templates

```django
{# create.html and update.html #}
<div class="form-group">
  {{ form.kernel|as_bootstrap }}
</div>

<div class="form-group">
  {{ form.ramdisk|as_bootstrap }}
</div>
```

#### Step 3: Update Edit Form Similarly

```python
class UpdateImageForm(forms.SelfHandlingForm):
    # ... similar changes as CreateImageForm ...
    
    def __init__(self, request, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        
        # Pre-populate with current values
        image = kwargs.get('initial', {}).get('image')
        if image:
            self.fields['kernel'].initial = getattr(image, 'kernel_id', '')
            self.fields['ramdisk'].initial = getattr(image, 'ramdisk_id', '')
        
        # ... populate choices as in CreateImageForm ...
```

### Phase 3: Testing (2 days)
1. **Functional Testing**
   - [ ] Create image without kernel/ramdisk
   - [ ] Create image with kernel only
   - [ ] Create image with ramdisk only
   - [ ] Create image with both kernel and ramdisk
   - [ ] Edit image to add kernel/ramdisk
   - [ ] Edit image to remove kernel/ramdisk
   - [ ] Edit image to change kernel/ramdisk

2. **Edge Cases**
   - [ ] No kernel images available
   - [ ] No ramdisk images available
   - [ ] Invalid image selected
   - [ ] Form submission with empty choices

3. **API Verification**
   - Verify image created with correct `kernel_id` property
   - Verify image created with correct `ramdisk_id` property
   - Use `openstack image show <id>` to check properties

### Phase 4: Documentation (1 day)

**Total Estimated Time**: 7 days (1.5 sprints)

## Code Areas of Concern

```
openstack_dashboard/dashboards/project/images/images/
├── forms.py                          # MODIFY: Add kernel/ramdisk fields
├── templates/
│   └── images/
│       └── images/
│           ├── create.html           # MODIFY: Add field rendering
│           └── update.html           # MODIFY: Add field rendering
└── tests/
    ├── test_forms.py                 # MODIFY: Add test cases
    └── test_views.py                 # MODIFY: Add test cases
```

## Proposed Work Items

### Patchset 1: Add Fields to Create Form
- Add kernel and ramdisk fields to `CreateImageForm`
- Populate dropdowns with available images
- Update create.html template
- Basic validation

**Commit**: "Add kernel and ramdisk fields to Image Create form"

### Patchset 2: Add Fields to Edit Form
- Add kernel and ramdisk fields to `UpdateImageForm`
- Pre-populate with current values
- Update update.html template
- Handle empty values

**Commit**: "Add kernel and ramdisk fields to Image Edit form"

### Patchset 3: Error Handling & Polish
- Improve error messages
- Handle API failures gracefully
- Optimize queries (caching?)
- Address reviewer feedback

**Commit**: "Improve kernel/ramdisk field handling"

### Patchset 4: Tests
- Unit tests for form initialization
- Unit tests for form validation
- Unit tests for form handling
- PEP8 compliance

**Commit**: "Add tests for kernel/ramdisk fields"

## Dependencies

### Upstream Dependencies
- None (can start immediately)

### Downstream Dependencies
- None

## Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Performance with many kernel/ramdisk images | Low | Low | Pagination or lazy loading if needed |
| Glance API filter issues | Medium | Low | Test thoroughly, add error handling |
| User confusion about when to use | Low | Medium | Add helpful tooltips/help text |

## Testing Checklist

### Setup
1. Create test kernel image:
   ```bash
   openstack image create \
     --disk-format aki \
     --container-format aki \
     --file vmlinuz-test \
     test-kernel
   ```

2. Create test ramdisk image:
   ```bash
   openstack image create \
     --disk-format ari \
     --container-format ari \
     --file initrd-test \
     test-ramdisk
   ```

### Test Cases
- [ ] Kernel dropdown populated correctly
- [ ] Ramdisk dropdown populated correctly
- [ ] Can create image with kernel
- [ ] Can create image with ramdisk
- [ ] Can create image with both
- [ ] Can edit to add kernel/ramdisk
- [ ] Can edit to remove kernel/ramdisk
- [ ] Fields optional (can submit empty)
- [ ] API properties set correctly

## References

- [Glance Image Properties](https://docs.openstack.org/glance/latest/admin/useful-image-properties.html)
- [AMI Image Format](https://docs.openstack.org/image-guide/obtain-images.html)
- [Horizon Forms Documentation](https://docs.openstack.org/horizon/latest/contributor/topics/forms.html)
- [AngularJS Tickets Overview](../docs/ANGULAR_JS_TICKETS.md)

---

**Status**: 📋 Planning  
**Assigned To**: TBD  
**Target Completion**: TBD  
**Estimated Effort**: 7 days (1.5 sprints)

