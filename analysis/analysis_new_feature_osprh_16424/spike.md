# Spike: OSPRH-16424 - Update Visibility Settings in Image Create/Edit Form

**Jira**: [OSPRH-16424](https://issues.redhat.com/browse/OSPRH-16424)  
**Epic**: [OSPRH-12801](https://issues.redhat.com/browse/OSPRH-12801) - Remove angular.js from Horizon  
**Related**: OSPRH-16423 (Image form fields)  
**Type**: Feature Enhancement  
**Estimated Complexity**: Medium  
**Date Created**: November 15, 2025

---

## Overview

Update the Image Create and Edit forms to include all visibility options available in the AngularJS version. The Python version has limited visibility options compared to Angular.

## Problem Statement

The Angular version provides more granular visibility settings than the Python version. Users need access to all visibility options to properly manage image sharing and access control.

### Current State (Angular)
- ✅ Public
- ✅ Private
- ✅ Shared
- ✅ Community
- Policy-based field rendering

### Current State (Python)
- ✅ Public
- ✅ Private
- ❌ Shared (missing)
- ❌ Community (missing)
- Limited options

### Desired State
- All four visibility options available
- Policy-aware rendering (only show options user has permission for)
- Proper Glance API integration

## Success Criteria

- [ ] All visibility options implemented (public, private, shared, community)
- [ ] Policy checks determine which options are shown
- [ ] Shared visibility properly creates/updates image members
- [ ] Community visibility properly set
- [ ] Form validation ensures valid visibility transitions
- [ ] Help text explains each visibility option
- [ ] PEP8 compliant
- [ ] Tested with various user roles
- [ ] Upstream review submitted with topic: `de-angularize`

## Key Technical Areas

### 1. Glance Image Visibility

Glance v2 supports four visibility levels:

| Visibility | Description | Who Can See | Who Can Use |
|------------|-------------|-------------|-------------|
| **public** | Available to all users | Everyone | Everyone |
| **private** | Available only to owner | Owner only | Owner only |
| **shared** | Available to specific tenants | Owner + specified projects | Owner + specified projects |
| **community** | Available to all, but not validated | Everyone | Everyone |

### 2. Policy Considerations

Visibility options are governed by Glance policies:
- `publicize_image` - Can set visibility to `public`
- `communitize_image` - Can set visibility to `community`
- User's project membership determines `shared` capabilities

### 3. Image Members (Shared Visibility)

When visibility is `shared`:
- Must specify which projects can access the image
- Uses Glance Image Members API
- Requires additional form UI for project selection

## Investigation Plan

### Phase 1: Angular Analysis (2 days)
1. **Document Angular Visibility UI**
   - Screenshot visibility field options
   - Document conditional rendering (policy-based)
   - Test shared visibility → project selection UI
   - Document validation and error messages

2. **Test Each Visibility Type**
   - Create image as public (admin role)
   - Create image as private (regular user)
   - Create image as shared + add projects
   - Create image as community (if allowed)
   - Edit image to change visibility
   - Document state transitions (e.g., public → private allowed?)

3. **Map to Glance API**
   - `visibility` field in image properties
   - Image Members API for shared images
   - Policy checks required

### Phase 2: Implementation (5 days)

#### Step 1: Update Visibility Field in Forms

```python
# forms.py
class CreateImageForm(forms.SelfHandlingForm):
    # ... existing fields ...
    
    visibility = forms.ChoiceField(
        label=_("Visibility"),
        required=False,
        help_text=_("Determines who can see and use this image"),
        initial='private'
    )
    
    # For shared visibility
    shared_with = forms.MultipleChoiceField(
        label=_("Share with Projects"),
        required=False,
        widget=forms.CheckboxSelectMultiple(),
        help_text=_("Select projects to share this image with")
    )
    
    def __init__(self, request, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        
        # Build visibility choices based on policy
        visibility_choices = [
            ('private', _('Private - visible only to you')),
        ]
        
        # Check if user can create public images
        if policy.check((("image", "publicize_image"),), request):
            visibility_choices.append(
                ('public', _('Public - visible to all users'))
            )
        
        # Check if user can create community images
        if policy.check((("image", "communitize_image"),), request):
            visibility_choices.append(
                ('community', _('Community - visible to all but not official'))
            )
        
        # Shared is always available
        visibility_choices.append(
            ('shared', _('Shared - visible to specific projects'))
        )
        
        self.fields['visibility'].choices = visibility_choices
        
        # Populate projects for sharing (if user is admin or has cross-project view)
        if has_permission_to_share(request):
            projects = get_accessible_projects(request)
            self.fields['shared_with'].choices = [
                (project.id, project.name) for project in projects
            ]
    
    def clean(self):
        cleaned_data = super().clean()
        visibility = cleaned_data.get('visibility')
        shared_with = cleaned_data.get('shared_with', [])
        
        # If visibility is shared, must select at least one project
        if visibility == 'shared' and not shared_with:
            raise forms.ValidationError(
                _("You must select at least one project to share with")
            )
        
        return cleaned_data
    
    def handle(self, request, data):
        # ... create image ...
        
        # Set visibility
        image_properties['visibility'] = data.get('visibility', 'private')
        
        # If shared, create image members
        if data['visibility'] == 'shared':
            image = api.glance.image_create(request, **image_properties)
            for project_id in data['shared_with']:
                try:
                    api.glance.image_member_create(
                        request, image.id, project_id
                    )
                except Exception as e:
                    messages.error(request, f"Failed to share with {project_id}: {e}")
            return image
        else:
            return api.glance.image_create(request, **image_properties)
```

#### Step 2: Add JavaScript for Dynamic UI

```javascript
// images.js
$(function() {
    var $visibilityField = $('#id_visibility');
    var $sharedWithField = $('#id_shared_with').closest('.form-group');
    
    function toggleSharedProjects() {
        if ($visibilityField.val() === 'shared') {
            $sharedWithField.show();
        } else {
            $sharedWithField.hide();
        }
    }
    
    $visibilityField.on('change', toggleSharedProjects);
    toggleSharedProjects(); // Initial state
});
```

#### Step 3: Update Templates

```django
{# create.html #}
<div class="form-group">
  {{ form.visibility|as_bootstrap }}
</div>

<div class="form-group" id="shared-projects-group">
  {{ form.shared_with|as_bootstrap }}
  <p class="help-block">
    {% trans "This image will be visible to the selected projects." %}
  </p>
</div>
```

#### Step 4: Update Edit Form

```python
class UpdateImageForm(forms.SelfHandlingForm):
    # Similar to CreateImageForm
    
    def __init__(self, request, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        
        # Pre-populate with current visibility
        image = kwargs.get('initial', {}).get('image')
        if image:
            self.fields['visibility'].initial = getattr(image, 'visibility', 'private')
            
            # If currently shared, load existing members
            if image.visibility == 'shared':
                members = api.glance.image_member_list(request, image.id)
                self.fields['shared_with'].initial = [m.member_id for m in members]
    
    def handle(self, request, data):
        # Update image visibility
        image_id = data['image_id']
        
        # Update visibility property
        api.glance.image_update(request, image_id, visibility=data['visibility'])
        
        # Handle shared visibility changes
        if data['visibility'] == 'shared':
            # Get current members
            current_members = {
                m.member_id for m in api.glance.image_member_list(request, image_id)
            }
            new_members = set(data['shared_with'])
            
            # Add new members
            for project_id in new_members - current_members:
                api.glance.image_member_create(request, image_id, project_id)
            
            # Remove old members
            for project_id in current_members - new_members:
                api.glance.image_member_delete(request, image_id, project_id)
        else:
            # If visibility changed from shared to something else, remove all members
            members = api.glance.image_member_list(request, image_id)
            for member in members:
                api.glance.image_member_delete(request, image_id, member.member_id)
```

### Phase 3: Testing (3 days)
1. **Policy Testing** (different user roles)
   - Admin user: all options available
   - Regular user: limited options
   - Project member: appropriate options

2. **Visibility Testing**
   - Create image with each visibility type
   - Edit image to change visibility
   - Test visibility transitions (public → private, etc.)

3. **Shared Visibility Testing**
   - Create shared image with 1 project
   - Create shared image with multiple projects
   - Edit to add projects
   - Edit to remove projects
   - Edit to change from shared to private (members removed?)

4. **Edge Cases**
   - User without policy permission tries to create public image
   - Shared image with no projects selected (validation error)
   - Image member API failures

### Phase 4: Documentation (1 day)

**Total Estimated Time**: 11 days (2+ sprints)

## Code Areas of Concern

```
openstack_dashboard/dashboards/project/images/images/
├── forms.py                          # MODIFY: Add visibility options, shared_with field
├── views.py                          # MODIFY: Handle image members
├── templates/
│   └── images/
│       └── images/
│           ├── create.html           # MODIFY: Add visibility and shared_with rendering
│           └── update.html           # MODIFY: Add visibility and shared_with rendering
└── static/
    └── dashboard/
        └── project/
            └── images/
                └── images/
                    └── images.js     # MODIFY: Toggle shared_with field
```

## Glance API Calls Required

```python
# Set visibility
api.glance.image_update(request, image_id, visibility='shared')

# List image members
members = api.glance.image_member_list(request, image_id)

# Create image member
api.glance.image_member_create(request, image_id, member_project_id)

# Delete image member
api.glance.image_member_delete(request, image_id, member_project_id)
```

## Proposed Work Items

### Patchset 1: Add All Visibility Options
- Add visibility choices (public, private, shared, community)
- Policy-based option filtering
- Update Create form

**Commit**: "Add all visibility options to Image Create form"

### Patchset 2: Shared Visibility + Project Selection
- Add shared_with field
- Populate with project choices
- JavaScript to toggle field visibility
- Image Members API integration

**Commit**: "Add project selection for shared image visibility"

### Patchset 3: Update Form Support
- Add visibility options to Edit form
- Pre-populate current visibility
- Handle image member updates

**Commit**: "Add visibility options to Image Edit form"

### Patchset 4: Testing & Polish
- Comprehensive testing
- Error handling
- UI refinements
- PEP8 compliance

**Commit**: "Improve visibility handling and add tests"

## Dependencies

### Upstream Dependencies
- OSPRH-16423 (Image form fields) - can proceed in parallel

### Downstream Dependencies
- None

## Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Policy complexity | High | Medium | Thorough testing with multiple user roles |
| Image Members API issues | Medium | Low | Robust error handling, transaction-like logic |
| User confusion about visibility types | Medium | Medium | Clear help text, tooltips, documentation |
| Visibility transition rules | High | Low | Research Glance API constraints, test thoroughly |

## Testing Checklist

### Admin User Tests
- [ ] Can create public image
- [ ] Can create private image
- [ ] Can create shared image
- [ ] Can create community image
- [ ] Can edit visibility of any image

### Regular User Tests
- [ ] Cannot create public image (option not shown)
- [ ] Can create private image
- [ ] Can create shared image
- [ ] Can/cannot create community image (policy dependent)
- [ ] Can only edit own images

### Shared Visibility Tests
- [ ] Create image shared with 1 project
- [ ] Create image shared with 3 projects
- [ ] Edit to add a project
- [ ] Edit to remove a project
- [ ] Edit to change from shared to private (members removed)
- [ ] Verify members via API: `openstack image member list <image-id>`

## References

- [Glance Image Visibility](https://docs.openstack.org/glance/latest/user/glancemetadefcatalogapi.html#image-visibility)
- [Glance Image Sharing](https://docs.openstack.org/glance/latest/admin/sharing.html)
- [Image Members API](https://docs.openstack.org/api-ref/image/v2/#image-members)
- [Glance Policies](https://docs.openstack.org/glance/latest/configuration/policy.html)
- [AngularJS Tickets Overview](../docs/ANGULAR_JS_TICKETS.md)

---

**Status**: 📋 Planning  
**Assigned To**: TBD  
**Target Completion**: TBD  
**Estimated Effort**: 11 days (2+ sprints)

