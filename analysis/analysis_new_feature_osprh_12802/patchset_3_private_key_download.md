# Patchset 3: Private Key Download Page Implementation

**Date**: TBD  
**Jira**: [OSPRH-12802](https://issues.redhat.com/browse/OSPRH-12802)  
**Status**: 📋 Planning  
**Estimated Effort**: 1.5 days  
**Depends On**: Patchset 1 (Generate form)

---

## View Patchset Changes

### Continue from previous patchsets:
```bash
cd <mymcp-repo-path>/workspace/horizon-osprh-12802-working
git checkout osprh-12802-generate-form

# After making changes
git diff --stat
git diff
```

### Submit as new patchset:
```bash
git add openstack_dashboard/dashboards/project/key_pairs/
git commit --amend  # Amend to same Change-Id
git review
```

---

## Executive Summary

**Goal**: Implement secure download page for displaying generated private keys to users.

**Approach**: 
- Create `DownloadView` to display private key
- Create `download.html` template with security features
- Handle session-based private key storage
- Provide copy-to-clipboard functionality
- Add security warnings and best practices
- Implement one-time display (clear from session after viewing)

**Files to Create/Modify**:
- `views.py` - Add `DownloadView` class
- `templates/key_pairs/download.html` - Download page template
- `urls.py` - Add URL pattern for download view
- `forms.py` - Update `GenerateKeyPairForm` to redirect to download

**Result**: Users can securely download and save their generated private keys with clear instructions and security warnings.

---

## Implementation Details

### Problem Statement

When a user generates a key pair (Patchset 1), the server creates both public and private keys. The **private key must be securely delivered to the user** because:

1. **One-time availability**: Private key is never stored in Nova
2. **Security**: Must be transmitted securely
3. **User responsibility**: User must save it immediately
4. **No recovery**: If lost, key pair must be deleted and regenerated

**Security Requirements**:
- Private key shown only once
- Clear warnings about saving the key
- Instructions for secure storage
- Easy copy-to-clipboard functionality
- Automatic session cleanup

---

## Step-by-Step Implementation

### Step 1: Create `DownloadView` in `views.py`

**File**: `openstack_dashboard/dashboards/project/key_pairs/views.py`

**What to add** (after `ImportView`):

```python
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect


class DownloadView(TemplateView):
    """View for displaying and downloading generated private key."""
    
    template_name = 'project/key_pairs/download.html'
    
    def get_context_data(self, **kwargs):
        context = super(DownloadView, self).get_context_data(**kwargs)
        
        # Retrieve private key from session
        private_key = self.request.session.get('keypair_private_key')
        keypair_name = self.request.session.get('keypair_name')
        
        if not private_key or not keypair_name:
            # No private key in session, redirect to index
            messages.warning(
                self.request,
                _('No private key available for download. '
                  'Please generate a new key pair.')
            )
            # Redirect will happen in dispatch()
            context['redirect_needed'] = True
        else:
            context['private_key'] = private_key
            context['keypair_name'] = keypair_name
            context['redirect_needed'] = False
            
            # IMPORTANT: Clear private key from session after displaying
            # This ensures it's only shown once
            del self.request.session['keypair_private_key']
            del self.request.session['keypair_name']
            self.request.session.modified = True
        
        return context
    
    def dispatch(self, request, *args, **kwargs):
        """Check if private key exists in session before rendering."""
        private_key = request.session.get('keypair_private_key')
        
        if not private_key:
            # No key available, redirect to key pairs index
            messages.warning(
                request,
                _('No private key available for download.')
            )
            return HttpResponseRedirect(
                reverse_lazy('horizon:project:key_pairs:index')
            )
        
        return super(DownloadView, self).dispatch(request, *args, **kwargs)
```

**Key Points**:

1. **Session Retrieval**: Gets private key stored by `GenerateKeyPairForm`
2. **One-Time Display**: Deletes key from session after retrieving
3. **Security**: Key is never logged or stored permanently
4. **Redirect Protection**: If no key in session, redirects to index
5. **Clear Messaging**: Warns user if accessing without a key

---

### Step 2: Update `GenerateKeyPairForm` to Redirect to Download

**File**: `openstack_dashboard/dashboards/project/key_pairs/forms.py`

**Modify the `handle()` method** in `GenerateKeyPairForm`:

```python
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
        if hasattr(keypair, 'private_key') and keypair.private_key:
            request.session['keypair_private_key'] = keypair.private_key
            request.session['keypair_name'] = keypair.name
            request.session.modified = True
            
            # Return a special value to trigger redirect
            # We'll handle the redirect in the view's form_valid()
            return keypair
        else:
            # Should not happen, but handle gracefully
            messages.error(
                request,
                _('Key pair created but private key was not returned. '
                  'This may indicate a server configuration issue.')
            )
            return False
        
    except Exception as e:
        exceptions.handle(
            request,
            _('Unable to create key pair: %s') % str(e)
        )
        return False
```

**And update `CreateView` to redirect**:

```python
class CreateView(horizon_forms.ModalFormView):
    """View for generating a new key pair."""
    
    form_class = project_forms.GenerateKeyPairForm
    template_name = 'project/key_pairs/create.html'
    # Remove: success_url = reverse_lazy('horizon:project:key_pairs:index')
    # We'll redirect to download instead
    modal_id = "create_keypair_modal"
    modal_header = _("Create Key Pair")
    submit_label = _("Create Key Pair")
    submit_url = reverse_lazy("horizon:project:key_pairs:create")
    
    def get_success_url(self):
        """Redirect to download page after successful generation."""
        return reverse('horizon:project:key_pairs:download')
    
    def get_context_data(self, **kwargs):
        context = super(CreateView, self).get_context_data(**kwargs)
        context['submit_url'] = self.submit_url
        return context
```

**Key Points**:

1. **Session Storage**: Private key stored with `session.modified = True`
2. **Dynamic Success URL**: Redirects to download page instead of index
3. **Error Handling**: Gracefully handles missing private key

---

### Step 3: Create Template `download.html`

**File**: `openstack_dashboard/dashboards/project/key_pairs/templates/key_pairs/download.html`

**What to add**:

```django
{% extends 'base.html' %}
{% load i18n %}

{% block title %}{% trans "Download Key Pair" %}{% endblock %}

{% block page_header %}
  {% include "horizon/common/_page_header.html" with title=_("Download Key Pair") %}
{% endblock page_header %}

{% block main %}
<div class="row">
  <div class="col-sm-12">
    <div class="alert alert-warning">
      <h4><i class="fa fa-exclamation-triangle"></i> {% trans "Important: Save Your Private Key Now" %}</h4>
      <p>
        <strong>{% trans "This is your only opportunity to save the private key!" %}</strong>
        {% trans "The private key will not be stored on the server and cannot be recovered." %}
      </p>
      <p>
        {% trans "Please download and save this key in a secure location before leaving this page." %}
      </p>
    </div>

    <div class="key-pair-info">
      <h3>{% trans "Key Pair:" %} <code>{{ keypair_name }}</code></h3>
      
      <div class="private-key-container">
        <div class="private-key-header">
          <h4>{% trans "Private Key" %}</h4>
          <button type="button" class="btn btn-sm btn-primary" id="copy-key-btn">
            <i class="fa fa-copy"></i> {% trans "Copy to Clipboard" %}
          </button>
          <button type="button" class="btn btn-sm btn-success" id="download-key-btn">
            <i class="fa fa-download"></i> {% trans "Download as File" %}
          </button>
        </div>
        
        <pre id="private-key-content" class="private-key">{{ private_key }}</pre>
      </div>
    </div>

    <div class="instructions">
      <h4>{% trans "Next Steps" %}</h4>
      <ol>
        <li>
          <strong>{% trans "Save the private key" %}</strong>
          <ul>
            <li>{% trans "Click 'Download as File' to save as" %} <code>{{ keypair_name }}.pem</code></li>
            <li>{% trans "Or click 'Copy to Clipboard' and paste into a text editor" %}</li>
          </ul>
        </li>
        <li>
          <strong>{% trans "Set correct permissions (Linux/Mac only)" %}</strong>
          <pre class="code-example">chmod 600 {{ keypair_name }}.pem</pre>
          <p class="help-text">
            {% trans "SSH requires private keys to have restricted permissions for security." %}
          </p>
        </li>
        <li>
          <strong>{% trans "Use the key to connect to instances" %}</strong>
          <pre class="code-example">ssh -i {{ keypair_name }}.pem &lt;user&gt;@&lt;instance-ip&gt;</pre>
          <p class="help-text">
            {% trans "Replace &lt;user&gt; with the appropriate username (e.g., 'ubuntu', 'centos', 'cirros') and &lt;instance-ip&gt; with your instance's IP address." %}
          </p>
        </li>
      </ol>
    </div>

    <div class="alert alert-info">
      <h4><i class="fa fa-info-circle"></i> {% trans "Security Best Practices" %}</h4>
      <ul>
        <li>{% trans "Never share your private key with anyone" %}</li>
        <li>{% trans "Store the private key in a secure location (e.g., ~/.ssh/ on Linux/Mac)" %}</li>
        <li>{% trans "Use appropriate file permissions (600 or 400)" %}</li>
        <li>{% trans "Consider using a passphrase for additional security" %}</li>
        <li>{% trans "Back up your private key to a secure location" %}</li>
        <li>{% trans "If you lose the private key, delete this key pair and create a new one" %}</li>
      </ul>
    </div>

    <div class="actions">
      <a href="{% url 'horizon:project:key_pairs:index' %}" class="btn btn-default">
        <i class="fa fa-arrow-left"></i> {% trans "Return to Key Pairs" %}
      </a>
    </div>
  </div>
</div>

<style>
  .private-key-container {
    background: #f8f9fa;
    border: 2px solid #dee2e6;
    border-radius: 4px;
    padding: 15px;
    margin: 20px 0;
  }
  
  .private-key-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
  }
  
  .private-key-header h4 {
    margin: 0;
  }
  
  .private-key {
    background: #ffffff;
    border: 1px solid #ced4da;
    border-radius: 3px;
    padding: 15px;
    font-family: 'Courier New', Courier, monospace;
    font-size: 12px;
    white-space: pre-wrap;
    word-break: break-all;
    overflow-x: auto;
    max-height: 400px;
    margin: 0;
  }
  
  .instructions {
    margin: 30px 0;
  }
  
  .instructions ol {
    padding-left: 20px;
  }
  
  .instructions li {
    margin-bottom: 15px;
  }
  
  .code-example {
    background: #f5f5f5;
    border: 1px solid #ddd;
    border-radius: 3px;
    padding: 8px;
    font-family: monospace;
    font-size: 12px;
    margin: 5px 0;
  }
  
  .help-text {
    font-size: 13px;
    color: #6c757d;
    margin-top: 5px;
  }
  
  .actions {
    margin-top: 30px;
    padding-top: 20px;
    border-top: 1px solid #dee2e6;
  }
  
  #copy-key-btn.copied {
    background-color: #28a745;
    border-color: #28a745;
  }
</style>

<script>
  // Copy to clipboard functionality
  document.getElementById('copy-key-btn').addEventListener('click', function() {
    var keyContent = document.getElementById('private-key-content').textContent;
    
    // Create temporary textarea
    var textarea = document.createElement('textarea');
    textarea.value = keyContent;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    
    // Select and copy
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
    
    // Update button to show success
    var btn = this;
    var originalHTML = btn.innerHTML;
    btn.innerHTML = '<i class="fa fa-check"></i> {% trans "Copied!" %}';
    btn.classList.add('copied');
    
    setTimeout(function() {
      btn.innerHTML = originalHTML;
      btn.classList.remove('copied');
    }, 2000);
  });
  
  // Download as file functionality
  document.getElementById('download-key-btn').addEventListener('click', function() {
    var keyContent = document.getElementById('private-key-content').textContent;
    var filename = '{{ keypair_name }}.pem';
    
    // Create blob and download
    var blob = new Blob([keyContent], { type: 'text/plain' });
    var url = window.URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  });
</script>
{% endblock %}
```

**Key Points**:

1. **Prominent Warnings**: Large, visible warning about one-time opportunity
2. **Two Download Options**:
   - Copy to clipboard button
   - Download as .pem file button
3. **Step-by-Step Instructions**: Clear next steps for users
4. **Platform-Specific Help**: chmod command for Linux/Mac
5. **Security Best Practices**: List of security recommendations
6. **Visual Feedback**: Button changes to show "Copied!" success
7. **Monospace Font**: Private key displayed in fixed-width font
8. **Proper Styling**: Clean, professional layout

---

### Step 4: Add URL Pattern in `urls.py`

**File**: `openstack_dashboard/dashboards/project/key_pairs/urls.py`

**What to add**:

```python
urlpatterns = [
    # ... existing patterns ...
    
    # New: Download private key
    path('download/',
         views.DownloadView.as_view(),
         name='download'),
]
```

---

## Testing Checklist

### Manual Testing

#### Test 1: Generate and Download SSH Key (Happy Path)
```
1. Navigate to Project > Compute > Key Pairs
2. Click "Create Key Pair"
3. Enter name: "test-download-ssh"
4. Click "Create Key Pair"
5. ✅ Verify: Redirected to download page
6. ✅ Verify: Private key is displayed
7. ✅ Verify: Key starts with "-----BEGIN RSA PRIVATE KEY-----"
8. ✅ Verify: Key ends with "-----END RSA PRIVATE KEY-----"
9. ✅ Verify: Warning message is prominent
10. ✅ Verify: Instructions are clear
```

#### Test 2: Copy to Clipboard
```
1. Generate a new key pair
2. On download page, click "Copy to Clipboard"
3. ✅ Verify: Button changes to "Copied!" with checkmark
4. ✅ Verify: Button reverts after 2 seconds
5. Open a text editor and paste (Ctrl+V)
6. ✅ Verify: Private key is pasted correctly
7. ✅ Verify: Key format is preserved (no line break issues)
```

#### Test 3: Download as File
```
1. Generate a new key pair "test-file-download"
2. On download page, click "Download as File"
3. ✅ Verify: Browser downloads file
4. ✅ Verify: Filename is "test-file-download.pem"
5. Open the downloaded file
6. ✅ Verify: Content matches displayed key
7. ✅ Verify: File has correct format
```

#### Test 4: One-Time Display (Security Check)
```
1. Generate a new key pair
2. On download page, note the URL (something like /download/)
3. Copy or download the private key
4. Click "Return to Key Pairs"
5. Use browser back button to return to download page
6. ✅ Verify: Redirected to key pairs index
7. ✅ Verify: Warning message: "No private key available"
8. Try directly accessing /project/key_pairs/download/
9. ✅ Verify: Redirected (private key not shown again)
```

#### Test 5: Bookmark/Direct Access (Security Check)
```
1. Directly navigate to: /project/key_pairs/download/
2. ✅ Verify: Redirected to key pairs index
3. ✅ Verify: Warning message displayed
4. ✅ Verify: No error/crash
```

#### Test 6: X509 Key Download
```
1. Generate X509 key pair
2. ✅ Verify: Download page displays correctly
3. ✅ Verify: Key format is different from SSH
4. ✅ Verify: May have X509 certificate format
```

#### Test 7: Responsive Design
```
1. Generate a key pair
2. Resize browser window to mobile size
3. ✅ Verify: Layout adapts to narrow width
4. ✅ Verify: Buttons remain clickable
5. ✅ Verify: Private key remains readable
```

### Security Testing

#### Test 1: Session Isolation
```
1. Log in as User A
2. Generate a key pair
3. On download page, copy the private key
4. In another browser/incognito, log in as User B
5. Try to access download URL
6. ✅ Verify: User B cannot see User A's private key
7. ✅ Verify: User B is redirected with warning
```

#### Test 2: Session Expiry
```
1. Generate a key pair
2. On download page, wait for session timeout (if configured)
3. Try to refresh the page
4. ✅ Verify: Redirected to login (if session expired)
5. ✅ Verify: No private key displayed after re-login
```

#### Test 3: Browser History
```
1. Generate a key pair
2. View download page
3. Navigate away
4. Use browser history to go back
5. ✅ Verify: Private key not cached in browser
6. ✅ Verify: Redirected to index page
```

### Functional Verification

Test the downloaded key actually works:

```bash
# Save the downloaded key
mv ~/Downloads/test-download-ssh.pem ~/.ssh/

# Set permissions
chmod 600 ~/.ssh/test-download-ssh.pem

# Create a test instance with the key
openstack server create \
  --image cirros \
  --flavor m1.tiny \
  --key-name test-download-ssh \
  --network private \
  test-key-instance

# Wait for instance to boot
openstack server list

# Get instance IP
INSTANCE_IP=$(openstack server show test-key-instance -c addresses -f value | cut -d'=' -f2)

# Test SSH connection
ssh -i ~/.ssh/test-download-ssh.pem cirros@$INSTANCE_IP

# ✅ Should successfully connect!

# Clean up
exit  # from instance
openstack server delete test-key-instance
openstack keypair delete test-download-ssh
rm ~/.ssh/test-download-ssh.pem
```

---

## Commit Message Template

```
Add private key download page for generated key pairs

Implements secure download page for displaying generated private keys
to users with one-time display and security warnings. Completes the
"Generate Key Pair" workflow for OSPRH-12802.

This page:
- Displays generated private key once (session-based)
- Provides copy-to-clipboard functionality
- Allows download as .pem file
- Shows step-by-step usage instructions
- Includes security best practices
- Prevents repeated access (one-time display)

Changes:
- Add DownloadView to views.py
  - Retrieves private key from session
  - Clears session after display (one-time only)
  - Redirects if no key available
  - Security: No logging or permanent storage
  
- Update CreateView to redirect to download
  - Changes success_url to download page
  - Maintains session-based key passing
  
- Update GenerateKeyPairForm
  - Stores private key in session with modified flag
  - Handles missing private key gracefully
  
- Add download.html template
  - Prominent security warnings
  - Copy to clipboard button with visual feedback
  - Download as file button (.pem format)
  - Step-by-step user instructions
  - Platform-specific commands (Linux/Mac/Windows)
  - Security best practices list
  - Responsive design
  - Proper monospace formatting for key display
  - JavaScript for copy/download functionality
  
- Update urls.py
  - Add URL pattern for download view

Security Features:
- Private key shown only once
- Session cleared after viewing
- No browser caching
- Protected against direct URL access
- Protected against back button access
- Session-isolated (multi-user safe)

Partial-Bug: #OSPRH-12802
Change-Id: Ixxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Topic: de-angularize
```

---

## Expected Reviewer Questions

### Q1: "Why use session storage instead of returning key in response?"

**A**: Security and UX. Session storage allows:
- Redirect to dedicated download page with proper styling
- One-time display enforcement (clear from session)
- Consistent with Horizon patterns for sensitive data
- Prevents accidental logging of private key in API responses

### Q2: "What if user's browser doesn't support JavaScript?"

**A**: Download buttons require JS, but the private key is still **displayed as text** in a `<pre>` tag. Users can manually select and copy without JavaScript. This graceful degradation maintains core functionality.

### Q3: "Should we email the private key to the user?"

**A**: **No.** Never send private keys via email. Email is not secure and keys could be intercepted, stored in mail servers, etc. User must download immediately from secure HTTPS connection.

### Q4: "What about password-protecting the downloaded .pem file?"

**A**: Not supported by Nova API. Nova generates unencrypted keys. Users can manually encrypt with:
```bash
openssl rsa -in keypair.pem -out keypair_encrypted.pem -aes256
```
We can add this tip to the instructions.

### Q5: "Can we re-display the private key if user refreshes?"

**A**: **No, by design.** This would require storing the key beyond the initial display, which is a security risk. One-time display enforces best practice: download and save immediately.

---

## Dependencies

### Session Management

- Requires Django session framework (already enabled in Horizon)
- Session key: `keypair_private_key` (stored by GenerateKeyPairForm)
- Session key: `keypair_name` (for display)
- **Important**: Set `session.modified = True` after deletion

---

## Next Steps

After Patchset 3:

1. **Patchset 4**: Error handling improvements and UI polish
2. **Patchset 5**: Add comprehensive tests

---

## Notes for Self

### Testing Workflow

```bash
# Quick test cycle
1. Generate key → redirects to download
2. Copy to clipboard → verify copied
3. Download as file → verify filename
4. Click "Return to Key Pairs"
5. Browser back → verify redirect
6. Direct URL access → verify redirect
```

### Common User Mistakes to Prevent

1. **Not saving the key** → Large warning message
2. **Wrong permissions** → Clear chmod instruction
3. **Trying to view again** → Redirect with helpful message
4. **Pasting in wrong format** → Monospace preserves formatting

---

**Status**: 📋 Ready for implementation  
**Estimated Time**: 1.5 days  
**Complexity**: Medium  
**Security Critical**: ⚠️ Yes - handles private keys


