# Testing Guide for Horizon OSPRH-12803 Patchsets

## ✅ Complete Repository Extraction Complete

Each patchset directory now contains the **FULL Horizon codebase** at the state of that specific patchset. You can now run `tox` and test the code in each directory.

---

## 📁 Directory Structure

Each of these directories is now a **complete, standalone Horizon repository**:

```
horizon-osprh-12803-patch-set-1/  → Patchset 1 (commit 0725b0bee)
horizon-osprh-12803-patch-set-2/  → Patchset 2 (commit 76a7af68f)
horizon-osprh-12803-patch-set-3/  → Patchset 3 (commit 6737fdbfb)
horizon-osprh-12803-patch-set-4/  → Patchset 4 (commit 365530300)
horizon-osprh-12803-patch-set-5/  → Patchset 5 (commit 565d6d69d) ← CURRENT
```

---

## 🚀 How to Test Each Patchset

### General Testing Commands

For any patchset directory, you can run:

```bash
# Navigate to a patchset directory
cd horizon-osprh-12803-patch-set-5/

# Run all tox tests
tox

# Run specific test environments
tox -e pep8          # PEP8 linting
tox -e py312         # Python 3.12 tests
tox -e py310         # Python 3.10 tests
tox -e docs          # Documentation build
tox -e bandit        # Security checks

# Run Django-specific tests
tox -e python3-django42
tox -e python3-django52

# Run Node.js tests
tox -e nodejs20-run-lint
tox -e nodejs20-run-test

# Run integration tests
tox -e integration-pytest
tox -e ui-pytest
```

---

## 📋 Recommended Testing Workflow

### 1. Test Patchset 5 (Current/Latest)

```bash
cd /home/omcgonag/Work/mymcp/workspace/horizon-osprh-12803-patch-set-5

# Start with the tests that are currently failing
tox -e pep8
tox -e bandit

# Run full Python tests
tox -e py312

# Test Django compatibility
tox -e python3-django42
```

### 2. Compare with Earlier Patchsets

If you want to see when a test started failing:

```bash
# Test patchset 3 (before maintainer refactor)
cd /home/omcgonag/Work/mymcp/workspace/horizon-osprh-12803-patch-set-3
tox -e pep8

# Test patchset 4 (after maintainer refactor)
cd /home/omcgonag/Work/mymcp/workspace/horizon-osprh-12803-patch-set-4
tox -e pep8
```

---

## 🔍 What's Changed in Each Patchset

### Patchset 1 (0725b0bee)
- **Files Modified:** `tables.py`
- **Files Added:** `expandable_row.html` (4 lines)
- **Test this to verify:** Initial implementation works

### Patchset 2 (76a7af68f)
- **Files Modified:** `.gitignore`, `tables.py`
- **Files Added:** `expandable_row.html` (4 lines)
- **Test this to verify:** .gitignore addition doesn't break anything
- **Known Issues:** pep8 failures

### Patchset 3 (6737fdbfb)
- **Files Modified:** `.gitignore`, `tables.py`, `expandable_row.html` (32 lines)
- **Test this to verify:** Expanded template functionality
- **Known Issues:** pep8 failures

### Patchset 4 (365530300)
- **Files Modified:** `.gitignore`, `tables.py` (+16 lines), `expandable_row.html` (23 lines)
- **Test this to verify:** Maintainer refactoring improvements
- **Known Issues:** pep8, bandit failures

### Patchset 5 (565d6d69d) ← CURRENT
- **No code changes from Patchset 4** (trivial rebase)
- **Test this to verify:** Same as Patchset 4
- **Known Issues:** pep8, bandit failures

---

## 🐛 Known Test Failures (from Zuul CI)

### Patchset 5 Failures:
1. **openstack-tox-pep8** ❌ - Style/linting issues
2. **horizon-tox-bandit-baseline** ❌ - Security baseline check
3. **horizon-tox-python3-django52** ❌ - Django 5.2 compatibility (non-voting)

### Recommended Fix Order:
1. Fix PEP8 issues first (likely formatting/imports)
2. Address bandit security concerns
3. Optionally address Django 5.2 issues (non-voting, may be framework issue)

---

## 📊 Directory Contents Verification

Each directory contains:
- ✅ `tox.ini` (7.5K) - Tox configuration
- ✅ `setup.cfg` (1.9K) - Package setup
- ✅ `requirements.txt` (2.7K) - Python dependencies
- ✅ `.git/` - Full git repository
- ✅ `openstack_dashboard/` - Dashboard code
- ✅ `horizon/` - Framework code
- ✅ `manage.py` - Django management
- ✅ All other Horizon source files

---

## 🔧 Setting Up Test Environment

If you need to set up a virtual environment for testing:

```bash
cd horizon-osprh-12803-patch-set-5/

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -U pip
pip install tox

# Run tests
tox -e pep8
```

---

## 📝 Testing Specific Changes

### To test the Key Pairs de-angularization:

```bash
cd horizon-osprh-12803-patch-set-5/

# Check the modified files
cat openstack_dashboard/dashboards/project/key_pairs/tables.py

# View the new template
cat openstack_dashboard/dashboards/project/templates/key_pairs/expandable_row.html

# Run specific tests for key pairs
tox -e py312 -- openstack_dashboard.dashboards.project.key_pairs
```

---

## 🆚 Comparing Patchsets

### See exact differences between patchsets:

```bash
# Compare patchset 3 vs 4 (maintainer refactor)
diff -u horizon-osprh-12803-patch-set-3/openstack_dashboard/dashboards/project/key_pairs/tables.py \
        horizon-osprh-12803-patch-set-4/openstack_dashboard/dashboards/project/key_pairs/tables.py

# Compare templates
diff -u horizon-osprh-12803-patch-set-3/openstack_dashboard/dashboards/project/templates/key_pairs/expandable_row.html \
        horizon-osprh-12803-patch-set-4/openstack_dashboard/dashboards/project/templates/key_pairs/expandable_row.html
```

---

## 💡 Tips

1. **Start with patchset 5** - It's the current version and what needs to pass tests
2. **Fix PEP8 first** - Usually the quickest to resolve
3. **Use tox list** - Run `tox -l` to see all available test environments
4. **Parallel testing** - Run `tox -p auto` to run tests in parallel (faster)
5. **Watch mode** - Use `tox -e py312 -- --watch` for continuous testing during development

---

## 📁 File Sizes

Each complete patchset directory is approximately:
- **Size:** ~50-100 MB (includes .git history)
- **Files:** ~2000+ files (complete Horizon codebase)

---

## ✅ Ready to Test!

You can now:
1. ✅ Navigate to any patchset directory
2. ✅ Run `tox` to test that specific patchset
3. ✅ Compare test results between patchsets
4. ✅ Develop and test fixes
5. ✅ Run the full Horizon dashboard with each patchset

---

*Guide created: 2025-11-10*  
*Each directory is a complete, testable Horizon repository*



