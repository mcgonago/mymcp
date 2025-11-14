# Spike: Key Pairs Expandable Rows Feature - Initial Investigation

**Feature**: Add expandable row details to Key Pairs table  
**Review**: [https://review.opendev.org/c/openstack/horizon/+/966349](https://review.opendev.org/c/openstack/horizon/+/966349)  
**JIRA**: OSPRH-12803  
**Investigation Period**: November 6-7, 2025  
**Status**: Investigation Complete - Ready for Implementation

---

## Executive Summary

This spike documents our initial investigation into adding expandable row functionality to the Horizon Key Pairs table. The goal was to understand:

1. How Horizon's table rendering system works
2. What approach to take for expandable rows
3. How to add chevron icons for visual indication
4. What the implementation complexity would be

**Key Finding**: We can implement this feature with ~110 lines of code across 4 files using Django templates, jQuery, and CSS - a manageable scope.

---

## Development Environment Setup

Before diving into the investigation, we needed a proper development environment to test and iterate on changes.

### Environment Options

We documented two approaches for running Horizon development:

1. **DevStack on PSI (Cloud Infrastructure)**
   - Remote development on Red Hat's PSI cloud
   - See: [`HOWTO_install_devstack_on_psi.org`](HOWTO_install_devstack_on_psi.org)
   - Best for: Stable, always-on environment

2. **DevStack on Laptop (Virtual Machine)**
   - Local VM using virt-manager on Ubuntu 22.04
   - See: [`HOWTO_install_devstack_on_laptop.org`](HOWTO_install_devstack_on_laptop.org)
   - Best for: Offline development, faster iteration

Both environments provide full OpenStack deployments with Horizon UI for testing table modifications.

---

## Initial Understanding: What We Thought We Needed

Going into this work, we knew we wanted to achieve "feature parity with the AngularJS version" of the Key Pairs table. The AngularJS implementation had:

- Summary rows showing basic key pair info (name, type, fingerprint)
- Expandable detail rows showing full information (including public key)
- Chevron icons indicating expandable state
- Smooth animations when expanding/collapsing

**Initial Questions**:
1. How does Horizon render table rows?
2. Can we customize row rendering without breaking the table?
3. Where do we add the chevron icons?
4. How do we implement show/hide functionality?

---

## Investigation Phase 1: Understanding Horizon's Template System

### Discovery: Template Inlining Strategy

**File Analyzed**: `horizon/templates/horizon/common/_data_table_cell.html`

We discovered that Horizon's standard cell template is **42 lines** with three rendering modes:

1. **Mode 1**: Active inline edit (21 lines) - edit forms, submit/cancel buttons
2. **Mode 2**: Inline edit available (11 lines) - edit button with pencil icon  
3. **Mode 3**: Simple display (3 lines) - just the cell value

**Key Insight**: Key Pairs table doesn't need inline editing, so we only need Mode 3 (3 lines).

**Decision**: Inline the simple cell rendering code rather than using `{% include %}`:

```django
<td{{ cell.attr_string|safe }}>
    {% if cell.wrap_list %}<ul>{% endif %}{{ cell.value }}{% if cell.wrap_list %}</ul>{% endif %}
</td>
```

**Reasoning**:
- ✅ Performance: Eliminates template resolution overhead
- ✅ Clarity: Makes rendering logic explicit and self-contained
- ✅ Simplicity: 3 lines instead of 42
- ✅ Best Practice: Django recommends inlining simple, single-use code

### Standard Row Template Analysis

**File**: `horizon/templates/horizon/common/_data_table_row.html`

Standard structure:
```django
<tr{{ row.attr_string|safe }}>
    {% spaceless %}
        {% for cell in row %}
            {% include "horizon/common/_data_table_cell.html" %}
        {% endfor %}
    {% endspaceless %}
</tr>
```

**Our custom approach**: Inline both the row structure AND the simplified cell rendering in one template.

---

## Investigation Phase 2: Hide/Show Functionality

### Requirement

Show detail rows hidden by default with ability to toggle visibility on demand.

**Desired Behavior**:

Initial state (all collapsed):
```
┌────────────────────────────────────────────────┐
│ test1    │ ssh  │ 83:9d:ce:... │ Delete      │
│ mykey    │ ssh  │ aa:bb:cc:... │ Delete      │
└────────────────────────────────────────────────┘
```

After clicking test1:
```
┌────────────────────────────────────────────────┐
│ test1    │ ssh  │ 83:9d:ce:... │ Delete      │
├────────────────────────────────────────────────┤
│ Key Pair Name    test1                         │
│ Key Pair Type    ssh                           │
│ Fingerprint      83:9d:ce:a7...                │
│ Public Key       ssh-rsa AAAAB3...             │
├────────────────────────────────────────────────┤
│ mykey    │ ssh  │ aa:bb:cc:... │ Delete      │
└────────────────────────────────────────────────┘
```

### Options Evaluated

#### Option 1: CSS-Only Hover
- **How**: Show detail on mouse hover using `:hover` selector
- **Pros**: No JavaScript, simple
- **Cons**: ❌ Mobile unfriendly, accidental triggers, not discoverable
- **Verdict**: ❌ Not suitable for production

#### Option 2: CSS-Only Checkbox
- **How**: Hidden checkbox + label, uses `:checked` selector
- **Pros**: No JavaScript, works on mobile
- **Cons**: ❌ Complex HTML, adds extra column, breaks table structure
- **Verdict**: ❌ Overly complex

#### Option 3: JavaScript Click Toggle ⭐ **SELECTED**
- **How**: Click anywhere on summary row to toggle detail visibility
- **Pros**: 
  - ✅ Simple (~15 lines of JavaScript)
  - ✅ Mobile friendly
  - ✅ Standard UX pattern
  - ✅ Preserves table structure
  - ✅ Flexible for future enhancements
- **Cons**: Requires JavaScript (acceptable trade-off)
- **Verdict**: ✅ **Best balance of simplicity and functionality**

### Implementation Approach

**Template Changes**:
```django
{# Summary row - add data attribute for targeting #}
<tr{{ row.attr_string|safe }} 
    class="keypair-summary-row" 
    data-keypair-id="{{ row.datum.name|escapejs }}"
    style="cursor: pointer;">
    {# ... cells ... #}
</tr>

{# Detail row - hidden by default #}
<tr class="keypair-detail-row" 
    data-keypair-id="{{ row.datum.name|escapejs }}"
    style="display: none;">
    {# ... detail content ... #}
</tr>
```

**JavaScript Logic** (simplified):
```javascript
$(document).on('click', '.keypair-summary-row', function(e) {
    if ($(e.target).is('a, button, input, select')) {
        return;  // Don't toggle if clicking interactive elements
    }
    
    var keypairId = $(this).data('keypair-id');
    var detailRow = $('.keypair-detail-row[data-keypair-id="' + keypairId + '"]');
    
    if (detailRow.is(':visible')) {
        detailRow.hide();
    } else {
        detailRow.show();
    }
});
```

---

## Investigation Phase 3: Adding Chevron Icons

### Why Chevrons Matter

Without a visual indicator, users won't know rows are expandable. Chevrons provide:
- Discoverable UI (users see the ▸ icon)
- State indication (▸ = collapsed, ▾ = expanded)
- Standard UX pattern (familiar to users)

### Options Evaluated

#### Option 1: Add Chevron Column (Like Angular)
- **How**: Add new `<td class="expander">` column with chevron
- **Pros**: Matches Angular structure, clean separation
- **Cons**: ❌ Requires table header modification, ~150+ lines of code
- **Verdict**: ❌ Too complex

#### Option 2: CSS ::before Pseudo-Element
- **How**: Use CSS to add chevron before first cell content
- **Pros**: No HTML changes needed
- **Cons**: ❌ Hard to position, can't use Font Awesome easily
- **Verdict**: ⚠️ Works but not ideal

#### Option 3: Inject Chevron with JavaScript
- **How**: Add chevron HTML element via JavaScript after page load
- **Pros**: Simple, flexible, uses Font Awesome
- **Cons**: ⚠️ Brief moment before chevron appears
- **Verdict**: ✅ Good approach

#### Option 4: Add Chevron in Template (Hybrid) ⭐ **SELECTED**
- **How**: Modify template to add chevron in first cell
- **Pros**:
  - ✅ Chevron immediately visible (no FOUC)
  - ✅ Simple template change (just one line)
  - ✅ Semantic HTML
  - ✅ Uses Font Awesome (consistent with Horizon)
- **Cons**: Chevron appears before link text (minor)
- **Verdict**: ✅ **Best balance - slight preference over Option 3**

### Implementation Approach

**Template Addition**:
```django
{% for cell in row %}
    <td{{ cell.attr_string|safe }}>
        {# Add chevron icon to first cell #}
        {% if forloop.first %}
            <i class="fa fa-chevron-right chevron-icon" aria-hidden="true"></i> 
        {% endif %}
        {% if cell.wrap_list %}<ul>{% endif %}{{ cell.value }}{% if cell.wrap_list %}</ul>{% endif %}
    </td>
{% endfor %}
```

**JavaScript Enhancement**:
```javascript
// Find chevron icon and toggle rotation
var chevronIcon = $(this).find('.chevron-icon');

if (detailRow.is(':visible')) {
    detailRow.hide();
    chevronIcon.removeClass('rotated');  // Point right (▸)
} else {
    detailRow.show();
    chevronIcon.addClass('rotated');     // Point down (▾)
}
```

**CSS Animation**:
```css
.chevron-icon {
    transition: transform 0.2s ease-in-out;
    display: inline-block;
    margin-right: 6px;
}

.chevron-icon.rotated {
    transform: rotate(90deg);  /* Rotate from ▸ to ▾ */
}
```

---

## Final Design: Combined Approach

### Decision: Implement Hide/Show + Chevron Together

**Rationale**:
1. **Better UX from the start**: Chevron provides necessary visual cue
2. **Similar effort**: Both features modify the same files
3. **Single review cycle**: One OpenDev review instead of two
4. **Matches Angular**: Angular has chevrons from the beginning
5. **More complete feature**: Hide/show without visual indicator feels incomplete

### Complete File Changes

| File | Type | Lines | Purpose |
|------|------|-------|---------|
| `expandable_row.html` | Modified | +7 | Add chevron, hide detail, data attrs |
| `keypairs.js` | NEW | +50 | Toggle + rotate chevron |
| `keypairs.scss` | NEW | +50 | Chevron animation + styling |
| `panel.py` | Modified | +8 | Register JS and CSS files |
| **TOTAL** | | **~115 lines** | Complete feature |

---

## Complexity Assessment

### Estimated Implementation Time

- **Template changes**: 10 minutes
- **JavaScript**: 15 minutes  
- **SCSS**: 10 minutes
- **Panel registration**: 5 minutes
- **Testing**: 10 minutes
- **TOTAL**: ~50 minutes

### Risk Level

✅ **LOW**

**Reasons**:
- Well-understood patterns (jQuery, event delegation, CSS transforms)
- Additive changes (doesn't modify existing Horizon code)
- Minimal dependencies
- Simple logic with clear behavior

---

## Key Technical Decisions

### 1. Inline Simple Cell Rendering

**What**: Copy 3 lines of simple cell rendering instead of including 42-line template

**Why**:
- 93% code reduction (3 lines vs 42 lines)
- Better performance (no template resolution)
- Clearer intent (explicit in our template)
- Follows Django best practices

### 2. Data Attributes for Row Matching

**What**: Use `data-keypair-id` to match summary and detail rows

**Why**:
- Robust (works with special characters in names)
- Standard HTML5 pattern
- More explicit than sibling selectors
- Survives table reordering

### 3. CSS Transform for Chevron Rotation

**What**: Use `transform: rotate(90deg)` instead of swapping icons

**Why**:
- Smoother animation
- Less DOM manipulation
- More modern approach
- Hardware accelerated

### 4. Event Delegation Pattern

**What**: Attach one click handler to `document` instead of individual row handlers

**Why**:
- Handles dynamically added rows (AJAX updates, pagination)
- More efficient (one handler vs many)
- Standard Horizon/jQuery pattern

---

## Comparison with Angular Implementation

| Aspect | Angular Version | Our Approach | Note |
|--------|----------------|--------------|------|
| **Chevron location** | Separate `<td>` column | Inside first `<td>` | Simpler (no header change) |
| **Icon animation** | Toggle classes | Transform rotation | Smoother animation |
| **Row matching** | Next sibling | Data attribute | More robust |
| **Framework** | Angular directives | jQuery + event delegation | Leverages existing Horizon stack |
| **Rendering** | Client-side | Server-side | Faster initial load |
| **Complexity** | Higher | Lower | ~115 lines vs ~300+ lines |

**Conclusion**: Our approach achieves similar functionality with less complexity by leveraging Horizon's existing Django/jQuery architecture.

---

## What We Learned

### About Horizon's Architecture

1. **Template system is flexible**: Can customize row rendering without breaking tables
2. **Inline editing is optional**: Not all tables need the full 42-line cell template
3. **jQuery is available**: Can use event delegation for interactive features
4. **Font Awesome is standard**: Chevron icons fit naturally into Horizon's UI

### About Implementation Strategy

1. **Start simple, iterate**: Combine hide/show + chevron (don't over-phase)
2. **Inline when appropriate**: 3-line templates don't need separate files
3. **Use platform features**: Data attributes, jQuery, CSS transforms
4. **Test key interactions**: Ensure links and buttons still work

### About Scope Management

1. **Defer animations**: Start with instant show/hide (add slideDown later)
2. **Defer accessibility**: Get basic functionality working first
3. **Defer accordion behavior**: Let users expand multiple rows initially
4. **One feature at a time**: Don't try to do everything in first patchset

---

## Risks and Mitigation

### Risk 1: JavaScript Disabled

**Impact**: Detail rows remain hidden, feature doesn't work

**Likelihood**: Very low (< 0.1% of users)

**Mitigation**: 
- Accept this trade-off (JavaScript is required for most Horizon features)
- Could add noscript fallback showing all details (future work)

### Risk 2: Special Characters in Key Pair Names

**Impact**: Toggle might not work if name has quotes, slashes, etc.

**Likelihood**: Medium (users can create arbitrary names)

**Mitigation**:
- Use `|escapejs` filter in template for data attributes
- Use proper escaping in jQuery selectors
- Test with edge case names

### Risk 3: Performance with Many Key Pairs

**Impact**: Slow rendering with 100+ key pairs

**Likelihood**: Low (most users have < 20 key pairs)

**Mitigation**:
- Event delegation keeps JavaScript fast
- Hidden rows don't render (display: none)
- Can add pagination if needed

---

## Success Criteria

This spike is successful if we can answer:

- ✅ **How do we customize Horizon table rendering?** 
  - Answer: Override `Row.render()` and provide custom template

- ✅ **What's the implementation complexity?**
  - Answer: ~115 lines across 4 files (~50 minutes work)

- ✅ **Can we achieve feature parity with Angular?**
  - Answer: Yes, with simpler implementation

- ✅ **What's the best approach for chevrons?**
  - Answer: Template-based, in first cell, with CSS transform rotation

- ✅ **Are there any blockers?**
  - Answer: No significant blockers identified

---

## Next Steps

### Immediate Actions

1. ✅ **Spike complete** - We understand the approach
2. **Create implementation branch** - Start actual code
3. **Implement template changes** - Add chevron, hide detail
4. **Implement JavaScript** - Toggle functionality
5. **Implement CSS** - Chevron animation
6. **Manual testing** - Verify all interactions work
7. **Create OpenDev review** - Push for upstream review

### Future Enhancements (Separate Patchsets)

- **Phase 4**: Add smooth animations (slideDown/slideUp)
- **Phase 5**: Add keyboard support (Enter/Space keys)
- **Phase 6**: Add ARIA attributes (screen reader support)
- **Phase 7**: Consider accordion behavior (user feedback)

---

## References

### Source Documents

This spike synthesizes findings from:
- [`analysis_peer_review_day_1_phase_1_study_1.md`](../analysis_new_feature_966349_wip/analysis_peer_review_day_1_phase_1_study_1.md) - Template inlining analysis
- [`analysis_peer_review_day_2.md`](../analysis_new_feature_966349_wip/analysis_peer_review_day_2.md) - Hide/show functionality investigation
- [`analysis_peer_review_day_2_study_chevron.md`](../analysis_new_feature_966349_wip/analysis_peer_review_day_2_study_chevron.md) - Chevron implementation options

### Development Environment

- [`HOWTO_install_devstack_on_psi.org`](HOWTO_install_devstack_on_psi.org) - PSI cloud setup
- [`HOWTO_install_devstack_on_laptop.org`](HOWTO_install_devstack_on_laptop.org) - Local VM setup

### External References

- [Horizon Documentation](https://docs.openstack.org/horizon/latest/)
- [Django Template Documentation](https://docs.djangoproject.com/en/stable/topics/templates/)
- [jQuery Event Delegation](https://learn.jquery.com/events/event-delegation/)
- [CSS Transform](https://developer.mozilla.org/en-US/docs/Web/CSS/transform)

---

## Conclusion

**Status**: ✅ **Investigation Complete - Ready to Implement**

**Key Finding**: We can implement expandable rows with chevrons using ~115 lines of code across 4 files, achieving feature parity with the Angular version while maintaining simplicity.

**Confidence Level**: **HIGH**
- Clear implementation path identified
- All technical questions answered
- No significant blockers
- Manageable scope (~50 minutes implementation)

**Recommendation**: **Proceed with implementation** using the combined hide/show + chevron approach documented in this spike.

---

**Spike Duration**: 2 days (November 6-7, 2025)  
**Investigation Effort**: ~8 hours  
**Outcome**: Ready for implementation with high confidence  
**Next Action**: Begin implementation of Phase 1 (combined hide/show + chevron)

