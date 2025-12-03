#!/usr/bin/env bash
#
# unplanned-add.sh - Quick add unplanned work items
#
# Usage:
#   ./unplanned-add.sh CATEGORY "Description" HOURS
#   ./unplanned-add.sh INTERRUPT "Helped debug filter issue" 1.5
#   ./unplanned-add.sh MEETING "Sync with PM about release" 0.5
#   ./unplanned-add.sh FIREFIGHT "CI pipeline investigation" 2.0
#
# Categories: INTERRUPT, MEETING, FIREFIGHT, LEARNING, HELPING, ADMIN, OTHER
#

UNPLANNED_FILE="$HOME/Work/mymcp/workspace/iproject/activity/unplanned.txt"

# Check arguments
if [ $# -lt 3 ]; then
    echo "Usage: $0 CATEGORY \"Description\" HOURS"
    echo ""
    echo "Categories:"
    echo "  INTERRUPT  - Someone asked for help"
    echo "  MEETING    - Unplanned meeting/discussion"
    echo "  FIREFIGHT  - Production issue / urgent fix"
    echo "  LEARNING   - Research, reading, training"
    echo "  HELPING    - Pairing, code review, mentoring"
    echo "  ADMIN      - HR, expenses, compliance"
    echo "  OTHER      - Anything else"
    echo ""
    echo "Example:"
    echo "  $0 INTERRUPT \"Helped Tatiana debug filter\" 1.5"
    exit 1
fi

CATEGORY="$1"
DESCRIPTION="$2"
HOURS="$3"
TODAY=$(date +%Y-%m-%d)

# Validate category
VALID_CATEGORIES="INTERRUPT MEETING FIREFIGHT LEARNING HELPING ADMIN OTHER"
if [[ ! " $VALID_CATEGORIES " =~ " $CATEGORY " ]]; then
    echo "❌ Invalid category: $CATEGORY"
    echo "Valid categories: $VALID_CATEGORIES"
    exit 1
fi

# Add to file
echo "$TODAY | $CATEGORY | $DESCRIPTION | $HOURS" >> "$UNPLANNED_FILE"

# Get category icon
case $CATEGORY in
    INTERRUPT)  ICON="💬" ;;
    MEETING)    ICON="📅" ;;
    FIREFIGHT)  ICON="🔥" ;;
    LEARNING)   ICON="📚" ;;
    HELPING)    ICON="🤝" ;;
    ADMIN)      ICON="📋" ;;
    OTHER)      ICON="📌" ;;
esac

echo "✅ Added unplanned work:"
echo "   $ICON $CATEGORY: $DESCRIPTION ($HOURS hours)"
echo ""
echo "📝 When done, remove from unplanned.txt and add to unplanned_done.txt with outcome"
echo "   File: $UNPLANNED_FILE"

