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

### Real-World Example (Owen → Francesco)

**What was sent to Slack (with proper `<url|text>` format):**

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

**The `<url|text>` syntax** is Slack's special format that displays "text" as a clickable link.

**How Francesco sees it in Slack:**
- **standup_mcp** ← clickable, hides the long GitLab URL
- **mymcp Activity Tracker Agent** ← clickable, hides the long GitHub URL  
- **Status Report: Week 2025-W46** ← clickable with 📊 emoji

**The input file that generated this:**

Put URL on one line, title on the next:
```
Hi Francesco,

I took some liberty and integrated part of your standup_mcp project:
https://gitlab.cee.redhat.com/fpantano/standup_mcp
standup_mcp

Into my mymcp Activity Tracker Agent:
https://github.com/mcgonago/mymcp?tab=readme-ov-file#activity-tracker-agent
mymcp Activity Tracker Agent

📊 Status Report: Week 2025-W46
https://gitlab.cee.redhat.com/omcgonag/iproject/-/blob/master/activity/2025-W46_report.md
Status Report: Week 2025-W46

Thanks for sharing your `standup_mcp` with me!
```

Script auto-converts to `<url|text>` format!

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

**Your current use case:**

```bash
# 1. Create message file
cat > francesco_message.txt << 'EOF'
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
EOF

# 2. Preview
./scripts/send_to_slack.py francesco_message.txt --preview

# 3. Send (DM to Francesco)
./scripts/send_to_slack.py francesco_message.txt --channel "@francesco"
```

---

**That's it! You're ready to send beautifully formatted Slack messages! 🎉**

