# Review 964474: Replace DOMNodeInserted events with a mutation observer

## Table of Contents

- [Review Information](#review-information)
- [High-Level Description of Changes](#high-level-description-of-changes)
- [What Problem Does This Solve?](#what-problem-does-this-solve)
- [How to Test This Change](#how-to-test-this-change)
- [Top Challenges in Reviewing This Change](#top-challenges-in-reviewing-this-change)
- [Recommended Steps for Completing the Review](#recommended-steps-for-completing-the-review)
- [Key Areas of Concern](#key-areas-of-concern)
- [Technology and Testing Framework Background](#technology-and-testing-framework-background)
- [Estimated Review Time](#estimated-review-time)
- [Questions to Ask the Author](#questions-to-ask-the-author)
- [Follow-Up Actions](#follow-up-actions)

---

## Review Information

- **Change ID**: 964474
- **URL**: https://review.opendev.org/c/openstack/horizon/+/964474
- **Author**: Tatiana Ovchinnikova <t.v.ovtchinnikova@gmail.com>
- **Project**: openstack/horizon
- **Branch**: stable/2024.1
- **Status**: NEW
- **Created**: 2025-10-21 14:31:43.000000000
- **Updated**: 2025-10-23 10:48:38.000000000

## High-Level Description of Changes

This change modernizes Horizon's frontend JavaScript by replacing deprecated `DOMNodeInserted` events with the modern `MutationObserver` API. The modification affects a single file:
- **`horizon/static/horizon/js/horizon.forms.js`**: +24/-10 lines

This is a focused technical debt reduction change targeting the stable/2024.1 branch, aimed at improving compatibility with modern browsers and removing deprecated web API usage.

## What Problem Does This Solve?

The `DOMNodeInserted` event is part of the deprecated Mutation Events API, which has been:
1. **Deprecated by W3C**: Removed from modern web standards
2. **Performance Issues**: Known to cause significant performance degradation in applications with frequent DOM changes
3. **Browser Support Declining**: Modern browsers are phasing out support, with warnings in developer consoles
4. **Unpredictable Behavior**: Can lead to race conditions and timing issues

**Specific Issues Addressed:**
- **Browser Console Warnings**: Users and developers see deprecation warnings when using Horizon
- **Future Compatibility**: Ensuring Horizon continues to work as browsers remove deprecated API support
- **Performance**: MutationObserver is significantly more efficient than mutation events
- **Code Modernization**: Aligning with current web development best practices

## How to Test This Change

Testing this change requires verifying that form-related functionality in Horizon continues to work correctly with the new implementation.

### Prerequisites
1. **Horizon Development Environment**: A working stable/2024.1 Horizon instance
2. **Multiple Browsers**: Test in Chrome, Firefox, and Safari to ensure compatibility
3. **Browser Developer Tools**: To verify no console errors or warnings appear

### Testing Steps

#### 1. Identify Form Functionality Scope
The file `horizon.forms.js` likely handles:
- Dynamic form updates
- Field validation
- Form element additions/removals
- Dynamic select options
- Help text updates

#### 2. Test Form Rendering
1. Navigate to various forms in Horizon:
   - **Instance Launch** form (`/project/instances`)
   - **Volume Creation** form (`/project/volumes`)
   - **Network Creation** form (`/project/networks`)
   - **User Creation** form (admin panel)
   
2. **Verify**: All form fields render correctly
3. **Check**: No JavaScript errors in browser console
4. **Confirm**: No deprecation warnings about mutation events

#### 3. Test Dynamic Form Behavior
1. **Cascading Dropdowns**: 
   - Select options that trigger other field updates
   - Example: Selecting a network might update available subnets
   - **Verify**: Dependent fields update correctly

2. **Conditional Fields**:
   - Toggle checkboxes or radio buttons that show/hide other fields
   - **Verify**: Fields appear and disappear as expected

3. **Dynamic Field Addition**:
   - Forms with "Add Another" buttons (e.g., security group rules)
   - **Verify**: New fields appear correctly and are functional

4. **Field Validation**:
   - Enter invalid data and blur fields
   - **Verify**: Validation messages appear appropriately
   - **Check**: Error messages are styled correctly

#### 4. Performance Testing
1. Open browser developer tools, Performance tab
2. Perform actions on forms with many dynamic updates
3. **Compare**: If possible, compare performance before and after the change
4. **Verify**: No performance degradation (should actually improve)

#### 5. Browser Compatibility Testing
Test in multiple browsers:
```bash
# Chrome/Chromium
google-chrome --incognito http://localhost:8000

# Firefox
firefox -private-window http://localhost:8000

# Safari (macOS)
open -a Safari -n --args -private http://localhost:8000
```

**For each browser:**
1. Complete the form tests above
2. Check developer console for errors
3. Verify all form interactions work identically

#### 6. Regression Testing with Selenium
If Horizon has Selenium tests for forms:
```bash
tox -e selenium -- openstack_dashboard.test.selenium.integration.test_forms
```
**Expected Result**: All tests pass without issues.

## Top Challenges in Reviewing This Change

1. **Understanding MutationObserver API**: Reviewers unfamiliar with `MutationObserver` may need to study the API to properly assess the implementation.

2. **Identifying All Affected Scenarios**: The file name (`horizon.forms.js`) suggests form-related functionality, but without seeing the actual code changes, it's difficult to identify all scenarios that need testing.

3. **Performance Verification**: While MutationObserver should improve performance, quantifying this improvement requires proper benchmarking setup.

4. **Event Timing Differences**: MutationObserver batches mutations and fires asynchronously, which can introduce subtle timing differences compared to synchronous mutation events. Need to ensure no race conditions are introduced.

5. **Stable Branch Implications**: This is targeted at `stable/2024.1`, indicating either a bug fix or important modernization effort. Understanding the urgency and risk assessment is important.

6. **Browser Compatibility Matrix**: Need to verify that the new implementation works across all browsers Horizon officially supports.

## Recommended Steps for Completing the Review

### Phase 1: Code Review (Estimated: 1.5-2 hours)
- **Review the patch**: Request to see the actual diff to understand:
  - Which specific mutation events are being replaced
  - How MutationObserver is configured (observe what? config options?)
  - Whether any callback logic was modified beyond the event replacement
- **Verify implementation**: Check that:
  - MutationObserver is properly initialized and cleaned up (disconnect when done)
  - The observation configuration is appropriate (childList, subtree, attributes, etc.)
  - Callback functions handle mutations correctly
  - No memory leaks (observers are disconnected when no longer needed)
- **Check browser compatibility**: Ensure MutationObserver is used with appropriate polyfills/fallbacks if needed
- **Review documentation**: Check if inline comments explain the migration

### Phase 2: Functional Testing (Estimated: 2-3 hours)
- **Environment setup**: Set up stable/2024.1 Horizon instance (30 minutes)
- **Form testing**: Test all major form types in Horizon (60-90 minutes):
  - Instance launch
  - Volume creation
  - Network/subnet configuration
  - User/project management
  - Security groups
  - Any forms with dynamic behavior
- **Browser testing**: Repeat critical tests in Chrome, Firefox, Safari (30-45 minutes)
- **Performance check**: Use browser profiler to verify no performance regression (15 minutes)

### Phase 3: Review Feedback (Estimated: 30 minutes)
- **Document findings**: List any issues, unexpected behaviors, or browser-specific problems
- **Suggest improvements**: If code can be optimized or better documented
- **Provide +1 or request changes**: Based on testing results

## Key Areas of Concern

- **Event Timing**: MutationObserver is asynchronous while DOMNodeInserted was synchronous. Ensure this doesn't break timing-dependent code.
- **Observer Configuration**: The `options` object for `observe()` must be correct (childList, subtree, attributes, etc.)
- **Memory Leaks**: MutationObservers must be disconnected when no longer needed; failure to do so can cause memory leaks.
- **Browser Support**: While MutationObserver is well-supported, ensure the minimum browser versions Horizon supports include full MutationObserver support.
- **Error Handling**: Ensure the mutation callback has proper error handling to prevent silent failures.
- **Multiple Observers**: If multiple observers are created on the same element, ensure they don't conflict.

## Technology and Testing Framework Background

### DOMNodeInserted (Deprecated)
- Part of the **Mutation Events** specification
- Fired synchronously whenever a node was inserted into the DOM
- **Problems**:
  - Performance: Fires for every single node insertion, blocking the rendering thread
  - Causes layout thrashing
  - Deprecated in DOM Level 3 Events specification

### MutationObserver (Modern)
- Part of the **DOM Living Standard**
- Asynchronously observes DOM changes and batches them
- **Advantages**:
  - Much better performance (doesn't block rendering)
  - Batches multiple mutations into a single callback
  - Precise control over what to observe
  - Can observe attributes, childList, characterData, subtree
- **Browser Support**: Excellent (all modern browsers, IE11+)

### Configuration Options
```javascript
observer.observe(targetNode, {
  childList: true,      // Observe direct children additions/removals
  subtree: true,        // Observe all descendants
  attributes: true,     // Observe attribute changes
  attributeOldValue: true, // Record previous attribute values
  characterData: true,  // Observe text content changes
  characterDataOldValue: true  // Record previous text
});
```

### Best Practices
- Always `disconnect()` the observer when no longer needed
- Keep callback functions lightweight
- Use appropriate configuration to avoid observing unnecessary mutations
- Handle errors gracefully within the callback

## Estimated Review Time

- **Complexity Level**: Medium
- **Estimated Total Hours**: 4-5.5 hours

**Breakdown:**
- **Code Review (Phase 1)**: 1.5-2 hours
- **Functional Testing (Phase 2)**: 2-3 hours
- **Review Feedback & Discussion (Phase 3)**: 30 minutes

**Factors affecting time:**
- Familiarity with MutationObserver API: saves 30-60 minutes
- If stable/2024.1 environment already exists: saves 30 minutes
- Number of forms requiring testing: could add 30-60 minutes
- Browser compatibility testing: adds 30-45 minutes

## Questions to Ask the Author

1. **What specific functionality prompted this change?** Was there a browser warning/error, or is this proactive modernization?
2. **Were there specific forms or scenarios where DOMNodeInserted was causing issues?** Performance problems? Console warnings?
3. **What testing was performed?** Which browsers were tested? Which forms were verified?
4. **Are there any known edge cases or limitations?** Are there scenarios where the new implementation behaves differently?
5. **Why target stable/2024.1 instead of master?** Is this a backport? Should it be applied to other branches?
6. **Was performance testing done?** Are there measurable improvements in performance?
7. **Observer cleanup?** How is the MutationObserver disconnected to prevent memory leaks?
8. **Polyfill considerations?** Does Horizon still support browsers that might not have full MutationObserver support?

## Follow-Up Actions

- **Request Diff**: If not already visible, ask for the actual code changes to be shared or review on Gerrit
- **Extended Browser Testing**: If possible, test on minimum supported browser versions
- **Performance Benchmarking**: Create before/after performance profiles for forms with heavy DOM mutations
- **Documentation Update**: Suggest adding comments in the code explaining the migration from mutation events
- **Backport Consideration**: If this is not a backport, consider proposing this for other stable branches
- **Additional Testing**: Consider adding automated tests specifically for dynamic form behavior
- **Release Notes**: Ensure this modernization is documented in release notes as a technical improvement

