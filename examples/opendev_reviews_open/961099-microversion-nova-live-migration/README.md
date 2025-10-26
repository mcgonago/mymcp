# Review 961099: Add microversion support for Nova live migration

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

- **Change ID**: 961099
- **URL**: https://review.opendev.org/c/openstack/horizon/+/961099
- **Project**: openstack/horizon
- **Branch**: master
- **Status**: NEW
- **Created**: 2025-09-15
- **Last Updated**: 2025-10-22
- **Files Changed**: 3 files
- **Changes**: +12/-3 lines

## High-Level Description of Changes

This is a small, focused change that adds Nova microversion support for live migration operations in Horizon. With only 3 files modified and a net gain of 9 lines, this appears to be adding or updating microversion headers for live migration API calls.

**Key Changes:**
- Adds or updates Nova API microversion specifications
- Affects live migration functionality in Horizon's UI
- Small code footprint suggests targeted enhancement

## What Problem Does This Solve?

**Nova Microversions and Live Migration:**
Nova's live migration capabilities have evolved across microversions, with each version adding new features, parameters, or behaviors. Without specifying the correct microversion:

1. **Missing Features**: Newer live migration options may not be available
2. **API Compatibility**: Calls might fail or behave unexpectedly with newer Nova versions
3. **Feature Enablement**: Certain live migration modes (e.g., block migration, forced hosts) require specific microversions

**Specific Issues Likely Addressed:**
- **Block Migration Options**: Newer microversions offer better block migration controls
- **Host Selection**: Enhanced host targeting capabilities in newer APIs
- **Migration Parameters**: Additional parameters for controlling migration behavior
- **Error Handling**: Better error messages and validation in newer microversions

**Example Microversion Evolution:**
- **2.25**: Added forced host and force parameter
- **2.30**: Added block_migration parameter
- **2.56**: Changed block_migration to auto, removing disk_over_commit
- **2.68**: Added additional migration parameters

## How to Test This Change

Testing requires a functional Nova environment capable of live migration with appropriate microversion support.

### Prerequisites
1. **Horizon Development Environment**: master branch
2. **Nova with Live Migration**: OpenStack environment configured for live migration
3. **Multiple Compute Nodes**: At least 2 compute hosts to migrate between
4. **Test Instances**: Running instances suitable for live migration
5. **Appropriate Hardware**: Shared storage or block migration capable setup

### Testing Steps

#### 1. Verify Microversion Configuration
Check what microversion is being requested:
- Review the code changes to identify target microversion
- Verify Nova API supports this microversion
```bash
openstack --os-compute-api-version 2.68 server list
```

#### 2. Test Live Migration via Horizon UI
1. **Navigate to Instance List**: Project → Compute → Instances
2. **Select a Running Instance**
3. **Open Actions Menu** → **Migrate Instance** or **Live Migrate Instance**
4. **Check Migration Options**:
   - Verify all expected options appear (host selection, block migration, etc.)
   - **Look for**: Options that were added in the target microversion
5. **Perform Live Migration**:
   - Select target host (if option available)
   - Check block migration option (if applicable)
   - Click **Migrate**
6. **Verify Success**:
   - Instance migrates successfully
   - Instance remains running during and after migration
   - No errors in Horizon or Nova logs

#### 3. Test with Network Monitoring
In browser developer tools → Network tab:
```
Expected API Call:
POST /api/nova/servers/{id}/action
Headers:
  X-OpenStack-Nova-API-Version: 2.XX
  
Body:
{
  "os-migrateLive": {
    "host": "compute-02",
    "block_migration": "auto"
  }
}
```

**Verify:**
- Correct microversion header is present
- Request body matches microversion requirements
- Response is successful (HTTP 202)

#### 4. Test Microversion Compatibility
Test with different Nova API versions if possible:
- **Older Nova**: Verify graceful handling if microversion not supported
- **Target Nova**: Verify full functionality with target microversion
- **Newer Nova**: Verify forward compatibility

#### 5. Test Edge Cases
- **Migration Failures**: Test with invalid host, insufficient resources
  - **Verify**: Appropriate error messages displayed
- **Migration Restrictions**: Test with instance that can't be live migrated
  - **Verify**: Option disabled or clear error message
- **Block Migration**: If applicable, test with non-shared storage
  - **Verify**: Block migration option works correctly

#### 6. Unit and Functional Tests
```bash
# Run relevant tests
tox -e py3 -- openstack_dashboard.dashboards.project.instances.tests.test_instances

# Test live migration specific functionality
tox -e py3 -- openstack_dashboard.dashboards.project.instances.tests.test_live_migration
```
**Expected**: All tests pass.

## Top Challenges in Reviewing This Change

1. **Microversion Knowledge**: Understanding the specific microversion being targeted and what features it enables requires Nova API expertise.

2. **Live Migration Setup**: Testing live migration requires a complex environment with multiple compute nodes and proper configuration (shared storage or block migration capable).

3. **API Compatibility**: Ensuring the change works with a range of Nova versions (not just the target microversion).

4. **Feature Discovery**: Identifying what new capability this microversion enables without seeing the actual code diff.

5. **Backward Compatibility**: Ensuring Horizon still works with older Nova deployments that don't support the target microversion.

## Recommended Steps for Completing the Review

### Phase 1: Code Review (Estimated: 1-1.5 hours)
- **Review the patch**: Identify:
  - Which microversion is being targeted
  - What API calls are affected
  - New parameters or options being enabled
  - Changes to API client calls
- **Check Nova API docs**: Review Nova API documentation for the target microversion
  - What features does it add?
  - Are there breaking changes?
  - What's the minimum required version?
- **Verify error handling**: Check for graceful degradation if microversion isn't supported
- **Review tests**: Ensure tests are updated for new functionality

### Phase 2: Functional Testing (Estimated: 1.5-2.5 hours)
- **Environment check**: Verify lab has required setup (1 hour if setup needed)
- **Live migration tests**: Perform live migrations via UI (30-45 minutes)
- **API verification**: Check network calls and responses (15 minutes)
- **Edge case testing**: Test failures and restrictions (30 minutes)

### Phase 3: Review Feedback (Estimated: 30 minutes)
- **Document findings**: Note any issues or improvements
- **Verify feature completeness**: Ensure all microversion features are accessible
- **Suggest improvements**: Documentation, error messages, user experience

## Key Areas of Concern

- **Microversion Negotiation**: Does Horizon check if Nova supports the required microversion?
- **Graceful Degradation**: What happens if Nova doesn't support the target microversion?
- **API Parameter Changes**: Microversions can deprecate or rename parameters; are these handled?
- **User Experience**: Are new options clearly presented and explained in the UI?
- **Error Messages**: Do error messages make sense in the context of the microversion?
- **Documentation**: Is the required Nova microversion documented?

## Technology and Testing Framework Background

### Nova API Microversions

Nova uses microversions to evolve the API without breaking compatibility:
- **Format**: `X-OpenStack-Nova-API-Version: 2.XX`
- **Negotiation**: Client requests a version, server returns supported version
- **Backward Compatible**: Newer Nova supports older microversions

### Live Migration Microversion History

Key microversions for live migration:
- **2.25**: Added `force` parameter
- **2.30**: Added `block_migration` parameter (True/False/"auto")
- **2.56**: Changed `block_migration` to `block_migration="auto"` default, removed `disk_over_commit`
- **2.68**: Added `block_migration` as nullable boolean (None means auto-detect)

### Example API Call with Microversion

```bash
curl -X POST \
  -H "X-Auth-Token: $TOKEN" \
  -H "X-OpenStack-Nova-API-Version: 2.68" \
  -H "Content-Type: application/json" \
  -d '{
    "os-migrateLive": {
      "host": "compute-02",
      "block_migration": null
    }
  }' \
  http://nova:8774/v2.1/servers/{server_id}/action
```

### Horizon API Client

Horizon's Nova client (`novaclient` or SDK) handles microversions:
```python
# In Horizon code
client = nova_client.get_client(request, version='2.68')
client.servers.live_migrate(instance_id, host='compute-02', block_migration=None)
```

## Estimated Review Time

- **Complexity Level**: Small-Medium
- **Estimated Total Hours**: 3-4.5 hours

**Breakdown:**
- **Code Review (Phase 1)**: 1-1.5 hours
- **Functional Testing (Phase 2)**: 1.5-2.5 hours (assumes live migration environment available)
- **Review Feedback & Discussion (Phase 3)**: 30 minutes

**Factors affecting time:**
- Live migration environment ready: saves 1 hour
- Familiarity with Nova microversions: saves 30-45 minutes
- Need to research specific microversion features: adds 30 minutes
- Testing multiple Nova versions: adds 30-45 minutes

## Questions to Ask the Author

1. **Which microversion is targeted?** What specific version is this change enabling?
2. **What new features does this enable?** What can users now do that they couldn't before?
3. **Backward compatibility?** How does Horizon handle older Nova versions?
4. **Testing performed?** Was this tested with actual live migrations? Multiple Nova versions?
5. **Documentation updates?** Are there any user-facing docs that need updating?
6. **Why this microversion?** Is this the minimum required, or the latest recommended?
7. **Error handling?** What happens if Nova rejects the microversion?
8. **Related changes?** Are there companion changes in other parts of Horizon or OpenStack?

## Follow-Up Actions

- **Documentation Update**: Ensure minimum Nova version is documented
- **Release Notes**: Document the new microversion support and any new features enabled
- **User Documentation**: Update Horizon user docs if new migration options are available
- **API Version Matrix**: Update compatibility matrix for Horizon-Nova versions
- **Further Testing**: Test with multiple Nova versions in CI
- **Feature Announcement**: If significant new features enabled, announce in community channels

