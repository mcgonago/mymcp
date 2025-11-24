#!/usr/bin/env python3
"""
Send formatted messages to Slack with automatic link detection and formatting.

Usage:
    ./send_to_slack.py message.txt
    ./send_to_slack.py message.txt --channel "#general"
    ./send_to_slack.py message.txt --webhook "https://hooks.slack.com/..."
    cat message.txt | ./send_to_slack.py --stdin

Features:
    - Auto-detects URLs followed by text and formats as <url|text>
    - Preserves Slack formatting (bold, italic, code)
    - Supports emojis
    - Can send to specific channels or DMs
"""

import sys
import os
import re
import json
import argparse
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


def load_webhook_url():
    """Load Slack webhook URL from config."""
    config_file = Path.home() / "Work" / "mymcp" / ".mymcp-config"
    
    if config_file.exists():
        with open(config_file) as f:
            for line in f:
                if line.startswith("SLACK_WEBHOOK_URL="):
                    return line.split("=", 1)[1].strip().strip('"')
    
    # Try environment variable
    webhook = os.environ.get("SLACK_WEBHOOK_URL")
    if webhook:
        return webhook
    
    return None


def format_message_for_slack(text):
    """
    Convert plain text with URLs to Slack-formatted message.
    
    Detects patterns like:
        https://example.com
        Link Text Here
    
    And converts to: <https://example.com|Link Text Here>
    """
    lines = text.strip().split('\n')
    formatted_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if this line is a URL and next line is its title
        url_match = re.match(r'^(https?://[^\s]+)$', line.strip())
        if url_match and i + 1 < len(lines):
            url = url_match.group(1)
            next_line = lines[i + 1].strip()
            
            # If next line is not empty and not another URL, use it as link text
            if next_line and not re.match(r'^https?://', next_line):
                formatted_lines.append(f"<{url}|{next_line}>")
                i += 2  # Skip both lines
                continue
        
        # Otherwise, just add the line as-is
        formatted_lines.append(line)
        i += 1
    
    return '\n'.join(formatted_lines)


def send_to_slack(webhook_url, message, channel=None):
    """
    Send message to Slack via webhook.
    
    Args:
        webhook_url: Slack webhook URL
        message: Formatted message text
        channel: Optional channel override (e.g., "#general" or "@username")
    
    Returns:
        True if successful, False otherwise
    """
    payload = {
        "text": message,
        "mrkdwn": True,
        "unfurl_links": True,
        "unfurl_media": True
    }
    
    if channel:
        payload["channel"] = channel
    
    try:
        request = Request(
            webhook_url,
            data=json.dumps(payload).encode('utf-8'),
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'mymcp-slack-sender/1.0'
            }
        )
        
        with urlopen(request, timeout=10) as response:
            result = response.read().decode('utf-8')
            if result == "ok":
                return True
            else:
                print(f"❌ Slack API returned: {result}", file=sys.stderr)
                return False
                
    except HTTPError as e:
        print(f"❌ HTTP Error {e.code}: {e.reason}", file=sys.stderr)
        print(f"   Response: {e.read().decode('utf-8')}", file=sys.stderr)
        return False
    except URLError as e:
        print(f"❌ URL Error: {e.reason}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Send formatted messages to Slack',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ./send_to_slack.py message.txt
  ./send_to_slack.py message.txt --channel "#general"
  cat message.txt | ./send_to_slack.py --stdin
  echo "Hello World!" | ./send_to_slack.py --stdin --preview

Setup:
  1. Create a Slack webhook: https://api.slack.com/messaging/webhooks
  2. Add to ~/.mymcp-config:
     SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
        """
    )
    
    parser.add_argument(
        'file',
        nargs='?',
        help='Message file to send'
    )
    parser.add_argument(
        '--stdin',
        action='store_true',
        help='Read message from stdin'
    )
    parser.add_argument(
        '--channel',
        help='Slack channel or DM (e.g., "#general" or "@username")'
    )
    parser.add_argument(
        '--webhook',
        help='Slack webhook URL (overrides config)'
    )
    parser.add_argument(
        '--preview',
        action='store_true',
        help='Preview formatted message without sending'
    )
    parser.add_argument(
        '--raw',
        action='store_true',
        help='Send message as-is without auto-formatting URLs'
    )
    
    args = parser.parse_args()
    
    # Read message
    if args.stdin:
        message = sys.stdin.read()
    elif args.file:
        try:
            with open(args.file) as f:
                message = f.read()
        except FileNotFoundError:
            print(f"❌ File not found: {args.file}", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"❌ Error reading file: {e}", file=sys.stderr)
            return 1
    else:
        parser.print_help()
        return 1
    
    # Format message
    if not args.raw:
        formatted_message = format_message_for_slack(message)
    else:
        formatted_message = message
    
    # Preview mode
    if args.preview:
        print("=" * 60)
        print("📋 FORMATTED MESSAGE PREVIEW")
        print("=" * 60)
        print(formatted_message)
        print("=" * 60)
        return 0
    
    # Get webhook URL
    webhook_url = args.webhook or load_webhook_url()
    
    if not webhook_url:
        print("❌ No Slack webhook URL configured!", file=sys.stderr)
        print("\nSetup instructions:", file=sys.stderr)
        print("1. Create webhook: https://api.slack.com/messaging/webhooks", file=sys.stderr)
        print("2. Add to /home/omcgonag/Work/mymcp/.mymcp-config:", file=sys.stderr)
        print('   SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"', file=sys.stderr)
        print("\nOr use --webhook flag to specify URL", file=sys.stderr)
        return 1
    
    # Send to Slack
    print("📤 Sending to Slack...", file=sys.stderr)
    if send_to_slack(webhook_url, formatted_message, args.channel):
        print("✅ Message sent successfully!", file=sys.stderr)
        return 0
    else:
        print("❌ Failed to send message", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

