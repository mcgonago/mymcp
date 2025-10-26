# Review 963263: Fix TOTP view redirection

## Table of Contents

- [Review Information](#review-information)
- [High-Level Description of Changes](#high-level-description-of-changes)
- [What Problem Does This Solve?](#what-problem-does-this-solve)
- [How to Test This Change](#how-to-test-this-change)
- [Top Challenges in Reviewing This Change](#top-challenges-in-reviewing-this-change)
- [Recommended Steps for Completing the Review](#recommended-steps-for-completing-the-review)
- [Key Areas of Concern](#key-areas-of-concern)
- [Technology and Testing Framework Background](#technology-and-testing-framework-background)
- [Estimated Review Time](#estimated-review-time)
- [Questions to Ask the Author](#questions-to-ask-the-author)
- [Follow-Up Actions](#follow-up-actions)

---

## Review Information

- **Change ID**: 963263
- **URL**: https://review.opendev.org/c/openstack/horizon/+/963263
- **Author**: Maksim Malchuk <maksim.malchuk@gmail.com>
- **Project**: openstack/horizon
- **Branch**: stable/2024.2
- **Status**: NEW
- **Created**: 2025-10-07 10:53:54.000000000
- **Updated**: 2025-10-24 08:05:24.000000000

## High-Level Description of Changes

This is a targeted bug fix for the TOTP (Time-based One-Time Password) authentication view in Horizon. The change modifies the redirection logic after TOTP authentication, involving only 2 files with 13 lines added and 1 line removed. This is a small, focused change on the stable/2024.2 branch.

The modification affects:
- **`openstack_auth/views.py`**: The main authentication view logic (+9/-1 lines)
- **`openstack_auth/tests/unit/test_auth.py`**: Unit test additions (+4 lines)

## What Problem Does This Solve?

The change addresses a redirection issue in the TOTP authentication flow. When users complete TOTP authentication, they should be redirected to the appropriate page, but the current implementation appears to have incorrect or missing redirection logic. This bug could result in:
- Users landing on incorrect pages after TOTP verification
- Poor user experience during multi-factor authentication
- Potential confusion or security concerns if redirection behavior is unpredictable

## How to Test This Change

Testing this change requires a Horizon environment with TOTP authentication enabled.

### Prerequisites
1. **Horizon Development Environment**: A working stable/2024.2 Horizon instance
2. **TOTP Enabled**: Multi-factor authentication must be configured and enabled
3. **Test User with TOTP**: At least one test user account with TOTP configured

### Testing Steps

#### 1. Set Up TOTP Authentication
```bash
# In your Horizon local_settings.py, ensure TOTP is enabled
# WEBSSO_ENABLED = True
# Enable TOTP in your Keystone backend
```

#### 2. Test Normal TOTP Flow
1. Log out of Horizon if already logged in
2. Navigate to the Horizon login page
3. Enter valid credentials for a user with TOTP enabled
4. When prompted, enter a valid TOTP code
5. **Verify**: User is redirected to the expected landing page (typically the dashboard or project overview)
6. **Check**: URL in the browser matches the expected destination
7. **Confirm**: No console errors appear in browser developer tools

#### 3. Test Edge Cases
1. **Deep Link Test**: 
   - Access a specific Horizon URL that requires authentication (e.g., `/project/instances/`)
   - Go through TOTP authentication
   - **Verify**: Redirected back to the originally requested URL, not just the homepage

2. **Invalid TOTP Code**:
   - Enter incorrect TOTP code
   - **Verify**: Error message appears, no unexpected redirection

3. **Session Timeout**:
   - Start TOTP process, wait for session to expire, then complete
   - **Verify**: Appropriate error handling

#### 4. Review Unit Tests
```bash
cd /path/to/horizon
tox -e py3 -- openstack_auth.tests.unit.test_auth
```
**Expected Result**: All tests pass, including the 4 new lines of test coverage added in this change.

#### 5. Manual Code Review
- Examine `openstack_auth/views.py` changes
- Verify the redirection logic follows Django best practices
- Check that the fix doesn't introduce security vulnerabilities (e.g., open redirects)

## Top Challenges in Reviewing This Change

1. **TOTP Environment Setup**: Setting up a complete TOTP authentication environment can be complex, requiring proper Keystone configuration and test users.

2. **Understanding Redirection Context**: Without seeing the exact code changes, it's difficult to assess whether the new redirection logic covers all edge cases (deep links, query parameters, etc.).

3. **Stable Branch Implications**: This is targeted at `stable/2024.2`, so understanding why this fix is needed for a stable release (vs. master) requires context about the bug's severity and impact.

4. **Test Coverage**: With only 4 lines added to tests, there's a risk that edge cases aren't fully covered. Need to verify if existing tests plus these additions provide adequate coverage.

5. **Security Considerations**: Redirection logic in authentication flows can be security-sensitive. Need to ensure no open redirect vulnerabilities are introduced.

## Recommended Steps for Completing the Review

### Phase 1: Code Review (Estimated: 1-1.5 hours)
- **Review the patch**: Request to see the actual diff of `openstack_auth/views.py`
- **Verify redirection logic**: Ensure it properly handles:
  - Original requested URL preservation
  - Default landing page fallback
  - Query parameter handling
  - Prevention of open redirects (validate redirect targets)
- **Check test additions**: Verify the 4 new test lines adequately cover the fix
- **Security audit**: Ensure no open redirect or session fixation vulnerabilities
- **Django conventions**: Confirm the code follows Django redirection best practices

### Phase 2: Functional Testing (Estimated: 2-3 hours)
- **Environment setup**: Configure Horizon with TOTP (1-1.5 hours if starting from scratch)
- **Positive tests**: Verify normal TOTP flow redirects correctly
- **Deep link tests**: Access protected pages directly, complete TOTP, verify redirect to original URL
- **Negative tests**: Test with invalid codes, expired sessions
- **Browser testing**: Test in multiple browsers if possible

### Phase 3: Review Feedback (Estimated: 30 minutes)
- **Document findings**: List any issues discovered
- **Ask clarifying questions**: Engage with the author on design decisions
- **Provide +1 or request changes**: Based on findings

## Key Areas of Concern

- **Open Redirect Vulnerability**: Must ensure the redirection target is validated and doesn't allow redirecting to arbitrary external URLs
- **Session Security**: Verify that session tokens are properly handled during the redirect
- **Query Parameter Preservation**: Ensure original query parameters (if any) are preserved during redirect
- **Backwards Compatibility**: Since this is for stable/2024.2, confirm no breaking changes for existing deployments
- **Test Coverage Adequacy**: Only 4 lines of test code were added; may not cover all scenarios

## Technology and Testing Framework Background

- **TOTP (Time-based One-Time Password)**: An algorithm that generates one-time passwords based on the current time, commonly used for multi-factor authentication (MFA)
- **OpenStack Keystone**: The identity service for OpenStack, which handles authentication and authorization
- **Django Views**: Horizon is built on Django; views handle HTTP requests and responses
- **Django Redirect**: Django provides secure redirection utilities (e.g., `HttpResponseRedirect`, `redirect()`)
- **Open Redirect**: A security vulnerability where an attacker can craft a malicious URL that redirects users to an untrusted external site
- **Unit Testing with Python**: The changes include additions to `test_auth.py`, likely using Python's `unittest` or `pytest` framework

## Estimated Review Time

- **Complexity Level**: Small-Medium
- **Estimated Total Hours**: 3.5-5 hours

**Breakdown:**
- **Code Review (Phase 1)**: 1-1.5 hours
- **Functional Testing (Phase 2)**: 2-3 hours (includes TOTP environment setup)
- **Review Feedback & Discussion (Phase 3)**: 30 minutes

**Factors affecting time:**
- If TOTP environment is already set up: -1 hour
- If security audit requires deeper investigation: +1-2 hours
- Familiarity with Django redirection patterns: impacts Phase 1 time

## Questions to Ask the Author

1. **What specific bug prompted this fix?** Was there a bug report or user-reported issue?
2. **Can you describe the incorrect behavior before this fix?** Where were users being redirected?
3. **How was the fix tested?** Beyond the unit test additions, was manual testing performed?
4. **Why target stable/2024.2 instead of master?** Is this a backport, or was the bug only present in the stable branch?
5. **Are there any known edge cases this doesn't address?** Are there limitations to be aware of?
6. **Was a security review performed?** Has anyone audited this for potential open redirect vulnerabilities?
7. **Should this be backported to older stable branches?** If the bug exists in older releases, should this fix be applied there too?

## Follow-Up Actions

- **Request Diff**: If not already visible, ask for the actual code changes to be shared
- **Security Review**: Recommend a security team review if open redirect concerns exist
- **Documentation**: Suggest adding inline code comments explaining the redirection logic
- **Backport Consideration**: If the bug affects older releases, propose backports
- **Additional Tests**: If test coverage appears insufficient, suggest additional test cases
- **Release Notes**: Ensure this fix is documented in release notes for stable/2024.2

