#!/usr/bin/env bash
#
# unplanned-done.sh - Mark unplanned work as complete
#
# Usage:
#   ./unplanned-done.sh "Description" ACTUAL_HOURS "Outcome"
#   ./unplanned-done.sh "Helped debug filter issue" 2.0 "Fixed, PR merged"
#
# This will:
# 1. Find and remove the matching item from unplanned.txt
# 2. Add it to unplanned_done.txt with the outcome
#

UNPLANNED_FILE="$HOME/Work/mymcp/workspace/iproject/activity/unplanned.txt"
UNPLANNED_DONE_FILE="$HOME/Work/mymcp/workspace/iproject/activity/unplanned_done.txt"

# Check arguments
if [ $# -lt 3 ]; then
    echo "Usage: $0 \"Description\" ACTUAL_HOURS \"Outcome\""
    echo ""
    echo "Example:"
    echo "  $0 \"Helped debug filter issue\" 2.0 \"Fixed, PR merged\""
    echo ""
    echo "Current unplanned items:"
    echo ""
    grep -v "^#" "$UNPLANNED_FILE" | grep -v "^$" | while read -r line; do
        echo "  $line"
    done
    exit 1
fi

DESCRIPTION="$1"
ACTUAL_HOURS="$2"
OUTCOME="$3"

# Find the matching line in unplanned.txt
MATCHED_LINE=$(grep -F "$DESCRIPTION" "$UNPLANNED_FILE" | head -1)

if [ -z "$MATCHED_LINE" ]; then
    echo "❌ Could not find item matching: $DESCRIPTION"
    echo ""
    echo "Current unplanned items:"
    grep -v "^#" "$UNPLANNED_FILE" | grep -v "^$" | while read -r line; do
        echo "  $line"
    done
    exit 1
fi

# Extract date and category from matched line
# Format: YYYY-MM-DD | Category | Description | Hours
DATE=$(echo "$MATCHED_LINE" | cut -d'|' -f1 | xargs)
CATEGORY=$(echo "$MATCHED_LINE" | cut -d'|' -f2 | xargs)
ORIG_DESC=$(echo "$MATCHED_LINE" | cut -d'|' -f3 | xargs)

# Remove from unplanned.txt (escape special chars for sed)
ESCAPED_LINE=$(printf '%s\n' "$MATCHED_LINE" | sed 's/[[\.*^$()+?{|]/\\&/g')
sed -i "\|$ESCAPED_LINE|d" "$UNPLANNED_FILE"

# Add to unplanned_done.txt
echo "$DATE | $CATEGORY | $ORIG_DESC | $ACTUAL_HOURS | $OUTCOME" >> "$UNPLANNED_DONE_FILE"

# Get category icon
case $CATEGORY in
    INTERRUPT)  ICON="💬" ;;
    MEETING)    ICON="📅" ;;
    FIREFIGHT)  ICON="🔥" ;;
    LEARNING)   ICON="📚" ;;
    HELPING)    ICON="🤝" ;;
    ADMIN)      ICON="📋" ;;
    OTHER)      ICON="📌" ;;
    *)          ICON="✅" ;;
esac

echo "✅ Marked as complete:"
echo "   $ICON $CATEGORY: $ORIG_DESC"
echo "   Hours: $ACTUAL_HOURS | Outcome: $OUTCOME"
echo ""
echo "📊 Run ./standup-prep.sh to see it in Success Stories"

