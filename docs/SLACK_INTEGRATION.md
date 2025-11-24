# Slack Integration Guide

Send beautifully formatted messages to Slack with automatic link formatting.

## Overview

The `send_to_slack.py` script automatically detects URLs and their titles, converting them to Slack's native link format `<url|title>` which renders as clickable text.

## Quick Start

### 1. Create a Slack Webhook

1. Go to: https://api.slack.com/messaging/webhooks
2. Click **"Create your Slack app"**
3. Choose **"From scratch"**
4. Name it: `mymcp-sender` (or whatever you like)
5. Select your workspace
6. Under **"Incoming Webhooks"**, toggle **"Activate Incoming Webhooks"** to ON
7. Click **"Add New Webhook to Workspace"**
8. Select the channel you want to post to (usually yourself for testing)
9. Copy the webhook URL (looks like: `https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX`)

### 2. Configure the Webhook URL

Add to `/home/omcgonag/Work/mymcp/.mymcp-config`:

```bash
SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

Or set as environment variable:

```bash
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

### 3. Send Your First Message

```bash
cd /home/omcgonag/Work/mymcp

# Preview formatting without sending
./scripts/send_to_slack.py scripts/test_slack_message.txt --preview

# Send to Slack
./scripts/send_to_slack.py scripts/test_slack_message.txt

# Send to specific channel
./scripts/send_to_slack.py scripts/test_slack_message.txt --channel "#general"

# Send from stdin
echo "Hello Slack! 👋" | ./scripts/send_to_slack.py --stdin
```

## Message Format

### Auto-Detected Link Format

The script detects this pattern:
```
URL on one line
Title text on next line
```

**Example Input:**
```
Check out my project:
https://github.com/mcgonago/mymcp
mymcp Activity Tracker
```

**Slack Output:**
```
Check out my project:
<https://github.com/mcgonago/mymcp|mymcp Activity Tracker>
```

**Renders as:** "mymcp Activity Tracker" (clickable text, not full URL)

### Supported Slack Formatting

The script preserves these Slack formatting codes:

| Format | Syntax | Example |
|--------|--------|---------|
| Bold | `*text*` | `*important*` → **important** |
| Italic | `_text_` | `_emphasis_` → _emphasis_ |
| Strike | `~text~` | `~wrong~` → ~~wrong~~ |
| Code | `` `text` `` | `` `variable` `` → `variable` |
| Emoji | `:name:` or 🎉 | `:rocket:` → 🚀 |

### Example Message

**Input file (`my_message.txt`):**
```
Good afternoon! 👋

A few FYIs to share...

I integrated this awesome project:
https://github.com/user/project
Amazing Project

Into my implementation:
https://github.com/mcgonago/mymcp
My MCP Repository

Check out the `README.md` for more details!

Thanks for the *excellent* work! 🚀
```

**Preview before sending:**
```bash
./scripts/send_to_slack.py my_message.txt --preview
```

**Send:**
```bash
./scripts/send_to_slack.py my_message.txt
```

**Slack Output:**
```
Good afternoon! 👋

A few FYIs to share...

I integrated this awesome project:
<https://github.com/user/project|Amazing Project>

Into my implementation:
<https://github.com/mcgonago/mymcp|My MCP Repository>

Check out the `README.md` for more details!

Thanks for the *excellent* work! 🚀
```

---

## Real-World Example: Sharing Project Updates

This is an actual message sent by Owen to Francesco to share activity tracking results.

### What Was Sent to Slack

**The formatted message with proper Slack link syntax:**

```
Hi Francesco,

I hope you don't mind me sharing a few FYIs...

I took some liberty and integrated part of your standup_mcp project:
<https://gitlab.cee.redhat.com/fpantano/standup_mcp|standup_mcp>

Into my mymcp Activity Tracker Agent:
<https://github.com/mcgonago/mymcp?tab=readme-ov-file#activity-tracker-agent|mymcp Activity Tracker Agent>

I hope you don't mind me giving you kudos for the baseline `standup_mcp` project...

I was experimenting and didn't need the `did` integration (no pun intended), but I got my first activity tracker report working:

📊 Status Report: Week 2025-W46
<https://gitlab.cee.redhat.com/omcgonag/iproject/-/blob/master/activity/2025-W46_report.md|Status Report: Week 2025-W46>

I need to get better statistics over time, but it's a great start!

Thanks for sharing your `standup_mcp` with me a few weeks ago. Really appreciate it!
```

**Notice the `<url|text>` format** - that's Slack's special syntax that makes the text clickable while hiding the long URL.

### How Francesco Sees It

In Slack, Francesco sees:
- **"standup_mcp"** as a clickable link (not the long GitLab URL)
- **"mymcp Activity Tracker Agent"** as a clickable link (not the long GitHub URL)
- **"Status Report: Week 2025-W46"** with 📊 emoji as a clickable link
- All code terms like `standup_mcp` and `did` properly formatted with gray background
- Clean, professional message with no ugly URLs

### The Input File That Generated This

**File: `francesco_message.txt`**

```
Hi Francesco,

I hope you don't mind me sharing a few FYIs...

I took some liberty and integrated part of your standup_mcp project:
https://gitlab.cee.redhat.com/fpantano/standup_mcp
standup_mcp

Into my mymcp Activity Tracker Agent:
https://github.com/mcgonago/mymcp?tab=readme-ov-file#activity-tracker-agent
mymcp Activity Tracker Agent

I hope you don't mind me giving you kudos for the baseline `standup_mcp` project...

I was experimenting and didn't need the `did` integration (no pun intended), but I got my first activity tracker report working:

📊 Status Report: Week 2025-W46
https://gitlab.cee.redhat.com/omcgonag/iproject/-/blob/master/activity/2025-W46_report.md
Status Report: Week 2025-W46

I need to get better statistics over time, but it's a great start!

Thanks for sharing your `standup_mcp` with me a few weeks ago. Really appreciate it!
```

**Notice:** URLs and titles are on consecutive lines. The script auto-detects this pattern and converts to Slack's `<url|text>` format.

### The Commands Used

```bash
# 1. Preview what will be sent
./scripts/send_to_slack.py francesco_message.txt --preview

# 2. Send to Francesco via DM
./scripts/send_to_slack.py francesco_message.txt --channel "@francesco"

# Or send to a team channel
./scripts/send_to_slack.py francesco_message.txt --channel "#team-updates"
```

**The Power:** Write your message naturally (URL, then title), run one command, and the script automatically converts to Slack's special `<url|text>` format. No manual formatting needed!

---

## Usage Examples

### Send File to Default Channel

```bash
./scripts/send_to_slack.py message.txt
```

### Send to Specific Channel

```bash
./scripts/send_to_slack.py message.txt --channel "#general"
```

### Send Direct Message

```bash
./scripts/send_to_slack.py message.txt --channel "@username"
```

### Preview Without Sending

```bash
./scripts/send_to_slack.py message.txt --preview
```

### Send from Stdin

```bash
cat message.txt | ./scripts/send_to_slack.py --stdin

echo "Quick update!" | ./scripts/send_to_slack.py --stdin
```

### Send Without Auto-Formatting

```bash
# If you've already formatted the message yourself
./scripts/send_to_slack.py message.txt --raw
```

### Override Webhook URL

```bash
./scripts/send_to_slack.py message.txt --webhook "https://hooks.slack.com/services/..."
```

## Advanced: Integrate with Activity Reports

### Weekly Activity Report to Slack

```bash
# Generate activity report
cd /home/omcgonag/Work/mymcp
./scripts/send_to_slack.py - --stdin << EOF
📊 *Weekly Activity Report: $(date +%Y-W%W)*

This week's development activity is ready:

https://gitlab.cee.redhat.com/omcgonag/iproject/-/blob/master/activity/$(date +%Y-W%W)_report.md
Status Report: Week $(date +%Y-W%W)

Let me know if you have questions! 🚀
EOF
```

### Automate Weekly Posts

Add to your crontab:
```bash
# Every Monday at 9am
0 9 * * 1 cd /home/omcgonag/Work/mymcp && ./scripts/send_to_slack.py weekly_template.txt --channel "#team"
```

## Troubleshooting

### "No Slack webhook URL configured"

**Solution:** Add webhook URL to `.mymcp-config` or use `--webhook` flag.

### "HTTP Error 403: Forbidden"

**Cause:** Invalid webhook URL or webhook was revoked.

**Solution:** 
1. Regenerate webhook in Slack app settings
2. Update `.mymcp-config` with new URL

### "HTTP Error 404: Not Found"

**Cause:** Malformed webhook URL.

**Solution:** Double-check the URL starts with `https://hooks.slack.com/services/`

### Links Not Formatting as Expected

**Cause:** URL and title not on consecutive lines.

**Example Problem:**
```
https://github.com/user/project

My Project  ← Empty line breaks detection
```

**Solution:** Remove empty lines between URL and title:
```
https://github.com/user/project
My Project
```

### Want to Keep Full URLs Visible?

**Solution:** Use `--raw` flag or put URL and title on same line:
```
My project: https://github.com/user/project
```

## Security Notes

- **Never commit webhook URLs to git** - they're secret tokens
- Store in `.mymcp-config` (gitignored) or environment variables
- Webhooks can only post to channels they're authorized for
- Anyone with your webhook URL can post to your Slack workspace
- Rotate webhook URLs periodically

## Creating Multiple Webhooks

You can create different webhooks for different purposes:

```bash
# In .mymcp-config
SLACK_WEBHOOK_PERSONAL="https://hooks.slack.com/services/T.../B.../XXX"
SLACK_WEBHOOK_TEAM="https://hooks.slack.com/services/T.../B.../YYY"
SLACK_WEBHOOK_STATUS="https://hooks.slack.com/services/T.../B.../ZZZ"
```

Then use with `--webhook` flag:
```bash
./scripts/send_to_slack.py message.txt --webhook "$SLACK_WEBHOOK_TEAM"
```

## Related Documentation

- [Activity Tracker Agent](../README.md#activity-tracker-agent)
- [Central Configuration](./CENTRAL_CONFIGURATION.md)
- [Slack Webhook Documentation](https://api.slack.com/messaging/webhooks)

## Quick Reference Card

```bash
# Setup
echo 'SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."' >> .mymcp-config

# Basic usage
./scripts/send_to_slack.py message.txt

# Preview first
./scripts/send_to_slack.py message.txt --preview

# Specific channel
./scripts/send_to_slack.py message.txt --channel "#team"

# From stdin
echo "Hello!" | ./scripts/send_to_slack.py --stdin

# Get help
./scripts/send_to_slack.py --help
```

---

**Pro Tip:** Test with DMs to yourself first before posting to team channels! Send to `--channel "@yourusername"` for testing.

