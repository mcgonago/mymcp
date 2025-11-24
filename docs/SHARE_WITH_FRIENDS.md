# Stop Wasting Time on Slack Formatting! 🚀

## The Problem You Have

You want to send this to Slack:
```
Check out my project:
https://github.com/user/awesome-project
Awesome Project

See the docs:
https://docs.company.com/guide
Complete Guide
```

But Slack shows ugly long URLs instead of nice clickable text.

So you manually:
1. Highlight "Awesome Project"
2. Press Cmd+Shift+U
3. Paste the URL again
4. Repeat for each link...
5. Take 2-5 minutes per message 😫

---

## The Solution

**One command. Auto-formats everything. 10 seconds.**

```bash
./scripts/send_to_slack.py my_message.txt --channel "#team"
```

---

## 5-Minute Setup

### 1. Get Slack Webhook (2 min)
- Visit: https://api.slack.com/messaging/webhooks
- Create app → Enable "Incoming Webhooks" → Copy URL

### 2. Clone & Configure (2 min)
```bash
git clone https://github.com/mcgonago/mymcp.git
cd mymcp
echo 'SLACK_WEBHOOK_URL="YOUR_URL_HERE"' >> .mymcp-config
```

### 3. Send First Message (1 min)
```bash
cat > test.txt << 'EOF'
Hello! 👋
Testing automation:
https://github.com/mcgonago/mymcp
mymcp Slack Tool
EOF

./scripts/send_to_slack.py test.txt
```

Check Slack - it worked! 🎉

---

## Real Example

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

**Result:** Three clickable links. Zero manual work. Clean text, no ugly URLs.

---

## Time Savings

| Messages/Day | Time Saved/Day | Time Saved/Year |
|--------------|----------------|-----------------|
| 5 | 15 min | 60 hours |
| 10 | 30 min | 120 hours |
| 20 | 60 min | 240 hours |

**That's weeks of your life back!**

---

## Get Started

**Full guide:** [SLACK_BOOST_PRODUCTIVITY.md](SLACK_BOOST_PRODUCTIVITY.md)  
**Quick start:** [SLACK_QUICK_START.md](SLACK_QUICK_START.md)  
**Repo:** https://github.com/mcgonago/mymcp

---

**Share this doc** with anyone who wastes time formatting Slack messages! 📤

