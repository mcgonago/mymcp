# In Progress Report Feature

**Version**: 2.3  
**Date**: 2025-11-25  
**Author**: mymcp activity-tracker-agent

## Overview

New feature that separates "ownership status" (current open work) from historical weekly activity reports.

## What Changed

### New Function: `generate_in_progress_report()`

**Location**: `server.py` (line ~1368)

**Purpose**: Generate a live snapshot of all open items owned by you across platforms

**Key Features**:
- ✅ Always fetches fresh data (no caching)
- ✅ Shows ALL open items (not limited to date range)
- ✅ Saves to `in_progress.md` (not week-specific)
- ✅ Separate from weekly activity reports

**Data Shown**:
1. 🟠 **OpenDev: My Active Reviews** - Reviews not merged/abandoned
2. 🔵 **GitHub: My Open PRs** - Open pull requests
3. 🦊 **GitLab: My Open MRs** - Open merge requests
4. 📋 **Jira: My Open Tickets** - All open tickets assigned to you
5. 📋 **Jira: Tickets Requiring Update** - Tickets idle > 7 days (🔴 highlighted)

### Removed from Weekly Reports

The "Ownership Status" section was removed from weekly reports (`generate_status_report()`) to keep them focused on historical activity within a specific time period.

**Rationale**:
- Weekly reports = "What did I do this week?" (historical, cached)
- In-progress report = "What am I working on now?" (current, always fresh)

### New Wrapper Script

**File**: `generate_in_progress.sh`

**Usage**:
```bash
cd activity-tracker-agent
./generate_in_progress.sh
```

**Output**: `~/Work/mymcp/workspace/iproject/activity/in_progress.md`

## Usage Examples

### From Cursor

```
@activity-tracker generate_in_progress_report()
```

### From Command Line

```bash
cd ~/Work/mymcp/activity-tracker-agent
./generate_in_progress.sh
```

### From Python

```python
from activity_tracker_agent.server import generate_in_progress_report

report = generate_in_progress_report()
print(report)
```

## File Structure

```
workspace/iproject/activity/
├── 2025-W46.json          # Weekly cache (historical)
├── 2025-W46_report.md     # Weekly report (historical)
├── 2025-W47.json
├── 2025-W47_report.md
├── in_progress.md         # ← NEW: Current work status (always fresh)
└── ...
```

## Implementation Details

### No Caching by Design

Unlike weekly reports, `in_progress.md` is NEVER cached because:
1. Ownership status changes frequently (reviews merged, PRs closed, tickets updated)
2. Users want current state, not a snapshot from hours ago
3. Caching would require cache invalidation logic (complex)

**Trade-off**: Slightly slower generation (~5-10 seconds) but always accurate.

### Date Range Strategy

To fetch all open items:
- Start date: `2020-01-01` (covers all historical data)
- End date: Today
- Filter results to only show open/active items

This ensures we capture:
- Old reviews still in NEW state
- PRs opened months ago but still open
- Jira tickets from previous quarters

### Helper Functions

The report reuses helper functions from `generate_status_report()`:
- `days_since_update(date_str)` - Calculate idle days
- `get_status_icon(status)` - Colorful status emojis

These are defined inside the function (not module-level) to keep the code self-contained.

## Benefits

1. **Clarity**: Separates "what I did" (weekly) from "what I'm doing" (in-progress)
2. **Freshness**: Always shows current state of your work
3. **Simplicity**: Single command to see all open work
4. **No Caching**: Avoids stale data issues
5. **Cross-Platform**: Unified view across OpenDev, GitHub, GitLab, Jira

## Use Cases

### Daily Standup

```bash
./generate_in_progress.sh
cat ~/Work/mymcp/workspace/iproject/activity/in_progress.md
```

Quick snapshot of what you're actively working on.

### Weekly Review

```bash
# What did I do this week?
./generate_report.sh "this week"

# What am I still working on?
./generate_in_progress.sh
```

Combines historical activity with current ownership status.

### Sprint Planning

```bash
./generate_in_progress.sh
```

See all open work to plan capacity for new tickets.

### Jira Ticket Triage

The "Tickets Requiring Update" section (tickets idle > 7 days) helps identify:
- Blocked tickets needing updates
- Stale tickets to close
- Work items needing status changes

## Testing

Tested successfully on 2025-11-25:
- ✅ Fetches data from all 4 platforms
- ✅ Filters to show only open items
- ✅ Calculates "days idle" correctly
- ✅ Saves to `in_progress.md`
- ✅ Wrapper script works

**Test Output**:
```
# In Progress

**Generated**: 2025-11-25 09:36:00

_Current ownership status across all platforms_

---

## 🟠 OpenDev: My Active Reviews

**3 active review(s)**

| Review | Project | Subject | Status | Created | Last Updated | Days Idle |
|--------|---------|---------|--------|---------|--------------|-----------|
| [967269](...) | horizon | De-angularize Key Pairs... | 🟢 NEW | 2025-11-17 | 2025-11-18 | 6 |
...
```

## Future Enhancements

Potential improvements for v2.4+:
- Add "Recently Closed" section (last 7 days)
- Add estimated time-to-completion (based on average)
- Add "Blockers" detection (no activity + not updated)
- Add priority sorting (urgent tickets first)
- Add integration with calendar (due dates)

## Documentation Updates

Updated files:
- ✅ `activity-tracker-agent/README.md` - Added usage section
- ✅ `activity-tracker-agent/server.py` - Added function + docstring
- ✅ `activity-tracker-agent/generate_in_progress.sh` - New wrapper script
- ✅ `activity-tracker-agent/IN_PROGRESS_REPORT_FEATURE.md` - This file

## Related Issues

- User request: 2025-11-25 "Move Ownership Status to separate report"
- Design decision: No caching for current work status
- Implementation: ~200 lines of Python code

---

**Status**: ✅ Complete and tested  
**Version**: 2.3  
**Backward Compatible**: Yes (weekly reports unchanged)

