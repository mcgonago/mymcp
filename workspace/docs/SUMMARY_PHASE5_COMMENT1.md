# Phase 5, Comment 1: Remove Visual Gap in Collapsed Rows

## Summary
Implemented Radomir's CSS suggestion to eliminate unwanted spacing that appears between rows when details are collapsed.

## The Problem

When detail rows are collapsed, there's a visible gap between rows caused by default table cell padding. Even though the Bootstrap collapse div has `height: 0`, the `<td>` element still has padding, creating unwanted space.

**Visual Issue:**
```
Row 1: test1        ▶
(unwanted gap here)     ← Problem!
Row 2: test2        ▶
```

## The Solution

Move spacing from table cell **padding** (always present) to inner content **margin** (only visible when expanded).

### Two CSS Rules Added

#### 1. Remove Table Cell Padding
```css
tr.keypair-detail-row td {
  padding: 0;
}
```

**What it does:** Removes all padding from detail row table cells.
**Why:** Padding always takes up space, even when content has `height: 0`.

#### 2. Add Margin to Inner Content
```css
tr.keypair-detail-row td div.keypair-details {
  margin: 8px;
}
```

**What it does:** Adds 8px margin around the content wrapper div.
**Why:** Margin on a zero-height element doesn't create visual space, but provides proper spacing when expanded.

## How It Works

### Collapsed State
```
<td padding: 0>                    ← No padding = no gap!
  <div class="collapse" height: 0> ← Collapsed by Bootstrap
    <div margin: 8px>              ← Margin doesn't create space when height is 0
    </div>
  </div>
</td>
```

**Result:** No visual gap between rows ✅

### Expanded State
```
<td padding: 0>                    ← No padding on cell
  <div class="collapse" height: auto> ← Expanded by Bootstrap
    <div margin: 8px>              ← Margin creates 8px spacing
      Content displayed here
    </div>
  </div>
</td>
```

**Result:** Proper 8px spacing around content ✅

## Key Insight: Padding vs Margin

| Property | Location | Behavior with `height: 0` |
|----------|----------|---------------------------|
| **Padding** | Inside element | Always takes up space (creates gap) |
| **Margin** | Outside element | No visual space when element height is 0 |

This is why we:
- ❌ Remove padding from `<td>` (would create permanent gap)
- ✅ Add margin to inner `<div>` (only visible when content is shown)

## Changes Made

**File:** `openstack_dashboard/dashboards/project/templates/key_pairs/expandable_row.html`

**Lines added:** 10 (8 lines of CSS + 2 blank lines)

```diff
 .chevron-toggle:not(.collapsed) .fa-chevron-right {
   transform: rotate(90deg);
 }
+
+/* Remove padding from detail row cells to eliminate gap when collapsed */
+tr.keypair-detail-row td {
+  padding: 0;
+}
+
+/* Add margin to inner content to maintain spacing when expanded */
+tr.keypair-detail-row td div.keypair-details {
+  margin: 8px;
+}
 </style>
```

## Note: Typo Correction

Radomir's original comment had a typo:
```css
tr.keypair-detail-row tod div.keypair-details { margin: 8px };
                      ^^^
```

**Corrected to:**
```css
tr.keypair-detail-row td div.keypair-details { margin: 8px };
                      ^^
```

Changed `tod` → `td` (table data cell).

## Testing Checklist

### Visual Verification
- [ ] Load Key Pairs page
- [ ] All rows start collapsed
- [ ] **No gap between collapsed rows** ← Key test!
- [ ] Click chevron to expand
- [ ] Details have proper spacing (8px margin)
- [ ] Content doesn't touch cell edges
- [ ] Click to collapse
- [ ] Gap disappears smoothly
- [ ] Multiple rows behave consistently

### Browser Testing
- [ ] Chrome/Chromium
- [ ] Firefox
- [ ] Safari
- [ ] Edge

### DevTools Verification

**Collapsed state:**
1. Inspect `<tr class="keypair-detail-row">`
2. Check `<td>` computed padding → should be `0`
3. Measure row height → should be minimal (no gap)

**Expanded state:**
1. Inspect `<div class="keypair-details">`
2. Check computed margin → should be `8px` on all sides
3. Measure space from cell edge to content → should be 8px

## Why This Pattern Works

### Bootstrap Collapse Behavior
When Bootstrap collapses an element:
- Sets `height: 0`
- Sets `overflow: hidden`
- Content is hidden but still in DOM

### The Padding Problem
Table cells use the CSS box model:
```
┌─────────────────────┐
│ ← Padding           │  ← Always takes up space
│   ┌─────────────┐   │
│   │   Content   │   │  ← Can be height: 0
│   └─────────────┘   │
│           Padding → │  ← Always takes up space
└─────────────────────┘
```

Even with `height: 0`, padding remains visible!

### The Margin Solution
Margin is **outside** the element:
- When element has `height: 0` → margin creates no visual space
- When element is expanded → margin provides proper spacing

Perfect match for Bootstrap's collapse behavior!

## Commit Message Suggestion

```
Remove visual gap in collapsed key pair detail rows

Eliminate unwanted spacing when detail rows are collapsed by
moving spacing from table cell padding to inner content margin.

Changes:
- Remove padding from tr.keypair-detail-row td elements
- Add 8px margin to div.keypair-details inner content
- Maintains spacing when expanded, no gap when collapsed

The issue: Default table cell padding creates a visible gap even
when the Bootstrap collapse div has height: 0. The solution uses
CSS margin on the inner content div instead, since margin doesn't
create visual space when the element has zero height.

Result: Clean collapse animation with no visual gaps, proper
spacing maintained when details are expanded.

Addresses: Radomir Dopieralski's feedback on Patchset 11
Partial-Bug: #OSPRH-12803
```

## File Modified

```
openstack_dashboard/dashboards/project/templates/key_pairs/expandable_row.html
  +10 lines (8 CSS + 2 blank)
```

## Related Documentation

- **Analysis:** `mymcp/analysis/analysis_osprh_12803_fix_javascript_collapse_phase5_comment_1.org`
- **Gerrit Comment:** https://review.opendev.org/c/openstack/horizon/+/966349/comment/9cf9a894_d4bd10a0/

## Status

✅ **Implemented** - CSS changes added
⏳ **Pending** - User review and testing
📦 **Ready** - For commit to Patchset 12 (or whatever is next)

## Benefits

✅ **Better UX:** No confusing gaps in collapsed state
✅ **Clean animations:** Smooth expand/collapse transitions
✅ **Proper spacing:** Content well-spaced when expanded
✅ **Simple CSS:** Two rules, easy to understand and maintain
✅ **Works with Bootstrap:** Leverages collapse behavior correctly

---

**Next Steps:** Test the visual appearance, then commit if satisfied with the result.

