# Analysis: Horizon Direct Mode Upload Revert (FR4 Blocker)

## Original Inquiry

**Date:** 2025-10-31  
**Asked to:** Cursor AI with MCP Agents  
**Query:**
```
UI team has identified a blocker for FR4 while testing
https://issues.redhat.com/browse/RHOSSTRAT-917

Probably because of the change in
OSPRH-18894: Switch default image upload mode in Horizon to "direct"

What we see:
- the Image starts creating (the Images are visible in tab)
- but we get stuck in Queued status later.
- that is probably reason why it passed our automated tests.

Bug: OSPRH-21433: Bug: Horizon UI - create image does not work
Trac: OSPRH-21435: TRAC Blocker: Horizon UI - create image does not work

Relates to OSPRH-18226 Use direct mode for image uploads in Horizon by default

Links to:
- https://github.com/openstack-k8s-operators/horizon-operator/pull/526: Revert Images direct mode upload
- https://github.com/openstack-k8s-operators/horizon-operator/pull/527: [18.0-fr4] Revert Images direct mode upload
```

## Data Sources

- [x] GitHub PRs
- [ ] OpenDev Reviews
- [ ] GitLab MRs
- [x] Jira Issues (partial - some permission restricted)
- [x] Other: MCP Agent queries, existing analysis documents

## Executive Summary

On October 31, 2025, the Horizon direct mode upload feature was reverted from both the main branch and the 18.0-fr4 release branch due to a critical blocker bug (OSPRH-21433) discovered during FR4 testing. The feature, which was implemented in September 2025 to improve image upload performance, caused images to become stuck in "Queued" status after creation, rendering the image upload functionality unusable in the Horizon UI.

**Key Points:**
- **Implementation Date:** September 2, 2025 (PR #506)
- **Discovery Date:** October 2025 (during FR4 testing)
- **Revert Date:** October 31, 2025 (PRs #526 and #527)
- **Impact:** Blocker for FR4 release
- **Status:** Under investigation (OSPRH-21433)

The revert was swift and targeted, removing only the single line that enabled direct mode (`HORIZON_IMAGES_UPLOAD_MODE = 'direct'`), returning the system to the legacy proxy mode while the root cause is investigated.

## Background

### Original Feature Goal (RHOSSTRAT-917, OSPRH-18226, OSPRH-18894)

The feature was requested to provide more efficient image uploads from Horizon to Glance. The direct mode allows browsers to upload image files directly to the Glance API rather than proxying through the Horizon Django application.

**Benefits of Direct Mode:**
- Improves upload performance for large images
- Reduces load on Horizon servers
- Solves the 1GB LimitRequestBody limitation in legacy mode (ref: https://access.redhat.com/articles/6975397)
- Provides better user experience with progress indicators
- Removes Horizon as a bandwidth bottleneck

**Legacy Mode (Before):**
```
Browser → Horizon (Django) → Glance → Storage
```

**Direct Mode (Attempted):**
```
Browser ------→ Glance → Storage
   ↓
Horizon (metadata only)
```

### Implementation Dependencies

The implementation required coordination between multiple operators:

1. **Glance Operator Changes** (PR #787 - merged August 24, 2025)
   - Added automatic CORS configuration
   - Watched for Horizon CR presence
   - Configured `allowed_origin` dynamically based on Horizon endpoint

2. **Horizon Operator Changes** (PR #506 - merged September 2, 2025)
   - Added `HORIZON_IMAGES_UPLOAD_MODE = 'direct'` to configuration
   - Changed default from 'legacy' to 'direct'

### Initial Testing Success

The feature initially passed automated tests, likely because:
- Automated tests may only verify image creation (metadata)
- Tests may not wait for image to reach "Active" status
- Tests may use small images that behave differently
- Tests may not exercise the full upload flow through the browser UI

## Detailed Findings

### The Bug: Images Stuck in "Queued" Status

**Symptom Description:**
When users attempt to upload an image through the Horizon UI with direct mode enabled:

1. ✅ Image metadata is created successfully
2. ✅ Image appears in the Images tab
3. ❌ Image status remains "Queued" indefinitely
4. ❌ Image never transitions to "Active" status
5. ❌ Image cannot be used to launch instances

**Why This Passed Automated Tests:**
The bug is particularly insidious because:
- The API call to create the image succeeds (returns 200 OK)
- The image object exists in the database
- Only the actual file upload/activation fails
- Automated tests likely check for image existence, not status transitions

### Root Cause Investigation Status

As of the revert date (October 31, 2025), the root cause is **still under investigation** (Jira: OSPRH-21433).

**Potential Causes to Investigate:**

1. **CORS Configuration Issues**
   - Horizon endpoint may not be correctly configured in Glance
   - CORS headers may be missing or incorrect
   - Browser may be blocking the direct upload requests

2. **Authentication/Authorization**
   - Token may not be correctly passed to Glance
   - Token may be scoped incorrectly for direct uploads
   - Service account permissions may be insufficient

3. **Network Connectivity**
   - Browser may not be able to reach Glance API endpoint
   - Firewall rules may be blocking direct connections
   - Endpoint may not be publicly accessible

4. **Glance API Configuration**
   - Direct upload endpoints may not be properly enabled
   - File upload handling may have issues
   - Stage/import workflow may have problems

5. **Horizon JavaScript Issues**
   - Direct upload code may have bugs
   - Error handling may be insufficient
   - Progress monitoring may be broken

### Impact Assessment

**Severity:** **BLOCKER** for FR4 Release

**Affected Components:**
- Horizon UI (Image creation workflow)
- End user functionality (Cannot upload custom images)
- All FR4 deployments would be affected

**Business Impact:**
- Users cannot upload custom VM images
- Cloud administrators cannot onboard new workloads
- Feature is critical for most OpenStack deployments
- Regression from previous releases (legacy mode worked)

**Workaround:**
Revert to legacy mode (which is what PRs #526 and #527 accomplished)

## Code References

### Jira Issues

#### RHOSSTRAT-917: More efficient image uploads from Horizon
- **URL:** https://issues.redhat.com/browse/RHOSSTRAT-917
- **Type:** Feature Request
- **Status:** Open
- **Description:** Make direct upload mode the default for improved performance
- **Goals:**
  - Glance ready for direct upload mode
  - Direct mode as default
  - Solve 1GB LimitRequestBody problem (https://access.redhat.com/articles/6975397)
- **Acceptance Criteria:**
  - Documentation for direct mode as default
  - Works without additional configuration

#### OSPRH-18226: Use direct mode for image uploads in Horizon by default
- **URL:** https://issues.redhat.com/browse/OSPRH-18226
- **Type:** Story
- **Status:** Open
- **Description:** Earlier initiative to switch to direct mode
- **Notes:** 
  - Legacy mode doesn't require additional configuration but has severe limitations and is not very efficient
  - Direct mode requires additional configuration in Glance and needs Glance API endpoint exposed to outside world
  - Requires cooperation with Storage DFG
- **Upstream Docs:** https://docs.openstack.org/horizon/latest/configuration/settings.html#horizon-images-upload-mode

#### OSPRH-18894: Switch default image upload mode in Horizon to "direct"
- **URL:** https://issues.redhat.com/browse/OSPRH-18894
- **Type:** Task
- **Status:** Open
- **Goal:** Setup direct mode as follow-up to glance-operator PR #787
- **Related PRs:** openstack-k8s-operators/horizon-operator#506

#### OSPRH-21433: Bug: Horizon UI - create image does not work
- **URL:** https://issues.redhat.com/browse/OSPRH-21433
- **Type:** Bug
- **Status:** Under Investigation (as of 2025-10-31)
- **Severity:** Blocker
- **Description:** Images get stuck in "Queued" status after creation
- **Discovery:** FR4 testing
- **Note:** Permission denied to access full details (HTTP 401)

#### OSPRH-21435: TRAC Blocker: Horizon UI - create image does not work
- **URL:** https://issues.redhat.com/browse/OSPRH-21435
- **Type:** Blocker (Trac)
- **Status:** Open
- **Related To:** OSPRH-21433
- **Impact:** Blocks FR4 release
- **Note:** Permission denied to access full details (HTTP 401)

### GitHub Pull Requests

#### PR #787: Automatically configure CORS section based on Horizon CR (glance-operator)
- **URL:** https://github.com/openstack-k8s-operators/glance-operator/pull/787
- **Author:** fmount (fpantano@redhat.com)
- **Status:** ✅ Merged
- **Created:** August 20, 2025 at 13:51 UTC
- **Merged:** August 24, 2025 at 12:25 UTC
- **Branch:** main
- **Related Jira:** OSPRH-19261

**Description:**
Add integration with Horizon to dynamically set CORS `allowed_origin` in Glance configuration when Horizon CR is present.

**Changes:**
- Add Horizon API dependency and RBAC permissions
- Watch for Horizon CR changes in GlanceAPI controller
- Fetch Horizon endpoint and inject into config template
- Update CORS section in glance.conf template
- Add functional test support for Horizon CRDs

**Files Changed (9 files, +64/-4):**
```
api/go.mod: +1 -0 (added Horizon API dependency)
api/go.sum: +2 -2 (dependency updates)
config/rbac/role.yaml: +8 -0 (added Horizon RBAC permissions)
controllers/glanceapi_controller.go: +34 -0 (watch Horizon CR, inject endpoint)
go.mod: +1 -0 (dependency)
go.sum: +4 -2 (dependency updates)
main.go: +2 -0 (register Horizon scheme)
templates/common/config/00-config.conf: +5 -0 (add CORS section)
test/functional/suite_test.go: +7 -0 (add Horizon CRD support)
```

**Key Implementation in 00-config.conf:**
```ini
{{ if (index . "HorizonEndpoint") }}
[cors]
allowed_origin={{ .HorizonEndpoint }}
{{ end }}
```

**Key Code in glanceapi_controller.go:**
```go
// GetHorizonEndpoint - Returns the horizon endpoint set in the CR .Status
func (r *GlanceAPIReconciler) GetHorizonEndpoint(
    ctx context.Context,
    h *helper.Helper,
    instance *glancev1.GlanceAPI,
) (string, error) {
    horizon, err := horizonv1.GetHorizon(ctx, h, instance.Namespace)
    if err != nil {
        return "", err
    }
    return horizon.GetEndpoint()
}
```

**Approved by:** abays, fmount, konan-abhi
**Dependencies:** https://github.com/openstack-k8s-operators/horizon-operator/pull/500

#### PR #506: Set HORIZON_IMAGES_UPLOAD_MODE to direct (horizon-operator)
- **URL:** https://github.com/openstack-k8s-operators/horizon-operator/pull/506
- **Author:** fmount (fpantano@redhat.com)
- **Status:** ✅ Merged (Later Reverted)
- **Created:** September 1, 2025 at 10:54 UTC
- **Merged:** September 2, 2025 at 14:36 UTC
- **Branch:** main
- **Related Jira:** OSPRH-18894

**Description:**
> When not specified, `HORIZON_IMAGES_UPLOAD_MODE` has `legacy` as default value.
> Because we already patched `glance-operator` to set the `cors` section automatically 
> when horizon is enabled, this change allows horizon to rely on `direct` mode.

**Files Changed (1 file):**
```diff
templates/horizon/config/local_settings.py: +1 -0 (modified)
```

**Exact Change:**
```python
# Before line 37:
HORIZON_CONFIG["enforce_password_check"] = True
POLICY_FILES_PATH = '/etc/openstack-dashboard'
+HORIZON_IMAGES_UPLOAD_MODE = 'direct'

DEBUG = False
```

**Review Comments:**
- Question about documentation → Answer: Will document in RHOSO guide when branching FR4
- All functional tests passed
- Approved by: ashu-011, konan-abhi, mcgonago, fmount

#### PR #526: Revert Images direct mode upload (horizon-operator)
- **URL:** https://github.com/openstack-k8s-operators/horizon-operator/pull/526
- **Author:** fmount (fpantano@redhat.com)
- **Status:** ✅ Merged
- **Created:** October 31, 2025 at 10:49 UTC
- **Merged:** October 31, 2025 at 12:16 UTC
- **Branch:** main
- **Related Jira:** OSPRH-21433

**Description:**
> This patch reverts https://github.com/openstack-k8s-operators/horizon-operator/pull/506 
> due to the blocker bug: `OSPRH-21433` that is still under investigation.

**Files Changed (1 file):**
```diff
templates/horizon/config/local_settings.py: +0 -1 (modified)
```

**Exact Change:**
```python
# Removed line:
-HORIZON_IMAGES_UPLOAD_MODE = 'direct'
```

**Review Timeline:**
- Created: 10:49 UTC
- Approved: 10:49 UTC (self-approved by fmount as author/approver)
- LGTM: 11:51 UTC (ashu-011)
- Merged: 12:16 UTC
- Cherry-pick command: `/cherry-pick 18.0-fr4` (created PR #527)
- **Total Time: ~1.5 hours** (emergency revert)

#### PR #527: [18.0-fr4] Revert Images direct mode upload (horizon-operator)
- **URL:** https://github.com/openstack-k8s-operators/horizon-operator/pull/527
- **Author:** openshift-cherrypick-robot (automated)
- **Status:** ✅ Merged
- **Created:** October 31, 2025 at 12:25 UTC (automated cherry-pick)
- **Merged:** October 31, 2025 at 14:27 UTC
- **Branch:** 18.0-fr4
- **Related Jira:** OSPRH-21433

**Description:**
> This is an automated cherry-pick of #526
> /assign fmount

**Files Changed (1 file):**
```diff
templates/horizon/config/local_settings.py: +0 -1 (modified)
```

**Exact Change:**
```python
# Removed line:
-HORIZON_IMAGES_UPLOAD_MODE = 'direct'
```

**Review Timeline:**
- Created: 12:25 UTC (automated)
- Approved: 12:29 UTC (fmount)
- Merged: 14:27 UTC
- **Total Time: ~2 hours**

### File Paths

**Affected File:**
- `templates/horizon/config/local_settings.py` - Horizon configuration template

**Related Files:**
- `templates/common/config/00-config.conf` (glance-operator) - CORS configuration
- `controllers/glanceapi_controller.go` (glance-operator) - Horizon endpoint integration

## Implementation Timeline

| Date | Event | Link | Status |
|------|-------|------|--------|
| 2025-08-20 | Glance CORS PR created | [PR #787](https://github.com/openstack-k8s-operators/glance-operator/pull/787) | Created |
| 2025-08-24 12:25 | Glance CORS PR merged | [PR #787](https://github.com/openstack-k8s-operators/glance-operator/pull/787) | ✅ Merged |
| 2025-09-01 10:54 | Horizon direct mode PR created | [PR #506](https://github.com/openstack-k8s-operators/horizon-operator/pull/506) | Created |
| 2025-09-02 14:36 | Horizon direct mode PR merged | [PR #506](https://github.com/openstack-k8s-operators/horizon-operator/pull/506) | ✅ Merged |
| 2025-09 to 2025-10 | Feature in production | - | ⚠️ Bug Dormant |
| 2025-10 | FR4 testing begins | - | Testing |
| 2025-10 | Bug discovered (images stuck) | [OSPRH-21433](https://issues.redhat.com/browse/OSPRH-21433) | 🐛 Bug Filed |
| 2025-10-31 10:49 | Revert PR created (main) | [PR #526](https://github.com/openstack-k8s-operators/horizon-operator/pull/526) | Created |
| 2025-10-31 12:16 | Revert PR merged (main) | [PR #526](https://github.com/openstack-k8s-operators/horizon-operator/pull/526) | ✅ Merged |
| 2025-10-31 12:25 | Revert PR created (FR4) | [PR #527](https://github.com/openstack-k8s-operators/horizon-operator/pull/527) | Created (automated) |
| 2025-10-31 14:27 | Revert PR merged (FR4) | [PR #527](https://github.com/openstack-k8s-operators/horizon-operator/pull/527) | ✅ Merged |

**Time to Revert:** ~4 hours from creation to both branches merged

## Testing and Verification

### Test Case 1: Verify Legacy Mode is Active

```bash
# After revert, verify the mode is set correctly
oc get horizon -n openstack -o yaml | grep -A 5 config

# Expected: HORIZON_IMAGES_UPLOAD_MODE should NOT be present
# (defaults to 'legacy' when not specified)
```

**Expected Result:**
```yaml
# Should NOT see:
# HORIZON_IMAGES_UPLOAD_MODE: 'direct'

# Mode will default to 'legacy' internally
```

### Test Case 2: Verify Image Upload Works (Legacy Mode)

```bash
# Test image upload through Horizon UI:
# 1. Log into Horizon dashboard
# 2. Navigate to Project → Compute → Images
# 3. Click "Create Image"
# 4. Fill in:
#    - Name: test-legacy-upload
#    - File: Select a small test image (e.g., Cirros)
#    - Format: QCOW2
# 5. Click "Create Image"
# 6. Monitor image status

# Expected: Image should transition through states:
# "Queued" → "Saving" → "Active"
```

**Expected Result:**
- Image uploads successfully
- Image reaches "Active" status within reasonable time
- Image can be used to launch instances

### Test Case 3: Verify No CORS Errors in Browser Console

```bash
# Open browser developer tools (F12)
# Network tab while uploading image
# Console tab for any errors

# Expected: No CORS-related errors
# Upload should go through Horizon (not directly to Glance)
```

**Expected Result:**
```
# Network tab should show:
# POST https://horizon.example.com/dashboard/project/images/create
# (Upload data goes to Horizon, not Glance)

# Console should NOT show:
# "has been blocked by CORS policy"
# "No 'Access-Control-Allow-Origin' header"
```

### Test Case 4: Compare Configuration Before and After Revert

```bash
# Check the deployed configuration
oc get configmap horizon-config -n openstack -o yaml | grep -i upload_mode

# Or exec into horizon pod:
oc exec -it horizon-xxx -n openstack -- \
  grep HORIZON_IMAGES_UPLOAD_MODE /etc/openstack-dashboard/local_settings.py
```

**Before Revert (PR #506):**
```python
HORIZON_IMAGES_UPLOAD_MODE = 'direct'
```

**After Revert (PRs #526/#527):**
```python
# Line not present (defaults to 'legacy')
```

### Verification Commands

```bash
# 1. Verify horizon-operator code
cd /home/omcgonag/Work/mymcp/workspace
git clone https://github.com/openstack-k8s-operators/horizon-operator horizon-verify-revert
cd horizon-verify-revert

# Check main branch
git checkout main
git pull
git log --oneline --grep="Revert" -5
# Should see: commit for PR #526

grep -n "HORIZON_IMAGES_UPLOAD_MODE" templates/horizon/config/local_settings.py
# Should NOT find the line

# Check FR4 branch
git checkout 18.0-fr4
git pull
grep -n "HORIZON_IMAGES_UPLOAD_MODE" templates/horizon/config/local_settings.py
# Should NOT find the line

# 2. Verify in deployed cluster (if accessible)
oc get horizon -n openstack
oc describe horizon -n openstack

# 3. Check pod logs for any upload errors
oc logs -n openstack deployment/horizon --tail=100 | grep -i image

# 4. Test actual image upload
openstack image create --file /path/to/test.img test-upload-verification
openstack image show test-upload-verification
# Should show status: active
```

## Configuration Examples

### Current Configuration (After Revert)

**File:** `templates/horizon/config/local_settings.py`

```python
# Horizon configuration
HORIZON_CONFIG = {
    ...
}
HORIZON_CONFIG["enforce_password_check"] = True
POLICY_FILES_PATH = '/etc/openstack-dashboard'
# HORIZON_IMAGES_UPLOAD_MODE line removed - defaults to 'legacy'

DEBUG = False
# rest of configuration...
```

### Previous Configuration (Before Revert - PR #506)

```python
# Horizon configuration
HORIZON_CONFIG = {
    ...
}
HORIZON_CONFIG["enforce_password_check"] = True
POLICY_FILES_PATH = '/etc/openstack-dashboard'
HORIZON_IMAGES_UPLOAD_MODE = 'direct'  # THIS LINE WAS REMOVED

DEBUG = False
# rest of configuration...
```

## Known Issues and Workarounds

### Issue 1: Images Stuck in "Queued" Status (BLOCKER)

**Problem:** When direct mode is enabled, images created through Horizon UI never transition from "Queued" to "Active" status.

**Symptoms:**
- User uploads image through Horizon UI
- Image metadata is created successfully
- Image appears in image list
- Status remains "Queued" indefinitely
- Image cannot be used
- No obvious error messages in UI

**Impact:**
- Complete loss of image upload functionality
- Users cannot onboard custom images
- Blocks FR4 release
- Severity: BLOCKER

**Workaround:**
```python
# WORKAROUND: Use legacy mode (current state after revert)
# In templates/horizon/config/local_settings.py:
# Remove or comment out:
# HORIZON_IMAGES_UPLOAD_MODE = 'direct'

# Or explicitly set:
HORIZON_IMAGES_UPLOAD_MODE = 'legacy'
```

**Root Cause:** Under investigation (OSPRH-21433)

**Possible Causes:**
1. CORS configuration not working as expected
2. Glance endpoint not accessible from browser
3. Authentication token issues
4. JavaScript upload code bugs
5. Glance API not properly handling direct uploads

**Investigation Commands:**
```bash
# Check Glance CORS configuration
oc exec -it glance-api-pod -n openstack -- \
  grep -A 10 "\[cors\]" /etc/glance/glance-api.conf

# Check if Horizon endpoint is set in Glance config
oc exec -it glance-api-pod -n openstack -- \
  grep "allowed_origin" /etc/glance/glance-api.conf

# Check Glance API logs during upload attempt
oc logs -n openstack deployment/glance-api --tail=100 -f

# Check Horizon logs during upload attempt
oc logs -n openstack deployment/horizon --tail=100 -f

# Check browser console for JavaScript errors
# (Manual: Open DevTools → Console during upload)

# Test Glance direct upload manually
TOKEN=$(openstack token issue -f value -c id)
IMAGE_ID=$(openstack image create --format value -c id test-direct-manual)
curl -X PUT \
  -H "X-Auth-Token: $TOKEN" \
  -H "Content-Type: application/octet-stream" \
  -H "Origin: https://horizon.example.com" \
  --data-binary @test.img \
  "https://glance-api.openstack.svc:9292/v2/images/$IMAGE_ID/file" \
  -v
```

### Issue 2: Automated Tests Don't Catch the Bug

**Problem:** The bug passed automated testing because tests only verify image creation, not the full upload flow.

**Why Tests Passed:**
```python
# Typical automated test:
def test_image_create():
    image = create_image(name="test", file="test.img")
    assert image is not None  # ✅ PASSES - image object exists
    # Missing: assert image.status == "active"  # ❌ Would FAIL
```

**Recommendation:**
```python
# Improved test:
def test_image_create_and_activate():
    image = create_image(name="test", file="test.img")
    assert image is not None
    
    # Wait for image to become active
    timeout = 300  # 5 minutes
    start_time = time.time()
    while time.time() - start_time < timeout:
        image = get_image(image.id)
        if image.status == "active":
            return  # ✅ SUCCESS
        elif image.status == "error":
            raise AssertionError(f"Image failed: {image.status}")
        time.sleep(5)
    
    raise AssertionError(f"Image stuck in {image.status} after {timeout}s")
```

## Related Work

### Related Analyses

- [docs/analysis_direct_mode.md](analysis_direct_mode.md) - Complete technical documentation of direct mode implementation, CORS configuration, and deployment procedures (878 lines, comprehensive)

### External References

- **Horizon Upload Mode Documentation:** https://docs.openstack.org/horizon/latest/configuration/settings.html#horizon-images-upload-mode
- **Glance CORS Documentation:** https://docs.openstack.org/glance/latest/configuration/index.html
- **OpenStack Security Guide - CORS:** https://docs.openstack.org/security-guide/
- **Red Hat Access Article (1GB Limit):** https://access.redhat.com/articles/6975397

### Upstream Discussions

- OpenStack Horizon Bugs: https://bugs.launchpad.net/horizon
- OpenStack Glance Bugs: https://bugs.launchpad.net/glance
- OpenStack Mailing Lists: http://lists.openstack.org/pipermail/openstack-discuss/

## Reproduction Steps

To replicate this investigation:

```bash
# Step 1: Query Jira for related issues
# Run these MCP commands:
mcp_jiraMcp_get_jira("RHOSSTRAT-917")
mcp_jiraMcp_get_jira("OSPRH-18894")
mcp_jiraMcp_get_jira("OSPRH-18226")
mcp_jiraMcp_get_jira("OSPRH-21433")  # May require permissions
mcp_jiraMcp_get_jira("OSPRH-21435")  # May require permissions

# Step 2: Fetch GitHub PRs
# Run these MCP commands:
mcp_github-reviewer-agent_github_pr_fetcher(
  "https://github.com/openstack-k8s-operators/glance-operator/pull/787"
)
mcp_github-reviewer-agent_github_pr_fetcher(
  "https://github.com/openstack-k8s-operators/horizon-operator/pull/506"
)
mcp_github-reviewer-agent_github_pr_fetcher(
  "https://github.com/openstack-k8s-operators/horizon-operator/pull/526"
)
mcp_github-reviewer-agent_github_pr_fetcher(
  "https://github.com/openstack-k8s-operators/horizon-operator/pull/527"
)

# Step 3: Clone and examine the code
cd /home/omcgonag/Work/mymcp/workspace
git clone https://github.com/openstack-k8s-operators/horizon-operator
cd horizon-operator

# View the timeline
git log --all --oneline --graph | grep -E "(direct|Revert)" | head -20

# Compare the changes
git log --oneline --all --grep="direct" -- templates/horizon/config/local_settings.py

# Step 4: Examine the exact file changes
# View PR #506 (implementation)
git log --all --oneline | grep -i "HORIZON_IMAGES_UPLOAD_MODE"

# View PR #526 (revert on main)
git log --all --oneline | grep -i "Revert.*direct"

# Step 5: Search for related bugs in logs (if cluster access available)
oc logs -n openstack deployment/horizon --since=24h | grep -i "image\|upload\|queue"
oc logs -n openstack deployment/glance-api --since=24h | grep -i "cors\|origin\|upload"
```

## Conclusions

### Key Takeaways

1. **Direct mode implementation was well-intentioned** but encountered a critical bug that wasn't caught by automated testing

2. **The bug is specific to the upload workflow** - image metadata creation works, but file upload/activation fails

3. **Automated tests need improvement** - tests should verify full workflow including status transitions, not just object creation

4. **Fast revert response** - team reverted in ~4 hours across both main and FR4 branches, preventing release impact

5. **Root cause still unknown** - investigation ongoing in OSPRH-21433, multiple potential causes (CORS, network, auth, JavaScript)

6. **Single-line change** - both implementation and revert were single-line changes, making rollback simple and safe

7. **Legacy mode is stable** - reverting to legacy mode restores full functionality immediately

### Recommendations

#### Immediate Actions (Completed ✅)

1. ✅ **Revert direct mode** - DONE via PRs #526 and #527 on October 31, 2025
2. ✅ **Block FR4 release** - Tracked via OSPRH-21435 (TRAC Blocker)
3. ✅ **Document the issue** - This analysis document created

#### Short-term Actions (Next Steps ⚠️)

1. ⚠️ **Investigate root cause** - Priority investigation in OSPRH-21433
   ```bash
   # Investigation areas:
   - Check Glance CORS configuration deployment
   - Verify Horizon endpoint accessibility from browser
   - Review browser JavaScript console logs
   - Test manual direct upload via curl with CORS headers
   - Check network policies/firewalls between browser and Glance
   - Verify token validity and scope for direct uploads
   ```

2. ⚠️ **Improve automated testing** - Add status verification
   ```python
   # Add to test suite:
   def test_image_upload_complete_workflow():
       # Create image metadata
       # Upload file data
       # Wait for "active" status with timeout
       # Verify can launch instance from image
       # Test with various image sizes/formats
   ```

3. ⚠️ **Add monitoring** - Detect stuck images proactively
   ```bash
   # Alert on images stuck in "queued" for > 5 minutes
   openstack image list --status queued --long
   ```

4. ⚠️ **Document troubleshooting** - Create runbook for future issues

#### Long-term Actions (Future Work 🔄)

1. 🔄 **Fix and re-enable direct mode** - After root cause is resolved
   - Verify fix in dev environment
   - Test with multiple browsers (Chrome, Firefox, Safari, Edge)
   - Test with various image sizes (small, medium, large 10GB+)
   - Verify CORS configuration in all deployment scenarios
   - Re-run all automated tests
   - Perform extensive manual UI testing
   - Document all configuration requirements

2. 🔄 **Enhance testing coverage**
   - Add integration tests for full upload workflow
   - Add browser-based UI tests (Selenium/Playwright)
   - Add CORS configuration validation tests
   - Add performance tests with large images
   - Add multi-browser compatibility tests
   - Add negative test cases (network failures, timeouts)

3. 🔄 **Add feature flag** - Allow gradual rollout
   ```python
   # Example configuration:
   HORIZON_IMAGES_UPLOAD_MODE = 'direct'  # or 'legacy'
   HORIZON_IMAGES_UPLOAD_MODE_FEATURE_FLAG = True  # Enable/disable dynamically
   # Could be controlled per-tenant or per-user
   ```

4. 🔄 **Improve observability**
   - Add metrics for upload success/failure rates
   - Add timing metrics for upload duration
   - Add logging for CORS requests/responses
   - Add browser-side error reporting to backend
   - Add dashboards for monitoring image upload health

5. 🔄 **Update documentation**
   - Document direct mode requirements and prerequisites
   - Document troubleshooting procedures for CORS issues
   - Document rollback procedures (as demonstrated here)
   - Create operator guide for enabling/disabling feature
   - Update RHOSO documentation when feature is re-enabled

### Decision Points

**Should we re-enable direct mode?**
- ✅ YES - after root cause is fixed and thoroughly tested
- The feature provides significant value (performance, scalability, better UX)
- Legacy mode is a fallback, not a long-term solution
- Customer demand is documented (RHOSSTRAT-917)

**What testing is needed before re-enabling?**
1. Unit tests for JavaScript upload code
2. Integration tests for full workflow (metadata → upload → activate)
3. CORS configuration validation in deployment
4. Manual UI testing with multiple browsers
5. Large file upload tests (multi-GB images)
6. Network failure/retry scenarios
7. Token expiration handling during long uploads

**How to prevent similar issues?**
1. Improve automated test coverage (verify status transitions)
2. Add browser-based integration tests
3. Require manual QA sign-off for UI changes
4. Add feature flags for gradual rollout
5. Improve monitoring and alerting
6. Test in staging environment with real user workflows

## Appendix

### Additional Information

#### Emergency Revert Checklist

For future reference, this is how to quickly revert a feature:

```bash
# 1. Identify the problematic PR
PR_TO_REVERT=506

# 2. Create revert PR on main branch
git checkout main
git pull
git revert <commit-sha-of-pr-506>
git push origin HEAD:revert-pr-${PR_TO_REVERT}

# 3. Open PR with clear description
# Title: "Revert <feature> due to <bug>"
# Body: Link to bug, describe impact
# Example: "Revert Images direct mode upload"
#          "Due to blocker bug OSPRH-21433"

# 4. Get fast-track approval
# For blockers, approver can self-approve
# Use /lgtm for additional reviewer approval

# 5. Cherry-pick to release branch
# Use /cherry-pick command in PR comments:
# /cherry-pick 18.0-fr4
# Or manually:
git checkout 18.0-fr4
git cherry-pick <revert-commit-sha>
git push origin 18.0-fr4:revert-pr-${PR_TO_REVERT}-fr4

# 6. Verify deployment
# Check that configuration is updated
oc rollout status deployment/horizon -n openstack
# Test the reverted functionality
```

#### Commands and Outputs Summary

**Commands executed during this analysis:**

```bash
# 1. Read analysis template
read_file /home/omcgonag/Work/mymcp/analysis/analysis_template.md
# Output: 213-line template retrieved

# 2. Query Jira issues
mcp_jiraMcp_get_jira("RHOSSTRAT-917")
# Output: Feature overview with goals and acceptance criteria

mcp_jiraMcp_get_jira("OSPRH-18894")
# Output: Task to setup direct mode as follow-up to PR #787

mcp_jiraMcp_get_jira("OSPRH-18226")
# Output: Earlier story about using direct mode by default

mcp_jiraMcp_get_jira("OSPRH-21433")
# Output: HTTP 401 - Permission denied

mcp_jiraMcp_get_jira("OSPRH-21435")
# Output: HTTP 401 - Permission denied

# 3. Fetch GitHub PRs
mcp_github-reviewer-agent_github_pr_fetcher(
  "https://github.com/openstack-k8s-operators/glance-operator/pull/787"
)
# Output: PR metadata, 9 files changed (+64/-4), merged 2025-08-24

mcp_github-reviewer-agent_github_pr_fetcher(
  "https://github.com/openstack-k8s-operators/horizon-operator/pull/506"
)
# Output: PR metadata, 1 file changed (+1/-0), merged 2025-09-02

mcp_github-reviewer-agent_github_pr_fetcher(
  "https://github.com/openstack-k8s-operators/horizon-operator/pull/526"
)
# Output: PR metadata, 1 file changed (+0/-1), merged 2025-10-31 12:16

mcp_github-reviewer-agent_github_pr_fetcher(
  "https://github.com/openstack-k8s-operators/horizon-operator/pull/527"
)
# Output: PR metadata, 1 file changed (+0/-1), merged 2025-10-31 14:27

# 4. Read existing analysis
read_file /home/omcgonag/Work/mymcp/analysis/analysis_direct_mode.md
# Output: 878-line comprehensive technical analysis of direct mode

# 5. Create new analysis document
cp analysis_template.md analysis_revert_horizon_direct_mode.md
write analysis_revert_horizon_direct_mode.md
# Output: This document created

# 6. Update analysis README
search_replace analysis/README.md
# Output: Added entry for this analysis to README
```

#### Timeline Summary

| Date/Time (UTC) | Event | Actor | Result |
|-----------------|-------|-------|--------|
| 2025-08-24 12:25 | Glance CORS merged | fmount | ✅ Foundation laid |
| 2025-09-02 14:36 | Direct mode merged | fmount | ✅ Feature enabled |
| 2025-10 | Bug discovered | UI Team | 🐛 Blocker found |
| 2025-10-31 10:49 | Revert PR #526 created | fmount | Emergency response |
| 2025-10-31 11:51 | LGTM given | ashu-011 | Approval |
| 2025-10-31 12:16 | PR #526 merged (main) | fmount | ✅ Main reverted |
| 2025-10-31 12:24 | Cherry-pick initiated | fmount | `/cherry-pick 18.0-fr4` |
| 2025-10-31 12:25 | PR #527 created (auto) | bot | Auto cherry-pick |
| 2025-10-31 12:29 | PR #527 approved | fmount | Approval |
| 2025-10-31 14:27 | PR #527 merged (FR4) | fmount | ✅ FR4 reverted |

**Total incident response time:** 3 hours 38 minutes (10:49 to 14:27)

#### Bug Symptom Details

**User Experience:**
1. User navigates to Horizon → Images
2. Clicks "Create Image"
3. Fills in form (name, format, file)
4. Clicks "Create"
5. ✅ Success message shown
6. ✅ Image appears in list
7. ❌ Status shows "Queued"
8. ❌ Status never changes
9. ❌ Cannot launch instances
10. ❌ No error messages

**Technical Flow (Expected vs Actual):**

Expected with Direct Mode:
```
Browser → Horizon (metadata) → Database [Image created, status: queued]
Browser → Glance (file data)  → Storage [Image uploaded, status: saving]
Glance → Database             → [Image activated, status: active]
```

Actual with Direct Mode:
```
Browser → Horizon (metadata) → Database [Image created, status: queued]
Browser → Glance (file data)  → ??? [FAILS HERE - no data uploaded]
                                 [Status stuck: queued]
```

Restored with Legacy Mode:
```
Browser → Horizon (metadata + file) → Glance → Storage [Works]
Glance → Database                   → [Image activated, status: active]
```

---

**Status:** ✅ Complete - Revert documented, investigation ongoing  
**Last Updated:** 2025-10-31  
**Author:** Owen McGonagle (via Cursor AI analysis with MCP agents)  
**Reviewers:** UI Team, Storage DFG Team  
**Related Bug:** OSPRH-21433 (Under Investigation)  
**Related TRAC:** OSPRH-21435 (FR4 Blocker)
