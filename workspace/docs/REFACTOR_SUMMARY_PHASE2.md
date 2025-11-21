# Bootstrap Native Collapse Refactoring - Phase 2

## Summary
Refactored expand/collapse functionality to use Bootstrap 3.4's native collapse component instead of custom JavaScript, as suggested by Radomir.

## Changes Made

### 1. `_chevron_column.html`
**Removed:**
- `href="#"` attribute
- `onclick="return horizon.key_pairs.toggleDetailRow(this, '{{ chevron_id }}');"` custom handler

**Added:**
- `data-toggle="collapse"` - enables Bootstrap's collapse functionality
- `data-target="#{{ chevron_id }}"` - specifies the target element to collapse

### 2. `expandable_row.html`
**Removed:**
- `id="{{ chevron_id }}"` from `<tr>` element
- `style="display: none;"` from `<tr>` element
- Entire `<script>` block (~30 lines of custom JavaScript)

**Added:**
- New wrapper `<div id="{{ chevron_id }}" class="collapse">` inside the `<td>`
- This div wraps the existing `.keypair-details` content

**Key Insight:**
Bootstrap's collapse doesn't work directly on `<tr>` elements due to CSS transition limitations with table rows. The solution is to collapse a `<div>` inside the `<td>` instead.

## How It Works

1. **Clicking the chevron:**
   - Bootstrap detects `data-toggle="collapse"` and `data-target="#{{ chevron_id }}"`
   - Toggles the `.collapse` class on the target div
   - Adds/removes `.in` class for visibility
   - Automatically updates `aria-expanded` attribute

2. **The collapsible content:**
   - Starts collapsed (no `.in` class)
   - Bootstrap animates height transitions with CSS
   - Content smoothly expands/collapses

3. **What Bootstrap handles automatically:**
   - Show/hide logic
   - CSS transitions
   - ARIA attribute updates (`aria-expanded`)
   - Event management
   - Keyboard accessibility

## Benefits

1. **Cleaner Code:** Removed ~30 lines of custom JavaScript
2. **Standards Compliance:** Uses Bootstrap's documented approach
3. **Better Maintainability:** Standard pattern that all developers understand
4. **Improved Reliability:** Leverage Bootstrap's extensively tested code
5. **Better Accessibility:** Bootstrap's built-in ARIA support
6. **Better Performance:** CSS transitions are GPU-accelerated

## Testing Checklist

Please verify:
- [ ] Chevron expands row when clicked
- [ ] Chevron collapses row when clicked again
- [ ] Each row's chevron controls only its own detail row
- [ ] Multiple rows can be expanded simultaneously
- [ ] `aria-expanded` attribute updates correctly
- [ ] Smooth CSS transitions
- [ ] No JavaScript console errors
- [ ] Keyboard navigation works (Tab to chevron, Enter/Space to toggle)

## Known Issue: Chevron Icon Rotation

Bootstrap does **not** automatically rotate the chevron icon. Currently, the icon stays as `fa-chevron-right` in both states.

### Solutions (choose one):

#### Option A: CSS-Only (Recommended)
Add to appropriate stylesheet:
```css
.chevron-toggle[aria-expanded="true"] .fa-chevron-right {
    transform: rotate(90deg);
    transition: transform 0.3s ease;
}

.chevron-toggle .fa-chevron-right {
    transition: transform 0.3s ease;
}
```

#### Option B: Minimal JavaScript
If CSS approach is not feasible:
```javascript
$(document).on('click', '.chevron-toggle', function() {
    $(this).find('.fa').toggleClass('fa-chevron-right fa-chevron-down');
});
```

## Files Modified
```
openstack_dashboard/dashboards/project/templates/key_pairs/_chevron_column.html
openstack_dashboard/dashboards/project/templates/key_pairs/expandable_row.html
```

## Related Analysis
See: `analysis/analysis_osprh_12803_fix_javascript_collapse_phase2.org`

## Commit Message Suggestion
```
Use Bootstrap's native collapse for key pair details

Replace custom JavaScript with Bootstrap's built-in collapse component
for expanding/collapsing key pair detail rows. This approach:

- Removes ~30 lines of custom JavaScript
- Uses Bootstrap's data-toggle and data-target attributes
- Improves maintainability by following Bootstrap conventions
- Enhances accessibility with automatic ARIA management
- Provides smoother transitions with CSS animations

The key insight is collapsing a div inside the table cell rather
than the table row itself, as Bootstrap's collapse works best with
block-level elements that support height transitions.

Addresses: Radomir's feedback on Patchset 7
Related: https://getbootstrap.com/docs/3.4/javascript/#collapse

Partial-Bug: #OSPRH-12803
```

## References
- Radomir's Comment: https://review.opendev.org/c/openstack/horizon/+/966349/7
- Bootstrap 3.4 Collapse: https://getbootstrap.com/docs/3.4/javascript/#collapse

