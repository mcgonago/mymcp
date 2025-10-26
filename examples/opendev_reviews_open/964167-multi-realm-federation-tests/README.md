# Review 964167: [WIP] Add multi-realm federation tests

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

- **Change ID**: 964167
- **URL**: https://review.opendev.org/c/openstack/horizon/+/964167
- **Project**: openstack/horizon
- **Branch**: master
- **Status**: NEW (**Work In Progress - WIP**)
- **Created**: 2025-10-15
- **Last Updated**: 2025-10-15
- **Files Changed**: 4 files
- **Changes**: +186/-0 lines (all additions)

## High-Level Description of Changes

**⚠️ This is a Work In Progress (WIP) change** - The author indicates this is not yet ready for final review/merge.

This change adds integration tests for multi-realm federation functionality in Horizon. With 4 files added/modified and 186 lines of new code (no deletions), this is a significant addition to Horizon's test suite focused on Keystone federation scenarios.

**Key Additions:**
- New integration test files for multi-realm federation
- Test scenarios for federated authentication across realms
- Test fixtures and setup for federation testing
- Likely uses Selenium or integration test framework

## What Problem Does This Solve?

**Current Testing Gap:**
OpenStack Keystone supports multi-realm federation, allowing users to authenticate across different identity providers and trust domains. However, testing this functionality comprehensively is complex and may not be well-covered in Horizon's current test suite.

**Problems This Addresses:**
1. **Lack of Federation Test Coverage**: Multi-realm scenarios are difficult to test manually
2. **Regression Risk**: Changes to federation code could break multi-realm support
3. **Complex Setup**: Federation testing requires complex environment setup
4. **Integration Points**: Multiple components (Keystone, federation protocols, Horizon) must work together

**Benefits of These Tests:**
- **Prevent Regressions**: Catch federation issues before they reach production
- **Documentation**: Tests serve as examples of how federation should work
- **Confidence**: Developers can refactor with confidence
- **CI Integration**: Automated testing of federation scenarios

## What is Multi-Realm Federation?

Multi-realm federation allows:
- **Multiple Identity Providers**: Support for SAML, OpenID Connect, OAuth
- **Cross-Realm Authentication**: Users from different organizations/domains
- **Trust Relationships**: Federated trust between different Keystone deployments or external IdPs
- **Single Sign-On (SSO)**: Users authenticate once, access multiple systems

**Example Scenario:**
- Company A (Realm A) trusts Company B (Realm B)
- User from Company B can authenticate and access Company A's OpenStack resources
- Horizon must properly handle federated sessions, tokens, and scope

## How to Test This Change

**⚠️ Note**: Since this is WIP, the tests themselves may not be complete or fully functional.

### Prerequisites
1. **Horizon Development Environment**: master branch with this patch applied
2. **Federation-Capable Keystone**: Keystone configured for federation
3. **Identity Providers**: Test IdPs (can use testshib or similar)
4. **Test Framework**: Selenium or integration test framework installed

### Testing Steps

#### 1. Review the Test Code
Before running tests, understand what they test:
```bash
cd horizon
find . -name "*federation*" -name "*test*"
```

Examine:
- What scenarios are tested?
- What assertions are made?
- What IdPs are required?
- What configuration is needed?

#### 2. Set Up Federation Environment
This is the most challenging part. Typically requires:

```yaml
# Example Keystone federation config
[federation]
trusted_dashboard = http://horizon.example.com/auth/websso/
sso_callback_template = /etc/keystone/sso_callback_template.html

[saml]
certfile = /etc/keystone/ssl/certs/signing_cert.pem
keyfile = /etc/keystone/ssl/private/signing_key.pem
idp_entity_id = https://idp.example.com/idp/shibboleth
idp_sso_endpoint = https://idp.example.com/idp/profile/SAML2/Redirect/SSO
idp_metadata_path = /etc/keystone/idp_metadata.xml
```

#### 3. Configure Test Environment
Check if tests have specific configuration requirements:
```bash
# Look for test configuration files
find . -path "*/tests/*" -name "*.conf" -o -name "*.yaml"
```

#### 4. Run the Federation Tests
```bash
# Run specific federation tests
tox -e integration -- *federation*

# OR if Selenium tests
tox -e selenium -- *federation*
```

**Expected (once WIP is complete)**:
- Tests should pass
- Federation login flow should be tested
- Multi-realm scenarios should be verified

#### 5. Manual Federation Testing
Complement automated tests with manual verification:
1. **Navigate to Horizon login page**
2. **Select federated login option** (e.g., "Login with SAML")
3. **Authenticate via IdP**
4. **Verify**: Successfully redirected back to Horizon
5. **Check**: Proper user identity and project scoping
6. **Test**: Cross-realm access if applicable

#### 6. Test Edge Cases
- **Expired federation tokens**: How does Horizon handle expiration?
- **Multiple IdPs**: Can user choose between different IdPs?
- **Failed authentication**: Is error handling appropriate?
- **Scope selection**: Can federated user select appropriate project/domain?

## Top Challenges in Reviewing This Change

1. **WIP Status**: This is explicitly work in progress, meaning:
   - Tests may not be complete
   - Some test scenarios might be placeholders
   - Configuration requirements might not be fully documented

2. **Federation Complexity**: Understanding multi-realm federation requires deep knowledge of:
   - Keystone federation architecture
   - SAML/OpenID Connect protocols
   - Trust relationships and mapping rules
   - Horizon's SSO implementation

3. **Environment Setup**: Testing federation requires complex setup:
   - Identity providers (real or mock)
   - Federation protocol configuration
   - SSL certificates and metadata
   - Mapping rules in Keystone

4. **Test Infrastructure**: May require CI infrastructure changes to support federation testing.

5. **Review Scope**: With 186 lines added, this is substantial. Full review will take time.

## Recommended Steps for Completing the Review

### Phase 1: Initial WIP Review (Estimated: 1-1.5 hours)
- **Review WIP intent**: What is the author trying to achieve?
- **Check test structure**: Are tests organized well?
- **Identify missing pieces**: What's incomplete?
- **Assess approach**: Is the testing strategy sound?
- **Provide early feedback**: Help guide the author toward completion

**Output**: Provide feedback to author on approach, suggest improvements, identify blockers

### Phase 2: Detailed Code Review (Once WIP→Ready) (Estimated: 2-3 hours)
- **Review test code**: Examine all 186 lines:
  - Test coverage completeness
  - Assert logic correctness
  - Fixture and setup code
  - Cleanup and teardown
- **Check test data**: Verify test IdPs, users, mappings are appropriate
- **Review documentation**: Are setup instructions clear?
- **Federation knowledge**: Verify tests match federation best practices

### Phase 3: Functional Testing (Once WIP→Ready) (Estimated: 3-4 hours)
- **Environment setup**: Configure federation environment (1-2 hours)
- **Run tests**: Execute the new federation tests (30-60 minutes)
- **Manual testing**: Verify federation scenarios manually (60-90 minutes)
- **Edge cases**: Test error scenarios (30 minutes)

### Phase 4: Review Feedback (Estimated: 30 minutes)
- **Summarize findings**
- **Provide constructive feedback**
- **+1 or request changes**

## Key Areas of Concern

- **WIP Completion**: What needs to be done before this is ready?
- **Test Coverage**: Do these tests cover the most important federation scenarios?
- **Environment Requirements**: Can these tests run in CI, or only in specially configured environments?
- **Mock vs Real IdPs**: Are tests using mock IdPs or requiring real ones?
- **Federation Protocol Support**: Are all relevant protocols tested (SAML, OpenID Connect)?
- **Mapping Rules**: Are identity mapping scenarios tested?
- **Error Handling**: Are federation failure scenarios tested?
- **Documentation**: Is there a README explaining how to run these tests?

## Technology and Testing Framework Background

### Keystone Federation

Keystone supports multiple federation protocols:
- **SAML 2.0**: Via Shibboleth or mod_auth_mellon
- **OpenID Connect**: Via mod_auth_openidc
- **OAuth**: Limited support

**Key Concepts:**
- **Identity Provider (IdP)**: External authentication service
- **Service Provider (SP)**: OpenStack/Keystone (trusts IdP)
- **Mapping Rules**: Transform IdP assertions to Keystone identities
- **Protocol**: The federation protocol (saml2, openid, etc.)
- **Remote Users**: Users authenticated via federation (not local Keystone users)

### Horizon WebSSO

Horizon supports federated login via WebSSO:
- **Login Flow**: User → Horizon → IdP → Horizon (with token)
- **Token Handling**: Federated tokens are scoped to projects/domains
- **Session Management**: Horizon manages federated sessions

### Testing Challenges

Federation testing is hard because:
- **Complex Setup**: Requires IdP, SP configuration, metadata exchange
- **Protocol Complexity**: SAML/OpenID protocols have many edge cases
- **Network Dependencies**: Real IdPs require network access
- **Certificate Management**: SSL certs, signing certs, metadata
- **State Management**: Sessions, redirects, callbacks

### Test Shib

Many federation tests use Test Shib (testshib.org):
- **Public Test IdP**: Free SAML IdP for testing
- **Known Metadata**: Well-documented
- **Test Users**: Predefined test accounts
- **No Setup Required**: Just configure SP to trust Test Shib

## Estimated Review Time

**⚠️ Note**: Given WIP status, initial review will be lighter.

- **Complexity Level**: Large (once complete)
- **Estimated Total Hours**: 
  - **WIP Review**: 1-1.5 hours
  - **Full Review (once ready)**: 5.5-8.5 hours total

**Breakdown (for final review):**
- **Code Review (Phase 2)**: 2-3 hours
- **Functional Testing (Phase 3)**: 3-4 hours (includes complex environment setup)
- **Review Feedback (Phase 4)**: 30 minutes

**Factors affecting time:**
- **WIP completion status**: significantly impacts review scope
- **Federation expertise**: saves 1-2 hours if expert
- **Existing federation environment**: saves 1-2 hours
- **Mock vs real IdP setup**: mock saves 1+ hours
- **CI integration requirements**: adds 1-2 hours

## Questions to Ask the Author

1. **WIP Status**: What specific items are incomplete? What's blocking completion?
2. **Target completion date**: When do you expect this to be ready for final review?
3. **Federation protocols**: Which protocols are tested? SAML? OpenID?
4. **Environment requirements**: What environment setup is needed? Can it run in CI?
5. **Mock vs real IdPs**: Do tests use mock IdPs or require real ones?
6. **Test coverage goals**: What specific scenarios are you aiming to test?
7. **Documentation plans**: Will there be setup instructions/README?
8. **CI integration**: Is CI infrastructure ready to support these tests?
9. **Related work**: Are there other federation improvements planned?
10. **Help needed**: What help do you need to complete this WIP?

## Follow-Up Actions

- **Provide WIP Feedback**: Help author complete the work
- **Environment Setup Guide**: Create/improve docs for federation test setup
- **CI Infrastructure**: Assess if CI can support these tests
- **Mock IdP**: Consider creating a mock IdP specifically for testing
- **Related Tests**: Identify other federation scenarios that should be tested
- **Review Again When Ready**: Re-review once WIP is marked ready
- **Federation Documentation**: Improve Horizon federation documentation based on learnings

