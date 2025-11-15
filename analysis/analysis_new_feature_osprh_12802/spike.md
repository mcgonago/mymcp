# Spike: OSPRH-12802 - Implement Key Pair Create Form in Python

**Jira**: [OSPRH-12802](https://issues.redhat.com/browse/OSPRH-12802)  
**Epic**: [OSPRH-12801](https://issues.redhat.com/browse/OSPRH-12801) - Remove angular.js from Horizon  
**Related**: OSPRH-12803 (Key Pairs expandable rows - ✅ Complete)  
**Type**: Feature Implementation  
**Estimated Complexity**: Medium  
**Date Created**: November 15, 2025

---

## Overview

Convert the Key Pair creation form from AngularJS to a pure Python/Django implementation. This completes the de-angularization of the Key Pairs panel, building on the successful expandable rows work (Review 966349).

## Problem Statement

The Key Pairs panel currently uses an AngularJS-based form for creating new key pairs when `ANGULAR_FEATURES['key_pairs_panel'] = True`. We need to implement equivalent functionality using Django forms and templates.

### Current State
- AngularJS handles form rendering and validation
- Located in: `openstack_dashboard/static/app/core/keypairs/`
- Uses Angular directives for dynamic form behavior

### Desired State
- Pure Python/Django form implementation
- Server-side validation
- Maintains all existing functionality
- Consistent UI/UX with Angular version

## Success Criteria

- [ ] Create form implemented in Python
- [ ] All form fields present and functional
- [ ] Validation matches Angular version
- [ ] Import key pair workflow supported
- [ ] Generate key pair workflow supported
- [ ] PEP8 compliant
- [ ] Unit tests pass
- [ ] Manual testing complete (3+ scenarios)
- [ ] Upstream review submitted with topic: `de-angularize`

## Key Technical Areas

### 1. Form Types

The Key Pairs panel supports **two creation workflows**:

#### A. Generate Key Pair
- User provides only a name
- Server generates SSH key pair
- Private key downloaded to user
- Public key stored in Nova

#### B. Import Key Pair
- User provides name and public key
- Server stores public key in Nova
- No private key (user already has it)

### 2. Form Fields

Based on Review 966349 knowledge and OpenStack Nova API:

| Field | Type | Required | Validation | Workflow |
|-------|------|----------|------------|----------|
| Name | Text | Yes | Alphanumeric, hyphens, underscores | Both |
| Key Type | Choice | No | `ssh` or `x509` (default: `ssh`) | Generate |
| Public Key | Textarea | Yes | Valid SSH public key format | Import |

### 3. Form Validation

**Name Field**:
- Must be unique per user/project
- 1-255 characters
- Pattern: `^[a-zA-Z0-9-_]+$`

**Public Key Field** (Import only):
- Must be valid SSH public key format
- Starts with algorithm (ssh-rsa, ssh-ed25519, etc.)
- Contains base64-encoded key data
- Optional comment at end

**Key Type Field** (Generate only):
- Default: `ssh`
- Alternative: `x509` (less common)

## Code Areas of Concern

### Files to Create/Modify

```
openstack_dashboard/dashboards/project/key_pairs/
├── forms.py                   # MODIFY: Add CreateKeyPair, ImportKeyPair forms
├── views.py                   # MODIFY: Add CreateView, ImportView
├── urls.py                    # MODIFY: Add URL patterns
├── tables.py                  # ALREADY DONE: ExpandableKeyPairRow (Review 966349)
├── templates/
│   └── key_pairs/
│       ├── create.html        # CREATE: Generate key pair form
│       ├── import.html        # CREATE: Import key pair form
│       └── download.html      # CREATE: Private key download page
└── tests/
    ├── test_forms.py          # MODIFY: Add test cases
    └── test_views.py          # MODIFY: Add test cases
```

### Integration Points

1. **Nova Client** (`novaclient.v2.keypairs`)
   - `keypairs.create(name, public_key=None, key_type='ssh')`
   - Error handling for duplicate names
   - Error handling for invalid public keys

2. **Horizon Base Forms**
   - Inherit from `horizon.forms.SelfHandlingForm`
   - Use horizon's form handling patterns
   - Integrate with horizon messages framework

3. **URL Routing**
   - Add routes for create/import views
   - Maintain backward compatibility

## Investigation Plan

### Phase 1: Angular Code Analysis (1 day)
1. Review existing AngularJS implementation
   - `openstack_dashboard/static/app/core/keypairs/actions/`
   - Identify all form fields and validation logic
   - Document UI/UX behavior

2. Map Angular features to Django patterns
   - Form field types
   - Validation rules
   - Error handling
   - Success messages

### Phase 2: Python Implementation (3 days)

#### Step 1: Create Forms (`forms.py`)
```python
class GenerateKeyPairForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length=255, label=_("Key Pair Name"))
    key_type = forms.ChoiceField(
        choices=[('ssh', 'SSH'), ('x509', 'X509')],
        initial='ssh',
        required=False
    )
    
    def handle(self, request, data):
        # Generate key pair via Nova
        # Return private key for download
        pass

class ImportKeyPairForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length=255, label=_("Key Pair Name"))
    public_key = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        label=_("Public Key")
    )
    
    def clean_public_key(self):
        # Validate SSH public key format
        pass
    
    def handle(self, request, data):
        # Import key pair via Nova
        pass
```

#### Step 2: Create Views (`views.py`)
```python
class CreateView(forms.ModalFormView):
    form_class = project_forms.GenerateKeyPairForm
    template_name = 'project/key_pairs/create.html'
    success_url = reverse_lazy('horizon:project:key_pairs:index')
    modal_id = "create_keypair_modal"
    modal_header = _("Create Key Pair")
    submit_label = _("Create Key Pair")

class ImportView(forms.ModalFormView):
    form_class = project_forms.ImportKeyPairForm
    template_name = 'project/key_pairs/import.html'
    success_url = reverse_lazy('horizon:project:key_pairs:index')
    modal_id = "import_keypair_modal"
    modal_header = _("Import Key Pair")
    submit_label = _("Import Key Pair")
```

#### Step 3: Create Templates
- `create.html` - Generation form
- `import.html` - Import form
- `download.html` - Private key download

#### Step 4: Update URLs (`urls.py`)
```python
urlpatterns = [
    path('create/', views.CreateView.as_view(), name='create'),
    path('import/', views.ImportView.as_view(), name='import'),
    # ... existing patterns ...
]
```

#### Step 5: Update Table Actions (`tables.py`)
```python
# Ensure actions point to new views
class CreateKeyPair(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Key Pair")
    url = "horizon:project:key_pairs:create"
    classes = ("ajax-modal",)

class ImportKeyPair(tables.LinkAction):
    name = "import"
    verbose_name = _("Import Key Pair")
    url = "horizon:project:key_pairs:import"
    classes = ("ajax-modal",)
```

### Phase 3: Testing (2 days)
1. Unit tests for forms
2. Unit tests for views
3. Manual testing scenarios:
   - Generate SSH key pair
   - Generate X509 key pair
   - Import valid public key
   - Import invalid public key (error handling)
   - Duplicate key pair name (error handling)
   - Download private key
4. Browser testing (Chrome, Firefox)

### Phase 4: Documentation (1 day)
1. Update inline code comments
2. Document form field choices
3. Update any user-facing documentation
4. Create patchset commit message

**Total Estimated Time**: 7 days (1.5 sprints)

## Proposed Work Items (Incremental Patchsets)

### Patchset 1: Generate Key Pair Form
- Add `GenerateKeyPairForm` to `forms.py`
- Add `CreateView` to `views.py`
- Create `create.html` template
- Basic validation only
- **Commit**: "Add Python implementation for key pair generation form"

### Patchset 2: Import Key Pair Form
- Add `ImportKeyPairForm` to `forms.py`
- Add `ImportView` to `views.py`
- Create `import.html` template
- Public key validation
- **Commit**: "Add Python implementation for key pair import form"

### Patchset 3: Private Key Download
- Create `download.html` template
- Implement secure private key display
- Add download functionality
- **Commit**: "Add private key download page"

### Patchset 4: Error Handling & Polish
- Enhanced validation
- Better error messages
- UI/UX refinements based on feedback
- **Commit**: "Improve error handling for key pair forms"

### Patchset 5: Tests & Documentation
- Unit tests for all forms
- Unit tests for all views
- PEP8 compliance
- **Commit**: "Add tests for key pair form implementations"

## Dependencies

### Upstream Dependencies
- Review 966349 (Key Pairs expandable rows) - ✅ Complete

### Downstream Dependencies
- None (this completes the Key Pairs de-angularization)

## Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Breaking existing workflows | High | Medium | Thorough testing, maintain backward compatibility |
| Private key security issues | Critical | Low | Follow Horizon patterns, secure download handling |
| Validation differences from Angular | Medium | Medium | Carefully map Angular validation to Django |
| Nova API changes | Medium | Low | Use stable Nova API v2 |

## Lessons from Review 966349

### Apply These Patterns
1. ✅ Use Bootstrap components (no custom JS unless necessary)
2. ✅ Prioritize CSS specificity over `!important`
3. ✅ Extract helper functions (DRY principle)
4. ✅ Respond to reviewer feedback gracefully
5. ✅ Ensure PEP8 compliance early

### Avoid These Issues
1. ❌ Don't assume framework features without testing
2. ❌ Don't add custom JS when framework provides it
3. ❌ Don't use `!important` in CSS
4. ❌ Don't skip validation edge cases

## Testing Checklist

### Functional Tests
- [ ] Generate SSH key pair - name only
- [ ] Generate X509 key pair - with key type
- [ ] Import valid SSH-RSA public key
- [ ] Import valid ED25519 public key
- [ ] Import multi-line public key
- [ ] Import key with comment
- [ ] Download generated private key
- [ ] Private key displayed correctly (monospace, copyable)

### Error Handling Tests
- [ ] Duplicate key pair name
- [ ] Invalid public key format
- [ ] Empty name field
- [ ] Name with invalid characters
- [ ] Public key too short
- [ ] Public key with invalid algorithm

### UI/UX Tests
- [ ] Form opens in modal
- [ ] Form validates on submit
- [ ] Error messages display inline
- [ ] Success message after creation
- [ ] Table updates after creation
- [ ] Download button works
- [ ] Form cancels cleanly

## Next Steps After Spike

1. Set up dev environment (if not already done)
2. Analyze Angular implementation in detail
3. Create Patchset 1 (Generate form)
4. Submit for review with topic: `de-angularize`
5. Iterate based on feedback
6. Continue with Patchsets 2-5

---

## References

- [Nova API Documentation](https://docs.openstack.org/api-ref/compute/)
- [Nova Keypairs API](https://docs.openstack.org/api-ref/compute/#keypairs-keypairs)
- [Horizon Forms Documentation](https://docs.openstack.org/horizon/latest/contributor/topics/forms.html)
- [Review 966349: Key Pairs Expandable Rows](https://review.opendev.org/c/openstack/horizon/+/966349)
- [Best Practices for Feature Development](../docs/BEST_PRACTICES_FEATURE_DEV.md)
- [AngularJS Tickets Overview](../docs/ANGULAR_JS_TICKETS.md)

---

**Status**: 📋 Planning  
**Assigned To**: TBD  
**Target Completion**: TBD  
**Estimated Effort**: 7 days (1.5 sprints)

