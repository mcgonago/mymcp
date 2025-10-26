# Review 963468: Use server filter mode for volumes and snapshots tables

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

- **Change ID**: 963468
- **URL**: https://review.opendev.org/c/openstack/horizon/+/963468
- **Project**: openstack/horizon
- **Branch**: master
- **Status**: NEW
- **Created**: 2025-10-08
- **Last Updated**: 2025-10-22
- **Files Changed**: 6 files
- **Changes**: +43/-37 lines

## High-Level Description of Changes

This change modifies how Horizon handles filtering and pagination for volumes and snapshots tables by switching from client-side filtering to server-side filtering. The change affects 6 files with a net of 6 lines added, indicating refactoring and optimization rather than adding significant new functionality.

**Key Modifications:**
- Refactors volume and snapshot table handling
- Implements server-side filtering instead of client-side
- Affects pagination and search functionality
- Likely improves performance for large datasets

## What Problem Does This Solve?

**Client-Side Filtering Limitations:**
1. **Scalability Issues**: Loading all volumes/snapshots to the client and filtering locally doesn't scale
2. **Performance**: With hundreds or thousands of volumes, client-side filtering causes slow page loads and UI lag
3. **Memory Consumption**: All data must be loaded into browser memory
4. **Network Bandwidth**: Transferring all data even if only a subset is needed

**Server-Side Filtering Benefits:**
1. **Better Performance**: Only requested data is fetched and rendered
2. **Reduced Network Traffic**: Filters applied at the API level
3. **Scalability**: Works efficiently with large deployments
4. **Consistent UX**: Faster response times regardless of dataset size
5. **API Efficiency**: Leverages Cinder's built-in filtering capabilities

## How to Test This Change

Testing requires a Horizon environment with a substantial number of volumes and snapshots to properly evaluate performance improvements.

### Prerequisites
1. **Horizon Development Environment**: master branch
2. **OpenStack with Cinder**: Accessible Cinder API
3. **Test Data**: Create a significant number of volumes and snapshots
   - At least 50-100 volumes
   - Mix of different statuses, names, sizes
   - Multiple snapshots

### Testing Steps

#### 1. Environment Setup
```bash
# Create test volumes and snapshots
for i in {1..100}; do
  openstack volume create --size 1 test-vol-$i
done

for i in {1..50}; do
  openstack volume snapshot create --volume test-vol-$i test-snap-$i
done
```

#### 2. Test Volumes Page
1. Navigate to **Project → Volumes → Volumes**
2. **Verify**: Page loads quickly (should be faster than before)
3. **Check**: All volumes display correctly
4. **Test Pagination**:
   - If more than one page of volumes exists, navigate between pages
   - **Verify**: Page transitions are smooth and fast
   - **Confirm**: Correct number of items per page

5. **Test Search/Filter**:
   - Use the search box to filter by name
   - **Verify**: Results update correctly
   - **Check**: Network tab shows API calls with filter parameters
   - **Confirm**: Only filtered results are fetched from server

#### 3. Test Snapshots Page
1. Navigate to **Project → Volumes → Snapshots**
2. Repeat all tests from Volumes page:
   - Page load performance
   - Pagination
   - Search/filtering
   - Results accuracy

#### 4. Verify Server-Side Filtering
Open browser developer tools → Network tab:

```
Expected API Calls (examples):
GET /api/cinder/volumes?marker=...&limit=20&search_opts={"name":"test-vol"}
GET /api/cinder/snapshots?marker=...&limit=20&search_opts={"name":"test-snap"}
```

**Verify**:
- API calls include filter parameters
- Only one page of data is fetched at a time
- No large bulk data transfers

#### 5. Test Edge Cases
- **Empty Results**: Search for non-existent volume name
  - **Verify**: "No items to display" message appears
  - **Check**: API call returns empty result set

- **Special Characters**: Search with special characters in names
  - **Verify**: Proper encoding and results

- **Large Page Size**: If configurable, test with maximum items per page
  - **Verify**: Performance remains acceptable

#### 6. Performance Comparison
If possible, compare before and after:
- **Page Load Time**: Use browser developer tools Performance tab
- **Network Transfer Size**: Check total KB transferred
- **Time to Interactive**: Measure when UI becomes responsive

#### 7. Regression Testing
Run automated tests:
```bash
tox -e py3 -- openstack_dashboard.dashboards.project.volumes.tests
```
**Expected**: All tests pass.

## Top Challenges in Reviewing This Change

1. **Understanding Client vs Server Filtering Architecture**: Reviewers need to understand the difference and implications of both approaches.

2. **API Compatibility**: Ensuring the Cinder API supports all required filtering capabilities that were previously handled client-side.

3. **Pagination Logic**: Server-side pagination can be complex, especially with markers and limits. Need to verify correct implementation.

4. **Search Functionality**: Ensuring all search/filter features that worked client-side are maintained server-side.

5. **Performance Measurement**: Quantifying performance improvements requires proper benchmarking setup and large test datasets.

6. **Backward Compatibility**: Understanding if this change affects any APIs or behaviors that downstream tools might depend on.

## Recommended Steps for Completing the Review

### Phase 1: Code Review (Estimated: 2-2.5 hours)
- **Review the patch**: Examine all 6 modified files to understand:
  - How filter parameters are constructed and passed to API
  - Changes to pagination logic (markers, limits)
  - Modifications to table definitions
  - Updates to any template or JavaScript files
- **Verify API calls**: Ensure Cinder API is called with correct parameters
- **Check error handling**: Verify appropriate error handling for API failures
- **Review tests**: Check if tests were updated to reflect server-side filtering
- **Documentation**: Look for comments explaining the architectural change

### Phase 2: Functional Testing (Estimated: 2.5-3.5 hours)
- **Environment setup**: Set up master branch Horizon (30 minutes)
- **Data preparation**: Create test volumes and snapshots (30 minutes)
- **Functional tests**: Test all scenarios listed above (90-120 minutes)
- **Performance testing**: Measure and compare load times (30 minutes)
- **Edge case testing**: Test boundary conditions (30 minutes)

### Phase 3: Review Feedback (Estimated: 30-45 minutes)
- **Document findings**: List performance improvements, issues, or concerns
- **API verification**: Confirm Cinder API calls are optimal
- **Suggest improvements**: Code quality, error handling, user experience

## Key Areas of Concern

- **API Parameter Handling**: Ensure filter parameters are properly encoded and sent to Cinder
- **Pagination State Management**: Verify correct handling of pagination markers between requests
- **Search Query Encoding**: Special characters in search queries must be properly escaped
- **Performance Regression**: In small datasets, server-side filtering could add latency overhead
- **Error Handling**: Network errors or API failures should gracefully degrade
- **Filter Persistence**: Should filter state be persisted across page refreshes?
- **Sort Order**: Verify sorting still works correctly with server-side filtering

## Technology and Testing Framework Background

### Client-Side vs Server-Side Filtering

**Client-Side Filtering (Old):**
```javascript
// Fetch all data once
GET /api/cinder/volumes  // Returns all volumes
// Filter in JavaScript
const filtered = allVolumes.filter(v => v.name.includes(searchTerm));
```

**Server-Side Filtering (New):**
```javascript
// Fetch only filtered data
GET /api/cinder/volumes?search_opts={"name":"searchTerm"}&limit=20
// Server returns pre-filtered results
```

### Cinder API Filtering

Cinder supports various filter options:
```python
GET /v3/{project_id}/volumes?name=test&status=available&limit=10&marker=<uuid>
```

**Common Parameters:**
- `name`: Filter by volume name
- `status`: Filter by status (available, in-use, error, etc.)
- `limit`: Number of results per page
- `marker`: UUID of last item from previous page (for pagination)
- `sort_key`: Field to sort by
- `sort_dir`: Sort direction (asc/desc)

### Horizon Table Framework

Horizon uses Django tables (`horizon.tables`) which support:
- Server-side pagination
- Filtering
- Actions (row and table-level)
- Custom rendering

## Estimated Review Time

- **Complexity Level**: Medium-High
- **Estimated Total Hours**: 5-6.5 hours

**Breakdown:**
- **Code Review (Phase 1)**: 2-2.5 hours
- **Functional Testing (Phase 2)**: 2.5-3.5 hours
- **Review Feedback & Discussion (Phase 3)**: 30-45 minutes

**Factors affecting time:**
- Familiarity with Horizon table framework: saves 30-60 minutes
- Existing test environment with data: saves 30 minutes
- Access to performance profiling tools: adds 15-30 minutes
- Number of edge cases discovered: could add 30-60 minutes

## Questions to Ask the Author

1. **What prompted this change?** Was there a specific performance issue or user complaint?
2. **Performance measurements?** Do you have before/after metrics demonstrating the improvement?
3. **Cinder API compatibility?** Are there any minimum Cinder API version requirements?
4. **Filter feature parity?** Do all client-side filters have server-side equivalents?
5. **Backward compatibility?** Are there any breaking changes to APIs or user workflows?
6. **Testing performed?** What testing was done? Manual? Automated? Performance testing?
7. **Pagination marker handling?** How are pagination markers managed across requests?
8. **Future plans?** Will this pattern be applied to other resource tables (e.g., instances, networks)?

## Follow-Up Actions

- **Performance Benchmarking**: Create detailed before/after performance profiles
- **Extend to Other Tables**: Consider applying this pattern to instances, images, networks
- **Documentation**: Update developer and user documentation about the architecture change
- **API Version Check**: Ensure compatibility checks for minimum Cinder API version
- **User Feedback**: Monitor for user-reported issues post-merge
- **Release Notes**: Document this as a performance improvement in release notes

