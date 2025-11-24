# Slack Integration - Quick Start

> **New to this?** See [SLACK_BOOST_PRODUCTIVITY.md](SLACK_BOOST_PRODUCTIVITY.md) for the full story of how this saves time!

---

## 🚀 30-Second Setup

### 1. Get Your Webhook URL

Visit: https://api.slack.com/messaging/webhooks
1. Create app → From scratch
2. Name: `mymcp-sender`
3. Enable "Incoming Webhooks"
4. Add webhook to workspace
5. **Copy the webhook URL**

### 2. Add to Config

```bash
cd /home/omcgonag/Work/mymcp
echo 'SLACK_WEBHOOK_URL="https://hooks.slack.com/services/T.../B.../XXX"' >> .mymcp-config
```

### 3. Done! ✅

---

## 📝 Create Your Message

**Format:** Put URL on one line, title on next line.

### Simple Example

**File: `my_message.txt`**

```
Good afternoon! 👋

Check out my project:
https://github.com/mcgonago/mymcp
mymcp Activity Tracker

Thanks! 🚀
```

### Real-World Example

**What Slack received (with `<url|text>` format):**

```
Hi Francesco,

I integrated your standup_mcp project:
<https://gitlab.cee.redhat.com/fpantano/standup_mcp|standup_mcp>

Into my Activity Tracker:
<https://github.com/mcgonago/mymcp#activity-tracker-agent|mymcp Activity Tracker>

My first report:
📊 <https://gitlab.cee.redhat.com/omcgonag/iproject/-/blob/master/activity/2025-W46_report.md|Status Report: Week 2025-W46>

Thanks!
```

**Input was simple** - URL on one line, title on next. Script auto-converts to `<url|text>` format!

**Result:** Three clickable links, no manual formatting needed.

---

## 📤 Send to Slack

### Preview First (Recommended)

```bash
./scripts/send_to_slack.py my_message.txt --preview
```

### Send to Default Channel

```bash
./scripts/send_to_slack.py my_message.txt
```

### Send to Specific Channel

```bash
./scripts/send_to_slack.py my_message.txt --channel "#team"
```

### Send Direct Message

```bash
./scripts/send_to_slack.py my_message.txt --channel "@francesco"
```

### Send to Private Channel (Best for Demos!)

**Pro Tip:** Want to demonstrate the automation to a colleague? Create a private channel!

```bash
# 1. In Slack: Create private channel (e.g., #demos-with-colleague)
# 2. Add your colleague as member
# 3. Create webhook for that channel
# 4. Send your demo!

./scripts/send_to_slack.py demo_message.txt --channel "#your-private-channel"
```

**Why this works:**
- ✅ Webhooks can post to private channels (unlike DMs to other users)
- ✅ Private space for demos and testing
- ✅ Colleague sees automation in action
- ✅ No spam in public channels

---

## 🎨 What You'll See in Slack

**Your message renders as:**

> Good afternoon! 👋
> 
> Check out my project:
> [mymcp Activity Tracker](https://github.com/mcgonago/mymcp) ← clickable text!
> 
> Thanks! 🚀

The URL is hidden, only the title shows (clickable).

---

## 💡 Quick Tips

### Use Slack Formatting

```
*bold text*
_italic text_
`code text`
~strikethrough~
:emoji_name:
```

### Multiple Links in One Message

```
My GitHub project:
https://github.com/user/project1
Project One

My GitLab project:
https://gitlab.com/user/project2
Project Two

Both are awesome! 🎉
```

### From Command Line

```bash
echo "Quick update! 🚀" | ./scripts/send_to_slack.py --stdin
```

---

## 🐛 Troubleshooting

### Error: "No Slack webhook URL configured"

➡️ **Solution:** Add webhook URL to `.mymcp-config`

### Error: "HTTP Error 403"

➡️ **Solution:** Webhook URL is wrong or expired. Create new webhook.

### Can't Send to Another User's DM

➡️ **Limitation:** Slack webhooks can't DM other users (security feature)

➡️ **Solution:** Create a **private channel** with both members! See "Send to Private Channel" above.

### Links Not Formatting

➡️ **Problem:** Empty line between URL and title

**Bad:**
```
https://example.com

My Title
```

**Good:**
```
https://example.com
My Title
```

---

## 📚 Full Documentation

See [SLACK_INTEGRATION.md](./SLACK_INTEGRATION.md) for:
- Advanced usage
- Automation examples
- Security notes
- Integration with activity reports

---

## 🎯 Real-World Example

**Example workflow:**

```bash
# 1. Create message file
cat > message.txt << 'EOF'
Hi Francesco,

I integrated your standup_mcp project:
https://gitlab.cee.redhat.com/fpantano/standup_mcp
standup_mcp

Into my Activity Tracker:
https://github.com/mcgonago/mymcp#activity-tracker-agent
mymcp Activity Tracker

My first report:
📊 https://gitlab.cee.redhat.com/omcgonag/iproject/-/blob/master/activity/2025-W46_report.md
Status Report: Week 2025-W46

Thanks!
EOF

# 2. Preview
./scripts/send_to_slack.py message.txt --preview

# 3. Send to a channel
./scripts/send_to_slack.py message.txt --channel "#team-updates"
```

---

**That's it! You're ready to send beautifully formatted Slack messages! 🎉**

