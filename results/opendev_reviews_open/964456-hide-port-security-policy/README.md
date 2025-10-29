# Review 964456: Hide enable_port_security checkbox when disallowed by policy

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

- **Change ID**: 964456
- **URL**: https://review.opendev.org/c/openstack/horizon/+/964456
- **Project**: openstack/horizon
- **Branch**: master
- **Status**: NEW
- **Created**: 2025-10-21
- **Last Updated**: 2025-10-21
- **Files Changed**: 4 files
- **Changes**: +37/-9 lines

## High-Level Description of Changes

This change improves Horizon's handling of Neutron policy-based restrictions by hiding the "enable port security" checkbox when the user's policy doesn't allow them to toggle it. With 4 files modified and 28 net lines added, this represents a targeted UI improvement that enforces policy restrictions at the presentation layer.

**Key Changes:**
- Policy-aware UI rendering for port security controls
- Affects network creation/editing forms
- Improves UX by hiding unavailable options rather than showing disabled or failing controls

## What Problem Does This Solve?

**Current Problem:**
Users may encounter a "port security" checkbox in network/port creation forms even when their role/policy doesn't allow them to modify this setting. This leads to:

1. **Confusing UX**: Users see an option they can't actually use
2. **Form Submission Errors**: User changes the setting, submits form, receives policy violation error
3. **Unclear Feedback**: Error messages may not clearly explain the policy restriction
4. **Frustration**: Users don't understand why they can't use a visible option

**Solution:**
Hide the checkbox entirely when policy doesn't allow port security modification:
- **Clearer UI**: Users only see options they can use
- **Prevent Errors**: Can't submit invalid requests if the control isn't visible
- **Better UX**: No confusion about disabled/unavailable features
- **Policy Compliance**: UI enforces backend policy restrictions

## How to Test This Change

Testing requires configuring Neutron policies to restrict port security modifications and verifying the UI adapts accordingly.

### Prerequisites
1. **Horizon Development Environment**: master branch
2. **OpenStack with Neutron**: Configured Neutron service
3. **Policy Configuration**: Ability to modify Neutron policies
4. **Multiple Test Users**: Users with different roles/permissions

### Testing Steps

#### 1. Configure Restrictive Policy
Edit Neutron policy file (`/etc/neutron/policy.yaml` or equivalent):

```yaml
# Example: Restrict port security to admin only
"update_network:port_security_enabled": "rule:admin_only"
"create_network:port_security_enabled": "rule:admin_only"
"update_port:port_security_enabled": "rule:admin_only"
"create_port:port_security_enabled": "rule:admin_only"
```

Restart Neutron services:
```bash
sudo systemctl restart neutron-*
```

#### 2. Test with Restricted User
Log in as a non-admin user (e.g., project member role):

**Network Creation Form:**
1. Navigate to **Project → Network → Networks → Create Network**
2. **Verify**: Port security checkbox is **NOT visible**
3. **Create network**: Should succeed with default port security settings
4. **Check**: No errors related to port security

**Port Creation Form:**
1. Navigate to **Project → Network → Networks → [Select Network] → Ports → Create Port**
2. **Verify**: Port security checkbox is **NOT visible**
3. **Create port**: Should succeed
4. **Check**: Port created with default settings

**Network Editing:**
1. Edit an existing network
2. **Verify**: Port security option is not shown
3. **Submit changes**: Should not affect port security setting

#### 3. Test with Unrestricted User
Log in as admin or user with appropriate permissions:

**Verify Checkbox is Visible:**
1. Navigate to network creation form
2. **Verify**: Port security checkbox **IS visible**
3. **Test**: Toggle the checkbox and create network
4. **Verify**: Setting is applied correctly

#### 4. Test Policy Combinations
Test various policy configurations:
- **Read-only**: User can see setting but not change it (if applicable)
- **Create-only**: User can set during creation but not edit later
- **Full access**: User can create and edit

For each configuration:
- **Verify**: UI reflects the policy correctly
- **Check**: Appropriate controls are shown/hidden

#### 5. Browser Testing
Open browser developer tools → Network tab:
- **Verify**: No failed API calls related to port security
- **Check**: No policy violation errors in responses

#### 6. Test Edge Cases
- **Network Templates**: If Horizon supports network templates, verify they work correctly
- **Bulk Operations**: Test if multiple networks/ports can be created
- **API Direct Access**: Verify API calls match UI restrictions

#### 7. Run Unit Tests
```bash
tox -e py3 -- openstack_dashboard.dashboards.project.networks.tests
```
**Expected**: All tests pass, including new tests for policy-based hiding.

## Top Challenges in Reviewing This Change

1. **Policy Configuration**: Setting up and testing various Neutron policy configurations can be complex and error-prone.

2. **Policy Evaluation Logic**: Understanding how Horizon evaluates Neutron policies to determine what UI elements to show/hide.

3. **Multiple Policy Scenarios**: Testing all permutations of policy restrictions (create vs update, network vs port) requires thorough test planning.

4. **Default Behavior**: Understanding what the default port security setting should be when the user can't modify it.

5. **UI Consistency**: Ensuring this pattern matches how Horizon handles other policy-restricted features.

6. **Cross-Feature Impact**: Verifying this doesn't break related features like security groups, which interact with port security.

## Recommended Steps for Completing the Review

### Phase 1: Code Review (Estimated: 1.5-2 hours)
- **Review the patch**: Examine the 4 modified files:
  - How is policy checked? (`policy.check()` calls?)
  - Which forms are affected? (NetworkForm, PortForm?)
  - Template changes (hiding checkbox conditionally)
  - Test additions/modifications
- **Verify policy check logic**: Ensure correct policy rules are checked
- **Check form rendering**: Verify conditional rendering logic
- **Review test coverage**: Ensure tests cover policy restricted and unrestricted scenarios
- **UI/UX consistency**: Compare with how other policy-restricted features are handled

### Phase 2: Functional Testing (Estimated: 2-3 hours)
- **Policy setup**: Configure test policies (30-45 minutes)
- **User testing**: Test with multiple users/roles (60-90 minutes)
- **Form testing**: Test all affected forms (30-45 minutes)
- **Edge cases**: Test unusual scenarios (15-30 minutes)

### Phase 3: Review Feedback (Estimated: 30 minutes)
- **Document findings**: List any policy scenarios not handled
- **UX assessment**: Evaluate user experience improvements
- **Suggest enhancements**: Additional hiding, better error messages, etc.

## Key Areas of Concern

- **Policy Check Performance**: Are policy checks cached or does each form load trigger API calls?
- **Default Values**: What happens to port security when user can't set it? Is there a safe default?
- **Partial Restrictions**: What if user can create but not update? Is this handled?
- **Error Handling**: If policy check fails, does the form fail gracefully?
- **Security**: Does hiding the checkbox actually prevent the API call, or just hide the UI?
- **Consistency**: Are all forms that expose port security updated?
- **Documentation**: Is the policy restriction pattern documented for developers?

## Technology and Testing Framework Background

### Neutron Port Security

Port security is a Neutron feature that:
- Enables anti-spoofing rules (MAC and IP)
- Controls whether security groups apply to a port
- Can be enabled/disabled per network or per port
- **Default**: Usually enabled

**Use Cases for Disabling:**
- SR-IOV ports
- Virtual appliances that need promiscuous mode
- Testing scenarios

### OpenStack Policy (Oslo.policy)

Horizon uses Oslo.policy to enforce Neutron policies:

```python
# Example policy check in Horizon
from openstack_dashboard import policy

def __init__(self, request, *args, **kwargs):
    super(MyForm, self).__init__(request, *args, **kwargs)
    
    # Check if user can set port security
    if not policy.check((("network", "update_network:port_security_enabled"),), request):
        # Hide the field
        del self.fields['port_security_enabled']
```

### Policy Rules in Neutron

Example policy file (`policy.yaml`):
```yaml
# Allow everyone to see port security setting
"get_network:port_security_enabled": ""

# Only admins can change it
"update_network:port_security_enabled": "rule:admin_only"
"create_network:port_security_enabled": "rule:admin_only"
```

### Horizon Form Framework

Horizon forms (based on Django forms):
- Can dynamically add/remove fields
- Support conditional rendering
- Integrate with policy checks
- Render to templates

## Estimated Review Time

- **Complexity Level**: Medium
- **Estimated Total Hours**: 4-5.5 hours

**Breakdown:**
- **Code Review (Phase 1)**: 1.5-2 hours
- **Functional Testing (Phase 2)**: 2-3 hours
- **Review Feedback & Discussion (Phase 3)**: 30 minutes

**Factors affecting time:**
- Familiarity with Neutron policies: saves 30 minutes
- Existing test users with varied roles: saves 30 minutes
- Understanding of Horizon form framework: saves 30 minutes
- Need to test multiple policy scenarios: adds 30-60 minutes

## Questions to Ask the Author

1. **Which policy rules are checked?** What specific Neutron policy rules does this code check?
2. **Affected forms?** Which forms are impacted? Network create/edit? Port create/edit?
3. **Default behavior?** When checkbox is hidden, what's the default port security value?
4. **Partial permissions?** How are scenarios handled where user can create but not update?
5. **Testing performed?** What testing was done? Different policies? Multiple user roles?
6. **Consistency?** Does this match the pattern for other policy-restricted features in Horizon?
7. **Documentation?** Should developer docs be updated to explain this pattern?
8. **Future plans?** Are there other policy-restricted features that should follow this pattern?

## Follow-Up Actions

- **Policy Documentation**: Document recommended Neutron policy configurations
- **User Documentation**: Update user docs to explain when port security controls are hidden
- **Developer Guidelines**: Add to developer docs as a pattern for policy-aware UI
- **Extend Pattern**: Apply similar logic to other policy-restricted features
- **Testing**: Add integration tests with various policy configurations
- **Release Notes**: Document this UX improvement in release notes

