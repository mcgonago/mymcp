# Reviews TODO

> **Note:** Reviews to be assessed when time permits.  
> **How to assess:** Use `check <review_number>` or run `fetch-review.sh --with-assessment opendev <url>`

---

## OpenDev Reviews Pending Assessment

| # | Review | Title | Created | Last Updated | URL |
|---|--------|-------|---------|--------------|-----|
| 1 | 927478 | Add SWIFT_PANEL_FULL_LISTING config option | 2024-08-29 | 2025-10-09 | https://review.opendev.org/c/openstack/horizon/+/927478 |
| 2 | 960464 | Add integration tests for region selection and switching | 2025-09-11 | 2025-10-24 | https://review.opendev.org/c/openstack/horizon/+/960464 |
| 3 | 961099 | feat(dashboard): add microversion support for Nova live migration | 2025-09-15 | 2025-10-22 | https://review.opendev.org/c/openstack/horizon/+/961099 |
| 4 | 963263 | Fix TOTP view redirection | 2025-10-07 | 2025-10-24 | https://review.opendev.org/c/openstack/horizon/+/963263 |
| 5 | 963468 | Use server filter mode for volumes and snapshots tables | 2025-10-08 | 2025-10-22 | https://review.opendev.org/c/openstack/horizon/+/963468 |
| 6 | 963576 | Force scope in all appcreds API calls | 2025-10-09 | 2025-10-13 | https://review.opendev.org/c/openstack/horizon/+/963576 |
| 7 | 964167 | [WIP] Add multi-realm federation tests | 2025-10-15 | 2025-10-15 | https://review.opendev.org/c/openstack/horizon/+/964167 |
| 8 | 964336 | Remove all references to INTEGRATION_TESTS_SUPPORT | 2025-10-17 | 2025-10-21 | https://review.opendev.org/c/openstack/horizon/+/964336 |
| 9 | 964456 | Hide enable_port_security checkbox when disallowed by policy | 2025-10-21 | 2025-10-21 | https://review.opendev.org/c/openstack/horizon/+/964456 |
| 10 | 964474 | Replace DOMNodeInserted events with a mutation observer | 2025-10-21 | 2025-10-23 | https://review.opendev.org/c/openstack/horizon/+/964474 |

---

## How to Assess a Review

### Quick Method (Using Check Command)

```bash
check 927478
```

This will:
1. Check if assessment exists
2. If not, fetch and analyze the review
3. Create `results/review_927478.md` with full assessment
4. Provide recommendation (+2/+1/0/-1)

### Manual Method (Using Script)

```bash
cd workspace
./scripts/fetch-review.sh --with-assessment opendev \
  https://review.opendev.org/c/openstack/horizon/+/927478
```

Then ask Cursor to complete the analysis:
```
Please analyze review 927478 and complete the assessment
```

### What Gets Created

Each assessment includes:
- Executive Summary with recommendation
- Code Quality Assessment
- Technical Analysis
- Review Checklist
- Testing Verification steps
- Comparison with master
- Related work and dependencies
- Questions for author
- Final decision (+2/+1/0/-1)

---

## Notes

**Source:** These reviews were migrated from `results/opendev_reviews_open/TRACKING.md` (now deleted).

**Old System vs. New:**
- ❌ Old: "Planning reviews" with complexity estimates, phases, time projections
- ✅ New: Just do the review - fetch, analyze, assess, done (5-15 minutes with AI)

---

## Priority Notes

**High Priority (Stale):**
- **927478** - Open since Aug 2024 (406 days old) - May need rebasing
- **960464** - 43 days old - Integration tests
- **961099** - 37 days old - Microversion support

**Recent (Active):**
- **964336** - 4 days old - Simple cleanup
- **964456** - 0 days old - Policy UX improvement
- **964474** - 2 days old - JavaScript modernization

**Work In Progress:**
- **964167** - Marked as WIP by author - Check if complete before reviewing

---

**Last Updated:** 2025-11-21  
**Source:** Migrated from `results/opendev_reviews_open/TRACKING.md`

