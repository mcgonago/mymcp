# How to Revert OpenDev Review 960204

## ✅ COMPLETE ANALYSIS AVAILABLE

**See [REVERT_COMPLETE_ANALYSIS.md](REVERT_COMPLETE_ANALYSIS.md) for:**
- Full analysis with all commands and outputs
- Conflict check results
- Step-by-step verification
- Complete revert process

---

## Quick Summary

- **Review:** https://review.opendev.org/c/openstack/horizon/+/960204
- **Title:** Remove all dependencies/connections of old integration test code
- **Status:** MERGED (October 21, 2025)
- **Merged Commit SHA:** `49e5fe185a915ab80ccf4c130225371ade323711`
- **Changes:** 100 files changed, +9 lines, -9,577 lines
- **Conflicts:** ✅ **NONE** - Safe to revert
- **Files Modified Since:** 0 files (verified)
- **Commits Since Merge:** 3 commits (none touch affected files)

---

## THE SIMPLE ONE-LINE REVERT

Since analysis shows **ZERO conflicts**, you can revert with one command:

```bash
git revert 49e5fe185a915ab80ccf4c130225371ade323711
```

See below for the complete process.

---

## Option 1: Use Gerrit's Web UI Revert Feature (EASIEST)

This is the simplest method and creates a proper revert review automatically.

### Steps:

1. **Go to the merged review:**
   ```
   https://review.opendev.org/c/openstack/horizon/+/960204
   ```

2. **Click the "Revert" button** at the top of the page
   - Look for the three-dot menu (⋮) or "Revert" button
   - This is usually visible for merged changes

3. **Enter a revert message:**
   ```
   Revert "Remove all dependencies/connections of old integration test code"
   
   This reverts commit <commit-sha>.
   
   Reason: [Explain why you need to revert this]
   ```

4. **Submit the revert**
   - Gerrit will automatically create a new review that reverts all the changes
   - The new review will restore all 100 deleted files

5. **Wait for CI/CD to pass** and get it merged

---

## Option 2: Manual Revert Using Git (If Web UI doesn't work)

### Step 1: Fetch the Review and Find the Commit

```bash
cd workspace
./fetch-review.sh opendev https://review.opendev.org/c/openstack/horizon/+/960204
cd horizon-960204
git log --oneline -1
```

This will show you the commit SHA. Copy it for the next step.

### Step 2: Create a Clean Horizon Clone

```bash
cd /home/omcgonag/Work/mymcp/workspace
git clone https://github.com/openstack/horizon horizon-revert-960204
cd horizon-revert-960204
```

### Step 3: Set Up Gerrit Remote

```bash
git remote add gerrit ssh://<your-username>@review.opendev.org:29418/openstack/horizon
git review -s
```

Replace `<your-username>` with your OpenDev username (probably `omcgonag`).

### Step 4: Create Revert Commit

```bash
# Find the commit SHA of the merged change
git log --oneline --grep="Remove all dependencies" -10

# Create a revert commit (replace <commit-sha> with the actual SHA)
git revert <commit-sha>
```

This will create a revert commit. Git will open an editor with a commit message like:
```
Revert "Remove all dependencies/connections of old integration test code"

This reverts commit <commit-sha>.
```

You can add more context to explain why you're reverting:
```
Revert "Remove all dependencies/connections of old integration test code"

This reverts commit <commit-sha>.

Reason: The integration test code is still needed for [specific reason].
We need to restore this functionality because [explanation].

Change-Id: I<generated-by-git>
```

### Step 5: Push for Review

```bash
git review master
```

This will push your revert commit to Gerrit as a new review.

---

## Option 3: Manual File Restoration (For Partial Reverts)

If you only need to restore specific files, not everything:

### Step 1: Clone and Set Up

```bash
cd /home/omcgonag/Work/mymcp/workspace
git clone https://github.com/openstack/horizon horizon-partial-revert
cd horizon-partial-revert
git review -s
```

### Step 2: Find the Parent Commit (Before the Deletion)

```bash
# Find the deletion commit
git log --oneline --grep="Remove all dependencies" -1

# This will show something like:
# abc123456 Remove all dependencies/connections of old integration test code

# Get the parent commit (the one BEFORE the deletion)
git log --oneline --grep="Remove all dependencies" -1 --format="%H"
# Let's say this gives you: abc123456

# The parent is: abc123456^
```

### Step 3: Restore Specific Files

```bash
# Create a new branch
git checkout -b restore-integration-tests

# Restore files from before the deletion
# Replace <commit-sha> with the SHA from step 2
git checkout <commit-sha>^ -- openstack_dashboard/test/integration_tests/

# Or restore specific files:
git checkout <commit-sha>^ -- openstack_dashboard/test/integration_tests/tests/test_defaults.py
git checkout <commit-sha>^ -- openstack_dashboard/test/integration_tests/pages/pageobject.py
```

### Step 4: Commit and Push

```bash
git add .
git commit -m "Restore integration test files

Restoring integration test code that was removed in review 960204.

Reason: [Explain why you need these files back]

Related-Change: I<change-id-from-960204>
"

git review master
```

---

## Verification After Reverting

Once your revert is merged, verify the files are restored:

```bash
cd workspace
./fetch-review.sh --with-master opendev https://review.opendev.org/c/openstack/horizon/+/<your-revert-review-number>

# Check that files exist
ls -la horizon-<revert-number>/openstack_dashboard/test/integration_tests/

# Run tests
cd horizon-<revert-number>
tox -e py3
```

---

## Important Notes

1. **Explain Your Reasoning**: When creating the revert, clearly explain WHY you need to revert this change. Reviewers will want to understand the justification.

2. **Check Dependencies**: Review 960204 removed 9,577 lines. Make sure reverting won't break other changes that were made since then.

3. **Consider Alternatives**: Instead of a full revert, could you:
   - Cherry-pick specific files back?
   - Create a new implementation that doesn't restore all the old code?
   - Fix the underlying issue without reverting?

4. **Related Changes**: Check if there were any follow-up changes that depended on 960204 being merged. These might also need adjustment.

5. **CI/CD**: The revert will need to pass all the same CI/CD checks. Make sure:
   - Tests pass
   - Linting passes
   - No merge conflicts with current master

---

## Quick Command Summary

**For full revert using git:**
```bash
cd /home/omcgonag/Work/mymcp/workspace
git clone https://github.com/openstack/horizon horizon-revert-960204
cd horizon-revert-960204
git review -s
git log --oneline --grep="Remove all dependencies" -1
git revert <commit-sha-from-above>
git review master
```

**For Gerrit web UI:**
1. Visit https://review.opendev.org/c/openstack/horizon/+/960204
2. Click "Revert" button
3. Enter reason and submit

---

## Need Help?

If you encounter issues:
- Check Gerrit documentation: https://review.opendev.org/Documentation/
- OpenStack contributor guide: https://docs.openstack.org/contributors/
- Ask in #openstack-horizon IRC channel

