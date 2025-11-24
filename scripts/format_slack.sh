#!/bin/bash
#
# Simple wrapper for Slack message formatting and sending
#
# Usage:
#   ./format_slack.sh message.txt           # Preview only
#   ./format_slack.sh message.txt send      # Send to Slack
#   ./format_slack.sh message.txt "#team"   # Send to specific channel
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SLACK_SCRIPT="${SCRIPT_DIR}/send_to_slack.py"

if [ $# -eq 0 ]; then
    echo "Usage: $0 <message-file> [send|#channel|@user]"
    echo ""
    echo "Examples:"
    echo "  $0 message.txt              # Preview formatted message"
    echo "  $0 message.txt send         # Send to default channel"
    echo "  $0 message.txt \"#general\"   # Send to #general"
    echo "  $0 message.txt \"@francesco\" # Send DM to francesco"
    echo ""
    echo "Setup: See docs/SLACK_INTEGRATION.md"
    exit 1
fi

MESSAGE_FILE="$1"
ACTION="${2:-preview}"

if [ ! -f "$MESSAGE_FILE" ]; then
    echo "❌ File not found: $MESSAGE_FILE"
    exit 1
fi

if [ "$ACTION" = "send" ]; then
    "$SLACK_SCRIPT" "$MESSAGE_FILE"
elif [ "$ACTION" = "preview" ]; then
    "$SLACK_SCRIPT" "$MESSAGE_FILE" --preview
else
    # Assume it's a channel or user
    "$SLACK_SCRIPT" "$MESSAGE_FILE" --channel "$ACTION"
fi

