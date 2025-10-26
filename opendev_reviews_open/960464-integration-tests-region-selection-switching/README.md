# Review 960464: Add integration tests for region selection and switching

## Review Information

- **Change ID**: 960464
- **URL**: https://review.opendev.org/c/openstack/horizon/+/960464
- **Author**: Radomir Dopieralski <openstack@dopieralski.pl>
- **Project**: openstack/horizon
- **Branch**: master
- **Status**: NEW (Open)
- **Created**: 2025-09-11
- **Last Updated**: 2025-10-24

## High-Level Description of Changes

This change adds automated integration tests for Horizon's region selection and switching functionality. The review introduces new Selenium-based tests that verify users can:
1. Select different OpenStack regions from the UI
2. Switch between regions
3. Verify that region switching works correctly

### Files Changed (5 files, +144/-3 lines)

1. **`openstack_dashboard/test/selenium/integration/test_regions.py`** (+117 new)
   - New test file with region selection/switching test cases
   
2. **`openstack_dashboard/test/selenium/conftest.py`** (+14/-2)
   - Updated pytest configuration for region testing support
   
3. **`openstack_dashboard/test/integration_tests/config.py`** (+6/-0)
   - Configuration additions for region testing
   
4. **`openstack_dashboard/test/integration_tests/horizon.conf`** (+6/-0)
   - Test configuration for region settings
   
5. **`tox.ini`** (+1/-1)
   - Tox configuration update

## What Problem Does This Solve?

**Problem**: Horizon's multi-region support lacked automated tests to verify that:
- Region selection dropdown works correctly
- Users can switch between regions
- The UI properly reflects the selected region
- Region switching doesn't break other functionality

**Solution**: This change adds Selenium integration tests that automatically verify region selection and switching behavior, improving test coverage for multi-region deployments.

## How to Test This Change

### Prerequisites

1. **Multi-Region OpenStack Environment**
   - You need an OpenStack deployment with multiple regions configured
   - At least 2 regions (e.g., RegionOne, RegionTwo)
   - Keystone configured with region endpoints

2. **Development Environment**
   ```bash
   git clone https://opendev.org/openstack/horizon
   cd horizon
   git fetch https://review.opendev.org/openstack/horizon refs/changes/64/960464/1 && git checkout FETCH_HEAD
   ```

3. **Install Test Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r test-requirements.txt
   ```

4. **Configure Test Environment**
   - Set up `openstack_dashboard/test/integration_tests/horizon.conf`
   - Configure credentials for a multi-region environment
   - Ensure Selenium WebDriver is installed (Chrome/Firefox)

### Testing Steps

#### 1. **Run the New Integration Tests**

```bash
# Run all region tests
tox -e selenium -- openstack_dashboard/test/selenium/integration/test_regions.py

# Or run specific test
pytest openstack_dashboard/test/selenium/integration/test_regions.py::TestRegions::test_region_selection

# Run with visible browser (for debugging)
pytest openstack_dashboard/test/selenium/integration/test_regions.py --headless=False
```

#### 2. **Manual Testing in UI**

1. **Log into Horizon**
   - Navigate to your Horizon dashboard
   - Log in with credentials

2. **Verify Region Selector**
   - Look for region dropdown (usually in top navigation)
   - Verify all configured regions appear in dropdown
   - Verify current region is highlighted

3. **Test Region Switching**
   - Select a different region from dropdown
   - Verify page refreshes or updates
   - Verify services/resources reflect new region
   - Check that subsequent API calls use correct region

4. **Test Edge Cases**
   - Switch regions multiple times rapidly
   - Switch regions on different pages (Compute, Network, etc.)
   - Verify region persists across page navigation
   - Check region selection survives browser refresh

#### 3. **Verify Test Configuration**

```bash
# Check test configuration is valid
cat openstack_dashboard/test/integration_tests/horizon.conf

# Verify pytest fixtures load correctly
pytest openstack_dashboard/test/selenium/conftest.py --collect-only
```

### Expected Test Results

**Pass Criteria**:
- All new tests in `test_regions.py` pass
- Region dropdown renders correctly
- Switching regions updates the UI
- API calls use the correct region endpoint
- No JavaScript errors in browser console
- Session maintains region selection

**Fail Indicators**:
- Tests timeout waiting for region selector
- Region switching doesn't update displayed resources
- API calls continue using old region after switch
- JavaScript errors related to region handling

## Top Challenges in Reviewing This Change

### 1. **Multi-Region Environment Required**
**Challenge**: Testing requires an actual multi-region OpenStack deployment
- Most dev environments are single-region
- Setting up multiple regions is complex
- CI/CD may not have multi-region test environment

**Impact**: Difficult to verify tests actually work without proper infrastructure

### 2. **Selenium Test Reliability**
**Challenge**: Selenium tests can be flaky and environment-dependent
- Timing issues (race conditions)
- Element locators may break with UI changes
- Browser-specific behavior
- Network latency affects test stability

**Impact**: Need to verify tests are robust and don't introduce flaky failures

### 3. **Configuration Complexity**
**Challenge**: Understanding the test configuration changes
- Multiple config files modified
- Need to understand how horizon.conf integrates with pytest
- Tox environment changes may affect other tests

**Impact**: Risk of breaking existing test infrastructure

### 4. **Limited Context in Commit Message**
**Challenge**: Minimal commit message provides little context
- No explanation of why this is needed
- No description of test scenarios covered
- No information about test environment requirements

**Impact**: Harder to understand the motivation and completeness

### 5. **Integration with Existing Tests**
**Challenge**: Need to verify this doesn't break existing test suite
- Changes to conftest.py affect all tests
- Tox.ini changes may impact CI
- Config changes could affect other integration tests

**Impact**: Risk of regression in test infrastructure

## Recommended Steps for Completing the Review

### Phase 1: Code Review (2-3 hours)

1. **Review Test Implementation** (1 hour)
   ```bash
   # Read the new test file
   cat openstack_dashboard/test/selenium/integration/test_regions.py
   ```
   - Verify test scenarios are comprehensive
   - Check for proper setup/teardown
   - Look for hardcoded values or assumptions
   - Verify error handling
   - Check if tests are idempotent

2. **Review Configuration Changes** (30 min)
   ```bash
   # Check config changes
   git diff openstack_dashboard/test/selenium/conftest.py
   git diff openstack_dashboard/test/integration_tests/config.py
   git diff openstack_dashboard/test/integration_tests/horizon.conf
   ```
   - Verify config changes are backward compatible
   - Check if new config options are documented
   - Ensure sensitive data isn't hardcoded

3. **Review Tox Changes** (30 min)
   ```bash
   git diff tox.ini
   ```
   - Verify tox changes don't break existing environments
   - Check if new dependencies are needed
   - Ensure CI compatibility

4. **Code Quality Check** (30 min)
   - Run linters: `tox -e pep8`
   - Check for code style issues
   - Verify docstrings and comments
   - Look for potential bugs or edge cases

### Phase 2: Functional Testing (3-4 hours)

1. **Set Up Test Environment** (1-2 hours)
   - Deploy multi-region OpenStack (DevStack or existing)
   - Configure Horizon for multiple regions
   - Install test dependencies
   - Configure horizon.conf for tests

2. **Run Automated Tests** (30 min)
   ```bash
   # Run new tests
   tox -e selenium -- openstack_dashboard/test/selenium/integration/test_regions.py
   
   # Run full selenium suite to check for regressions
   tox -e selenium
   ```

3. **Manual UI Testing** (1 hour)
   - Test region selection in browser
   - Verify switching between regions
   - Check different pages (Compute, Network, Volumes)
   - Test with different browsers

4. **Edge Case Testing** (30 min)
   - Test with single region (should gracefully handle)
   - Test with unavailable region
   - Test region switching during API operations
   - Test with slow network

### Phase 3: Review Feedback (1 hour)

1. **Ask Questions** (if needed)
   - Request more context in commit message
   - Ask about specific test scenarios
   - Clarify configuration requirements
   - Request documentation updates

2. **Suggest Improvements**
   - More comprehensive test coverage?
   - Better error messages?
   - Additional edge case handling?
   - Documentation for running tests?

3. **Final Decision**
   - +1/-1/+2 based on findings
   - List any blocking issues
   - Suggest follow-up changes

## Key Areas of Concern

### 1. **Test Environment Dependencies**
- **Concern**: Tests may only work in specific environments
- **Check**: Are there assumptions about region names, endpoints, or configuration?
- **Recommendation**: Verify tests work with any multi-region setup

### 2. **Selenium Element Selectors**
- **Concern**: UI changes could break tests
- **Check**: Are selectors robust? Using data attributes or CSS classes?
- **Recommendation**: Prefer data-testid attributes over brittle CSS selectors

### 3. **Test Timing and Waits**
- **Concern**: Race conditions or timeout issues
- **Check**: Are explicit waits used properly? Any arbitrary sleep() calls?
- **Recommendation**: Use WebDriverWait with proper conditions

### 4. **CI/CD Compatibility**
- **Concern**: Will these tests run in OpenStack CI?
- **Check**: Does CI have multi-region capability?
- **Recommendation**: May need to skip tests in single-region CI

### 5. **Documentation**
- **Concern**: No documentation for running or understanding these tests
- **Check**: Is there a README or docstring explaining test setup?
- **Recommendation**: Request documentation addition

## Technology and Testing Framework Background

### Selenium WebDriver
- Browser automation framework
- Requires WebDriver for Chrome/Firefox
- Can be flaky - needs proper waits and error handling

### Pytest
- Test framework used by Horizon
- Fixtures in conftest.py shared across tests
- Can run tests in parallel

### Multi-Region OpenStack
- Keystone manages region catalog
- Each region has its own service endpoints
- Horizon must query correct region endpoints

### Horizon Configuration
- `horizon.conf` - test-specific settings
- `config.py` - test configuration loading
- Must match actual environment

## Estimated Review Time

**Total Estimated Time: 6-8 hours**

- **Code Review**: 2-3 hours
- **Environment Setup**: 1-2 hours  
- **Testing**: 2-3 hours
- **Feedback & Documentation**: 1 hour

**Complexity Level**: Medium-High

**Factors Affecting Time**:
- ✅ If you have multi-region environment: 6 hours
- ❌ If you need to set up multi-region: +4 hours (10 hours total)
- ✅ If familiar with Selenium: -1 hour
- ❌ If new to Selenium testing: +2 hours

## Questions to Ask the Author

1. What specific region switching bugs motivated these tests?
2. Are there any known limitations with the test implementation?
3. How does this work in CI? Does CI support multi-region?
4. Should these tests run by default or only in specific environments?
5. Are there plans for additional region-related tests?
6. What happens if a region becomes unavailable during testing?

## Follow-Up Actions

After reviewing this change, consider:
1. Adding documentation for running region tests
2. Creating a multi-region DevStack configuration guide
3. Adding more test scenarios (error cases, edge cases)
4. Verifying CI pipeline supports these tests
5. Adding unit tests for region selection logic (if not covered)

---

**Status**: Ready for detailed review
**Next Steps**: Set up multi-region environment and run tests

