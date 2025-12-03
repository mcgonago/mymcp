#!/usr/bin/env bash
#
# standup-prep.sh - One-command standup preparation
#
# Usage: ./standup-prep.sh
#
# Run this 60 minutes before your daily standup
#

set -e

MYMCP_DIR="$HOME/Work/mymcp"
IPROJECT_DIR="$MYMCP_DIR/workspace/iproject"
ACTIVITY_DIR="$IPROJECT_DIR/activity"
ANALYSIS_DIR="$IPROJECT_DIR/analysis"

echo "🚀 Standup Prep Starting..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Step 1: Generate fresh reports
echo "📊 Step 1: Generating fresh activity reports..."
cd "$MYMCP_DIR/activity-tracker-agent"

echo "   → In Progress report..."
./generate_in_progress.sh 2>/dev/null | tail -1

echo "   → This week's activity report..."
./generate_report.sh "this week" 2>/dev/null | tail -1

echo ""

# Step 2: Show current context
echo "📍 Step 2: Your Current Work Context"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -f "$ANALYSIS_DIR/.current_context" ]; then
    grep -E "^TASK|^TASK_NAME|^STATUS" "$ANALYSIS_DIR/.current_context" 2>/dev/null | while read line; do
        echo "   $line"
    done
else
    echo "   No active context found"
fi
echo ""

# Step 3: Show people waiting for your review (PRIORITY!)
echo "🔔 Step 3: People Waiting for Your Review"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -f "$ACTIVITY_DIR/in_progress.md" ]; then
    # Extract "Needs Your Vote" section (OpenDev) - stop at next ### header
    OPENDEV_WAITING=$(sed -n '/OpenDev: Needs Your Vote/,/^###/p' "$ACTIVITY_DIR/in_progress.md" 2>/dev/null | \
        grep -E "^\| \[" | head -3)
    # Extract "Needs Your Review" section (GitLab) - stop at next ### or --- header
    GITLAB_WAITING=$(sed -n '/GitLab: Needs Your Review/,/^###\|^---/p' "$ACTIVITY_DIR/in_progress.md" 2>/dev/null | \
        grep -E "^\| \[" | head -3)
    # Extract "Needs Your Review" section (GitHub) - stop at next ### or --- header
    GITHUB_WAITING=$(sed -n '/GitHub: Needs Your Review/,/^###\|^---/p' "$ACTIVITY_DIR/in_progress.md" 2>/dev/null | \
        grep -E "^\| \[" | head -3)
    # Extract "Watching" section (Jira) - stop at next ### or --- header
    JIRA_WATCHING=$(sed -n '/Jira: Watching/,/^###\|^---/p' "$ACTIVITY_DIR/in_progress.md" 2>/dev/null | \
        grep -E "^\| \[" | head -3)
    
    if [ -n "$OPENDEV_WAITING" ] || [ -n "$GITLAB_WAITING" ] || [ -n "$GITHUB_WAITING" ] || [ -n "$JIRA_WATCHING" ]; then
        [ -n "$OPENDEV_WAITING" ] && echo "$OPENDEV_WAITING"
        [ -n "$GITLAB_WAITING" ] && echo "$GITLAB_WAITING"
        [ -n "$GITHUB_WAITING" ] && echo "$GITHUB_WAITING"
        [ -n "$JIRA_WATCHING" ] && echo "$JIRA_WATCHING"
    else
        echo "   ✅ No reviews waiting for your vote"
    fi
fi
echo ""

# Step 4: Show items needing attention
echo "🔴 Step 4: Tickets Needing Attention"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -f "$ACTIVITY_DIR/in_progress.md" ]; then
    # Extract tickets requiring update section
    grep -A 20 "Tickets Requiring Update" "$ACTIVITY_DIR/in_progress.md" 2>/dev/null | \
        grep -E "^\| \[" | head -5 || echo "   ✅ No tickets requiring immediate attention"
fi
echo ""

# Step 5: Summary
echo "📋 Step 5: Your Reports Are Ready"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   📄 In Progress:  $ACTIVITY_DIR/in_progress.md"
echo "   📄 This Week:    $ACTIVITY_DIR/$(date +%Y-W%V)_report.md"
echo ""

# Step 6: Quick stats
echo "📈 Quick Stats"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -f "$ACTIVITY_DIR/in_progress.md" ]; then
    OPENDEV=$(grep -c "review.opendev.org" "$ACTIVITY_DIR/in_progress.md" 2>/dev/null) || OPENDEV=0
    GITHUB=$(grep -c "github.com" "$ACTIVITY_DIR/in_progress.md" 2>/dev/null) || GITHUB=0
    GITLAB=$(grep -c "gitlab.cee.redhat.com" "$ACTIVITY_DIR/in_progress.md" 2>/dev/null) || GITLAB=0
    JIRA=$(grep -c "issues.redhat.com" "$ACTIVITY_DIR/in_progress.md" 2>/dev/null) || JIRA=0
    echo "   🟠 OpenDev Reviews: $((OPENDEV / 2))"
    echo "   🔵 GitHub PRs: $((GITHUB / 2))"
    echo "   🦊 GitLab MRs: $((GITLAB / 2))"
    echo "   📋 Jira Tickets: $((JIRA / 2))"
fi
echo ""

echo "✅ Standup prep complete! You're ready."
echo ""
echo "💡 Tip: Review your in_progress.md for full details"
echo "   cat $ACTIVITY_DIR/in_progress.md"

