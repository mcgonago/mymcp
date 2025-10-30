# PR #483 Verification Guide

## Overview

**PR:** https://github.com/openstack-k8s-operators/horizon-operator/pull/483  
**Title:** Removed TLS hook for include conf.d/*.conf  
**Author:** mcgonago (Owen McGonagle)  
**Merged:** 2025-08-08T17:10:13+00:00  
**Commit:** 93aa9b8a3a048c19bb9d077e543b1cd5b77c8893  
**Jira:** OSPRH-18585  

## What Changed

### The Problem Before PR #483

The `httpd.conf` template had this code:
```go
Include conf.modules.d/*.conf
{{- if .TLS }}
## TODO: fix default ssl.conf to comment not available tls certs. Than we can remove this condition
Include conf.d/*.conf
{{- end }}
```

**Issue:** The `Include conf.d/*.conf` directive was only executed when TLS was enabled. 

This meant:
- ✅ **With TLS enabled:** Files in `/etc/httpd/conf.d/` were loaded
- ❌ **Without TLS:** Files in `/etc/httpd/conf.d/` were **NOT** loaded

### The Solution in PR #483

Changed to:
```go
Include conf.modules.d/*.conf
Include conf.d/*.conf
```

**Result:** The `Include conf.d/*.conf` directive is now **ALWAYS** executed.

This means:
- ✅ **With TLS enabled:** Files in `/etc/httpd/conf.d/` are loaded (same as before)
- ✅ **Without TLS:** Files in `/etc/httpd/conf.d/` are **NOW** loaded (FIXED!)

### Why This Matters

1. **Custom httpd configuration** - Allows deploying custom httpd configs via conf.d even without TLS
2. **LimitRequestBody setting** - Specifically enables setting `LimitRequestBody` for large image uploads
3. **Removes TLS dependency** - No longer need TLS just to load custom httpd configs

## How to Verify

### Quick Verification (3 commands)

```bash
# 1. Check operator image version (must be built after 2025-08-08)
oc get deployment horizon-operator-controller-manager -n openstack-operators \
  -o jsonpath='{.spec.template.spec.containers[0].image}'

# 2. Check if conf.d is included in httpd.conf
oc exec -n openstack <horizon-pod> -- grep "Include conf.d" /etc/httpd/conf/httpd.conf

# 3. Verify httpd loads conf.d files
oc exec -n openstack <horizon-pod> -- httpd -t -D DUMP_INCLUDES 2>&1 | grep conf.d
```

### Automated Verification Script

We've created a comprehensive verification script:

```bash
cd /home/omcgonag/Work/mymcp/workspace
./verify-pr-483.sh [operator-namespace] [openstack-namespace]
```

**Example:**
```bash
./verify-pr-483.sh openstack-operators openstack
```

The script checks:
1. ✅ Operator image version and build date
2. ✅ Horizon pod existence and age
3. ✅ **CRITICAL:** Presence of `Include conf.d/*.conf` in httpd.conf
4. ✅ What files exist in `/etc/httpd/conf.d/`
5. ✅ TLS configuration status
6. ✅ httpd process running status
7. ✅ httpd error logs for conf.d issues

### Manual Deep Dive Verification

#### Step 1: Check Operator Version

```bash
# Get operator image
OPERATOR_IMAGE=$(oc get deployment horizon-operator-controller-manager \
  -n openstack-operators \
  -o jsonpath='{.spec.template.spec.containers[0].image}')

echo "Operator Image: $OPERATOR_IMAGE"

# Check if image was built after PR merge (2025-08-08)
# Look for tags like v0.X.Y where X.Y > version at merge time
```

#### Step 2: Examine httpd.conf Template in Operator

```bash
# Get operator pod
OPERATOR_POD=$(oc get pods -n openstack-operators \
  -l control-plane=controller-manager \
  -o jsonpath='{.items[0].metadata.name}')

# Check the template file
oc exec -n openstack-operators $OPERATOR_POD -- \
  cat /templates/horizon/config/httpd.conf | grep -B 2 -A 2 "Include conf"
```

**Expected output WITH PR #483:**
```
Include conf.modules.d/*.conf
Include conf.d/*.conf

LogFormat "%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\"" combined
```

**Output WITHOUT PR #483 (OLD):**
```
Include conf.modules.d/*.conf
{{- if .TLS }}
## TODO: fix default ssl.conf to comment not available tls certs. Than we can remove this condition
Include conf.d/*.conf
{{- end }}
```

#### Step 3: Check Rendered httpd.conf in Running Horizon

```bash
# Get Horizon pod
HORIZON_POD=$(oc get pods -n openstack -l service=horizon \
  -o jsonpath='{.items[0].metadata.name}')

# Check the actual rendered config
oc exec -n openstack $HORIZON_POD -- cat /etc/httpd/conf/httpd.conf | grep -B 3 -A 3 "Include conf"
```

**Expected output (with or without TLS):**
```
Include conf.modules.d/*.conf
Include conf.d/*.conf

LogFormat ...
```

**If you see this, PR #483 IS applied:**
- `Include conf.d/*.conf` is present
- No conditional logic around it

**If you DON'T see `Include conf.d/*.conf`, PR #483 is NOT applied**

#### Step 4: Verify conf.d Files Are Actually Loaded

```bash
# Check what conf.d files exist
oc exec -n openstack $HORIZON_POD -- ls -la /etc/httpd/conf.d/

# Test if httpd can parse the config (includes conf.d)
oc exec -n openstack $HORIZON_POD -- httpd -t

# Show all included files
oc exec -n openstack $HORIZON_POD -- httpd -t -D DUMP_INCLUDES 2>&1 | grep -E "(conf\.d|ssl\.conf)"
```

#### Step 5: Test with TLS Disabled

This is the key test case that PR #483 fixes:

```bash
# Check if TLS is enabled in Horizon CR
oc get horizon -n openstack -o yaml | grep -A 10 "tls:"

# If TLS is NOT configured:
# - WITH PR #483: conf.d/*.conf SHOULD be loaded ✅
# - WITHOUT PR #483: conf.d/*.conf would NOT be loaded ❌
```

**Verification:**
```bash
# Even with TLS disabled, these should work:
oc exec -n openstack $HORIZON_POD -- cat /etc/httpd/conf.d/ssl.conf
oc exec -n openstack $HORIZON_POD -- grep "conf.d" /etc/httpd/conf/httpd.conf
```

#### Step 6: Verify Custom Configs Work

If you have custom configs in conf.d (like LimitRequestBody):

```bash
# Check if your custom config exists
oc exec -n openstack $HORIZON_POD -- ls /etc/httpd/conf.d/99-custom.conf

# Check if the setting is active
oc exec -n openstack $HORIZON_POD -- httpd -M | grep <module-name>
oc exec -n openstack $HORIZON_POD -- httpd -D DUMP_VHOSTS
```

## Test Scenarios

### Scenario 1: Deployment with TLS Enabled

**Expected Behavior (before and after PR #483):**
- `Include conf.d/*.conf` is present in httpd.conf
- Files in `/etc/httpd/conf.d/` are loaded
- ssl.conf is processed
- Custom configs work

**Result:** No change - works the same

### Scenario 2: Deployment WITHOUT TLS (Key Test!)

**Before PR #483:**
- ❌ `Include conf.d/*.conf` is NOT in httpd.conf
- ❌ Files in `/etc/httpd/conf.d/` are ignored
- ❌ Custom configs don't work
- ❌ Cannot set LimitRequestBody via conf.d

**After PR #483:**
- ✅ `Include conf.d/*.conf` IS in httpd.conf
- ✅ Files in `/etc/httpd/conf.d/` are loaded
- ✅ Custom configs work
- ✅ Can set LimitRequestBody via conf.d

### Scenario 3: Adding Custom httpd Config

**Test this to confirm PR #483 is working:**

1. Create a ConfigMap with custom httpd config:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: horizon-httpd-custom
  namespace: openstack
data:
  99-custom.conf: |
    # Test config to verify conf.d loading
    LimitRequestBody 10737418240
```

2. Mount it in Horizon pod (via operator config)

3. Verify it's loaded:
```bash
oc exec -n openstack $HORIZON_POD -- cat /etc/httpd/conf.d/99-custom.conf
oc exec -n openstack $HORIZON_POD -- httpd -t
oc exec -n openstack $HORIZON_POD -- grep -r "LimitRequestBody" /etc/httpd/
```

**Result:**
- ✅ With PR #483: Your config is active even without TLS
- ❌ Without PR #483: Your config would be ignored without TLS

## Decision Matrix

| Condition | PR #483 Status | Result |
|-----------|----------------|--------|
| TLS Enabled | Applied | ✅ conf.d loaded (same as before) |
| TLS Enabled | NOT Applied | ✅ conf.d loaded (old behavior) |
| TLS Disabled | Applied | ✅ conf.d loaded (FIXED!) |
| TLS Disabled | NOT Applied | ❌ conf.d NOT loaded (PROBLEM!) |

**Conclusion:** PR #483 only makes a difference when TLS is disabled, but it's critical for that use case.

## Verification Checklist

- [ ] Operator image built after 2025-08-08
- [ ] `Include conf.d/*.conf` present in httpd.conf template
- [ ] `Include conf.d/*.conf` present in rendered httpd.conf
- [ ] conf.d files are listed in `/etc/httpd/conf.d/`
- [ ] `httpd -t -D DUMP_INCLUDES` shows conf.d files
- [ ] httpd starts successfully
- [ ] No conf.d related errors in httpd logs
- [ ] Custom configs in conf.d work (if applicable)
- [ ] Works regardless of TLS setting

## Common Issues

### Issue 1: conf.d/*.conf not in httpd.conf

**Symptom:** `grep "conf.d" /etc/httpd/conf/httpd.conf` returns nothing

**Cause:** PR #483 not applied

**Solution:** 
- Check operator version
- Upgrade to version that includes PR #483
- Rebuild/redeploy Horizon

### Issue 2: ssl.conf errors without TLS

**Symptom:** httpd fails to start, logs show ssl.conf certificate errors

**Cause:** This is the original problem PR #483 helps with

**Solution:**
- Ensure PR #483 is applied
- Or remove problematic lines from ssl.conf
- Or configure TLS properly

### Issue 3: Custom configs not working

**Symptom:** Files in conf.d exist but have no effect

**Verification:**
```bash
# Check if Include is there
oc exec $HORIZON_POD -- grep "Include conf.d" /etc/httpd/conf/httpd.conf

# Check httpd syntax
oc exec $HORIZON_POD -- httpd -t

# Check what's included
oc exec $HORIZON_POD -- httpd -t -D DUMP_INCLUDES 2>&1 | grep conf.d
```

## Related Information

**Jira:** https://issues.redhat.com/browse/OSPRH-18585

**Related Changes:**
- Topic branch: `missing-exports`
- May be part of a series of httpd configuration improvements

**References:**
- PR Discussion: Review comments in PR #483
- ssl.conf issue: Mentioned in PR comments about localhost.crt problems

## Files Changed

```
templates/horizon/config/httpd.conf
  Lines changed: -3 (removed)
  - Removed: {{- if .TLS }}
  - Removed: ## TODO: fix default ssl.conf...
  - Removed: {{- end }}
  - Kept: Include conf.d/*.conf (now unconditional)
```

## Summary

**One-line summary:** PR #483 makes `Include conf.d/*.conf` work regardless of TLS setting.

**Why it matters:** Enables custom httpd configuration (like LimitRequestBody) without requiring TLS.

**How to verify:** Check if `Include conf.d/*.conf` is unconditionally present in httpd.conf.

**Quick test:** Deploy without TLS and verify conf.d files are still loaded.

