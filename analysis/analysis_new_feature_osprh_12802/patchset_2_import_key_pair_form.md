# Patchset 2: Import Key Pair Form Implementation

**Date**: TBD  
**Jira**: [OSPRH-12802](https://issues.redhat.com/browse/OSPRH-12802)  
**Status**: 📋 Planning  
**Estimated Effort**: 2 days  
**Depends On**: Patchset 1 (Generate form)

---

## View Patchset Changes

### Continue from Patchset 1:
```bash
# Ensure you're on your working branch
cd /home/omcgonag/Work/mymcp/workspace/horizon-osprh-12802-working
git checkout osprh-12802-generate-form

# Create changes for Patchset 2
# After making changes, view your work
git diff --stat
git diff
```

### Submit as new patchset:
```bash
# Add and commit your changes
git add openstack_dashboard/dashboards/project/key_pairs/
git commit --amend  # Amend to same Change-Id, creating PS2

# Submit to Gerrit (will be Patchset 2 of same review)
git review
```

---

## Executive Summary

**Goal**: Implement the "Import Key Pair" form using Python/Django, allowing users to import their existing public keys.

**Approach**: 
- Create `ImportKeyPairForm` with public key validation
- Add `ImportView` as a modal form view
- Create Django template for the import form
- Handle form submission with Nova API
- Validate SSH public key format

**Files to Create/Modify**:
- `forms.py` - Add `ImportKeyPairForm` class
- `views.py` - Add `ImportView` class
- `templates/key_pairs/import.html` - Import form template
- `urls.py` - Add URL pattern for import view
- `tables.py` - Add/verify `ImportKeyPair` action

**Result**: Users can import existing SSH public keys, enabling use of their own key pairs with OpenStack instances.

---

## Implementation Details

### Problem Statement

In addition to generating new key pairs, users often have **existing SSH keys** they want to use with OpenStack. The Import workflow allows users to:

1. Provide a **name** for the key pair
2. Paste their **existing public key** (from `~/.ssh/id_rsa.pub` or similar)
3. Server validates the public key format
4. Public key is stored in Nova (no private key - user already has it)

**Key Difference from Generate**: Import only stores the public key; the user already has the private key on their local machine.

---

## Step-by-Step Implementation

### Step 1: Create `ImportKeyPairForm` in `forms.py`

**File**: `openstack_dashboard/dashboards/project/key_pairs/forms.py`

**What to add** (after `GenerateKeyPairForm`):

```python
class ImportKeyPairForm(forms.SelfHandlingForm):
    """Form for importing an existing public key."""
    
    name = forms.CharField(
        max_length=255,
        label=_("Key Pair Name"),
        help_text=_("Name for this key pair in OpenStack"),
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('my-existing-keypair'),
            'autofocus': 'autofocus'
        })
    )
    
    public_key = forms.CharField(
        label=_("Public Key"),
        required=True,
        widget=forms.Textarea(attrs={
            'rows': 6,
            'placeholder': _('ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAB... user@hostname'),
            'class': 'public-key-input'
        }),
        help_text=_("Paste your SSH public key here. Typically from ~/.ssh/id_rsa.pub")
    )
    
    def __init__(self, request, *args, **kwargs):
        super(ImportKeyPairForm, self).__init__(request, *args, **kwargs)
    
    def clean_name(self):
        """Validate key pair name format (same as Generate form)."""
        name = self.cleaned_data.get('name')
        
        if not name:
            raise forms.ValidationError(_("Key pair name is required"))
        
        import re
        if not re.match(r'^[a-zA-Z0-9-_]+$', name):
            raise forms.ValidationError(
                _("Key pair name can only contain letters, numbers, "
                  "hyphens, and underscores")
            )
        
        return name
    
    def clean_public_key(self):
        """Validate SSH public key format."""
        public_key = self.cleaned_data.get('public_key', '').strip()
        
        if not public_key:
            raise forms.ValidationError(_("Public key is required"))
        
        # Basic validation: must start with a known algorithm
        valid_algorithms = [
            'ssh-rsa',
            'ssh-dss',
            'ssh-ed25519',
            'ecdsa-sha2-nistp256',
            'ecdsa-sha2-nistp384',
            'ecdsa-sha2-nistp521',
            'sk-ssh-ed25519@openssh.com',
            'sk-ecdsa-sha2-nistp256@openssh.com',
        ]
        
        # Check if key starts with a valid algorithm
        if not any(public_key.startswith(algo) for algo in valid_algorithms):
            raise forms.ValidationError(
                _("Invalid public key format. Key must start with a valid "
                  "algorithm (e.g., ssh-rsa, ssh-ed25519)")
            )
        
        # Check for minimum key components (algorithm + key data)
        parts = public_key.split()
        if len(parts) < 2:
            raise forms.ValidationError(
                _("Invalid public key format. Key must contain at least "
                  "algorithm and key data")
            )
        
        # Validate base64 encoding of key data (second part)
        import base64
        try:
            # Try to decode the key data (second part)
            base64.b64decode(parts[1])
        except Exception:
            raise forms.ValidationError(
                _("Invalid public key format. Key data is not properly "
                  "base64 encoded")
            )
        
        return public_key
    
    def handle(self, request, data):
        """Import the key pair via Nova API."""
        try:
            # Call Nova API to import key pair
            keypair = api.nova.keypair_import(
                request,
                data['name'],
                data['public_key']
            )
            
            messages.success(
                request,
                _('Successfully imported key pair "%(name)s".') % {
                    'name': data['name']
                }
            )
            
            return keypair
            
        except Exception as e:
            exceptions.handle(
                request,
                _('Unable to import key pair: %s') % str(e)
            )
            return False
```

**Key Points**:

1. **Two Fields**: 
   - `name`: Same validation as Generate form
   - `public_key`: Textarea for pasting the public key

2. **Public Key Validation** (`clean_public_key()`):
   - Checks for valid SSH algorithm prefix
   - Supports common algorithms: RSA, DSS, ED25519, ECDSA
   - Validates base64 encoding of key data
   - Provides clear error messages for common issues

3. **API Call**: Uses `api.nova.keypair_import()` with name and public key

4. **No Private Key**: Unlike Generate, this doesn't create a private key

5. **Error Handling**: Same pattern as Generate form

---

### Step 2: Create `ImportView` in `views.py`

**File**: `openstack_dashboard/dashboards/project/key_pairs/views.py`

**What to add** (after `CreateView`):

```python
class ImportView(horizon_forms.ModalFormView):
    """View for importing an existing public key."""
    
    form_class = project_forms.ImportKeyPairForm
    template_name = 'project/key_pairs/import.html'
    success_url = reverse_lazy('horizon:project:key_pairs:index')
    modal_id = "import_keypair_modal"
    modal_header = _("Import Key Pair")
    submit_label = _("Import Key Pair")
    submit_url = reverse_lazy("horizon:project:key_pairs:import")
    
    def get_context_data(self, **kwargs):
        context = super(ImportView, self).get_context_data(**kwargs)
        context['submit_url'] = self.submit_url
        return context
```

**Key Points**:

1. **Nearly identical to CreateView**: Same pattern, different form class
2. **Different modal ID**: Prevents conflicts if both modals exist
3. **Different submit URL**: Points to import endpoint

---

### Step 3: Create Template `import.html`

**File**: `openstack_dashboard/dashboards/project/key_pairs/templates/key_pairs/import.html`

**What to add**:

```django
{% extends "horizon/common/_modal_form.html" %}
{% load i18n %}

{% block modal-body-right %}
  <h3>{% trans "Description" %}</h3>
  <p>
    {% trans "Import an existing SSH public key. This allows you to use your own key pair with OpenStack instances." %}
  </p>
  <p>
    {% trans "You should already have the private key on your local machine (typically in ~/.ssh/). Only the public key is imported to OpenStack." %}
  </p>
  
  <h4>{% trans "How to Find Your Public Key" %}</h4>
  <p>{% trans "On your local machine (Linux/Mac):" %}</p>
  <pre class="code">cat ~/.ssh/id_rsa.pub</pre>
  
  <p>{% trans "Or for ED25519 keys:" %}</p>
  <pre class="code">cat ~/.ssh/id_ed25519.pub</pre>
  
  <p>{% trans "On Windows (PowerShell):" %}</p>
  <pre class="code">type $env:USERPROFILE\.ssh\id_rsa.pub</pre>
  
  <h4>{% trans "Supported Key Types" %}</h4>
  <ul>
    <li>{% trans "SSH RSA (ssh-rsa)" %}</li>
    <li>{% trans "SSH ED25519 (ssh-ed25519) - Recommended" %}</li>
    <li>{% trans "SSH DSS (ssh-dss)" %}</li>
    <li>{% trans "ECDSA (ecdsa-sha2-nistp256/384/521)" %}</li>
  </ul>
  
  <h4>{% trans "Example Public Key Format" %}</h4>
  <pre class="code">ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC7... user@hostname</pre>
{% endblock %}

{% block modal-footer %}
  {{ block.super }}
  <style>
    /* Make public key input monospace for better readability */
    .public-key-input {
      font-family: monospace;
      font-size: 12px;
    }
    
    /* Style code examples */
    pre.code {
      background: #f5f5f5;
      border: 1px solid #ddd;
      border-radius: 3px;
      padding: 8px;
      font-size: 12px;
      overflow-x: auto;
    }
  </style>
{% endblock %}
```

**Key Points**:

1. **Comprehensive Help Text**: 
   - Explains what importing means
   - Shows how to find public key on different OSes
   - Lists supported key types
   - Provides example format

2. **User-Friendly**:
   - Copy-paste instructions
   - Platform-specific commands
   - Visual example of expected format

3. **Monospace Font**: Makes public key easier to read and verify

4. **Code Styling**: Makes examples stand out

---

### Step 4: Add URL Pattern in `urls.py`

**File**: `openstack_dashboard/dashboards/project/key_pairs/urls.py`

**What to add**:

```python
urlpatterns = [
    # ... existing patterns including create/ ...
    
    # New: Import key pair
    path('import/',
         views.ImportView.as_view(),
         name='import'),
]
```

**Key Points**:

1. **URL**: `project/key_pairs/import/`
2. **Name**: `horizon:project:key_pairs:import`

---

### Step 5: Add/Verify `ImportKeyPair` Action in `tables.py`

**File**: `openstack_dashboard/dashboards/project/key_pairs/tables.py`

**Check if this exists, if not add it**:

```python
class ImportKeyPair(tables.LinkAction):
    name = "import"
    verbose_name = _("Import Key Pair")
    url = "horizon:project:key_pairs:import"
    classes = ("ajax-modal",)
    icon = "upload"
```

**Update table actions**:

```python
class KeyPairsTable(tables.DataTable):
    # ... existing columns ...
    
    class Meta(object):
        name = "keypairs"
        verbose_name = _("Key Pairs")
        table_actions = (
            CreateKeyPair,      # From Patchset 1
            ImportKeyPair,      # New action
            DeleteKeyPair,
            KeyPairsFilterAction
        )
        # ... rest of Meta ...
```

**Key Points**:

1. **Two Actions**: Users can choose "Create" (generate) or "Import"
2. **Different Icons**: Plus for create, upload for import
3. **Same Pattern**: Both open as modal forms

---

## Testing Checklist

### Manual Testing

#### Test 1: Import Valid RSA Public Key (Happy Path)
```
1. Generate a test key on your local machine:
   ssh-keygen -t rsa -b 2048 -f /tmp/test_keypair -N ""
   
2. Copy the public key:
   cat /tmp/test_keypair.pub
   
3. Navigate to Project > Compute > Key Pairs
4. Click "Import Key Pair" button
5. Enter name: "test-import-rsa"
6. Paste the public key from step 2
7. Click "Import Key Pair"
8. ✅ Verify: Success message appears
9. ✅ Verify: Table shows new key pair
10. ✅ Verify: Fingerprint matches the imported key
```

#### Test 2: Import Valid ED25519 Public Key
```
1. Generate ED25519 key:
   ssh-keygen -t ed25519 -f /tmp/test_ed25519 -N ""
   
2. Copy the public key:
   cat /tmp/test_ed25519.pub
   
3. Click "Import Key Pair"
4. Enter name: "test-import-ed25519"
5. Paste the ED25519 public key
6. Click "Import Key Pair"
7. ✅ Verify: Successfully imported
8. ✅ Verify: Fingerprint is different from RSA key
```

#### Test 3: Import Key with Comment
```
1. Create key with comment:
   ssh-keygen -t rsa -b 2048 -f /tmp/test_comment -N "" -C "my-test-key@example.com"
   
2. Copy public key (will have comment at end):
   cat /tmp/test_comment.pub
   
3. Import with comment included
4. ✅ Verify: Import succeeds
5. ✅ Verify: Comment is preserved in Nova
```

#### Test 4: Multi-line Public Key
```
1. Create a key with wrapped lines:
   ssh-keygen -t rsa -b 4096 -f /tmp/test_long -N ""
   # Key will be longer, may wrap in terminal
   
2. Copy entire public key (may be multiple lines in some editors)
3. Import the key
4. ✅ Verify: Import succeeds even if pasted with line breaks
```

#### Test 5: Invalid Public Key - Missing Algorithm (Error)
```
1. Click "Import Key Pair"
2. Enter name: "test-invalid"
3. Paste just random text: "AAAAB3NzaC1yc2EAAAADAQAB..."
4. Click "Import Key Pair"
5. ✅ Verify: Validation error appears
6. ✅ Verify: Error mentions "must start with a valid algorithm"
```

#### Test 6: Invalid Public Key - Malformed Base64 (Error)
```
1. Click "Import Key Pair"
2. Enter name: "test-malformed"
3. Paste: "ssh-rsa THIS_IS_NOT_VALID_BASE64"
4. Click "Import Key Pair"
5. ✅ Verify: Validation error appears
6. ✅ Verify: Error mentions "not properly base64 encoded"
```

#### Test 7: Duplicate Name (Error)
```
1. Click "Import Key Pair"
2. Enter name: "test-import-rsa" (already exists from Test 1)
3. Paste any valid public key
4. Click "Import Key Pair"
5. ✅ Verify: Error message from Nova
6. ✅ Verify: Error indicates duplicate name
```

#### Test 8: Empty Public Key (Error)
```
1. Click "Import Key Pair"
2. Enter name: "test-empty"
3. Leave public key field empty
4. Click "Import Key Pair"
5. ✅ Verify: Validation error "Public key is required"
```

#### Test 9: Invalid Name Characters (Error)
```
1. Click "Import Key Pair"
2. Enter name: "test import@#$" (invalid)
3. Paste valid public key
4. Click "Import Key Pair"
5. ✅ Verify: Name validation error
```

### Command-Line Verification

```bash
# SSH to DevStack
ssh stack@<devstack-ip>
source ~/devstack/openrc admin admin

# List all key pairs
openstack keypair list

# Show details of imported key
openstack keypair show test-import-rsa

# Verify fingerprint matches
# Compare with local fingerprint:
ssh-keygen -lf /tmp/test_keypair.pub
# Should match Nova's fingerprint

# Show public key stored in Nova
openstack keypair show test-import-rsa -c public_key -f value

# Verify no private key exists (Nova shouldn't have it)
# (Private key was never sent to server, user has it locally)

# Test the imported key works for instance access
openstack server create --image cirros --flavor m1.tiny \
  --key-name test-import-rsa --network private test-instance

# Wait for instance to boot
openstack server list

# Get instance IP
INSTANCE_IP=$(openstack server show test-instance -c addresses -f value | cut -d'=' -f2)

# Try SSH with the private key
ssh -i /tmp/test_keypair cirros@$INSTANCE_IP
# Should successfully connect!

# Clean up
openstack server delete test-instance
openstack keypair delete test-import-rsa
openstack keypair delete test-import-ed25519
rm -f /tmp/test_keypair /tmp/test_keypair.pub
rm -f /tmp/test_ed25519 /tmp/test_ed25519.pub
```

---

## Commit Message Template

```
Add Python implementation for key pair import form

Implements the "Import Key Pair" form using Django forms and views,
allowing users to import their existing SSH public keys for use with
OpenStack instances. Continues OSPRH-12802 de-angularization effort.

This form allows users to:
- Import existing SSH/ED25519/ECDSA public keys
- Use their own locally-generated key pairs with OpenStack
- Maintain key pair security (private key never leaves user's machine)

Changes:
- Add ImportKeyPairForm to forms.py
  - Name field with validation (same as Generate form)
  - Public key field (textarea for paste)
  - Comprehensive public key validation:
    * Checks for valid SSH algorithm (RSA, ED25519, DSS, ECDSA)
    * Validates base64 encoding of key data
    * Supports keys with optional comments
    * Clear error messages for common issues
  - Nova API integration for key pair import
  
- Add ImportView to views.py
  - Modal form view for key pair import
  - Success/error message handling
  - Consistent with CreateView pattern
  
- Add import.html template
  - Comprehensive help text
  - Platform-specific instructions (Linux/Mac/Windows)
  - Shows how to find public keys locally
  - Lists supported key types with examples
  - Monospace font for public key input
  - Code styling for examples
  
- Update urls.py
  - Add URL pattern for import view
  
- Update tables.py
  - Add ImportKeyPair action to table toolbar
  - Upload icon for visual distinction from Create

Partial-Bug: #OSPRH-12802
Change-Id: Ixxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Topic: de-angularize
```

---

## Expected Reviewer Questions

### Q1: "Why validate public key client-side? Nova will reject invalid keys anyway."

**A**: Better UX - immediate feedback vs. waiting for API call. Also provides clearer error messages than Nova's generic errors. Validation catches common issues (wrong format, missing algorithm) before hitting the API.

### Q2: "Why not auto-detect key type from public key?"

**A**: Not needed for Import workflow. Key type is inherent in the public key algorithm (ssh-rsa → ssh, etc.). Nova determines this from the key itself.

### Q3: "What about supporting OpenSSH private key format?"

**A**: Import is **public key only** by design. Private keys should never be uploaded to the server. Users paste their `.pub` file contents, not their private key.

### Q4: "Should we support PuTTY keys?"

**A**: OpenSSH format is standard for OpenStack. PuTTY users should convert keys to OpenSSH format using `puttygen`. Adding PuTTY support would complicate validation significantly.

### Q5: "What about key size validation?"

**A**: Nova enforces minimum key sizes. Client-side validation would duplicate Nova's logic and may become outdated. Better to let Nova validate and return appropriate errors.

---

## Code Review Readiness

### Before Submitting

```bash
# Run PEP8 check
cd horizon-osprh-12802-working
tox -e pep8

# Run unit tests (even though we add tests in Patchset 5)
tox -e py39

# Check for common issues
grep -r "TODO\|FIXME\|XXX" openstack_dashboard/dashboards/project/key_pairs/

# Verify imports are sorted
# Should follow order: stdlib, third-party, horizon, local
```

### Self-Review Checklist

- [ ] All strings are translatable (`_("text")`)
- [ ] Help text is clear and actionable
- [ ] Error messages are user-friendly
- [ ] Variable names are descriptive
- [ ] Comments explain "why", not "what"
- [ ] No debug print statements
- [ ] No commented-out code
- [ ] Forms follow Horizon patterns
- [ ] Templates extend correct base
- [ ] URLs follow naming conventions

---

## Dependencies

### New Horizon APIs Used

- `api.nova.keypair_import(request, name, public_key)` - Imports public key
- Returns keypair object (no `private_key` attribute)

### Python Standard Library

- `re` - For name validation regex
- `base64` - For public key data validation

---

## Next Steps

After Patchset 2 is reviewed and merged:

1. **Patchset 3**: Implement private key download page (for Generate workflow)
2. **Patchset 4**: Add error handling enhancements and UI polish
3. **Patchset 5**: Add comprehensive tests for both forms

---

## Notes for Self

### Testing Strategy

Create a script to generate multiple test keys:

```bash
#!/bin/bash
# save as: generate_test_keys.sh

# RSA 2048
ssh-keygen -t rsa -b 2048 -f /tmp/test_rsa_2048 -N "" -C "test-rsa-2048"

# RSA 4096
ssh-keygen -t rsa -b 4096 -f /tmp/test_rsa_4096 -N "" -C "test-rsa-4096"

# ED25519
ssh-keygen -t ed25519 -f /tmp/test_ed25519 -N "" -C "test-ed25519"

# ECDSA
ssh-keygen -t ecdsa -b 256 -f /tmp/test_ecdsa -N "" -C "test-ecdsa"

echo "Test keys generated in /tmp/"
echo "Public keys:"
ls -la /tmp/test_*.pub
```

### Common Import Errors to Test

1. **Missing algorithm**: `AAAAB3NzaC1yc2EAAAADAQAB...`
2. **Wrong algorithm**: `ssh-invalid AAAAB3...`
3. **Malformed base64**: `ssh-rsa NOT_BASE64`
4. **Truncated key**: `ssh-rsa AAAAB3` (too short)
5. **Private key pasted**: `-----BEGIN RSA PRIVATE KEY-----`

---

**Status**: 📋 Ready for implementation  
**Estimated Time**: 2 days  
**Complexity**: Medium  
**Depends On**: Patchset 1 (Generate form must be reviewed first)


