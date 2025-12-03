#!/usr/bin/env bash
#
# notify-stale-reviews.sh - Send Slack alerts for reviews waiting > 3 days
#
# This script piggy-backs on the existing Slack integration at:
#   - scripts/send_to_slack.py
#   - .mymcp-config (SLACK_WEBHOOK_URL)
#
# Usage:
#   ./notify-stale-reviews.sh              # Send to default webhook
#   ./notify-stale-reviews.sh --preview    # Preview without sending
#   ./notify-stale-reviews.sh --channel "#team"  # Send to specific channel
#
# Cron example (8 AM on weekdays):
#   0 8 * * 1-5 ~/Work/mymcp/notify-stale-reviews.sh
#

set -e

MYMCP_DIR="$HOME/Work/mymcp"
ACTIVITY_DIR="$MYMCP_DIR/workspace/iproject/activity"
SEND_SCRIPT="$MYMCP_DIR/scripts/send_to_slack.py"

# Source config for SLACK_WEBHOOK_URL
source "$MYMCP_DIR/.mymcp-config"

# Parse arguments
PREVIEW=""
CHANNEL_ARG=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --preview)
            PREVIEW="--preview"
            shift
            ;;
        --channel)
            CHANNEL_ARG="--channel $2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

# Generate fresh report
echo "📊 Generating fresh activity report..."
cd "$MYMCP_DIR/activity-tracker-agent"
./generate_in_progress.sh > /dev/null 2>&1

# Check for stale items (waiting >= 3 days)
# Look for lines with day counts >= 3 in the "People Waiting" section
STALE_REVIEWS=""
STALE_COUNT=0

if [ -f "$ACTIVITY_DIR/in_progress.md" ]; then
    # Extract the "People Waiting for Your Review" section (up to the --- separator)
    WAITING_SECTION=$(sed -n '/## 🔔 People Waiting/,/^---$/p' "$ACTIVITY_DIR/in_progress.md")
    
    # Find items with >= 3 days idle
    while IFS= read -r line; do
        if [[ "$line" =~ ^\|\ \[ ]]; then
            # Extract days - look for a number in the second-to-last column
            # Format varies but days is usually before the last [View] or [Review] link
            DAYS=$(echo "$line" | grep -oE '\| [0-9]+ \|' | tail -1 | tr -d '| ' || echo "0")
            if [ -z "$DAYS" ]; then
                DAYS=0
            fi
            if [ "$DAYS" -ge 3 ] 2>/dev/null; then
                # Extract just the key info for the message
                KEY=$(echo "$line" | grep -oE '\[[^]]+\]' | head -1 | tr -d '[]')
                OWNER=$(echo "$line" | awk -F'|' '{print $3}' | xargs)
                TITLE=$(echo "$line" | awk -F'|' '{print $5}' | xargs | cut -c1-40)
                STALE_REVIEWS="$STALE_REVIEWS
• $KEY ($DAYS days) - $OWNER: $TITLE"
                STALE_COUNT=$((STALE_COUNT + 1))
            fi
        fi
    done <<< "$WAITING_SECTION"
fi

if [ $STALE_COUNT -eq 0 ]; then
    echo "✅ No stale reviews (all items < 3 days old)"
    exit 0
fi

echo "⚠️  Found $STALE_COUNT review(s) waiting > 3 days"

# Create message file
TEMP_MSG=$(mktemp)
cat > "$TEMP_MSG" << EOF
🚨 *Reviews Waiting for You (> 3 days)*

You have *$STALE_COUNT* review(s) that have been waiting for more than 3 days:

\`\`\`$STALE_REVIEWS
\`\`\`

_Run \`standup-prep.sh\` for full details_
EOF

# Send or preview
if [ -n "$PREVIEW" ]; then
    echo ""
    echo "=== PREVIEW ==="
    cat "$TEMP_MSG"
    echo "=== END PREVIEW ==="
else
    echo "📤 Sending to Slack..."
    "$SEND_SCRIPT" "$TEMP_MSG" $CHANNEL_ARG
    echo "✅ Notification sent!"
fi

rm -f "$TEMP_MSG"

