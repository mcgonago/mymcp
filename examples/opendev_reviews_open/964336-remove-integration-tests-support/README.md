# Review 964336: Remove all references to INTEGRATION_TESTS_SUPPORT

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

- **Change ID**: 964336
- **URL**: https://review.opendev.org/c/openstack/horizon/+/964336
- **Project**: openstack/horizon
- **Branch**: master
- **Status**: NEW
- **Created**: 2025-10-17
- **Last Updated**: 2025-10-21
- **Files Changed**: 5 files
- **Changes**: +0/-16 lines (pure deletion)

## High-Level Description of Changes

This is a cleanup change that removes all references to `INTEGRATION_TESTS_SUPPORT` from the Horizon codebase. With 5 files modified and 16 lines deleted (no additions), this is a pure removal of deprecated or unused configuration/feature flags.

**Key Changes:**
- Removes `INTEGRATION_TESTS_SUPPORT` variable/constant
- Removes conditional logic based on this flag
- Cleanup across 5 files

## What Problem Does This Solve?

**Technical Debt Reduction:**
The `INTEGRATION_TESTS_SUPPORT` flag was likely used to:
- Enable/disable integration test features
- Toggle test-specific functionality
- Control test environment behavior

**Problems with Keeping Deprecated Flags:**
1. **Code Clutter**: Unused code paths confuse developers
2. **Maintenance Burden**: Dead code still needs to be maintained during refactors
3. **Confusion**: New contributors don't know if the flag is still relevant
4. **False Dependencies**: Other code might reference it unnecessarily
5. **Testing Complexity**: Conditional code paths increase test matrix

**Why Remove Now:**
- Flag is no longer needed (integration tests work without it)
- Simplifies the codebase
- Part of ongoing cleanup efforts
- Integration tests have matured beyond needing this flag

## How to Test This Change

Since this is a pure deletion, testing focuses on ensuring nothing breaks without these references.

### Prerequisites
1. **Horizon Development Environment**: master branch
2. **Full Test Suite Access**: Ability to run all test types

### Testing Steps

#### 1. Verify Flag Removal is Complete
Search for any remaining references:
```bash
cd /path/to/horizon
grep -r "INTEGRATION_TESTS_SUPPORT" --include="*.py" --include="*.js" --include="*.sh"
```
**Expected**: No matches (or only in comments/documentation explaining the removal)

#### 2. Run Full Test Suite
```bash
# Unit tests
tox -e py3

# Integration tests (the key area)
tox -e integration

# Selenium tests
tox -e selenium

# All environments
tox
```
**Expected**: All tests pass without the flag.

#### 3. Test Horizon Functionality
Run Horizon and verify core functionality:
```bash
cd horizon
python manage.py runserver
```

Test key features:
- Login/logout
- Navigate all major sections
- Create/edit/delete resources
- No JavaScript errors in console

#### 4. Check Configuration Files
Verify no configuration templates or examples reference the removed flag:
```bash
find . -name "*.conf*" -o -name "*.yaml*" -o -name "*.json*" | xargs grep -l "INTEGRATION_TESTS_SUPPORT"
```
**Expected**: No matches, or matches are in comments explaining removal.

#### 5. Review Documentation
Check if documentation needs updates:
```bash
find ./doc -type f | xargs grep -l "INTEGRATION_TESTS_SUPPORT"
```
**If found**: Documentation should be updated to remove references or explain the removal.

#### 6. CI/CD Pipeline Check
After merging, monitor CI/CD:
- **Zuul jobs**: Verify all gate jobs pass
- **Integration tests**: Specifically watch integration test jobs
- **Selenium tests**: Ensure UI tests complete successfully

## Top Challenges in Reviewing This Change

1. **Incomplete Removal**: Ensuring ALL references are removed, including comments, docs, and configuration examples.

2. **Hidden Dependencies**: Identifying if any external tools or scripts depended on this flag.

3. **Test Coverage**: Verifying that tests previously conditional on this flag are now always running (or properly removed).

4. **Documentation**: Checking if user or developer documentation references this flag.

5. **Configuration Examples**: Ensuring sample config files don't still show this option.

6. **Commit Message Context**: Understanding the history - when was this flag introduced, why, and why is it safe to remove now?

## Recommended Steps for Completing the Review

### Phase 1: Code Review (Estimated: 45-60 minutes)
- **Review the patch**: Check all 5 files:
  - Where was the flag defined?
  - Where was it checked/used?
  - What behavior did it control?
  - Are the deletions clean (no orphaned conditions)?
- **Search for remaining references**: Use grep to find any missed references
- **Check related code**: Look for code that might have depended on flag being present (even if not directly referencing it)
- **Review git history**: Understand when and why the flag was introduced
- **Check tests**: Verify tests that might have used this flag are appropriately updated

### Phase 2: Functional Testing (Estimated: 1-1.5 hours)
- **Run test suite**: Execute full tox tests (45-60 minutes)
- **Manual verification**: Quick smoke test of Horizon UI (15-30 minutes)
- **Check CI**: Review CI job definitions for references (15 minutes)

### Phase 3: Review Feedback (Estimated: 15-30 minutes)
- **Verify completeness**: Confirm all references removed
- **Documentation check**: Flag any docs that need updating
- **Approve or request changes**: Based on findings

## Key Areas of Concern

- **Incomplete Removal**: Are there any remaining references in comments, docs, or config examples?
- **Test Behavior Change**: Did this flag control which tests ran? Are those tests now always running or always skipped?
- **External Dependencies**: Do any deployment tools, CI configs, or external scripts reference this flag?
- **Backward Compatibility**: Could old configuration files with this setting cause issues?
- **Migration Path**: Is there a deprecation notice or was this an internal-only flag?

## Technology and Testing Framework Background

### Horizon Testing Framework

Horizon has multiple test layers:
- **Unit Tests**: Python unittest/pytest, fast, no external dependencies
- **Integration Tests**: Test Horizon with mock OpenStack services
- **Selenium Tests**: Full browser-based UI testing
- **Functional Tests**: API-level testing with real OpenStack

### Feature Flags in Horizon

Horizon uses various feature flags:
- **Settings Variables**: In `local_settings.py` or `settings.py`
- **Environment Variables**: For deployment configuration
- **Conditional Imports**: For optional dependencies

### Integration Tests Evolution

Horizon's integration tests have evolved:
- **Old approach**: May have used `INTEGRATION_TESTS_SUPPORT` to enable features
- **Current approach**: Integration tests are first-class, no special flag needed
- **Testing tools**: Selenium, pytest, test fixtures

### Flag Removal Pattern

Typical pattern for removing feature flags:
1. Deprecate the flag (mark as unused)
2. Remove conditional logic (make it always on/off)
3. Remove flag references
4. Update documentation
5. Monitor for issues post-merge

## Estimated Review Time

- **Complexity Level**: Small
- **Estimated Total Hours**: 2-2.5 hours

**Breakdown:**
- **Code Review (Phase 1)**: 45-60 minutes
- **Functional Testing (Phase 2)**: 1-1.5 hours (mostly automated test runtime)
- **Review Feedback & Discussion (Phase 3)**: 15-30 minutes

**Factors affecting time:**
- Familiarity with Horizon test framework: saves 15-30 minutes
- Fast test environment: saves 30 minutes
- Understanding of flag's original purpose: saves 15 minutes
- Need to trace flag's history: adds 15-30 minutes

## Questions to Ask the Author

1. **When was this flag introduced?** What was its original purpose?
2. **Why remove it now?** What changed that makes it no longer necessary?
3. **Are there any external dependencies?** Do any CI jobs, deployment scripts, or tools reference this flag?
4. **Test coverage?** Were there tests conditional on this flag? What happens to them?
5. **Documentation?** Are there docs that need updating?
6. **Deprecation period?** Was this flag deprecated first, or is this a direct removal?
7. **Related cleanup?** Are there other similar flags that should be removed?
8. **Risk assessment?** What's the risk of removing this? Any known dependencies?

## Follow-Up Actions

- **Search for Similar Flags**: Identify other deprecated flags that can be removed
- **Documentation Update**: Update developer docs to remove references
- **CI Cleanup**: Remove any CI-related configuration for this flag
- **Release Notes**: Mention this cleanup in release notes (minor note)
- **Monitor Post-Merge**: Watch for any unexpected CI failures or issues
- **External Communication**: If this was a public flag, announce removal in appropriate channels

