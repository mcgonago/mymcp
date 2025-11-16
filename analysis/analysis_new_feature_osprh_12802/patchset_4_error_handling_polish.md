# Patchset 4: Error Handling & UI Polish

**Date**: TBD  
**Jira**: [OSPRH-12802](https://issues.redhat.com/browse/OSPRH-12802)  
**Status**: 📋 Planning  
**Estimated Effort**: 1 day  
**Depends On**: Patchsets 1-3

---

## Executive Summary

**Goal**: Enhance error handling, improve user experience, and polish the UI based on testing and feedback.

**Approach**: 
- Add comprehensive error handling for Nova API failures
- Improve validation error messages
- Add user-friendly tooltips and help text
- Handle edge cases (network errors, timeouts, quota limits)
- Improve accessibility (ARIA labels, keyboard navigation)
- Add loading indicators for async operations
- Refine responsive design
- Address any reviewer feedback from previous patchsets

**Files to Modify**:
- `forms.py` - Enhanced validation and error messages
- `views.py` - Better error handling
- `templates/key_pairs/*.html` - UI improvements, accessibility
- `static/dashboard/scss/_keypairs.scss` - Polish styles (if needed)

**Result**: Robust, user-friendly key pair forms with excellent error handling and accessibility.

---

## Implementation Details

### Problem Statement

After initial implementation (Patchsets 1-3), user testing and code review may reveal:

1. **Error Messages Too Generic**: "Unable to create key pair" doesn't help users
2. **Missing Edge Cases**: What if user hits quota limit? Network timeout?
3. **Accessibility Issues**: Screen readers, keyboard navigation
4. **UX Friction**: Unclear what went wrong, how to fix it
5. **Missing Loading States**: No feedback during API calls

**This patchset addresses these issues systematically.**

---

## Step-by-Step Implementation

### Step 1: Enhanced Error Handling in `forms.py`

**File**: `openstack_dashboard/dashboards/project/key_pairs/forms.py`

**Add helper method for better error messages**:

```python
def _get_user_friendly_error_message(self, exception):
    """Convert Nova exceptions to user-friendly messages."""
    error_str = str(exception).lower()
    
    # Quota exceeded
    if 'quota' in error_str or 'limit' in error_str:
        return _(
            'Key pair quota exceeded. Please delete unused key pairs '
            'or contact your administrator to increase your quota.'
        )
    
    # Duplicate name
    if 'already exists' in error_str or 'duplicate' in error_str:
        return _(
            'A key pair with this name already exists. '
            'Please choose a different name or delete the existing key pair.'
        )
    
    # Invalid public key format (for import)
    if 'invalid' in error_str and 'key' in error_str:
        return _(
            'The provided public key is invalid. Please ensure you are '
            'pasting the complete public key from your .pub file, including '
            'the algorithm prefix (e.g., ssh-rsa).'
        )
    
    # Network/connection errors
    if 'connection' in error_str or 'timeout' in error_str:
        return _(
            'Unable to connect to the compute service. Please check your '
            'network connection and try again.'
        )
    
    # Permission denied
    if 'forbidden' in error_str or 'not authorized' in error_str:
        return _(
            'You do not have permission to create key pairs. '
            'Please contact your administrator.'
        )
    
    # Generic fallback
    return _(
        'Unable to process key pair: %(error)s. '
        'Please verify your input and try again.'
    ) % {'error': str(exception)}
```

**Update `GenerateKeyPairForm.handle()`**:

```python
def handle(self, request, data):
    """Generate the key pair via Nova API."""
    try:
        keypair = api.nova.keypair_create(
            request,
            data['name'],
            key_type=data.get('key_type', 'ssh')
        )
        
        if hasattr(keypair, 'private_key') and keypair.private_key:
            request.session['keypair_private_key'] = keypair.private_key
            request.session['keypair_name'] = keypair.name
            request.session.modified = True
            return keypair
        else:
            messages.error(
                request,
                _('Key pair "%(name)s" was created, but the private key '
                  'was not returned by the server. This may indicate a '
                  'configuration issue. Please contact your administrator.') % {
                    'name': data['name']
                }
            )
            return False
            
    except exceptions.Conflict:
        # Duplicate key pair name
        msg = _('A key pair named "%(name)s" already exists. '
                'Please choose a different name.') % {'name': data['name']}
        exceptions.handle(request, msg)
        return False
        
    except exceptions.Quota:
        # Quota exceeded
        msg = _('Key pair quota exceeded. Please delete unused key pairs '
                'or request a quota increase from your administrator.')
        exceptions.handle(request, msg)
        return False
        
    except exceptions.NotAuthorized:
        # Permission denied
        msg = _('You do not have permission to create key pairs.')
        exceptions.handle(request, msg)
        return False
        
    except Exception as e:
        # Generic error with user-friendly message
        msg = self._get_user_friendly_error_message(e)
        exceptions.handle(request, msg)
        return False
```

**Update `ImportKeyPairForm.handle()`** similarly:

```python
def handle(self, request, data):
    """Import the key pair via Nova API."""
    try:
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
        
    except exceptions.Conflict:
        msg = _('A key pair named "%(name)s" already exists. '
                'Please choose a different name.') % {'name': data['name']}
        exceptions.handle(request, msg)
        return False
        
    except exceptions.Quota:
        msg = _('Key pair quota exceeded. Please delete unused key pairs '
                'or request a quota increase.')
        exceptions.handle(request, msg)
        return False
        
    except exceptions.NotAuthorized:
        msg = _('You do not have permission to import key pairs.')
        exceptions.handle(request, msg)
        return False
        
    except Exception as e:
        msg = self._get_user_friendly_error_message(e)
        exceptions.handle(request, msg)
        return False
```

**Enhanced `clean_public_key()` with better errors**:

```python
def clean_public_key(self):
    """Validate SSH public key format with detailed error messages."""
    public_key = self.cleaned_data.get('public_key', '').strip()
    
    if not public_key:
        raise forms.ValidationError(_("Public key is required"))
    
    # Check minimum length (avoid very short invalid inputs)
    if len(public_key) < 100:
        raise forms.ValidationError(
            _("Public key is too short. A valid SSH public key is typically "
              "several hundred characters long. Please ensure you copied the "
              "entire key.")
        )
    
    # Check if it looks like a private key (common mistake)
    if 'PRIVATE KEY' in public_key:
        raise forms.ValidationError(
            _("You appear to have pasted a private key. Please paste your "
              "public key instead (typically from ~/.ssh/id_rsa.pub or similar).")
        )
    
    # Valid algorithms
    valid_algorithms = [
        'ssh-rsa', 'ssh-dss', 'ssh-ed25519',
        'ecdsa-sha2-nistp256', 'ecdsa-sha2-nistp384', 'ecdsa-sha2-nistp521',
        'sk-ssh-ed25519@openssh.com', 'sk-ecdsa-sha2-nistp256@openssh.com',
    ]
    
    # Check algorithm
    algorithm = public_key.split()[0] if public_key.split() else ''
    if algorithm not in valid_algorithms:
        raise forms.ValidationError(
            _("Invalid public key format. Key must start with a valid "
              "algorithm such as: %(algorithms)s. "
              "You provided: %(provided)s") % {
                'algorithms': ', '.join(valid_algorithms[:4]) + ', ...',
                'provided': algorithm or _('(none)')
            }
        )
    
    # Check key structure
    parts = public_key.split()
    if len(parts) < 2:
        raise forms.ValidationError(
            _("Invalid public key format. A valid key consists of: "
              "algorithm, key data, and optionally a comment. "
              "Your key appears to be missing the key data.")
        )
    
    # Validate base64 encoding
    import base64
    try:
        base64.b64decode(parts[1])
    except Exception:
        raise forms.ValidationError(
            _("Invalid public key format. The key data (second part) "
              "is not properly base64 encoded. Please copy the entire "
              "key from your .pub file.")
        )
    
    return public_key
```

**Key Improvements**:

1. **Specific Exception Handling**: Catches `Conflict`, `Quota`, `NotAuthorized`
2. **User-Friendly Messages**: Explains what went wrong and how to fix it
3. **Actionable Guidance**: "delete unused key pairs" not just "quota exceeded"
4. **Common Mistake Prevention**: Detects private key vs. public key
5. **Detailed Validation Errors**: Shows what algorithm was provided vs. expected

---

### Step 2: Improve Templates with Accessibility

**File**: `openstack_dashboard/dashboards/project/key_pairs/templates/key_pairs/create.html`

**Add accessibility improvements**:

```django
{% extends "horizon/common/_modal_form.html" %}
{% load i18n %}

{% block modal-body-right %}
  <h3>{% trans "Description" %}</h3>
  <p>
    {% trans "Generate a new key pair. The private key will be generated and must be downloaded immediately after creation." %}
  </p>
  
  <div class="alert alert-info" role="alert">
    <strong>{% trans "What is a key pair?" %}</strong>
    <p>
      {% trans "Key pairs are SSH credentials used to access your instances securely. The private key must be kept safe on your local machine." %}
    </p>
  </div>
  
  <h4>{% trans "Key Types" %}</h4>
  <dl>
    <dt>{% trans "SSH Key (Recommended)" %}</dt>
    <dd>
      {% trans "Standard SSH key pair (RSA 2048-bit). Compatible with all Linux and most Unix-based instances." %}
    </dd>
    <dt>{% trans "X509 Certificate" %}</dt>
    <dd>
      {% trans "X509 certificate key pair. Required only for specific scenarios. Use SSH Key unless specifically required." %}
    </dd>
  </dl>
  
  <h4>{% trans "After Creation" %}</h4>
  <p>
    {% trans "You will be shown the private key only once. Make sure to download and save it securely before leaving the download page." %}
  </p>
{% endblock %}

{% block modal-footer %}
  {{ block.super }}
  <script>
    // Auto-focus on name field when modal opens
    $(document).on('shown.bs.modal', '#create_keypair_modal', function() {
      $('#id_name').focus();
    });
    
    // Add loading indicator on submit
    $('#create_keypair_modal form').on('submit', function() {
      var submitBtn = $(this).find('button[type="submit"]');
      submitBtn.prop('disabled', true);
      submitBtn.html('<i class="fa fa-spinner fa-spin"></i> {% trans "Creating..." %}');
    });
  </script>
{% endblock %}
```

**File**: `import.html` - Similar improvements:

```django
{% block modal-footer %}
  {{ block.super }}
  <script>
    // Auto-focus on name field
    $(document).on('shown.bs.modal', '#import_keypair_modal', function() {
      $('#id_name').focus();
    });
    
    // Add loading indicator on submit
    $('#import_keypair_modal form').on('submit', function() {
      var submitBtn = $(this).find('button[type="submit"]');
      submitBtn.prop('disabled', true);
      submitBtn.html('<i class="fa fa-spinner fa-spin"></i> {% trans "Importing..." %}');
    });
    
    // Character counter for public key (helps users ensure they pasted fully)
    $('#id_public_key').on('input', function() {
      var length = $(this).val().length;
      var feedback = $('#public-key-feedback');
      
      if (!feedback.length) {
        feedback = $('<small id="public-key-feedback" class="form-text text-muted"></small>');
        $(this).after(feedback);
      }
      
      if (length === 0) {
        feedback.text('');
      } else if (length < 100) {
        feedback.text('{% trans "Key seems too short" %} (' + length + ' {% trans "characters" %})');
        feedback.removeClass('text-success').addClass('text-warning');
      } else {
        feedback.text('{% trans "Key length looks good" %} (' + length + ' {% trans "characters" %})');
        feedback.removeClass('text-warning').addClass('text-success');
      }
    });
  </script>
{% endblock %}
```

**Key Improvements**:

1. **Auto-focus**: Name field focused when modal opens
2. **Loading Indicators**: Button shows spinner during API call
3. **Character Counter**: Helps users verify they pasted complete key
4. **ARIA Roles**: `role="alert"` for important messages
5. **Better Help Text**: Explains "why" not just "what"

---

### Step 3: Add Form Field Validation Feedback

**Enhance field rendering** by adding validation classes:

**File**: `forms.py` - Add widget attributes:

```python
class GenerateKeyPairForm(forms.SelfHandlingForm):
    name = forms.CharField(
        max_length=255,
        label=_("Key Pair Name"),
        help_text=_("Letters, numbers, hyphens, and underscores only"),
        required=True,
        error_messages={
            'required': _('Please enter a name for your key pair'),
            'max_length': _('Key pair name cannot exceed 255 characters'),
        },
        widget=forms.TextInput(attrs={
            'placeholder': _('my-keypair'),
            'autofocus': 'autofocus',
            'aria-describedby': 'name-help',
            'pattern': '[a-zA-Z0-9-_]+',
            'title': _('Letters, numbers, hyphens, and underscores only')
        })
    )
    
    key_type = forms.ChoiceField(
        label=_("Key Type"),
        choices=[
            ('ssh', _('SSH Key (Recommended)')),
            ('x509', _('X509 Certificate'))
        ],
        initial='ssh',
        required=False,
        help_text=_("Select SSH Key for standard Linux instances"),
        widget=forms.Select(attrs={
            'aria-describedby': 'key-type-help'
        })
    )
```

**For ImportKeyPairForm**:

```python
class ImportKeyPairForm(forms.SelfHandlingForm):
    name = forms.CharField(
        max_length=255,
        label=_("Key Pair Name"),
        help_text=_("Letters, numbers, hyphens, and underscores only"),
        required=True,
        error_messages={
            'required': _('Please enter a name for your key pair'),
            'max_length': _('Key pair name cannot exceed 255 characters'),
        },
        widget=forms.TextInput(attrs={
            'placeholder': _('my-existing-keypair'),
            'autofocus': 'autofocus',
            'aria-describedby': 'name-help',
            'pattern': '[a-zA-Z0-9-_]+',
            'title': _('Letters, numbers, hyphens, and underscores only')
        })
    )
    
    public_key = forms.CharField(
        label=_("Public Key"),
        required=True,
        error_messages={
            'required': _('Please paste your SSH public key'),
        },
        widget=forms.Textarea(attrs={
            'rows': 6,
            'placeholder': _('ssh-rsa AAAAB3NzaC1yc2EAAAADAQAB... user@hostname'),
            'class': 'public-key-input',
            'aria-describedby': 'public-key-help',
            'spellcheck': 'false',  # Don't spellcheck base64 data
            'wrap': 'soft'  # Allow soft wrapping for long keys
        }),
        help_text=_("Paste the contents of your public key file (e.g., ~/.ssh/id_rsa.pub)")
    )
```

**Key Improvements**:

1. **HTML5 Validation**: `pattern` attribute provides instant feedback
2. **ARIA Attributes**: `aria-describedby` links help text to fields
3. **Custom Error Messages**: More helpful than default messages
4. **Spellcheck Off**: Prevents browser from marking base64 as spelling errors
5. **Title Attribute**: Shows tooltip on invalid input

---

### Step 4: Handle Network/Timeout Errors Gracefully

**File**: `views.py` - Add timeout handling:

```python
from django.conf import settings


class CreateView(horizon_forms.ModalFormView):
    """View for generating a new key pair."""
    
    form_class = project_forms.GenerateKeyPairForm
    template_name = 'project/key_pairs/create.html'
    modal_id = "create_keypair_modal"
    modal_header = _("Create Key Pair")
    submit_label = _("Create Key Pair")
    submit_url = reverse_lazy("horizon:project:key_pairs:create")
    
    # Add timeout configuration
    api_timeout = getattr(settings, 'KEYPAIR_CREATION_TIMEOUT', 30)
    
    def get_success_url(self):
        return reverse('horizon:project:key_pairs:download')
    
    def get_context_data(self, **kwargs):
        context = super(CreateView, self).get_context_data(**kwargs)
        context['submit_url'] = self.submit_url
        # Add timeout info for JS (show warning if slow)
        context['api_timeout'] = self.api_timeout
        return context
    
    def form_invalid(self, form):
        """Handle form validation errors."""
        # Log validation errors for debugging (don't expose to user)
        import logging
        LOG = logging.getLogger(__name__)
        LOG.debug('Key pair creation form validation failed: %s', form.errors)
        
        return super(CreateView, self).form_invalid(form)
```

**Add timeout warning to template**:

```django
{% block modal-footer %}
  {{ block.super }}
  <script>
    var timeoutSeconds = {{ api_timeout|default:30 }};
    var timeoutWarning = null;
    
    $('#create_keypair_modal form').on('submit', function() {
      var submitBtn = $(this).find('button[type="submit"]');
      submitBtn.prop('disabled', true);
      submitBtn.html('<i class="fa fa-spinner fa-spin"></i> {% trans "Creating..." %}');
      
      // Show warning if API call takes too long
      timeoutWarning = setTimeout(function() {
        horizon.alert('info', 
          '{% trans "This is taking longer than expected. Please wait..." %}');
      }, timeoutSeconds * 1000);
    });
    
    // Clear timeout if page changes
    $(window).on('beforeunload', function() {
      if (timeoutWarning) clearTimeout(timeoutWarning);
    });
  </script>
{% endblock %}
```

---

## Testing Checklist

### Error Handling Tests

#### Test 1: Quota Exceeded
```
1. Find your current quota:
   openstack quota show
   
2. Create key pairs until quota is reached
3. Try to create one more
4. ✅ Verify: Clear error message about quota
5. ✅ Verify: Message suggests deleting old keys or requesting increase
6. ✅ Verify: Form stays open (doesn't close on error)
```

#### Test 2: Duplicate Name
```
1. Create a key pair "test-duplicate"
2. Try to create another with same name
3. ✅ Verify: Error mentions the specific name
4. ✅ Verify: Suggests choosing different name
5. ✅ Verify: Name field is highlighted as invalid
```

#### Test 3: Invalid Characters in Name
```
1. Try name: "test key@#$"
2. ✅ Verify: HTML5 validation catches it (instant feedback)
3. ✅ Verify: Tooltip shows allowed characters
4. ✅ Verify: Can't submit until fixed
```

#### Test 4: Private Key Pasted (Import)
```
1. Generate a key: ssh-keygen -t rsa -f /tmp/test -N ""
2. Copy PRIVATE key: cat /tmp/test
3. Try to import it
4. ✅ Verify: Clear error "You appear to have pasted a private key"
5. ✅ Verify: Suggests using .pub file instead
```

#### Test 5: Truncated Public Key
```
1. Copy a public key but only first 50 characters
2. Try to import
3. ✅ Verify: Error "Public key is too short"
4. ✅ Verify: Suggests copying entire key
5. ✅ Verify: Character counter shows warning
```

#### Test 6: Network Timeout (Simulated)
```
1. Temporarily block Nova API:
   sudo iptables -A OUTPUT -d <nova-api-ip> -j DROP
   
2. Try to create key pair
3. ✅ Verify: Loading spinner shows
4. ✅ Verify: After ~30 sec, timeout warning appears
5. ✅ Verify: Eventually shows connection error
6. ✅ Verify: Error message mentions network issue
   
7. Restore connection:
   sudo iptables -D OUTPUT -d <nova-api-ip> -j DROP
```

### Accessibility Tests

#### Test 1: Keyboard Navigation
```
1. Open create form
2. Use only keyboard (Tab, Enter, Esc)
3. ✅ Verify: Can navigate between all fields
4. ✅ Verify: Can submit with Enter
5. ✅ Verify: Can close with Esc
6. ✅ Verify: Focus is visible (outline/highlight)
```

#### Test 2: Screen Reader (if available)
```
1. Enable screen reader (VoiceOver, NVDA, etc.)
2. Navigate create form
3. ✅ Verify: Labels are read correctly
4. ✅ Verify: Help text is announced
5. ✅ Verify: Error messages are announced
6. ✅ Verify: Button states are announced
```

#### Test 3: High Contrast Mode
```
1. Enable high contrast mode (Windows/Linux)
2. View forms
3. ✅ Verify: All text is readable
4. ✅ Verify: Form fields are visible
5. ✅ Verify: Focus indicators are visible
```

### UX Tests

#### Test 1: Loading Indicators
```
1. Create key pair
2. ✅ Verify: Button changes to "Creating..." with spinner
3. ✅ Verify: Button is disabled during creation
4. ✅ Verify: Can't double-submit
5. On slow connection, verify timeout warning appears
```

#### Test 2: Character Counter (Import)
```
1. Start pasting public key
2. ✅ Verify: Counter shows character count
3. ✅ Verify: Warning if <100 characters
4. ✅ Verify: Success indicator if >100 characters
5. ✅ Verify: Updates in real-time
```

#### Test 3: Auto-focus
```
1. Click "Create Key Pair"
2. ✅ Verify: Name field is automatically focused
3. ✅ Verify: Can start typing immediately
4. No need to click in field
```

---

## Commit Message Template

```
Improve error handling and UX polish for key pair forms

Enhances the key pair forms with comprehensive error handling,
improved accessibility, and UI polish based on testing and
best practices. Addresses edge cases and provides better user
guidance throughout the workflow.

Improvements:
- Enhanced error handling in forms.py
  - Specific exception handling (Conflict, Quota, NotAuthorized)
  - User-friendly error messages with actionable guidance
  - Common mistake detection (private vs. public key)
  - Detailed validation error messages
  - Quota exceeded guidance (delete or request increase)
  - Network/timeout error handling
  
- Accessibility improvements in templates
  - ARIA labels and descriptions
  - Keyboard navigation support
  - Screen reader friendly
  - HTML5 form validation with pattern attributes
  - Auto-focus on form open
  - Clear focus indicators
  
- UX enhancements
  - Loading indicators during API calls
  - Disabled submit button to prevent double-submission
  - Character counter for public key import
  - Real-time validation feedback
  - Timeout warnings for slow API responses
  - Better help text and explanations
  
- Form field improvements
  - Custom error messages
  - HTML5 validation patterns
  - Spell check disabled for key data
  - Better placeholders
  - Tooltip guidance

Error Handling Cases:
- Quota exceeded → clear message with remediation steps
- Duplicate name → specific name mentioned in error
- Invalid public key → detailed format requirements
- Private key pasted → detects and warns user
- Network timeout → connection guidance
- Permission denied → suggests contacting admin
- Generic errors → user-friendly fallback messages

Accessibility Features:
- ARIA attributes for screen readers
- Keyboard-only navigation
- High contrast mode support
- Focus management
- Semantic HTML

Partial-Bug: #OSPRH-12802
Change-Id: Ixxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Topic: de-angularize
```

---

## Expected Reviewer Questions

### Q1: "Is HTML5 validation enough? Why also server-side?"

**A**: HTML5 validation provides instant UX feedback, but server-side validation is mandatory for security. Users can bypass client-side validation. Defense in depth.

### Q2: "Why not use JavaScript framework for validation?"

**A**: Horizon uses Django's form validation. Adding JS framework would be inconsistent with codebase. Progressive enhancement: HTML5 → Django validation → user-friendly errors.

### Q3: "Should we add rate limiting?"

**A**: Rate limiting is typically handled at the API gateway/Nova level, not in Horizon. Horizon should handle the resulting 429 errors gracefully (which we do).

---

## Next Steps

After Patchset 4:

1. **Patchset 5**: Add comprehensive unit and integration tests

---

**Status**: 📋 Ready for implementation  
**Estimated Time**: 1 day  
**Complexity**: Medium  
**Focus**: Error handling, accessibility, UX


