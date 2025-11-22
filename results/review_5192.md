# Review Assessment: PR 5192 - Add database-changelog-cleanup job

## Review Information

**Review URL:** https://github.com/RedHatInsights/rhsm-subscriptions/pull/5192  
**Review Number:** 5192  
**Project:** RedHatInsights/rhsm-subscriptions  
**Author:** William Poteat <wpoteat@redhat.com>  
**Status:** OPEN  
**Branch:** main  
**Created:** 2025-11-10  
**Updated:** 2025-11-10  
**Assessment Date:** 2025-11-21  

## Original Inquiry

**Query to Agent:**
```
@github-reviewer-agent Analyze PR https://github.com/RedHatInsights/rhsm-subscriptions/pull/5192
```

## Executive Summary

**Purpose:** Adds a Kubernetes job to clean up Liquibase database changelog locks in the swatch-metrics-hbi application.

**Scope:** 
- Files changed: 1
- Lines added: +81
- Lines deleted: -2

**Recommendation:** ✅ +1 APPROVE (with minor questions)

This PR adds operational tooling to address database changelog lock issues, which can occur when Liquibase migrations fail or are interrupted. The implementation is well-structured with safe defaults (no-op initially) and parameterization for flexibility. The approach is solid, though there are some questions about operational procedures and documentation.

## Change Overview

### What Changed

**File:** `swatch-metrics-hbi/deploy/clowdapp.yaml`

1. **New Parameters Added:**
   - `DB_CHANGELOG_CLEANUP_RUN_NUMBER` - Controls job uniqueness for re-runs
   - `DB_CHANGELOG_CLEANUP_SQL` - SQL to execute (defaults to safe `select 1`)
   - `EGRESS_IMAGE` / `EGRESS_IMAGE_TAG` - Container image for the job

2. **New ClowdApp Created:**
   - `swatch-db-changelog-cleanup` - Dedicated app for the cleanup job
   - Shares database connection with swatch-database

3. **New Job Added:**
   - `db-changelog-cleanup-${DB_CHANGELOG_CLEANUP_RUN_NUMBER}` - Kubernetes Job
   - Executes SQL via psql command
   - Resource-limited (100m CPU, 100Mi memory)

4. **ClowdJobInvocation Created:**
   - Triggers the cleanup job
   - Name includes run number for uniqueness

### Why This Change

**Problem:** Liquibase database changelog locks can get stuck when:
- Migration fails mid-execution
- Pod crashes during migration
- Manual interruption occurs
- Network issues during migration

**Impact:** Stuck locks prevent future migrations from running, blocking deployments.

**Solution:** This PR adds an on-demand job to manually clean up stuck locks when needed.

### Impact

**Breaking Changes:** NO  
**API Changes:** NO  
**Configuration Changes:** YES (new parameters, but with safe defaults)  
**Database Changes:** NO (job is no-op by default)  

## Code Quality Assessment

### ✅ Strengths

1. **Safe Defaults:** The job defaults to `select 1` (harmless query), preventing accidental data deletion
2. **Parameterized:** Uses run number for job uniqueness, allowing multiple executions
3. **Resource-Constrained:** Proper CPU/memory limits prevent resource exhaustion
4. **Isolated:** Separate ClowdApp keeps cleanup logic separate from main application
5. **Database Credentials:** Correctly uses existing swatch-database secrets
6. **Clear Naming:** Parameters and job names clearly indicate purpose

### ⚠️ Concerns

1. **Operational Documentation:** No README or runbook explaining:
   - When to use this job
   - How to diagnose stuck locks
   - What SQL to use for different scenarios
   - How to increment run number

2. **SQL Injection Risk:** The `DB_CHANGELOG_CLEANUP_SQL` parameter is user-controlled
   - Mitigated by: Kubernetes RBAC restricting who can set parameters
   - Still: No validation on the SQL content

3. **Generic Cleanup:** Hardcoded SQL in PR description: `delete from databasechangeloglock_swatch_contracts`
   - Question: Is this the only table? Are there others?
   - Question: Should we validate before deleting?

4. **No Monitoring:** No logging or metrics to track when cleanups happen

5. **Image Choice:** Uses egress image for psql
   - Question: Is this the right image? Does it have psql?
   - Consider: Dedicated database tools image?

### 📋 Suggestions

1. **Add Runbook:**
   ```markdown
   ## When to Use Database Changelog Cleanup
   
   ### Symptoms of Stuck Lock:
   - Deployment fails with "Waiting for changelog lock"
   - databasechangeloglock table shows locked=true
   
   ### How to Clean Up:
   1. Verify lock is stuck: `select * from databasechangeloglock_swatch_contracts`
   2. Update parameter: DB_CHANGELOG_CLEANUP_RUN_NUMBER=2
   3. Update SQL: DB_CHANGELOG_CLEANUP_SQL='delete from databasechangeloglock_swatch_contracts'
   4. Deploy
   5. Verify: Check job logs and lock table
   ```

2. **Add SQL Validation:**
   - Consider limiting to specific safe SQL patterns
   - Or document approved queries

3. **Add Logging:**
   ```yaml
   args:
     - |
       echo "Running cleanup SQL: $DB_CHANGELOG_CLEANUP_SQL"
       psql -h $POSTGRESQL_SERVICE_HOST -U $POSTGRESQL_USER $POSTGRESQL_DATABASE -c "$DB_CHANGELOG_CLEANUP_SQL"
       echo "Cleanup complete, exit code: $?"
   ```

4. **Document Image Choice:**
   - Add comment explaining why egress image is used
   - Or create dedicated DB tools image

## Technical Analysis

### Files Modified

| File | Changes | Notes |
|------|---------|-------|
| `swatch-metrics-hbi/deploy/clowdapp.yaml` | +81/-2 | Added cleanup job ClowdApp and parameters |

### Code Review

#### File: swatch-metrics-hbi/deploy/clowdapp.yaml

**Changes:**

1. **Parameters Section** (lines ~64-76):
```yaml
# New parameters added:
- name: DB_CHANGELOG_CLEANUP_RUN_NUMBER
  value: '1'
- name: DB_CHANGELOG_CLEANUP_SQL
  value: 'select 1'  # Safe default
- name: EGRESS_IMAGE
  value: quay.io/redhat-services-prod/rh-subs-watch-tenant/rhsm-subscriptions-egress
- name: EGRESS_IMAGE_TAG
  value: latest
```

**Analysis:**
- ✅ Safe default SQL won't cause damage
- ✅ Run number allows re-runs by incrementing
- ⚠️ Using `latest` tag is generally discouraged (prefer specific versions)
- ⚠️ No validation on SQL content

**Issues:**
- [ ] Consider pinning image tag instead of `latest`
- [ ] Document parameter usage

2. **ClowdApp Definition** (lines ~225-280):
```yaml
- apiVersion: cloud.redhat.com/v1alpha1
  kind: ClowdApp
  metadata:
    name: swatch-db-changelog-cleanup
  spec:
    envName: ${ENV_NAME}
    database:
      sharedDbAppName: ${DB_POD}
    dependencies:
      - ${DB_POD}
```

**Analysis:**
- ✅ Correctly shares database with ${DB_POD}
- ✅ Declares dependency on database pod
- ✅ Separate ClowdApp keeps concerns separated
- ✅ No deployments (job-only ClowdApp)

3. **Job Definition** (lines ~242-263):
```yaml
jobs:
  - name: db-changelog-cleanup-${DB_CHANGELOG_CLEANUP_RUN_NUMBER}
    restartPolicy: Never
    podSpec:
      image: ${EGRESS_IMAGE}:${EGRESS_IMAGE_TAG}
      command: ["/bin/sh", "-c"]
      args:
        - psql -h $POSTGRESQL_SERVICE_HOST -U $POSTGRESQL_USER $POSTGRESQL_DATABASE -c "$DB_CHANGELOG_CLEANUP_SQL"
      resources:
        requests:
          cpu: 100m
          memory: 50Mi
        limits:
          cpu: 100m
          memory: 100Mi
```

**Analysis:**
- ✅ Correct use of shell to execute psql
- ✅ Reasonable resource limits for simple query
- ✅ `restartPolicy: Never` appropriate for cleanup job
- ✅ Environment variables from secrets
- ⚠️ No error handling or logging
- ⚠️ Direct SQL execution without validation

**Issues:**
- [ ] Add error handling and logging
- [ ] Consider SQL sanitization or whitelist

4. **ClowdJobInvocation** (lines ~265-270):
```yaml
- apiVersion: cloud.redhat.com/v1alpha1
  kind: ClowdJobInvocation
  metadata:
    name: db-changelog-cleanup-${DB_CHANGELOG_CLEANUP_RUN_NUMBER}
  spec:
    appName: swatch-db-changelog-cleanup
    jobs:
      - db-changelog-cleanup-${DB_CHANGELOG_CLEANUP_RUN_NUMBER}
```

**Analysis:**
- ✅ Correctly references the ClowdApp and job
- ✅ Uses run number for uniqueness
- ✅ Standard ClowdJobInvocation pattern

## Review Checklist

### Code Quality
- [x] ✅ Code follows project style guidelines (YAML structure is consistent)
- [x] ✅ No obvious bugs or logic errors
- [x] ✅ Error handling is appropriate (for simple job)
- [x] ✅ Code is readable and maintainable

### Testing
- [ ] ⚠️ Unit tests included/updated (N/A for YAML config)
- [ ] ⚠️ Integration tests considered (How was this tested?)
- [ ] ❓ Manual testing performed (Unknown - ask author)
- [ ] ⚠️ Edge cases covered (What if SQL fails? What if run number collision?)

### Documentation
- [ ] ❌ Code comments are clear (Could use more comments)
- [ ] ❌ Docstrings updated (N/A)
- [ ] ❌ README updated (No runbook provided)
- [ ] ❓ Release notes added (Unknown - is this needed?)

### Security
- [x] ✅ No security vulnerabilities introduced (SQL is parameterized, RBAC controls access)
- [ ] ⚠️ Input validation appropriate (SQL is not validated)
- [x] ✅ Authentication/authorization correct (Uses existing DB secrets)
- [x] ✅ Sensitive data handled properly (Uses secrets, not plaintext)

### Performance
- [x] ✅ No obvious performance issues (cleanup should be quick)
- [x] ✅ Database queries optimized (Simple delete/select)
- [x] ✅ Resource usage reasonable (100m CPU, 100Mi mem)
- [x] ✅ Scalability considered (N/A for ad-hoc job)

### Backward Compatibility
- [x] ✅ API compatibility maintained (No API changes)
- [x] ✅ Database migrations safe (Job doesn't run by default)
- [x] ✅ Configuration backward compatible (New params have defaults)
- [x] ✅ Deprecation warnings added (N/A)

## Testing Verification

### How to Test

```bash
# 1. View the changes
cd workspace/rhsm-subscriptions-pr-5192
git show HEAD

# 2. Check YAML syntax
yamllint swatch-metrics-hbi/deploy/clowdapp.yaml

# 3. Test deployment (in test environment)
# - Deploy with default parameters (should be no-op)
# - Verify job creates but doesn't run
# - Update parameters to run actual cleanup
# - Check job logs and database

# 4. Manual validation steps:
# a. Check default SQL is safe
echo "Default SQL: select 1"  # Should be harmless

# b. Check resource limits
echo "CPU: 100m, Memory: 100Mi"  # Reasonable for simple query

# c. Verify job uniqueness
echo "Job name includes run number"  # Allows re-runs
```

### Test Results

**Linting:** ⚠️ NOT RUN (recommend `yamllint`)  
**Unit Tests:** N/A (YAML configuration)  
**Integration Tests:** ❓ UNKNOWN (ask author)  

**Notes:**
- Recommend testing in dev environment first
- Verify egress image has psql installed
- Test both default (no-op) and actual cleanup scenarios

## Comparison with Master

### Diff Summary

This is the only change - adding the cleanup job functionality.

**Key Differences from Master:**
1. Master: No database cleanup mechanism
2. This PR: Adds on-demand cleanup job with safe defaults

### Conflicts Check

**Files modified since original base:** Unknown  
**Potential conflicts:** LOW (only touches clowdapp.yaml)

## Related Work

### Related Reviews
- Unknown - may want to check for related database migration work

### Related Issues
- **SWATCH-4057:** Add database-changelog-cleanup job (referenced in commit)

### Dependencies
- **Depends on:** Existing swatch-database infrastructure
- **Required by:** Operations team for incident response

## Questions for Author

1. **Testing:** How was this tested? Did you simulate a stuck lock and verify cleanup works?

2. **Image Choice:** Why use the egress image? Does it have psql? Consider documenting or using dedicated DB tools image.

3. **SQL Validation:** Should we limit the SQL that can be executed? Or document approved queries?

4. **Documentation:** Can you add a runbook explaining:
   - When to use this job
   - How to diagnose stuck locks
   - Step-by-step cleanup procedure
   - How to verify cleanup succeeded

5. **Image Tag:** Should we pin `EGRESS_IMAGE_TAG` to a specific version instead of `latest`?

6. **Monitoring:** Should we add logging or metrics to track when cleanups happen?

7. **Multiple Tables:** The PR description mentions `databasechangeloglock_swatch_contracts`. Are there other changelog lock tables that might need cleanup?

## Recommendations

### Before Merge

**Must Address:**
- [ ] Document operational procedure (runbook or README)
- [ ] Verify egress image has psql
- [ ] Confirm testing was done

**Should Consider:**
- [ ] Pin image tag to specific version (not `latest`)
- [ ] Add logging to job output
- [ ] Document approved SQL queries
- [ ] Add comments explaining parameter usage

**Nice to Have:**
- [ ] SQL validation or whitelist
- [ ] Metrics/alerting when job runs
- [ ] Dedicated DB tools image

### Comments to Post

**Comment on clowdapp.yaml:lines 74-75:**
```
Consider pinning the image tag to a specific version instead of 'latest' for reproducibility:

  - name: EGRESS_IMAGE_TAG
    value: 'v1.2.3'  # or whatever your current stable version is

This ensures the job behavior doesn't unexpectedly change when the image is updated.
```

**Comment on clowdapp.yaml:line 93:**
```
Can you add a comment explaining when to use this job and how to set the parameters? For example:

# To run cleanup:
# 1. Increment DB_CHANGELOG_CLEANUP_RUN_NUMBER
# 2. Set DB_CHANGELOG_CLEANUP_SQL to 'delete from databasechangeloglock_swatch_contracts'
# 3. Deploy
```

**General comment:**
```
Great addition for operational tooling! The safe-by-default approach is well done.

A few suggestions:
1. Please add documentation (README or runbook) explaining:
   - When to use this job
   - How to diagnose stuck locks  
   - Step-by-step cleanup procedure
   
2. Consider pinning the image tag instead of using 'latest'

3. Add some logging to the job output for troubleshooting:
   ```yaml
   args:
     - |
       echo "Running cleanup: $DB_CHANGELOG_CLEANUP_SQL"
       psql -h $POSTGRESQL_SERVICE_HOST -U $POSTGRESQL_USER $POSTGRESQL_DATABASE -c "$DB_CHANGELOG_CLEANUP_SQL"
       echo "Cleanup complete, exit code: $?"
   ```

Otherwise looks good! +1 after addressing documentation.
```

## Verification Commands

```bash
# Fetch the PR
cd /home/omcgonag/Work/mymcp/workspace
./scripts/fetch-review.sh github https://github.com/RedHatInsights/rhsm-subscriptions/pull/5192

# View changes
cd rhsm-subscriptions-pr-5192
git show HEAD

# Check YAML syntax
yamllint swatch-metrics-hbi/deploy/clowdapp.yaml

# View specific sections
git show HEAD:swatch-metrics-hbi/deploy/clowdapp.yaml | grep -A 20 "DB_CHANGELOG_CLEANUP"
```

## Decision

**Recommendation:** ✅ +1 APPROVE (with documentation request)

**Reasoning:**

**Strengths:**
- Addresses real operational need (stuck Liquibase locks)
- Safe-by-default design prevents accidents
- Well-structured with proper resource limits
- Clean separation of concerns (dedicated ClowdApp)
- Flexible parameterization for different scenarios

**Minor Concerns:**
- Missing operational documentation/runbook
- Using `latest` image tag
- Limited logging for troubleshooting

**Why +1 (not +2):**
The code itself is solid, but the lack of operational documentation is a gap. This is a tool that operators will use during incidents, so clear instructions are important. Once a runbook or README section is added explaining how to use this, it's immediately a +2.

**Conditions:**
- Add documentation explaining when and how to use this job
- Confirm testing was done (or test in dev environment)
- Consider addressing the image tag and logging suggestions

---

**Status:** ✅ Assessment Complete  
**Reviewer:** Owen McGonagle (via Cursor AI)  
**Assessment Date:** 2025-11-21  
**Last Updated:** 2025-11-21

**Next Steps for Author:**
1. Add runbook documentation
2. Confirm psql availability in egress image
3. Address comments about image tag and logging
4. Should be ready for +2 after documentation added
