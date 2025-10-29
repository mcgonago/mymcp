# Quick Reference: Revert Review 960204

## Critical Information

```
Review URL:    https://review.opendev.org/c/openstack/horizon/+/960204
Commit SHA:    49e5fe185a915ab80ccf4c130225371ade323711
Merge Date:    October 21, 2025
Files:         100 files (+9, -9577 lines)
Conflicts:     NONE ✅
Status:        SAFE TO REVERT ✅
```

## The Simple Revert Commands

```bash
# Clone horizon
cd /home/omcgonag/Work/mymcp/workspace
git clone https://github.com/openstack/horizon horizon-revert-960204
cd horizon-revert-960204

# Setup Gerrit
git review -s

# Create revert
git revert 49e5fe185a915ab80ccf4c130225371ade323711

# Edit commit message in your editor to add:
#   Reason: [Why you need to revert this]

# Push for review
git review master
```

## Commit Message Template

```
Revert "Remove all dependencies/connections of old integration test code"

This reverts commit 49e5fe185a915ab80ccf4c130225371ade323711.

Reason: The integration test code is still needed for [FILL IN YOUR REASON].

The removal was premature because [EXPLAIN THE ISSUE].

This revert restores:
- 96 deleted files in openstack_dashboard/test/integration_tests/
- Integration test infrastructure (basewebobject, helpers, decorators)
- All page objects and test files
- Related configuration in tox.ini and templates

Related-Change: I013972aac7a6ed998bb33513024e06039232d1d4
Change-Id: I<will-be-generated>
```

## Verification Commands

```bash
# After revert is merged, verify:
cd /home/omcgonag/Work/mymcp/workspace
./fetch-review.sh opendev https://review.opendev.org/c/openstack/horizon/+/<YOUR-REVERT-NUMBER>
cd horizon-<YOUR-REVERT-NUMBER>

# Check files exist
ls -la openstack_dashboard/test/integration_tests/

# Count files
find openstack_dashboard/test/integration_tests/ -type f | wc -l
# Should show ~96 files

# Run tests
tox -e py3
tox -e pep8
```

## Why It's Safe

- ✅ 0 files modified since merge
- ✅ Only 3 commits since merge (Oct 21)
- ✅ None of those commits touch affected files
- ✅ Revert tested successfully with no conflicts
- ✅ Only 6 days since merge

## Need Help?

See detailed analysis: [REVERT_COMPLETE_ANALYSIS.md](REVERT_COMPLETE_ANALYSIS.md)

