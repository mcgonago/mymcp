# Review 963576: Force scope in all appcreds API calls

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

- **Change ID**: 963576
- **URL**: https://review.opendev.org/c/openstack/horizon/+/963576
- **Project**: openstack/horizon
- **Branch**: master
- **Status**: NEW
- **Created**: 2025-10-09
- **Last Updated**: 2025-10-13
- **Files Changed**: 2 files
- **Changes**: +14/-16 lines (net -2 lines)

## High-Level Description of Changes

This change modifies how Horizon handles application credentials (appcreds) API calls to ensure proper scoping is always enforced. With only 2 files changed and a net reduction of 2 lines, this appears to be a targeted fix or refactoring to ensure security and consistency in appcreds operations.

**Key Changes:**
- Forces explicit scope in all application credentials API calls
- Refactors appcreds API client usage
- Ensures consistent scoping behavior

## What Problem Does This Solve?

**Application Credentials and Scoping:**
Application credentials in OpenStack allow automation and service accounts to authenticate without sharing passwords. Proper scoping is critical for security:

**Current Problem:**
Without forced scope, application credentials API calls might:
1. **Operate without explicit scope**: Leading to ambiguous authorization context
2. **Use implicit scoping**: Which may not match user expectations
3. **Security Risk**: Credentials might have broader access than intended
4. **Inconsistent Behavior**: Different API calls might use different scoping strategies

**Security Issues:**
- **Privilege Escalation**: Appcreds without proper scope might access unintended resources
- **Scope Confusion**: Users might think credentials are project-scoped when they're not
- **Audit Trail**: Unclear scoping makes auditing difficult

**Solution:**
Force explicit scope parameter in all appcreds API calls:
- **Consistency**: All calls use same scoping strategy
- **Security**: Explicit scope prevents accidental over-privileging
- **Clarity**: Clear authorization context for each credential
- **Best Practice**: Follows OpenStack security guidelines

## How to Test This Change

Testing requires verifying that application credentials are created and used with proper scoping.

### Prerequisites
1. **Horizon Development Environment**: master branch with this patch
2. **Keystone with Appcreds**: Keystone v3 API with application credentials support
3. **Test User with Projects**: User with access to multiple projects

### Testing Steps

#### 1. Test Application Credential Creation
1. **Navigate to Identity → Application Credentials**
2. **Click "Create Application Credential"**
3. **Fill in the form**:
   - Name: test-appcred
   - Description: Test credential
   - (Check for scope-related options)
4. **Create the credential**
5. **Verify**: Credential is created successfully

#### 2. Verify Scope in API Call
Open browser developer tools → Network tab:

Expected API call:
```http
POST /api/keystone/application_credentials
Headers:
  X-Auth-Token: ...

Body:
{
  "application_credential": {
    "name": "test-appcred",
    "description": "Test credential",
    "roles": [...],
    ...
  }
}
```

**Check:**
- Is scope information included in the request?
- Does the request explicitly specify project/domain scope?
- Are headers correct?

#### 3. Test Listing Application Credentials
1. **Navigate to Application Credentials page**
2. **Verify**: All credentials are listed
3. **Check Network Tab**: Verify API call includes scope parameter

Expected:
```http
GET /api/keystone/users/{user_id}/application_credentials?scope=...
```

#### 4. Test Credential Details
1. **Click on a credential** to view details
2. **Verify**: Scope information is displayed correctly
3. **Check**: API call includes scope

#### 5. Test Credential Deletion
1. **Delete an application credential**
2. **Verify**: Deletion succeeds
3. **Check**: API call includes proper scope

#### 6. Test with Multiple Projects
1. **Switch to a different project** in Horizon
2. **Navigate to Application Credentials**
3. **Verify**: Only credentials for current project are shown (if project-scoped)
4. **Create credential in new project**
5. **Verify**: Credential is scoped to correct project

#### 7. Test Edge Cases
- **No project selected**: What happens if user isn't scoped to a project?
- **Domain-admin user**: How do domain-scoped users interact with appcreds?
- **System-admin user**: Are system-scoped credentials handled?

#### 8. Run Unit Tests
```bash
tox -e py3 -- openstack_dashboard.dashboards.identity.application_credentials.tests
```
**Expected**: All tests pass.

#### 9. Test with OpenStack CLI
Verify credentials work correctly when used:
```bash
# Create credential via Horizon, download the RC file or clouds.yaml

# Test using the credential
openstack --os-auth-type v3applicationcredential \
  --os-application-credential-id <id> \
  --os-application-credential-secret <secret> \
  server list
```
**Expected**: Credential works within its intended scope.

## Top Challenges in Reviewing This Change

1. **Understanding Keystone Scoping**: Requires knowledge of Keystone v3 scoping (project, domain, system).

2. **Application Credentials API**: Understanding Keystone's application credentials API and its scoping requirements.

3. **Security Implications**: Assessing whether the forced scope appropriately restricts credential usage.

4. **Backward Compatibility**: Ensuring existing credentials and workflows aren't broken.

5. **Edge Cases**: Understanding behavior with domain-scoped and system-scoped users.

6. **API Version Compatibility**: Ensuring this works with various Keystone API versions.

## Recommended Steps for Completing the Review

### Phase 1: Code Review (Estimated: 1.5-2 hours)
- **Review the patch**: Examine both modified files:
  - How is scope parameter added/modified?
  - Which API calls are affected? (create, list, get, delete?)
  - How is the scope value determined? (from session, request, etc.?)
  - Error handling for missing scope
- **Check Keystone API docs**: Verify scope parameter requirements for appcreds API
- **Review tests**: Ensure tests cover scoped API calls
- **Security assessment**: Verify this improves security without breaking functionality

### Phase 2: Functional Testing (Estimated: 2-2.5 hours)
- **Environment setup**: Prepare multi-project environment (30 minutes if needed)
- **Create appcreds**: Test creation via UI (30 minutes)
- **List and manage**: Test listing, viewing, deleting (30 minutes)
- **Multi-project**: Test with multiple projects (30 minutes)
- **Edge cases**: Test with various user scopes (30 minutes)

### Phase 3: Review Feedback (Estimated: 30 minutes)
- **Document findings**: Security improvements, issues, concerns
- **Verify scope correctness**: Confirm scope is appropriate for all scenarios
- **Suggest improvements**: Better error handling, user messaging, etc.

## Key Areas of Concern

- **Scope Source**: Where does the scope value come from? Session? Request parameter?
- **Default Scope**: What happens if scope can't be determined?
- **Error Handling**: Are errors clear if scope is invalid or missing?
- **Backward Compatibility**: Do existing credentials continue to work?
- **Multi-Scope Support**: Can users create credentials with different scopes?
- **Privilege Check**: Does user have permission to create credentials in the specified scope?
- **Audit Logging**: Is the scope logged for audit purposes?

## Technology and Testing Framework Background

### Application Credentials in OpenStack

Application credentials (introduced in Queens) allow:
- **Password-less Authentication**: No need to share user passwords
- **Limited Scope**: Credentials can be restricted to specific roles and projects
- **Automation-Friendly**: Ideal for CI/CD, scripts, and service accounts
- **Revocable**: Can be deleted without changing user password

**Key Properties:**
- **Name**: Human-readable identifier
- **Roles**: Subset of user's roles (can't exceed user's permissions)
- **Expiration**: Optional expiration date
- **Access Rules**: Fine-grained restrictions (optional)

### Keystone v3 Scoping

Keystone v3 supports multiple scope types:
- **Project Scope**: Token valid for specific project
- **Domain Scope**: Token valid for entire domain
- **System Scope**: Token valid for system-level operations (admin)
- **Unscoped**: Token not tied to any specific scope

**API Format:**
```json
{
  "auth": {
    "identity": {...},
    "scope": {
      "project": {
        "id": "project-uuid"
      }
    }
  }
}
```

### Application Credentials API

**Create:**
```http
POST /v3/users/{user_id}/application_credentials
{
  "application_credential": {
    "name": "my-appcred",
    "description": "For CI system",
    "roles": [{"id": "role-uuid"}],
    "expires_at": "2025-12-31T23:59:59Z"
  }
}
```

**List:**
```http
GET /v3/users/{user_id}/application_credentials
```

**Get:**
```http
GET /v3/users/{user_id}/application_credentials/{credential_id}
```

**Delete:**
```http
DELETE /v3/users/{user_id}/application_credentials/{credential_id}
```

### Horizon Identity Panel

Horizon's identity panel provides UI for:
- Creating application credentials
- Listing user's credentials
- Viewing credential details
- Deleting credentials
- Downloading credential files (clouds.yaml, openrc.sh)

## Estimated Review Time

- **Complexity Level**: Medium
- **Estimated Total Hours**: 4-5 hours

**Breakdown:**
- **Code Review (Phase 1)**: 1.5-2 hours
- **Functional Testing (Phase 2)**: 2-2.5 hours
- **Review Feedback & Discussion (Phase 3)**: 30 minutes

**Factors affecting time:**
- Familiarity with Keystone application credentials: saves 30-45 minutes
- Understanding of Keystone scoping: saves 30 minutes
- Multi-project test environment ready: saves 30 minutes
- Need to research appcreds API: adds 30-45 minutes

## Questions to Ask the Author

1. **Scope source**: Where is the scope value obtained from? User session?
2. **Specific bug**: Was there a specific bug or security issue that prompted this?
3. **Keystone version**: Any minimum Keystone version requirements?
4. **Backward compatibility**: How are existing credentials affected?
5. **Scope type**: Does this handle project, domain, and system scopes?
6. **Error scenarios**: What happens if scope is invalid or missing?
7. **Testing performed**: What testing was done? Multiple projects? Different user types?
8. **Security review**: Was this reviewed from a security perspective?
9. **Related changes**: Are there companion changes in other OpenStack projects?

## Follow-Up Actions

- **Security Advisory**: If this fixes a security issue, coordinate disclosure
- **Documentation Update**: Update user docs about application credentials scoping
- **Developer Docs**: Document the scoping requirement for contributors
- **Backport**: Consider backporting to stable branches if this fixes a security issue
- **Related APIs**: Check if other credential-related APIs need similar changes
- **Release Notes**: Document this change in release notes
- **User Communication**: If this changes behavior, communicate to users/operators

