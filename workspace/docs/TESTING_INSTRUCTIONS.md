# Testing Instructions for Chevron Expand/Collapse Fix

## Quick Test (5 minutes)

### 1. Restart Horizon Development Server

If you're running Horizon in development mode:

```bash
cd /home/omcgonag/Work/mymcp/workspace/horizon-osprh-12803-working
python manage.py runserver 0.0.0.0:8000
```

Or if using Apache/production:
```bash
sudo systemctl restart apache2
# or
sudo systemctl restart httpd
```

### 2. Navigate to Key Pairs Page

1. Open your browser
2. Go to Horizon dashboard
3. Login
4. Navigate to: **Project → Compute → Key Pairs**

### 3. Test Expand/Collapse

For each key pair row:

#### Test 1: Expand First Row
- [ ] Click the chevron (►) on the first key pair
- [ ] **Expected:** Detail row expands showing:
  - Key Pair Name
  - Key Pair Type
  - Fingerprint
  - Public Key
- [ ] **Expected:** Chevron changes from ► to ▼

#### Test 2: Collapse First Row
- [ ] Click the chevron (▼) again on the first key pair
- [ ] **Expected:** Detail row collapses (hides)
- [ ] **Expected:** Chevron changes from ▼ to ►

#### Test 3: Multiple Rows Independent
- [ ] Expand the first row (click ►)
- [ ] Expand the second row (click ►)
- [ ] Expand the third row (click ►)
- [ ] **Expected:** All three detail rows are visible simultaneously
- [ ] **Expected:** All three chevrons show ▼

#### Test 4: Independent Collapse
- [ ] With multiple rows expanded, collapse just the second row
- [ ] **Expected:** Only the second row collapses
- [ ] **Expected:** First and third rows remain expanded
- [ ] **Expected:** Only second chevron changes back to ►

### 4. Check Browser Console

Open browser DevTools (F12) → Console tab

- [ ] **Expected:** No JavaScript errors
- [ ] **Expected:** No missing function warnings

### 5. Verify Unique IDs (Optional)

In browser console, run:

```javascript
// Check that all chevron IDs are unique
var ids = [];
document.querySelectorAll('.keypair-detail-row').forEach(function(el) {
    ids.push(el.id);
});
console.log('Total rows:', ids.length);
console.log('Unique IDs:', new Set(ids).size === ids.length ? 'YES ✓' : 'NO ✗');
```

**Expected output:**
```
Total rows: 3 (or however many keypairs you have)
Unique IDs: YES ✓
```

## What Success Looks Like

✅ **Before:** Only first chevron worked, rest did nothing
✅ **After:** Every chevron works independently

✅ **Before:** All rows had same ID (keypairs_table_chevron1)
✅ **After:** Each row has unique ID (keypairs_chevron_test1, keypairs_chevron_test2, etc.)

✅ **Before:** Chevron didn't rotate
✅ **After:** Chevron changes ► ↔ ▼ when clicked

## If Something Doesn't Work

### Issue: Chevrons Still Don't Expand

**Check:**
1. Clear browser cache (Ctrl+Shift+Delete)
2. Hard refresh page (Ctrl+F5 or Cmd+Shift+R)
3. Check browser console for JavaScript errors

**Debug in console:**
```javascript
// Check if function exists
typeof horizon.key_pairs.toggleDetailRow
// Should output: "function"

// If it outputs "undefined", the script didn't load
```

### Issue: Multiple Rows Expand When Clicking One

**This means:** IDs are not unique

**Check in console:**
```javascript
// Find duplicate IDs
var ids = [];
document.querySelectorAll('.keypair-detail-row').forEach(function(el) {
    ids.push(el.id);
});
var duplicates = ids.filter((item, index) => ids.indexOf(item) !== index);
console.log('Duplicate IDs:', duplicates);
```

**If duplicates found:** The `get_object_id()` fix didn't apply

### Issue: JavaScript Error About jQuery

**Error:** `$ is not defined`

**Fix:** jQuery isn't loaded. Check that Horizon's base template includes jQuery.

## After Successful Testing

If all tests pass:

```bash
cd /home/omcgonag/Work/mymcp/workspace/horizon-osprh-12803-working

# Commit the changes
git commit -m "Fix chevron expand/collapse functionality and unique IDs

Bootstrap's collapse class doesn't work with table rows, causing the
chevron click to have no effect. This fix implements a custom JavaScript
solution using jQuery show/hide which properly handles table row display.

Additionally fixes the unique chevron_id generation issue where all rows
received the same ID, preventing proper row identification.

Changes:
- Use get_object_id(datum) for unique chevron IDs per row
- Remove Bootstrap collapse class (doesn't work with <tr>)
- Add custom JavaScript toggle function using jQuery show/hide
- Replace data-toggle='collapse' with onclick handler
- Add style='display: none;' for initial hidden state
- Rotate chevron icon on toggle (fa-chevron-right ↔ fa-chevron-down)
- Update aria-expanded attribute for accessibility

Fixes: All chevron expand/collapse functionality now works correctly
for every key pair row independently.

Change-Id: Id5e0a7a75fb42499b605e91f9b6ddfea9b7a002e
Signed-off-by: Owen McGonagle <omcgonag@redhat.com>
"

# Submit to Gerrit
git review
```

## Screenshot Checklist

For documentation, capture screenshots showing:

1. [ ] Initial state - all rows collapsed, all chevrons show ►
2. [ ] First row expanded - details visible, chevron shows ▼
3. [ ] Multiple rows expanded simultaneously
4. [ ] Browser console showing no errors

---

*Test created: 2025-11-10*


