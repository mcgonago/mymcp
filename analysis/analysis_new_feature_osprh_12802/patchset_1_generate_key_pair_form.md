# Patchset 1: Generate Key Pair Form Implementation

**Date**: TBD  
**Jira**: [OSPRH-12802](https://issues.redhat.com/browse/OSPRH-12802)  
**Status**: 📋 Planning  
**Estimated Effort**: 2 days

---

## View Patchset Changes

### After implementation, compare changes:
```bash
# Set up your working directory
cd /home/omcgonag/Work/mymcp/workspace
git clone https://review.opendev.org/openstack/horizon horizon-osprh-12802-working
cd horizon-osprh-12802-working
git checkout -b osprh-12802-generate-form

# After making changes, view your work
git diff --stat
git diff
```

### Submit for review:
```bash
# Add and commit your changes
git add openstack_dashboard/dashboards/project/key_pairs/
git commit

# Use this commit message template (see below)

# Submit to Gerrit
git review
```

---

## Executive Summary

**Goal**: Implement the "Generate Key Pair" form using Python/Django, replacing the AngularJS implementation.

**Approach**: 
- Create `GenerateKeyPairForm` inheriting from `horizon.forms.SelfHandlingForm`
- Add `CreateView` as a modal form view
- Create Django template for the form
- Handle form submission and Nova API interaction
- Return generated private key for download

**Files to Create/Modify**:
- `forms.py` - Add `GenerateKeyPairForm` class
- `views.py` - Add `CreateView` class
- `templates/key_pairs/create.html` - Form template
- `urls.py` - Add URL pattern for create view

**Result**: Users can generate new SSH or X509 key pairs through a pure Python implementation, receiving the private key for download.

---

## Implementation Details

### Problem Statement

The Key Pairs panel currently relies on AngularJS for the key pair generation form. This patchset implements the "Generate" workflow where:

1. User provides a **name** for the key pair
2. User optionally selects a **key type** (SSH or X509)
3. Server generates the key pair via Nova API
4. Private key is returned to user for download
5. Public key is stored in Nova

**Key Difference from Import**: Generate creates both keys server-side; Import only stores a user-provided public key.

---

## Step-by-Step Implementation

### Step 1: Create `GenerateKeyPairForm` in `forms.py`

**File**: `openstack_dashboard/dashboards/project/key_pairs/forms.py`

**What to add**:

```python
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages

from openstack_dashboard import api


class GenerateKeyPairForm(forms.SelfHandlingForm):
    """Form for generating a new key pair (server-generated keys)."""
    
    name = forms.CharField(
        max_length=255,
        label=_("Key Pair Name"),
        help_text=_("Name for the new key pair"),
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('my-keypair'),
            'autofocus': 'autofocus'
        })
    )
    
    key_type = forms.ChoiceField(
        label=_("Key Type"),
        choices=[
            ('ssh', _('SSH Key')),
            ('x509', _('X509 Certificate'))
        ],
        initial='ssh',
        required=False,
        help_text=_("Type of key pair to generate (SSH is recommended)")
    )
    
    def __init__(self, request, *args, **kwargs):
        super(GenerateKeyPairForm, self).__init__(request, *args, **kwargs)
        
    def clean_name(self):
        """Validate key pair name format."""
        name = self.cleaned_data.get('name')
        
        if not name:
            raise forms.ValidationError(_("Key pair name is required"))
        
        # Validate name pattern (alphanumeric, hyphens, underscores)
        import re
        if not re.match(r'^[a-zA-Z0-9-_]+$', name):
            raise forms.ValidationError(
                _("Key pair name can only contain letters, numbers, "
                  "hyphens, and underscores")
            )
        
        return name
    
    def handle(self, request, data):
        """Generate the key pair via Nova API."""
        try:
            # Call Nova API to generate key pair
            keypair = api.nova.keypair_create(
                request,
                data['name'],
                key_type=data.get('key_type', 'ssh')
            )
            
            # Store private key in session for download page
            # (We'll handle download in Patchset 3, for now just show message)
            if hasattr(keypair, 'private_key'):
                request.session['keypair_private_key'] = keypair.private_key
                request.session['keypair_name'] = keypair.name
            
            messages.success(
                request,
                _('Successfully created key pair "%(name)s". '
                  'Your private key is ready for download.') % {'name': data['name']}
            )
            
            return keypair
            
        except Exception as e:
            exceptions.handle(
                request,
                _('Unable to create key pair: %s') % str(e)
            )
            return False
```

**Key Points**:

1. **Inherits from `SelfHandlingForm`**: This is the Horizon pattern for forms that handle their own API calls
2. **Two fields**: `name` (required) and `key_type` (optional, defaults to 'ssh')
3. **Validation**: `clean_name()` ensures name follows Nova's requirements
4. **API Call**: Uses `api.nova.keypair_create()` to generate the key pair
5. **Session Storage**: Temporarily stores private key in session for download (Patchset 3 will handle download)
6. **Error Handling**: Uses Horizon's `exceptions.handle()` for consistent error messages

---

### Step 2: Create `CreateView` in `views.py`

**File**: `openstack_dashboard/dashboards/project/key_pairs/views.py`

**What to add**:

```python
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from horizon import forms as horizon_forms

from openstack_dashboard.dashboards.project.key_pairs \
    import forms as project_forms


class CreateView(horizon_forms.ModalFormView):
    """View for generating a new key pair."""
    
    form_class = project_forms.GenerateKeyPairForm
    template_name = 'project/key_pairs/create.html'
    success_url = reverse_lazy('horizon:project:key_pairs:index')
    modal_id = "create_keypair_modal"
    modal_header = _("Create Key Pair")
    submit_label = _("Create Key Pair")
    submit_url = reverse_lazy("horizon:project:key_pairs:create")
    
    def get_context_data(self, **kwargs):
        context = super(CreateView, self).get_context_data(**kwargs)
        context['submit_url'] = self.submit_url
        return context
```

**Key Points**:

1. **Inherits from `ModalFormView`**: Opens form in a modal dialog (Horizon pattern)
2. **Template**: Points to our Django template (created in Step 3)
3. **Success URL**: Returns to key pairs index after successful creation
4. **Modal Configuration**: Sets modal ID, header, and submit button label
5. **Submit URL**: Used by template to know where to POST form data

---

### Step 3: Create Template `create.html`

**File**: `openstack_dashboard/dashboards/project/key_pairs/templates/key_pairs/create.html`

**What to add**:

```django
{% extends "horizon/common/_modal_form.html" %}
{% load i18n %}

{% block modal-body-right %}
  <h3>{% trans "Description" %}</h3>
  <p>
    {% trans "Generate a new key pair. The private key will be generated and must be downloaded immediately after creation." %}
  </p>
  <p>
    {% trans "Key pairs are used to access instances via SSH. The private key should be kept secure." %}
  </p>
  <h4>{% trans "Key Types" %}</h4>
  <dl>
    <dt>{% trans "SSH Key" %}</dt>
    <dd>
      {% trans "Standard SSH key pair (RSA). Recommended for most use cases." %}
    </dd>
    <dt>{% trans "X509 Certificate" %}</dt>
    <dd>
      {% trans "X509 certificate key pair. Used for specific authentication scenarios." %}
    </dd>
  </dl>
{% endblock %}
```

**Key Points**:

1. **Extends `_modal_form.html`**: Reuses Horizon's modal form structure
2. **Right-side help text**: Provides user guidance (Horizon UX pattern)
3. **Descriptions**: Explains what key pairs are and the difference between SSH and X509
4. **i18n**: All user-facing strings are translatable

---

### Step 4: Add URL Pattern in `urls.py`

**File**: `openstack_dashboard/dashboards/project/key_pairs/urls.py`

**What to add**:

Find the existing `urlpatterns` list and add:

```python
from openstack_dashboard.dashboards.project.key_pairs import views

urlpatterns = [
    # ... existing patterns ...
    
    # New: Generate key pair
    path('create/',
         views.CreateView.as_view(),
         name='create'),
]
```

**Key Points**:

1. **URL**: `project/key_pairs/create/`
2. **Name**: `horizon:project:key_pairs:create` (used in table actions and templates)
3. **View**: Maps to our `CreateView` class

---

### Step 5: Update Table Actions in `tables.py` (if needed)

**File**: `openstack_dashboard/dashboards/project/key_pairs/tables.py`

**Check if this exists**:

```python
class CreateKeyPair(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Key Pair")
    url = "horizon:project:key_pairs:create"
    classes = ("ajax-modal",)
    icon = "plus"
```

**If it doesn't exist, add it** and include it in the table:

```python
class KeyPairsTable(tables.DataTable):
    # ... existing columns ...
    
    class Meta(object):
        name = "keypairs"
        verbose_name = _("Key Pairs")
        table_actions = (CreateKeyPair, DeleteKeyPair, KeyPairsFilterAction)
        # ... rest of Meta ...
```

**Key Points**:

1. **LinkAction**: Creates a clickable button in the table toolbar
2. **ajax-modal**: Opens the form in a modal (no page reload)
3. **Icon**: Bootstrap icon name for the button

---

## Testing Checklist

### Manual Testing

Before submitting, test these scenarios on your DevStack:

#### Test 1: Generate SSH Key Pair (Happy Path)
```
1. Navigate to Project > Compute > Key Pairs
2. Click "Create Key Pair" button
3. Enter name: "test-keypair-ssh"
4. Leave Key Type as "SSH Key" (default)
5. Click "Create Key Pair"
6. ✅ Verify: Success message appears
7. ✅ Verify: Table refreshes and shows new key pair
8. ✅ Verify: Key pair type shows "ssh"
```

#### Test 2: Generate X509 Key Pair
```
1. Click "Create Key Pair"
2. Enter name: "test-keypair-x509"
3. Select Key Type: "X509 Certificate"
4. Click "Create Key Pair"
5. ✅ Verify: Success message appears
6. ✅ Verify: Key pair created with x509 type
```

#### Test 3: Duplicate Name (Error Handling)
```
1. Click "Create Key Pair"
2. Enter name: "test-keypair-ssh" (already exists)
3. Click "Create Key Pair"
4. ✅ Verify: Error message appears
5. ✅ Verify: Form stays open (doesn't close on error)
6. ✅ Verify: Error message is clear and actionable
```

#### Test 4: Invalid Name Characters
```
1. Click "Create Key Pair"
2. Enter name: "test keypair@#$" (invalid characters)
3. Click "Create Key Pair"
4. ✅ Verify: Validation error appears
5. ✅ Verify: Error indicates allowed characters
```

#### Test 5: Empty Name
```
1. Click "Create Key Pair"
2. Leave name field empty
3. Click "Create Key Pair"
4. ✅ Verify: Validation error appears
5. ✅ Verify: "This field is required" message shown
```

### Command-Line Verification

Verify the key pair was actually created in Nova:

```bash
# SSH into your DevStack
ssh stack@<devstack-ip>

# Source admin credentials
source ~/devstack/openrc admin admin

# List key pairs
openstack keypair list

# Show details of your test key pair
openstack keypair show test-keypair-ssh

# Verify key type
openstack keypair show test-keypair-ssh -c type -f value
# Should output: ssh

# Clean up test key pairs
openstack keypair delete test-keypair-ssh
openstack keypair delete test-keypair-x509
```

---

## Commit Message Template

Use this format for your commit:

```
Add Python implementation for key pair generation form

Implements the "Generate Key Pair" form using Django forms and views,
replacing the AngularJS implementation for OSPRH-12802.

This form allows users to:
- Generate a new SSH key pair (default)
- Generate a new X509 certificate key pair
- Receive the private key for download (Patchset 3)

Changes:
- Add GenerateKeyPairForm to forms.py
  - Name field with validation (alphanumeric, hyphens, underscores)
  - Key type field (SSH or X509)
  - Server-side validation for name format
  - Nova API integration for key pair generation
  
- Add CreateView to views.py
  - Modal form view for key pair generation
  - Success/error message handling
  - Session storage for private key (temporary, for download)
  
- Add create.html template
  - User-friendly form layout
  - Help text explaining key pair types
  - i18n support for all user-facing strings
  
- Update urls.py
  - Add URL pattern for create view
  
- Update tables.py (if needed)
  - Ensure CreateKeyPair action exists
  - Link to new Python view

Partial-Bug: #OSPRH-12802
Change-Id: Ixxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Topic: de-angularize
```

**Important**: The `Change-Id` will be auto-generated by the git-review hook. Just include the line and let git-review fill it in.

---

## Expected Reviewer Questions

Based on Review 966349 experience, anticipate these questions:

### Q1: "Why store private key in session?"

**A**: Temporary storage to pass the private key from form submission to download page (implemented in Patchset 3). The session is cleared after download. Alternative would be to return the key directly in the response, but that's less secure for multi-user environments.

### Q2: "Why not combine generate and import into one form?"

**A**: Following Django best practices and Horizon patterns: separate forms for distinct workflows. Generate and Import have different fields and validation rules. Combining them would complicate validation logic and user experience.

### Q3: "What about key pair length/algorithm selection?"

**A**: Nova API handles key generation with secure defaults. Exposing algorithm selection would require Nova API support and add complexity. Current implementation matches AngularJS version's functionality.

### Q4: "PEP8 compliance?"

**A**: Will be verified in Patchset 5. For Patchset 1, focus is on working implementation. However, aim to follow PEP8 as you code:
```bash
# Check your changes
cd horizon-osprh-12802-working
tox -e pep8
```

---

## Dependencies

### Required Horizon APIs

- `api.nova.keypair_create(request, name, key_type='ssh')` - Creates key pair
- Returns keypair object with `private_key` attribute (if generated)

### Required Horizon Modules

- `horizon.forms.SelfHandlingForm` - Base form class
- `horizon.forms.ModalFormView` - Modal form view
- `horizon.exceptions.handle()` - Error handling
- `horizon.messages` - User messages

---

## Next Steps

After Patchset 1 is reviewed and merged:

1. **Patchset 2**: Implement Import Key Pair form
2. **Patchset 3**: Add private key download page
3. **Patchset 4**: Enhance error handling and UI polish
4. **Patchset 5**: Add tests and final PEP8 compliance

---

## Notes for Self

### Development Environment Setup

```bash
# If not already done
cd /home/omcgonag/Work/mymcp/workspace
git clone https://review.opendev.org/openstack/horizon horizon-osprh-12802-working
cd horizon-osprh-12802-working

# Configure git
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Install git-review
pip install git-review
git review -s

# Create working branch
git checkout -b osprh-12802-generate-form
```

### Key Files Reference

From Review 966349, reference these for patterns:
- `analysis/analysis_new_feature_966349/patchset_008_bootstrap_refactor_phases_1to4.md` - Form implementation patterns
- `analysis/docs/BEST_PRACTICES_FEATURE_DEV.md` - Best practices checklist

### Testing on DevStack

```bash
# SSH to DevStack
ssh stack@<your-devstack-ip>

# Source credentials
source ~/devstack/openrc admin admin

# Sync your changes (if using shared devstack)
cd /opt/stack/horizon
git fetch <your-remote> osprh-12802-generate-form
git checkout FETCH_HEAD

# Restart Horizon
sudo systemctl restart apache2  # or httpd on RHEL
```

---

**Status**: 📋 Ready for implementation  
**Estimated Time**: 2 days  
**Complexity**: Medium


