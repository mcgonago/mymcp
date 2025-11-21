# Fix: Chevron Collapse/Expand Functionality

## Problem

The chevron icon appeared in the correct location, but clicking it did not expand/collapse the detail row.

## Root Cause

**Bootstrap's `.collapse` class doesn't work properly with `<tr>` (table row) elements.**

Bootstrap's collapse component is designed for block-level elements like `<div>`, not for table rows. The CSS transitions and display toggling don't work correctly on `<tr>` elements.

### Why Bootstrap Collapse Failed

1. **Bootstrap expects `<div>` elements**
   - The `.collapse` class uses `display: none` and `display: block`
   - Table rows need `display: table-row`, not `display: block`
   - Bootstrap's JavaScript doesn't handle this correctly

2. **data-toggle="collapse" relies on Bootstrap's JS**
   - Bootstrap's collapse module looks for `[data-toggle="collapse"]`
   - It tries to apply `.collapse()` jQuery plugin
   - The plugin doesn't work well with `<tr>` elements

## Solution Implemented

### 1. Remove Bootstrap's `collapse` Class

**Before:**
```html
<tr class="keypair-detail-row collapse" id="{{ chevron_id }}">
```

**After:**
```html
<tr class="keypair-detail-row" id="{{ chevron_id }}" style="display: none;">
```

**Changes:**
- Removed `collapse` class
- Added `style="display: none;"` to hide rows initially
- This uses standard CSS display property that works with table rows

### 2. Replace `data-toggle="collapse"` with Custom JavaScript

**Before (in _chevron_column.html):**
```html
<a role="button"
   class="chevron-toggle"
   data-toggle="collapse"
   href="#{{ chevron_id }}"
   ...>
```

**After:**
```html
<a role="button"
   class="chevron-toggle"
   href="#"
   onclick="return horizon.key_pairs.toggleDetailRow(this, '{{ chevron_id }}');"
   ...>
```

**Changes:**
- Removed `data-toggle="collapse"` (Bootstrap's hook)
- Changed href from `#{{ chevron_id }}` to just `#`
- Added `onclick` handler that calls our custom JavaScript function

### 3. Added Custom JavaScript Toggle Function

**In expandable_row.html template:**
```javascript
horizon.key_pairs = {
  toggleDetailRow: function(chevron, targetId) {
    var $chevron = $(chevron);
    var $icon = $chevron.find('.fa');
    var $targetRow = $('#' + targetId);
    
    if ($targetRow.is(':visible')) {
      // Hide the row
      $targetRow.hide();
      $icon.removeClass('fa-chevron-down').addClass('fa-chevron-right');
      $chevron.attr('aria-expanded', 'false');
    } else {
      // Show the row
      $targetRow.show();
      $icon.removeClass('fa-chevron-right').addClass('fa-chevron-down');
      $chevron.attr('aria-expanded', 'true');
    }
    return false;
  }
};
```

**What this does:**
- ✅ Toggles `display: none` ↔ `display: table-row` (jQuery `.hide()/.show()` handles this)
- ✅ Rotates chevron icon: `fa-chevron-right` (►) ↔ `fa-chevron-down` (▼)
- ✅ Updates `aria-expanded` attribute for accessibility
- ✅ Returns `false` to prevent default link behavior

### 4. Wrapped Content in `<div>` for Better Structure

**Added wrapper div in expandable_row.html:**
```html
<tr class="keypair-detail-row" id="{{ chevron_id }}" style="display: none;">
  <td colspan="{{ row.cells|length }}">
    <div class="keypair-details">  <!-- NEW WRAPPER -->
      <dl class="dl-horizontal">
        ...
      </dl>
    </div>
  </td>
</tr>
```

**Benefits:**
- Better semantic structure
- Allows for easier CSS styling
- Provides clean container for detail content

## Files Modified

### 1. tables.py
- Fixed unique chevron ID generation (from previous commit)
- Uses `get_object_id(datum)` for per-row uniqueness

### 2. _chevron_column.html
- Changed from Bootstrap's `data-toggle="collapse"` to custom `onclick` handler
- Calls `horizon.key_pairs.toggleDetailRow()` function

### 3. expandable_row.html
- Removed `collapse` class from `<tr>`
- Added `style="display: none;"` for initial hidden state
- Wrapped content in `<div class="keypair-details">`
- Added inline JavaScript to define `horizon.key_pairs.toggleDetailRow()` function

## How It Works Now

### User Clicks Chevron

```
1. User clicks chevron (►)
   ↓
2. onclick="return horizon.key_pairs.toggleDetailRow(this, 'keypairs_chevron_test1')"
   ↓
3. JavaScript function executes:
   - Finds target row: $('#keypairs_chevron_test1')
   - Checks if visible: $targetRow.is(':visible')
   - Since hidden: $targetRow.show()
   - Changes icon: fa-chevron-right → fa-chevron-down
   - Updates aria: aria-expanded="false" → aria-expanded="true"
   ↓
4. Row becomes visible with display: table-row
   ↓
5. User sees expanded details
```

### User Clicks Again

```
1. User clicks chevron again (▼)
   ↓
2. Same onclick handler
   ↓
3. JavaScript executes:
   - Row is now visible
   - $targetRow.hide()
   - fa-chevron-down → fa-chevron-right
   - aria-expanded="true" → aria-expanded="false"
   ↓
4. Row hidden again with display: none
```

## Why This Solution Works

### 1. Direct DOM Manipulation
- Uses jQuery `.show()` and `.hide()` which correctly handle table rows
- jQuery knows to use `display: table-row` for `<tr>` elements
- No reliance on Bootstrap's problematic collapse behavior

### 2. Simple and Reliable
- No complex CSS transitions that might break with table rows
- Direct JavaScript control over visibility
- Works in all browsers that support jQuery (which Horizon requires)

### 3. Accessible
- Still maintains `aria-expanded` attribute
- Screen readers can track expanded/collapsed state
- Keyboard accessible (can be triggered via Enter key)

### 4. Visual Feedback
- Chevron rotates: ► (collapsed) ↔ ▼ (expanded)
- Clear visual indicator of current state
- Consistent with UI conventions

## Alternative Approaches Considered

### Alternative 1: Use Bootstrap 5 Syntax
```html
<a data-bs-toggle="collapse" ...>
```
**Rejected:** Still doesn't work with table rows

### Alternative 2: Nest `<div>` with collapse Inside `<tr>`
```html
<tr>
  <td>
    <div class="collapse" id="...">
      content
    </div>
  </td>
</tr>
```
**Rejected:** Creates layout issues, row always visible even when "collapsed"

### Alternative 3: External JavaScript File
```javascript
// In key_pairs.js
horizon.key_pairs.toggleDetailRow = function() { ... }
```
**Rejected:** Requires registering the file with Horizon's asset pipeline; inline is simpler

### Alternative 4: Pure CSS Solution
```css
.keypair-detail-row { display: none; }
.expanded + .keypair-detail-row { display: table-row; }
```
**Rejected:** Can't add `.expanded` class to previous sibling with CSS; needs JavaScript anyway

## Testing

### Manual Testing Steps

1. **Navigate to Key Pairs page**
   ```
   Project → Compute → Key Pairs
   ```

2. **Verify initial state**
   - ✓ Detail rows should be hidden
   - ✓ All chevrons show ►

3. **Click first chevron**
   - ✓ First detail row should expand
   - ✓ Chevron changes to ▼
   - ✓ Details visible (name, type, fingerprint, public key)

4. **Click first chevron again**
   - ✓ First detail row should collapse
   - ✓ Chevron changes back to ►
   - ✓ Details hidden

5. **Click multiple chevrons**
   - ✓ Each chevron independently controls its own row
   - ✓ Multiple rows can be expanded simultaneously
   - ✓ Expanding one row doesn't affect others

6. **Check browser console**
   - ✓ No JavaScript errors
   - ✓ No missing function warnings

### Browser Console Test

```javascript
// Verify function is defined
console.log(typeof horizon.key_pairs.toggleDetailRow);
// Should output: "function"

// Manually trigger toggle
horizon.key_pairs.toggleDetailRow(
  document.querySelector('.chevron-toggle'),
  'keypairs_chevron_test1'
);
// Should toggle the first row
```

### HTML Validation

```javascript
// Check IDs are unique
var ids = [];
document.querySelectorAll('[id^="keypairs_chevron"]').forEach(function(el) {
  ids.push(el.id);
});
console.log('Unique IDs:', new Set(ids).size === ids.length);
// Should output: true
```

## Performance Considerations

### Script Inclusion
The JavaScript is included inline in the template because:
- ✅ It's small (~20 lines)
- ✅ Only loads when Key Pairs page is rendered
- ✅ No additional HTTP request needed
- ✅ Immediately available when page loads

### Memory Footprint
- Single function definition regardless of number of rows
- No event listeners attached per row (uses onclick attribute)
- Minimal DOM queries (direct ID lookup)

### Browser Compatibility
- Works with jQuery (already required by Horizon)
- No ES6 syntax (compatible with older browsers)
- No external dependencies beyond jQuery

## Future Improvements

### 1. Add Transition Animation

```javascript
// Instead of immediate show/hide
$targetRow.slideToggle(200);  // 200ms slide animation
```

### 2. Remember Expanded State

```javascript
// Store in sessionStorage
sessionStorage.setItem('expanded_' + targetId, 'true');

// Restore on page load
if (sessionStorage.getItem('expanded_' + targetId) === 'true') {
  $targetRow.show();
  // ... update chevron ...
}
```

### 3. Collapse All Others Option

```javascript
// When expanding one, collapse all others
$('.keypair-detail-row').not($targetRow).hide();
$('.chevron-toggle').not($chevron).find('.fa')
  .removeClass('fa-chevron-down').addClass('fa-chevron-right');
```

### 4. Keyboard Navigation

```javascript
// Add keyboard handler
$chevron.on('keypress', function(e) {
  if (e.which === 13 || e.which === 32) {  // Enter or Space
    horizon.key_pairs.toggleDetailRow(this, targetId);
    e.preventDefault();
  }
});
```

## Summary

**Problem:** Bootstrap's collapse doesn't work with table rows
**Solution:** Custom JavaScript using jQuery's `.show()` and `.hide()`
**Result:** ✅ All chevrons now expand/collapse their respective rows independently

### Changes Summary

| File | Change | Reason |
|------|--------|--------|
| tables.py | Use `get_object_id(datum)` | Generate unique IDs per row |
| _chevron_column.html | Replace `data-toggle` with `onclick` | Use custom JS instead of Bootstrap |
| expandable_row.html | Add inline JavaScript | Define toggle function |
| expandable_row.html | Remove `collapse` class | Doesn't work with `<tr>` |
| expandable_row.html | Add `style="display: none;"` | Hide rows initially |
| expandable_row.html | Wrap in `<div>` | Better structure |

---

*Fix implemented: 2025-11-10*
*Status: ✅ Ready for testing and commit*


