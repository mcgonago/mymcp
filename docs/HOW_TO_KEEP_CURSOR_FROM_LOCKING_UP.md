# How to Keep Cursor from Locking Up

**A comprehensive guide to understanding Cursor's AI model architecture, optimizing performance, and avoiding the dreaded "Analyzing next steps..." hang**

---

## Table of Contents

1. [The Problem We're Solving](#the-problem-were-solving)
2. [How Cursor Uses AI Models](#how-cursor-uses-ai-models)
   - [Architecture Overview](#architecture-overview)
   - [The Request/Response Flow](#the-requestresponse-flow)
   - [Why "Analyzing next steps..." Happens](#why-analyzing-next-steps-happens)
3. [Available Models and Their Characteristics](#available-models-and-their-characteristics)
4. [Understanding Costs](#understanding-costs)
   - [How Pricing Works](#how-pricing-works)
   - [Estimating Your Usage](#estimating-your-usage)
   - [Red Hat / Enterprise Considerations](#red-hat--enterprise-considerations)
5. [Best Practices (Top 10)](#best-practices-top-10)
6. [Troubleshooting Guide](#troubleshooting-guide)
7. [Session Log](#session-log)

---

## The Problem We're Solving

You're deep in a productive coding session with Cursor. Everything is flowing. Then suddenly:

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                    ⏳ Analyzing next steps...                   │
│                                                                 │
│                         [Spinning...]                           │
│                                                                 │
│                    30 seconds... 1 minute...                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**This document will help you understand:**
- Why this happens
- How to prevent it
- How to recover when it does happen
- How to optimize your workflow for maximum productivity

---

## How Cursor Uses AI Models

### Architecture Overview

Cursor is not a single AI - it's an **orchestration layer** that routes your requests to various AI models based on the task type, complexity, and your settings.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CURSOR ARCHITECTURE                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐                                                            │
│  │   YOU       │                                                            │
│  │  (User)     │                                                            │
│  └──────┬──────┘                                                            │
│         │                                                                   │
│         ▼                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    CURSOR IDE (Local)                               │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                  │    │
│  │  │ Chat Panel  │  │ Composer    │  │ Inline Edit │                  │    │
│  │  │ (Ctrl+L)    │  │ (Ctrl+I)    │  │ (Ctrl+K)    │                  │    │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                  │    │
│  │         │                │                │                         │    │
│  │         └────────────────┼────────────────┘                         │    │
│  │                          ▼                                          │    │
│  │  ┌─────────────────────────────────────────────────────────────┐    │    │
│  │  │              REQUEST ORCHESTRATOR                           │    │    │
│  │  │  • Analyzes request complexity                              │    │    │
│  │  │  • Gathers context (open files, codebase, history)          │    │    │
│  │  │  • Selects appropriate model                                │    │    │
│  │  │  • Manages token budgets                                    │    │    │
│  │  └──────────────────────────┬──────────────────────────────────┘    │    │
│  └─────────────────────────────┼───────────────────────────────────────┘    │
│                                │                                            │
│                                ▼                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    CURSOR CLOUD / API GATEWAY                       │    │
│  │                                                                     │    │
│  │   Routes to appropriate model provider based on:                    │    │
│  │   • Your subscription tier                                          │    │
│  │   • Model availability                                              │    │
│  │   • Request type                                                    │    │
│  │   • Rate limits                                                     │    │
│  └──────────────────────────┬──────────────────────────────────────────┘    │
│                             │                                               │
│         ┌───────────────────┼───────────────────┐                           │
│         ▼                   ▼                   ▼                           │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                    │
│  │  Anthropic  │     │   OpenAI    │     │   Google    │                    │
│  │  (Claude)   │     │  (GPT-4)    │     │  (Gemini)   │                    │
│  │             │     │             │     │             │                    │
│  │ Claude 3.5  │     │ GPT-4o      │     │ Gemini 2.5  │                    │
│  │ Claude 4    │     │ GPT-4o-mini │     │ Flash       │                    │
│  └─────────────┘     └─────────────┘     └─────────────┘                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### The Request/Response Flow

When you send a message to Cursor, here's what happens:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      REQUEST/RESPONSE LIFECYCLE                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. USER INPUT                                                              │
│     ┌─────────────────────────────────────────┐                             │
│     │ "Please refactor this function to be    │                             │
│     │  more efficient and add error handling" │                             │
│     └─────────────────────┬───────────────────┘                             │
│                           │                                                 │
│                           ▼                                                 │
│  2. CONTEXT GATHERING (Local - can be slow!)                                │
│     ┌─────────────────────────────────────────┐                             │
│     │ • Current file content                  │  ← File I/O                 │
│     │ • Open tabs                             │                             │
│     │ • Recent edits                          │                             │
│     │ • Codebase indexing results             │  ← Can be HUGE              │
│     │ • MCP tool definitions                  │                             │
│     │ • Conversation history                  │  ← Grows over time!         │
│     └─────────────────────┬───────────────────┘                             │
│                           │                                                 │
│                           ▼                                                 │
│  3. TOKEN CALCULATION                                                       │
│     ┌─────────────────────────────────────────┐                             │
│     │ Input tokens: ~15,000                   │                             │
│     │ Reserved for output: ~8,000             │                             │
│     │ Context window used: 23,000 / 200,000   │                             │
│     └─────────────────────┬───────────────────┘                             │
│                           │                                                 │
│                           ▼                                                 │
│  4. API REQUEST (Network - variable latency)                                │
│     ┌─────────────────────────────────────────┐                             │
│     │ POST https://api.cursor.sh/v1/chat      │                             │
│     │ Headers: Authorization, Model-Preference│                             │
│     │ Body: { messages, tools, context... }   │                             │
│     └─────────────────────┬───────────────────┘                             │
│                           │                                                 │
│                           ▼                                                 │
│  5. MODEL PROCESSING (Cloud - THIS IS WHERE HANGS HAPPEN)                   │
│     ┌─────────────────────────────────────────┐                             │
│     │ ⏳ "Analyzing next steps..."            │                             │
│     │                                         │                             │
│     │ Model is:                               │                             │
│     │ • Parsing your request                  │                             │
│     │ • Understanding context                 │                             │
│     │ • Planning tool calls                   │                             │
│     │ • Generating response tokens            │                             │
│     │                                         │                             │
│     │ ⚠️  Can be slow if:                      │                             │
│     │ • Model is overloaded                   │                             │
│     │ • Request is very complex               │                             │
│     │ • Many tool calls needed                │                             │
│     │ • Rate limited                          │                             │
│     └─────────────────────┬───────────────────┘                             │
│                           │                                                 │
│                           ▼                                                 │
│  6. STREAMING RESPONSE                                                      │
│     ┌─────────────────────────────────────────┐                             │
│     │ Tokens stream back one at a time        │                             │
│     │ You see text appearing gradually        │                             │
│     └─────────────────────────────────────────┘                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Why "Analyzing next steps..." Happens

The "Analyzing next steps..." state occurs during **Step 5** above. Here are the main causes:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CAUSES OF "ANALYZING NEXT STEPS..." HANGS                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  🔴 MODEL OVERLOAD (Most Common)                                            │
│  ├─────────────────────────────────────────────────────────────────────┐    │
│  │ • Peak usage times (US business hours)                              │    │
│  │ • Everyone using the same model simultaneously                      │    │
│  │ • Model provider (Anthropic/OpenAI) experiencing high load          │    │
│  │                                                                     │    │
│  │ SOLUTION: Try a different model, or wait for off-peak hours         │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  🟠 CONTEXT TOO LARGE                                                       │
│  ├─────────────────────────────────────────────────────────────────────┐    │
│  │ • Long conversation history (100+ messages)                         │    │
│  │ • Many files attached (@file mentions)                              │    │
│  │ • Large codebase indexed                                            │    │
│  │ • Multiple MCP tools with extensive definitions                     │    │
│  │                                                                     │    │
│  │ SOLUTION: Start new chat, be selective with @mentions               │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  🟡 COMPLEX MULTI-STEP REASONING                                            │
│  ├─────────────────────────────────────────────────────────────────────┐    │
│  │ • Request requires many tool calls                                  │    │
│  │ • Ambiguous request needs clarification planning                    │    │
│  │ • Cross-file refactoring with dependencies                          │    │
│  │                                                                     │    │
│  │ SOLUTION: Break into smaller, specific requests                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  🟢 RATE LIMITING                                                           │
│  ├─────────────────────────────────────────────────────────────────────┐    │
│  │ • Hit your subscription's request limit                             │    │
│  │ • Too many requests in short time window                            │    │
│  │ • Premium model quota exhausted                                     │    │
│  │                                                                     │    │
│  │ SOLUTION: Wait, or switch to faster/cheaper model                   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  🔵 NETWORK ISSUES                                                          │
│  ├─────────────────────────────────────────────────────────────────────┐    │
│  │ • VPN latency (common with corporate VPNs)                          │    │
│  │ • Firewall inspection adding delay                                  │    │
│  │ • DNS resolution issues                                             │    │
│  │                                                                     │    │
│  │ SOLUTION: Check network, try without VPN if possible                │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Available Models and Their Characteristics

### Model Comparison Table

| Model | Provider | Context Window | Speed | Quality | Best For | Cost Tier |
|-------|----------|----------------|-------|---------|----------|-----------|
| **claude-3.5-sonnet** | Anthropic | 200K tokens | ⚡⚡⚡ | ⭐⭐⭐⭐⭐ | General coding, refactoring | $$ |
| **claude-3-opus** | Anthropic | 200K tokens | ⚡ | ⭐⭐⭐⭐⭐ | Complex reasoning, architecture | $$$$ |
| **claude-sonnet-4** | Anthropic | 200K tokens | ⚡⚡ | ⭐⭐⭐⭐⭐ | Latest, balanced | $$$ |
| **claude-opus-4** | Anthropic | 200K tokens | ⚡ | ⭐⭐⭐⭐⭐+ | Most capable, complex tasks | $$$$ |
| **gpt-4o** | OpenAI | 128K tokens | ⚡⚡⚡ | ⭐⭐⭐⭐ | Fast responses, good quality | $$ |
| **gpt-4o-mini** | OpenAI | 128K tokens | ⚡⚡⚡⚡ | ⭐⭐⭐ | Quick tasks, cost-effective | $ |
| **gpt-4-turbo** | OpenAI | 128K tokens | ⚡⚡ | ⭐⭐⭐⭐ | Balanced performance | $$$ |
| **gemini-2.5-pro** | Google | 1M tokens | ⚡⚡ | ⭐⭐⭐⭐ | Huge context, analysis | $$ |
| **gemini-2.5-flash** | Google | 1M tokens | ⚡⚡⚡⚡ | ⭐⭐⭐ | Fast, large context | $ |
| **cursor-small** | Cursor | 8K tokens | ⚡⚡⚡⚡⚡ | ⭐⭐ | Tab completion, simple edits | Free |

### Model Selection Decision Tree

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        WHICH MODEL SHOULD I USE?                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                    What are you trying to do?                               │
│                              │                                              │
│         ┌────────────────────┼────────────────────┐                         │
│         ▼                    ▼                    ▼                         │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐                  │
│  │ Quick edit  │      │ Complex     │      │ Large       │                  │
│  │ or question │      │ refactoring │      │ codebase    │                  │
│  └──────┬──────┘      └──────┬──────┘      │ analysis    │                  │
│         │                    │             └──────┬──────┘                  │
│         ▼                    ▼                    ▼                         │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐                  │
│  │ gpt-4o-mini │      │ claude-3.5  │      │ gemini-2.5  │                  │
│  │ or          │      │ -sonnet     │      │ -pro        │                  │
│  │ gemini-flash│      │ or          │      │ (1M context)│                  │
│  │             │      │ claude-     │      │             │                  │
│  │ Fast & cheap│      │ sonnet-4    │      │ Huge context│                  │
│  └─────────────┘      └─────────────┘      └─────────────┘                  │
│                                                                             │
│                              │                                              │
│                              ▼                                              │
│                    Is it still slow?                                        │
│                              │                                              │
│                    ┌─────────┴─────────┐                                    │
│                    ▼                   ▼                                    │
│               ┌────────┐          ┌────────┐                                │
│               │  YES   │          │   NO   │                                │
│               └────┬───┘          └────┬───┘                                │
│                    │                   │                                    │
│                    ▼                   ▼                                    │
│         ┌─────────────────┐    ┌─────────────────┐                          │
│         │ Try:            │    │ Great! Keep     │                          │
│         │ 1. New chat     │    │ using that      │                          │
│         │ 2. Smaller ask  │    │ model           │                          │
│         │ 3. Off-peak time│    │                 │                          │
│         │ 4. Check network│    │                 │                          │
│         └─────────────────┘    └─────────────────┘                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### What Makes One Model Better Than Another?

| Factor | Explanation |
|--------|-------------|
| **Context Window** | How much text the model can "see" at once. Larger = can handle bigger codebases, but slower. |
| **Training Data** | What code/text the model learned from. Newer models have more recent knowledge. |
| **Reasoning Ability** | How well the model can plan multi-step solutions. Opus/GPT-4 excel here. |
| **Speed (Latency)** | Time to first token. Mini/Flash models are fastest. |
| **Throughput** | Tokens per second generated. Affects how fast you see the response. |
| **Instruction Following** | How well the model follows your specific requests. Claude tends to excel. |
| **Code Quality** | Accuracy of generated code. Generally: Opus > Sonnet > GPT-4 > Mini |

---

## Understanding Costs

### How Pricing Works

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CURSOR PRICING MODEL                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    SUBSCRIPTION TIERS                               │    │
│  ├─────────────────────────────────────────────────────────────────────┤    │
│  │                                                                     │    │
│  │  FREE ($0/month)                                                    │    │
│  │  ├── 2,000 completions/month                                        │    │
│  │  ├── 50 slow premium requests/month                                 │    │
│  │  └── Limited model access                                           │    │
│  │                                                                     │    │
│  │  PRO ($20/month)                                                    │    │
│  │  ├── Unlimited completions                                          │    │
│  │  ├── 500 fast premium requests/month                                │    │
│  │  ├── Unlimited slow premium requests                                │    │
│  │  └── All models available                                           │    │
│  │                                                                     │    │
│  │  BUSINESS ($40/user/month)                                          │    │
│  │  ├── Everything in Pro                                              │    │
│  │  ├── Admin controls                                                 │    │
│  │  ├── SSO/SAML                                                       │    │
│  │  ├── Usage analytics                                                │    │
│  │  └── Priority support                                               │    │
│  │                                                                     │    │
│  │  ENTERPRISE (Custom)                                                │    │
│  │  ├── Everything in Business                                         │    │
│  │  ├── Custom model deployments                                       │    │
│  │  ├── On-premise options                                             │    │
│  │  └── Dedicated support                                              │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    WHAT COUNTS AS A "REQUEST"?                      │    │
│  ├─────────────────────────────────────────────────────────────────────┤    │
│  │                                                                     │    │
│  │  FAST PREMIUM REQUEST:                                              │    │
│  │  • Uses Claude Opus, GPT-4, or other premium models                 │    │
│  │  • Gets priority in the queue                                       │    │
│  │  • Counts against your 500/month limit                              │    │
│  │                                                                     │    │
│  │  SLOW PREMIUM REQUEST:                                              │    │
│  │  • Same models, but lower priority                                  │    │
│  │  • May wait longer during peak times                                │    │
│  │  • Unlimited on Pro plan                                            │    │
│  │                                                                     │    │
│  │  COMPLETION:                                                        │    │
│  │  • Tab completions, small inline edits                              │    │
│  │  • Uses cursor-small or similar                                     │    │
│  │  • Unlimited on Pro plan                                            │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Is "Cost" in Dollars?

**Yes and no.** Here's how it breaks down:

| What You See | What It Means |
|--------------|---------------|
| **Subscription cost** | Real dollars - $20/month for Pro |
| **"Request" limits** | Not dollars, but a quota system |
| **"Fast" vs "Slow"** | Priority tier, not dollar cost |
| **Model "cost tier"** | Relative expense to Cursor (affects your quota consumption) |

**You don't pay per-token like with raw API access.** Your subscription gives you a bucket of requests, and different models consume from that bucket at different rates.

### Estimating Your Usage

Unfortunately, Cursor doesn't expose detailed usage metrics to users. Here's what you CAN see:

```bash
# Check your Cursor settings for usage info
# Settings → Account → Usage (if available)
```

**Rough estimates based on typical usage:**

| Usage Pattern | Requests/Day | Monthly Consumption |
|---------------|--------------|---------------------|
| Light (occasional questions) | 10-20 | ~400 requests |
| Moderate (regular coding) | 30-50 | ~1,200 requests |
| Heavy (constant AI assistance) | 100+ | ~3,000+ requests |
| **Your pattern** (based on this session) | 50-80 | ~2,000 requests |

### Red Hat / Enterprise Considerations

> **Important:** If Red Hat provides Cursor through an enterprise agreement, the cost model may be different.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ENTERPRISE LICENSE SCENARIOS                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  SCENARIO A: Individual Pro License (You Pay)                               │
│  ├── $20/month from your pocket or expense                                  │
│  ├── 500 fast premium requests/month                                        │
│  ├── You manage your own quota                                              │
│  └── No company-wide limits                                                 │
│                                                                             │
│  SCENARIO B: Red Hat Business License (Company Pays)                        │
│  ├── $40/user/month billed to Red Hat                                       │
│  ├── May have company-wide usage policies                                   │
│  ├── Admin can see usage analytics                                          │
│  └── Possible shared pool or per-user limits                                │
│                                                                             │
│  SCENARIO C: Red Hat Enterprise Agreement (Custom)                          │
│  ├── Custom pricing negotiated with Cursor                                  │
│  ├── May have higher limits                                                 │
│  ├── Possible on-premise or dedicated capacity                              │
│  └── Contact IT/procurement for details                                     │
│                                                                             │
│  ❓ TO FIND OUT: Check with your manager or IT about how Cursor is          │
│     licensed at Red Hat. The answer affects your usage limits.              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Will You Run Out?

| Concern | Reality |
|---------|---------|
| **Will I run out of requests?** | On Pro: You have 500 fast + unlimited slow. You'd notice slowdowns before "running out." |
| **Will Red Hat run out of $?** | Enterprise agreements typically have high/unlimited caps. Check with IT. |
| **Am I using more than others?** | Probably yes, based on your usage pattern. But that's the point of having the tool! |
| **Should I worry about cost?** | Not really. The productivity gains far outweigh the subscription cost. |

---

## Best Practices (Top 10)

### 🏆 The Top 10 Rules for Smooth Cursor Usage

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TOP 10 BEST PRACTICES                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1️⃣  START FRESH CONVERSATIONS REGULARLY                                     │
│      ────────────────────────────────────────────────────────────────────   │
│      • Long conversations accumulate context → slower responses             │
│      • After ~20-30 messages, consider starting new chat                    │
│      • Use Ctrl+L for new chat panel                                        │
│      • Save important context to files, not conversation history            │
│                                                                             │
│  2️⃣  BE SPECIFIC AND CONCISE                                                 │
│      ────────────────────────────────────────────────────────────────────   │
│      ❌ "Fix my code"                                                       │
│      ✅ "Fix the null pointer exception in handleSubmit() on line 45"       │
│      • Specific requests = faster model processing                          │
│      • Less ambiguity = fewer "thinking" cycles                             │
│                                                                             │
│  3️⃣  USE THE RIGHT MODEL FOR THE JOB                                         │
│      ────────────────────────────────────────────────────────────────────   │
│      • Quick question? → gpt-4o-mini or gemini-flash                        │
│      • Complex refactor? → claude-3.5-sonnet                                │
│      • Architecture planning? → claude-opus-4                               │
│      • Don't use Opus for "what does this function do?"                     │
│                                                                             │
│  4️⃣  LIMIT @FILE AND @CODEBASE USAGE                                         │
│      ────────────────────────────────────────────────────────────────────   │
│      • Each @file adds to context → slower processing                       │
│      • @codebase can pull in HUGE amounts of context                        │
│      • Be surgical: @file only what's needed                                │
│      • Consider copying relevant snippets instead                           │
│                                                                             │
│  5️⃣  BREAK LARGE TASKS INTO SMALLER ONES                                     │
│      ────────────────────────────────────────────────────────────────────   │
│      ❌ "Refactor the entire authentication system"                         │
│      ✅ "First, let's update the login function"                            │
│      ✅ "Now, let's update the session management"                          │
│      ✅ "Finally, let's update the logout flow"                             │
│                                                                             │
│  6️⃣  USE COMPOSER FOR MULTI-FILE CHANGES                                     │
│      ────────────────────────────────────────────────────────────────────   │
│      • Composer (Ctrl+I) is optimized for multi-file edits                  │
│      • Chat is better for questions and single-file work                    │
│      • Don't ask Chat to edit 10 files at once                              │
│                                                                             │
│  7️⃣  KNOW WHEN TO STOP AND RESTART                                           │
│      ────────────────────────────────────────────────────────────────────   │
│      • If "Analyzing..." takes > 60 seconds, something's wrong              │
│      • Press Stop (Escape), then retry                                      │
│      • If retry fails, start new chat                                       │
│      • If still failing, try different model                                │
│                                                                             │
│  8️⃣  AVOID PEAK HOURS WHEN POSSIBLE                                          │
│      ────────────────────────────────────────────────────────────────────   │
│      • US business hours (9am-5pm EST) = highest load                       │
│      • Early morning or evening = faster responses                          │
│      • Weekends typically faster                                            │
│                                                                             │
│  9️⃣  KEEP YOUR CODEBASE INDEX HEALTHY                                        │
│      ────────────────────────────────────────────────────────────────────   │
│      • Large node_modules or build artifacts = slow indexing                │
│      • Use .cursorignore to exclude unnecessary directories                 │
│      • Periodically rebuild index: Cmd+Shift+P → "Reindex"                  │
│                                                                             │
│  🔟  MONITOR AND ADAPT                                                      │
│      ────────────────────────────────────────────────────────────────────   │
│      • Notice patterns in when slowdowns occur                              │
│      • Keep notes on which models work best for which tasks                 │
│      • Share learnings with team                                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Quick Reference Card

```
┌─────────────────────────────────────────────────────────────────┐
│                    CURSOR QUICK REFERENCE                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  KEYBOARD SHORTCUTS                                             │
│  ─────────────────                                              │
│  Ctrl+L      New chat                                           │
│  Ctrl+I      Composer (multi-file)                              │
│  Ctrl+K      Inline edit                                        │
│  Escape      Stop generation                                    │
│  Ctrl+/      Toggle AI panel                                    │
│                                                                 │
│  WHEN STUCK                                                     │
│  ──────────                                                     │
│  1. Press Escape to stop                                        │
│  2. Try again with simpler request                              │
│  3. Start new chat (Ctrl+L)                                     │
│  4. Switch model in dropdown                                    │
│  5. Check network/VPN                                           │
│                                                                 │
│  MODEL QUICK PICKS                                              │
│  ─────────────────                                              │
│  Fast & cheap:    gpt-4o-mini, gemini-flash                     │
│  Balanced:        claude-3.5-sonnet, gpt-4o                     │
│  Best quality:    claude-opus-4, claude-sonnet-4                │
│  Huge context:    gemini-2.5-pro (1M tokens)                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Troubleshooting Guide

### Problem: Stuck on "Analyzing next steps..."

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  STUCK ON "ANALYZING..."                                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Step 1: Wait 30 seconds                                                    │
│          └── Sometimes it's just processing a complex request               │
│                                                                             │
│  Step 2: Press Escape to stop                                               │
│          └── This cancels the current request                               │
│                                                                             │
│  Step 3: Simplify and retry                                                 │
│          └── Break your request into smaller parts                          │
│                                                                             │
│  Step 4: Start new chat (Ctrl+L)                                            │
│          └── Fresh context often fixes issues                               │
│                                                                             │
│  Step 5: Switch model                                                       │
│          └── Try gpt-4o-mini for speed                                      │
│                                                                             │
│  Step 6: Check network                                                      │
│          └── VPN issues? Try disconnecting                                  │
│                                                                             │
│  Step 7: Restart Cursor                                                     │
│          └── Nuclear option, but sometimes necessary                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Problem: Responses are slow but eventually complete

| Possible Cause | Solution |
|----------------|----------|
| Peak usage time | Wait for off-peak, or use faster model |
| Large context | Start new chat, reduce @file usage |
| Complex request | Break into smaller requests |
| Slow model selected | Switch to gpt-4o-mini or gemini-flash |

### Problem: Model seems "confused" or gives poor responses

| Possible Cause | Solution |
|----------------|----------|
| Conversation too long | Start fresh chat |
| Conflicting instructions | Be more explicit about what you want |
| Wrong model for task | Try claude-3.5-sonnet for coding |
| Missing context | Add relevant @file references |

---

## Session Log

This section tracks our ongoing learning about Cursor performance optimization.

### Session 1: Initial Investigation

**Date:** 2025-12-06  
**Trigger:** User experiencing frequent "Analyzing next steps..." hangs

#### Questions Explored

1. **Does the model get overwhelmed over time?**
   
   **Answer:** Not exactly "overwhelmed," but:
   - Context accumulates → larger payloads → slower processing
   - Model doesn't "remember" between sessions - each request is independent
   - Long conversations = more tokens sent each time = slower
   
2. **Can response time diminish over time?**
   
   **Answer:** Yes, within a conversation:
   - Each message adds to context
   - More context = more processing time
   - Solution: Start fresh conversations regularly

3. **Is it Cursor's fault?**
   
   **Answer:** It's a combination of factors:
   - Model provider capacity (Anthropic, OpenAI, Google)
   - Cursor's routing and queuing
   - Your request complexity
   - Network conditions
   - Time of day (peak usage)

#### Initial Recommendations

Based on this session, the top 3 things to try:

1. **Start new chats more frequently** - Don't let conversations get too long
2. **Use faster models for simple tasks** - gpt-4o-mini is great for quick questions
3. **Be specific** - Vague requests take longer to process

---

### Session Template (for future sessions)

```markdown
### Session N: [Topic]

**Date:** YYYY-MM-DD  
**Trigger:** [What prompted this investigation]

#### Questions Explored

1. **[Question]**
   
   **Answer:** [What we learned]

#### Findings

[Key discoveries]

#### Recommendations

[Actionable advice]
```

---

## Additional Resources

- [Cursor Documentation](https://docs.cursor.com/)
- [Anthropic Claude Documentation](https://docs.anthropic.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs/)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)

---

*Document Created: 2025-12-06*  
*Last Updated: 2025-12-06*  
*Maintained By: AI-assisted workflow in mymcp*

