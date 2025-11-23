# Patchset 5: Unit Tests & Final PEP8 Compliance

**Date**: TBD  
**Jira**: [OSPRH-12802](https://issues.redhat.com/browse/OSPRH-12802)  
**Status**: 📋 Planning  
**Estimated Effort**: 2 days  
**Depends On**: Patchsets 1-4  
**Final Patchset**: Yes - Ready for +2

---

## Executive Summary

**Goal**: Add comprehensive unit tests for all forms and views, ensure complete PEP8 compliance, and prepare for final review.

**Approach**: 
- Write unit tests for `GenerateKeyPairForm`
- Write unit tests for `ImportKeyPairForm`
- Write unit tests for `CreateView`, `ImportView`, `DownloadView`
- Test all error handling paths
- Test edge cases and validation
- Ensure 100% PEP8 compliance
- Run full test suite
- Final code review and cleanup

**Files to Create/Modify**:
- `tests/test_forms.py` - Comprehensive form tests
- `tests/test_views.py` - View tests
- All code files - PEP8 fixes

**Result**: Production-ready, fully-tested implementation ready for upstream merge.

---

## Implementation Details

### Problem Statement

Before submitting for final review, we must:

1. **Test Coverage**: Prove the code works in all scenarios
2. **PEP8 Compliance**: Follow OpenStack coding standards
3. **No Regressions**: Ensure existing tests still pass
4. **Documentation**: Add/update docstrings

**This patchset makes the code merge-ready.**

---

## Step-by-Step Implementation

### Step 1: Create Comprehensive Form Tests

**File**: `openstack_dashboard/dashboards/project/key_pairs/tests/test_forms.py`

**Create or update with**:

```python
# Copyright 2025 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from unittest import mock

from django.test.utils import override_settings

from openstack_dashboard import api
from openstack_dashboard.dashboards.project.key_pairs import forms
from openstack_dashboard.test import helpers as test


class GenerateKeyPairFormTests(test.TestCase):
    """Tests for GenerateKeyPairForm."""

    def setUp(self):
        super(GenerateKeyPairFormTests, self).setUp()
        self.request = self.factory.get('/project/key_pairs/create/')
        self.request.user = self.user
        self.request.session = {}

    @mock.patch.object(api.nova, 'keypair_create')
    def test_generate_keypair_success_ssh(self, mock_create):
        """Test successful SSH key pair generation."""
        # Mock Nova API response
        mock_keypair = mock.Mock()
        mock_keypair.name = 'test-keypair'
        mock_keypair.private_key = '-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----'
        mock_create.return_value = mock_keypair

        form_data = {
            'name': 'test-keypair',
            'key_type': 'ssh'
        }
        form = forms.GenerateKeyPairForm(self.request, data=form_data)

        self.assertTrue(form.is_valid())
        result = form.handle(self.request, form_data)

        # Verify Nova API called correctly
        mock_create.assert_called_once_with(
            self.request,
            'test-keypair',
            key_type='ssh'
        )

        # Verify private key stored in session
        self.assertEqual(
            self.request.session['keypair_private_key'],
            mock_keypair.private_key
        )
        self.assertEqual(
            self.request.session['keypair_name'],
            'test-keypair'
        )
        self.assertTrue(result)

    @mock.patch.object(api.nova, 'keypair_create')
    def test_generate_keypair_success_x509(self, mock_create):
        """Test successful X509 key pair generation."""
        mock_keypair = mock.Mock()
        mock_keypair.name = 'test-x509'
        mock_keypair.private_key = '-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----'
        mock_create.return_value = mock_keypair

        form_data = {
            'name': 'test-x509',
            'key_type': 'x509'
        }
        form = forms.GenerateKeyPairForm(self.request, data=form_data)

        self.assertTrue(form.is_valid())
        result = form.handle(self.request, form_data)

        mock_create.assert_called_once_with(
            self.request,
            'test-x509',
            key_type='x509'
        )
        self.assertTrue(result)

    def test_generate_keypair_invalid_name_special_chars(self):
        """Test validation error for invalid characters in name."""
        form_data = {
            'name': 'test keypair@#$',
            'key_type': 'ssh'
        }
        form = forms.GenerateKeyPairForm(self.request, data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_generate_keypair_empty_name(self):
        """Test validation error for empty name."""
        form_data = {
            'name': '',
            'key_type': 'ssh'
        }
        form = forms.GenerateKeyPairForm(self.request, data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_generate_keypair_name_too_long(self):
        """Test validation error for name exceeding max length."""
        form_data = {
            'name': 'a' * 256,  # Max is 255
            'key_type': 'ssh'
        }
        form = forms.GenerateKeyPairForm(self.request, data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    @mock.patch.object(api.nova, 'keypair_create')
    def test_generate_keypair_duplicate_name(self, mock_create):
        """Test error handling for duplicate key pair name."""
        from horizon import exceptions
        mock_create.side_effect = exceptions.Conflict('Duplicate')

        form_data = {
            'name': 'existing-keypair',
            'key_type': 'ssh'
        }
        form = forms.GenerateKeyPairForm(self.request, data=form_data)

        self.assertTrue(form.is_valid())
        result = form.handle(self.request, form_data)

        self.assertFalse(result)
        mock_create.assert_called_once()

    @mock.patch.object(api.nova, 'keypair_create')
    def test_generate_keypair_quota_exceeded(self, mock_create):
        """Test error handling for quota exceeded."""
        from horizon import exceptions
        mock_create.side_effect = exceptions.Quota('Quota exceeded')

        form_data = {
            'name': 'test-keypair',
            'key_type': 'ssh'
        }
        form = forms.GenerateKeyPairForm(self.request, data=form_data)

        self.assertTrue(form.is_valid())
        result = form.handle(self.request, form_data)

        self.assertFalse(result)

    @mock.patch.object(api.nova, 'keypair_create')
    def test_generate_keypair_not_authorized(self, mock_create):
        """Test error handling for permission denied."""
        from horizon import exceptions
        mock_create.side_effect = exceptions.NotAuthorized('Forbidden')

        form_data = {
            'name': 'test-keypair',
            'key_type': 'ssh'
        }
        form = forms.GenerateKeyPairForm(self.request, data=form_data)

        self.assertTrue(form.is_valid())
        result = form.handle(self.request, form_data)

        self.assertFalse(result)


class ImportKeyPairFormTests(test.TestCase):
    """Tests for ImportKeyPairForm."""

    def setUp(self):
        super(ImportKeyPairFormTests, self).setUp()
        self.request = self.factory.get('/project/key_pairs/import/')
        self.request.user = self.user
        self.valid_rsa_key = (
            'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC7Kxxx... test@example.com'
        )
        self.valid_ed25519_key = (
            'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIxxx... test@example.com'
        )

    @mock.patch.object(api.nova, 'keypair_import')
    def test_import_keypair_success_rsa(self, mock_import):
        """Test successful RSA key pair import."""
        mock_keypair = mock.Mock()
        mock_keypair.name = 'test-import'
        mock_import.return_value = mock_keypair

        form_data = {
            'name': 'test-import',
            'public_key': self.valid_rsa_key
        }
        form = forms.ImportKeyPairForm(self.request, data=form_data)

        self.assertTrue(form.is_valid())
        result = form.handle(self.request, form_data)

        mock_import.assert_called_once_with(
            self.request,
            'test-import',
            self.valid_rsa_key
        )
        self.assertTrue(result)

    @mock.patch.object(api.nova, 'keypair_import')
    def test_import_keypair_success_ed25519(self, mock_import):
        """Test successful ED25519 key pair import."""
        mock_keypair = mock.Mock()
        mock_keypair.name = 'test-ed25519'
        mock_import.return_value = mock_keypair

        form_data = {
            'name': 'test-ed25519',
            'public_key': self.valid_ed25519_key
        }
        form = forms.ImportKeyPairForm(self.request, data=form_data)

        self.assertTrue(form.is_valid())
        result = form.handle(self.request, form_data)

        self.assertTrue(result)

    def test_import_keypair_invalid_no_algorithm(self):
        """Test validation error for missing algorithm prefix."""
        form_data = {
            'name': 'test-invalid',
            'public_key': 'AAAAB3NzaC1yc2EAAAADAQABAAABgQC7...'
        }
        form = forms.ImportKeyPairForm(self.request, data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn('public_key', form.errors)

    def test_import_keypair_invalid_malformed_base64(self):
        """Test validation error for malformed base64 data."""
        form_data = {
            'name': 'test-invalid',
            'public_key': 'ssh-rsa NOT_VALID_BASE64'
        }
        form = forms.ImportKeyPairForm(self.request, data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn('public_key', form.errors)

    def test_import_keypair_private_key_pasted(self):
        """Test validation error when private key is pasted."""
        form_data = {
            'name': 'test-invalid',
            'public_key': '-----BEGIN RSA PRIVATE KEY-----\n...'
        }
        form = forms.ImportKeyPairForm(self.request, data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn('public_key', form.errors)
        self.assertIn('private key', str(form.errors['public_key']).lower())

    def test_import_keypair_too_short(self):
        """Test validation error for key that's too short."""
        form_data = {
            'name': 'test-invalid',
            'public_key': 'ssh-rsa AAAA'
        }
        form = forms.ImportKeyPairForm(self.request, data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn('public_key', form.errors)
        self.assertIn('too short', str(form.errors['public_key']).lower())

    def test_import_keypair_empty_key(self):
        """Test validation error for empty public key."""
        form_data = {
            'name': 'test-invalid',
            'public_key': ''
        }
        form = forms.ImportKeyPairForm(self.request, data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn('public_key', form.errors)

    @mock.patch.object(api.nova, 'keypair_import')
    def test_import_keypair_duplicate_name(self, mock_import):
        """Test error handling for duplicate key pair name."""
        from horizon import exceptions
        mock_import.side_effect = exceptions.Conflict('Duplicate')

        form_data = {
            'name': 'existing-keypair',
            'public_key': self.valid_rsa_key
        }
        form = forms.ImportKeyPairForm(self.request, data=form_data)

        self.assertTrue(form.is_valid())
        result = form.handle(self.request, form_data)

        self.assertFalse(result)
```

**Key Test Scenarios Covered**:

1. ✅ Happy paths (SSH, X509, RSA, ED25519)
2. ✅ Validation errors (name, public key format)
3. ✅ API errors (duplicate, quota, permissions)
4. ✅ Edge cases (too short, missing algorithm, private key)

---

### Step 2: Create View Tests

**File**: `openstack_dashboard/dashboards/project/key_pairs/tests/test_views.py`

**Add tests**:

```python
from unittest import mock

from django.urls import reverse

from openstack_dashboard import api
from openstack_dashboard.test import helpers as test


class CreateViewTests(test.TestCase):
    """Tests for CreateView."""

    @mock.patch.object(api.nova, 'keypair_create')
    def test_create_view_get(self, mock_create):
        """Test GET request to create view renders form."""
        url = reverse('horizon:project:key_pairs:create')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'project/key_pairs/create.html')
        self.assertContains(res, 'Create Key Pair')

    @mock.patch.object(api.nova, 'keypair_create')
    def test_create_view_post_success(self, mock_create):
        """Test successful POST to create view."""
        mock_keypair = mock.Mock()
        mock_keypair.name = 'test-create'
        mock_keypair.private_key = '-----BEGIN RSA PRIVATE KEY-----'
        mock_create.return_value = mock_keypair

        url = reverse('horizon:project:key_pairs:create')
        form_data = {
            'name': 'test-create',
            'key_type': 'ssh'
        }
        res = self.client.post(url, form_data)

        # Should redirect to download page
        self.assertRedirects(
            res,
            reverse('horizon:project:key_pairs:download')
        )

    @mock.patch.object(api.nova, 'keypair_create')
    def test_create_view_post_error(self, mock_create):
        """Test POST to create view with API error."""
        from horizon import exceptions
        mock_create.side_effect = exceptions.Conflict('Duplicate')

        url = reverse('horizon:project:key_pairs:create')
        form_data = {
            'name': 'duplicate-name',
            'key_type': 'ssh'
        }
        res = self.client.post(url, form_data)

        # Should return to form with error
        self.assertEqual(res.status_code, 200)
        self.assertFormError(res, 'form', None, mock.ANY)


class ImportViewTests(test.TestCase):
    """Tests for ImportView."""

    @mock.patch.object(api.nova, 'keypair_import')
    def test_import_view_get(self, mock_import):
        """Test GET request to import view renders form."""
        url = reverse('horizon:project:key_pairs:import')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'project/key_pairs/import.html')
        self.assertContains(res, 'Import Key Pair')

    @mock.patch.object(api.nova, 'keypair_import')
    def test_import_view_post_success(self, mock_import):
        """Test successful POST to import view."""
        mock_keypair = mock.Mock()
        mock_keypair.name = 'test-import'
        mock_import.return_value = mock_keypair

        url = reverse('horizon:project:key_pairs:import')
        form_data = {
            'name': 'test-import',
            'public_key': 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC7...'
        }
        res = self.client.post(url, form_data)

        # Should redirect to index
        self.assertRedirects(
            res,
            reverse('horizon:project:key_pairs:index')
        )


class DownloadViewTests(test.TestCase):
    """Tests for DownloadView."""

    def test_download_view_with_key_in_session(self):
        """Test download view with private key in session."""
        # Set up session with private key
        session = self.client.session
        session['keypair_private_key'] = '-----BEGIN RSA PRIVATE KEY-----'
        session['keypair_name'] = 'test-download'
        session.save()

        url = reverse('horizon:project:key_pairs:download')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'project/key_pairs/download.html')
        self.assertContains(res, 'test-download')
        self.assertContains(res, '-----BEGIN RSA PRIVATE KEY-----')

        # Verify key was cleared from session
        self.assertNotIn('keypair_private_key', self.client.session)

    def test_download_view_without_key_in_session(self):
        """Test download view redirects if no key in session."""
        url = reverse('horizon:project:key_pairs:download')
        res = self.client.get(url)

        # Should redirect to index
        self.assertRedirects(
            res,
            reverse('horizon:project:key_pairs:index')
        )
```

**Key Test Scenarios**:

1. ✅ View rendering (GET requests)
2. ✅ Form submissions (POST requests)
3. ✅ Success redirects
4. ✅ Error handling
5. ✅ Session management (download view)

---

### Step 3: Run Full Test Suite

**Commands to run**:

```bash
cd <mymcp-repo-path>/workspace/horizon-osprh-12802-working

# Run key pairs tests specifically
tox -e py39 -- openstack_dashboard.dashboards.project.key_pairs.tests

# Run full dashboard tests
tox -e py39 -- openstack_dashboard.dashboards.project.tests

# Run ALL Horizon tests (takes longer)
tox -e py39
```

**Expected Output**:

```
Ran X tests in Y.YYYs

OK
```

---

### Step 4: Ensure PEP8 Compliance

**Run PEP8 checker**:

```bash
# Check only key_pairs directory
tox -e pep8 -- openstack_dashboard/dashboards/project/key_pairs/

# Or check entire dashboard
tox -e pep8
```

**Common PEP8 Issues to Fix**:

1. **Line Length**: Max 79 characters
   ```python
   # Bad
   messages.success(request, _('Successfully created key pair "%(name)s". Your private key is ready for download.') % {'name': data['name']})
   
   # Good
   messages.success(
       request,
       _('Successfully created key pair "%(name)s". '
         'Your private key is ready for download.') % {'name': data['name']}
   )
   ```

2. **Import Order**: stdlib → third-party → horizon → local
   ```python
   # Good order
   import base64  # stdlib
   import re      # stdlib
   
   from django.urls import reverse  # third-party
   from django.utils.translation import gettext_lazy as _
   
   from horizon import exceptions  # horizon
   from horizon import forms
   
   from openstack_dashboard import api  # local
   ```

3. **Whitespace**: 2 blank lines between top-level definitions
   ```python
   class GenerateKeyPairForm(forms.SelfHandlingForm):
       pass
   
   
   class ImportKeyPairForm(forms.SelfHandlingForm):
       pass
   ```

4. **Docstrings**: All public methods need docstrings
   ```python
   def clean_public_key(self):
       """Validate SSH public key format with detailed error messages."""
       # ... implementation ...
   ```

---

### Step 5: Final Code Review Checklist

**Before submitting**:

- [ ] All new code has tests
- [ ] All tests pass (tox -e py39)
- [ ] PEP8 compliant (tox -e pep8)
- [ ] All strings are translatable `_("text")`
- [ ] Docstrings for all public methods/classes
- [ ] No TODO/FIXME/XXX comments
- [ ] No debug print statements
- [ ] No commented-out code
- [ ] Import statements properly ordered
- [ ] Commit message follows OpenStack format
- [ ] Change-Id present in commit message
- [ ] Topic set to "de-angularize"

---

## Testing Checklist

### Unit Test Coverage

Run with coverage report:

```bash
# Generate coverage report
coverage run --source='.' manage.py test openstack_dashboard.dashboards.project.key_pairs.tests
coverage report -m

# Target: >80% coverage for new code
```

**Expected Coverage**:

- `forms.py`: >90% (all paths tested)
- `views.py`: >85% (most paths tested)
- `urls.py`: 100% (simple routing)

### Integration Testing

```bash
# If you have a full Horizon test environment
./run_tests.sh --integration openstack_dashboard.dashboards.project.key_pairs
```

### Manual Regression Testing

Quick smoke test to ensure nothing broke:

```
1. Navigate to Key Pairs panel
2. ✅ Verify: Table loads
3. ✅ Verify: Existing expandable rows still work (Review 966349)
4. Click "Create Key Pair"
5. ✅ Verify: Form opens
6. Create a key pair
7. ✅ Verify: Download page works
8. Click "Import Key Pair"
9. ✅ Verify: Form opens
10. Import a key
11. ✅ Verify: Success message
12. Delete a key pair
13. ✅ Verify: Still works (not broken by our changes)
```

---

## Commit Message Template

```
Add comprehensive tests for key pair forms

Adds unit tests for GenerateKeyPairForm, ImportKeyPairForm, and
associated views. Ensures PEP8 compliance and completes test
coverage for OSPRH-12802 key pair form implementations.

Test Coverage:
- GenerateKeyPairForm
  * Happy path: SSH and X509 key generation
  * Validation: name format, length, special characters
  * Error handling: duplicate name, quota exceeded, not authorized
  * Session storage of private key
  
- ImportKeyPairForm
  * Happy path: RSA and ED25519 key import
  * Validation: public key format, algorithm detection
  * Error detection: private key pasted, truncated key
  * Error handling: duplicate name, quota exceeded
  
- CreateView
  * GET request rendering
  * POST success with redirect to download
  * POST error handling
  
- ImportView
  * GET request rendering
  * POST success with redirect to index
  * POST error handling
  
- DownloadView
  * Download with key in session
  * Redirect when no key in session
  * Session cleanup (one-time display)

Code Quality:
- PEP8 compliant (tox -e pep8 passes)
- Import ordering corrected
- Docstrings added for all public methods
- Type hints where appropriate
- No debug code or commented-out code
- All strings translatable

Test Execution:
- All new tests pass
- No regressions in existing tests
- Coverage >85% for new code

This completes the test suite for OSPRH-12802 and makes the
implementation ready for final review and merge.

Partial-Bug: #OSPRH-12802
Change-Id: Ixxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Topic: de-angularize
```

---

## Expected Reviewer Questions

### Q1: "Why not 100% test coverage?"

**A**: Some error paths are difficult to test (e.g., specific Nova API internal errors). We focus on realistic scenarios and critical paths. 85%+ coverage for new code is excellent and matches Horizon standards.

### Q2: "Should we add integration tests?"

**A**: Unit tests are mandatory. Integration tests are valuable but optional and typically run in CI. If project has integration test suite, we can add some, but not required for initial merge.

### Q3: "What about JavaScript tests?"

**A**: The JavaScript in our implementation is minimal (copy/download buttons). For such simple JavaScript, manual testing is sufficient. More complex JS would warrant automated tests.

### Q4: "Why mock Nova API?"

**A**: Unit tests should not require live Nova API. Mocking allows fast, isolated tests. Integration tests (separate) would use real APIs.

---

## Final Checklist Before Submission

### Code Quality
- [ ] `tox -e pep8` passes with no errors
- [ ] `tox -e py39` passes with no failures
- [ ] No flake8 warnings
- [ ] No pylint errors (if project uses it)

### Test Coverage
- [ ] All forms have unit tests
- [ ] All views have unit tests
- [ ] Happy paths tested
- [ ] Error paths tested
- [ ] Edge cases tested
- [ ] Coverage report shows >80%

### Documentation
- [ ] All functions have docstrings
- [ ] All classes have docstrings
- [ ] Complex logic has inline comments
- [ ] Commit message is detailed

### Git
- [ ] Commit message follows OpenStack format
- [ ] Change-Id present (git review -s)
- [ ] Topic set: `de-angularize`
- [ ] Signed-off-by present (if required)
- [ ] No merge commits
- [ ] Single logical commit (or properly ordered patchsets)

### Functionality
- [ ] Manual testing complete
- [ ] All scenarios from previous patchsets still work
- [ ] No regressions
- [ ] Error messages are user-friendly
- [ ] Accessibility maintained

### Review Preparation
- [ ] Self-review complete
- [ ] Checklist items documented in commit message
- [ ] Known issues/limitations documented
- [ ] Related issues/bugs referenced
- [ ] Ready for +2

---

## Success Metrics

### Test Results
```
======================================================================
Ran 28 tests in 1.234s

OK

----------------------------------------------------------------------
Name                                     Stmts   Miss  Cover
----------------------------------------------------------------------
key_pairs/forms.py                         142      8    94%
key_pairs/views.py                          48      4    92%
key_pairs/urls.py                            6      0   100%
----------------------------------------------------------------------
TOTAL                                      196     12    94%
```

### PEP8 Results
```
All checks passed!
```

---

## Next Steps

**After this patchset is submitted and reviewed**:

1. Address any reviewer feedback
2. Iterate on patchsets as needed
3. Wait for +2 approval
4. **Celebrate merge!** 🎉
5. Update spike document with actual timeline
6. Move to next ticket (OSPRH-16421 - Images chevrons)

---

## Notes for Self

### Running Specific Tests

```bash
# Single test class
./run_tests.sh openstack_dashboard.dashboards.project.key_pairs.tests.test_forms.GenerateKeyPairFormTests

# Single test method
./run_tests.sh openstack_dashboard.dashboards.project.key_pairs.tests.test_forms.GenerateKeyPairFormTests.test_generate_keypair_success_ssh

# With verbose output
./run_tests.sh -v openstack_dashboard.dashboards.project.key_pairs.tests
```

### Common Test Failures and Fixes

1. **"Mock not called"**: Check mock patch path matches import path
2. **"Session error"**: Ensure test client has session enabled
3. **"Template not found"**: Check template path in assertTemplateUsed
4. **"Form errors not found"**: Use assertFormError with correct field name

---

**Status**: 📋 Ready for implementation  
**Estimated Time**: 2 days  
**Complexity**: Medium  
**Final**: Yes - this completes OSPRH-12802 implementation


