# Work Contexts Guide

This repository supports multiple work contexts for different security levels and purposes.

## Quick Reference

| Context | Location | Git Tracked? | Use For |
|---------|----------|--------------|---------|
| **default** | `results/`, `analysis/` | ✅ Yes | Public/upstream work, OpenDev reviews |
| **customer** | `customer-work/` | ❌ No | Customer SEs, confidential data |
| **rh-internal** | `rh-internal/` | ❌ No | RH internal bugs, RH-only docs |

---

## Usage

### Default Context (Public/Git-Tracked)

**For:** OpenDev reviews, public bug reports, upstream contributions

**How to use:**
```
"Analyze review 967773"
"Analyze review 967773" → saves to results/review_967773.md
```

**Files are:**
- ✅ Git tracked
- ✅ Can be committed
- ✅ Can be pushed to GitHub
- ✅ Public/visible

### With fetch-review.sh Script

The `fetch-review.sh` script supports automatic context selection:

```bash
# Default: Public/upstream work (git-tracked)
cd workspace
./scripts/fetch-review.sh --with-assessment opendev \
  https://review.opendev.org/c/openstack/horizon/+/967773
# → Creates results/review_967773.md (git-tracked)

# Customer: Confidential work (gitignored)
./scripts/fetch-review.sh --with-assessment --context customer opendev \
  https://review.opendev.org/c/openstack/horizon/+/967773
# → Creates customer-work/results/review_967773.md (never pushed)

# RH Internal: Internal-only work (gitignored)
./scripts/fetch-review.sh --with-assessment --context rh-internal opendev \
  https://review.opendev.org/c/openstack/horizon/+/967773
# → Creates rh-internal/results/review_967773.md (not in public repo)
```

See `workspace/scripts/README.md` for full `fetch-review.sh` documentation.

---

### Customer Context (Confidential)

**For:** Support Exceptions, customer bugs, account-specific data

**How to use:**
```
"Analyze SUPPORTEX-28104, customer context"
"Analyze SUPPORTEX-28104, save to customer-work/results/"
→ saves to customer-work/results/supportex-28104.md
```

**Auto-detection keywords:**
- "customer", "confidential", "SE", "account", "Verisign", etc.

**Files are:**
- ❌ NOT git tracked
- ❌ Never pushed to public GitHub
- ✅ Can be shared with customers via email
- ✅ Can be uploaded to support cases

**Location:** `customer-work/` → `/home/omcgonag/Work/customer-confidential/`

---

### RH Internal Context

**For:** Internal bugs, pre-release analysis, RH-only documentation

**How to use:**
```
"Analyze BZ#12345, rh-internal context"
"Save to rh-internal/analysis/"
→ saves to rh-internal/analysis/bug-12345.md
```

**Auto-detection keywords:**
- "internal", "rh-only", "bugzilla", "BZ#", etc.

**Files are:**
- ❌ NOT in public GitHub
- ✅ Can be pushed to internal RH GitLab
- ✅ Can be shared with RH colleagues
- ⚠️ May be appropriate for upstream (case by case)

**Location:** `rh-internal/` → `/home/omcgonag/Work/rh-internal/`

---

## Directory Structure

```
<mymcp-repo-path>/
├── .mymcp-config            # Your personal config (gitignored)
├── .mymcp-config.template   # Config structure (committed)
├── customer-work/ → /home/.../customer-confidential/  (gitignored)
│   ├── results/
│   ├── analysis/
│   └── workspace/
├── rh-internal/ → /home/.../rh-internal/              (gitignored)
│   ├── results/
│   ├── analysis/
│   └── workspace/
├── results/                 # Public assessments (git-tracked)
├── analysis/                # Public research (git-tracked)
└── workspace/
    └── external/
        └── cursor/          # Reference code repos
```

---

## Examples

### Example 1: Public OpenDev Review

```
You: "Analyze review 967773"

Cursor:
  → Fetches from OpenDev
  → Saves to results/review_967773.md
  → Git tracked, can be committed
```

### Example 2: Customer Support Exception

```
You: "Analyze SUPPORTEX-28104, customer context.
      Use workspace/external/cursor/horizon for reference."

Cursor:
  → Reads Jira SUPPORTEX-28104
  → Searches workspace/external/cursor/horizon/
  → Saves to customer-work/results/supportex-28104.md
  → NOT in git, never pushed
  → Can share with customer directly
```

### Example 3: Internal Bug Investigation

```
You: "Analyze BZ#2123456, rh-internal context"

Cursor:
  → Analyzes internal bug
  → Saves to rh-internal/analysis/bz-2123456.md
  → NOT in public GitHub
  → Can push to internal GitLab
```

---

## Security

### What's NEVER Pushed to Public GitHub

- ❌ `customer-work/*` - Customer confidential
- ❌ `rh-internal/*` - RH internal only
- ❌ `.mymcp-config` - Your personal paths

### What IS Pushed to GitHub

- ✅ `.mymcp-config.template` - Structure example
- ✅ `results/*` - Public assessments
- ✅ `analysis/*` - Public research
- ✅ `workspace/scripts/` - Tools
- ✅ `.gitignore` - Ignore rules

---

## Configuration

Edit `.mymcp-config` to customize paths:

```ini
[default]
results=results/
analysis=analysis/

[customer]
results=customer-work/results/
analysis=customer-work/analysis/

[rh-internal]
results=rh-internal/results/
analysis=rh-internal/analysis/
```

See `.mymcp-config.template` for full documentation.

---

## Verifying Gitignore

```bash
# Check what's ignored
git status

# customer-work/ and rh-internal/ should NOT appear
# Only public files should be listed

# Verify specific file is ignored
git check-ignore customer-work/results/supportex-28104.md
# Should output: customer-work/results/supportex-28104.md
```

---

**Last Updated:** 2025-11-21  
**See Also:** `.mymcp-config.template`, `results/README.md`

