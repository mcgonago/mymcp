# Debug Guide: Chevron Collapse Not Working

## Issue
The chevron icon appears in the correct location, but clicking it does not expand/collapse the detail row.

## Debugging Steps

### 1. Verify HTML Structure in Browser

Open the Key Pairs page and view the page source (Right-click → Inspect Element).

Look for the generated HTML structure. It should look like:

```html
<!-- Main data row -->
<tr>
  <td>
    <a role="button"
       class="chevron-toggle"
       data-toggle="collapse"
       href="#keypairs_chevron_test1"
       aria-expanded="false"
       aria-controls="keypairs_chevron_test1">
      <span class="fa fa-chevron-right"></span>
    </a>
  </td>
  <td>test1</td>
  <td>ssh</td>
  ...
</tr>

<!-- Detail row (should start hidden) -->
<tr class="keypair-detail-row collapse" id="keypairs_chevron_test1">
  <td colspan="5">
    <dl>
      <dt>Key Pair Name</dt>
      <dd>test1</dd>
      ...
    </dl>
  </td>
</tr>
```

**Check:**
- ✓ Does the `<a>` tag have `href="#keypairs_chevron_test1"`?
- ✓ Does the `<tr>` tag have `id="keypairs_chevron_test1"`?
- ✓ Do the IDs match exactly (including the keypair name)?
- ✓ Does the detail row have class `collapse`?
- ✓ Does the link have `data-toggle="collapse"`?

### 2. Check Browser Console for Errors

Open browser DevTools (F12) and check the Console tab for JavaScript errors.

Common errors:
- `Bootstrap is not defined`
- `$ is not defined`
- `Uncaught TypeError: ... .collapse is not a function`

### 3. Verify Bootstrap Version

Horizon might use different Bootstrap versions. Check which version:

**In browser console, run:**
```javascript
// Check Bootstrap version
if (typeof $.fn.collapse !== 'undefined') {
    console.log('Bootstrap collapse is loaded');
    console.log('Bootstrap version:', $.fn.tooltip.Constructor.VERSION);
} else {
    console.log('Bootstrap collapse NOT loaded!');
}
```

### 4. Check if data-toggle Works

**In browser console, run:**
```javascript
// Try to manually trigger collapse
$('#keypairs_chevron_test1').collapse('toggle');
```

If this works, Bootstrap is loaded but the click handler isn't attached.

### 5. Test with Browser DevTools

**In Elements tab:**
1. Find the chevron `<a>` element
2. Manually add/remove the `collapse` class on the detail `<tr>`
3. If manually changing the class shows/hides the row, Bootstrap CSS is working but JS isn't

---

## Possible Issues and Solutions

### Issue 1: Bootstrap Version Mismatch

**Symptom:** `data-toggle="collapse"` doesn't work
**Cause:** Bootstrap 5 uses `data-bs-toggle="collapse"` instead

**Solution:** Check Bootstrap version and update template accordingly

### Issue 2: Table Rows Can't Use collapse Class

**Symptom:** The `collapse` class doesn't hide table rows properly
**Cause:** Bootstrap's collapse is designed for `<div>` elements, not `<tr>` elements

**Solution:** Wrap the detail content in a `<div>` or use custom CSS

### Issue 3: Missing Bootstrap JavaScript

**Symptom:** Nothing happens when clicking
**Cause:** Bootstrap's JavaScript isn't loaded

**Solution:** Verify Bootstrap JS is included in the page

### Issue 4: IDs Don't Match at Runtime

**Symptom:** Wrong row expands or nothing happens
**Cause:** The ID generation differs between column and row

**Solution:** Verify both use the same ID generation method

---

## Common Fix: Table Rows and Bootstrap Collapse

Bootstrap's collapse works best with `<div>` elements, not `<tr>` elements. 

### Current Structure (May Not Work)
```html
<tr class="collapse" id="...">
  <td>content</td>
</tr>
```

### Better Structure
```html
<tr id="..." style="display: none;">
  <td>
    <div class="collapse">
      content
    </div>
  </td>
</tr>
```

Or use `display: none` initially and toggle with JavaScript.

---

## Manual Testing Commands

Run these in the browser console when on the Key Pairs page:

```javascript
// 1. Check if jQuery is loaded
console.log('jQuery version:', $.fn.jquery);

// 2. Check if Bootstrap collapse is available
console.log('Collapse available:', typeof $.fn.collapse !== 'undefined');

// 3. Find all chevron links
var chevrons = document.querySelectorAll('.chevron-toggle');
console.log('Chevron links found:', chevrons.length);

// 4. Check first chevron's href
if (chevrons.length > 0) {
    console.log('First chevron href:', chevrons[0].getAttribute('href'));
}

// 5. Find all detail rows
var details = document.querySelectorAll('.keypair-detail-row');
console.log('Detail rows found:', details.length);

// 6. Check first detail row's id
if (details.length > 0) {
    console.log('First detail row id:', details[0].getAttribute('id'));
}

// 7. Check if IDs match
if (chevrons.length > 0 && details.length > 0) {
    var href = chevrons[0].getAttribute('href');
    var id = details[0].getAttribute('id');
    console.log('IDs match:', href === '#' + id);
}

// 8. Try manual collapse toggle
if (details.length > 0) {
    $('#' + details[0].id).collapse('toggle');
}
```

---

## Next Steps

Based on your findings from the debugging steps above, we can implement the appropriate fix.

Most likely issues:
1. **Bootstrap collapse doesn't work well with `<tr>` elements** - Need to restructure
2. **Bootstrap version mismatch** - Need to update `data-toggle` attribute
3. **JavaScript not firing** - Need to manually initialize collapse or add click handler

Please run the debugging steps and report back what you find!


