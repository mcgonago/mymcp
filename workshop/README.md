# mymcp Workshop: Mastering AI-Assisted Code Review and Feature Development

**Duration:** 3-4 hours  
**Level:** Intermediate  
**Prerequisites:** Basic Git, Python, and command-line knowledge

---

## 🎯 Workshop Overview

Learn how to leverage the mymcp framework to:
- ✅ Perform AI-assisted code reviews on OpenDev, GitHub, and GitLab
- ✅ Analyze Jira tickets and support exceptions
- ✅ Plan and implement complex features using structured spike-driven development
- ✅ Automate documentation and assessment creation
- ✅ Track review changes and patchset evolution

---

## 📋 Agenda

### Section 1: Authentication Setup (30 minutes)
**Goal:** Configure all MCP agent tokens and verify setup

1. **Pre-Workshop Task** - Complete BEFORE attending
   - 📖 Read: [`GET_TOKENS.md`](GET_TOKENS.md)
   - 🔑 Generate all required API tokens
   - ⚙️ Create `.env` and configuration files
   - ✅ Run: `./check_authentication_tokens.sh`

2. **Workshop Start** - Verify everyone's setup
   - Quick troubleshooting session
   - Confirm all agents are operational
   - Run: `test-mcp-setup.sh`

**Expected Result:** All MCP agents showing ✅ green checks

---

### Section 2: MCP Agent Installation and Testing (45 minutes)
**Goal:** Install and verify each MCP agent

#### 2.1 OpenDev Review Agent (10 minutes)
- Install Python environment
- Test with a real OpenStack review
- Understand Gerrit integration

**Hands-on:**
```
@opendev-reviewer-agent Analyze review https://review.opendev.org/c/openstack/horizon/+/967773
```

#### 2.2 GitHub Agent (10 minutes)
- Configure GitHub personal access token
- Test with a pull request
- Explore PR analysis features

**Hands-on:**
```
@github-reviewer-agent Review https://github.com/openstack-k8s-operators/horizon-operator/pull/402
```

#### 2.3 GitLab Agent (10 minutes)
- Set up internal GitLab token
- Test with merge request and commit
- Analyze security fixes

**Hands-on:**
```
@gitlab-cee-agent Analyze https://gitlab.cee.redhat.com/eng/openstack/python-django/-/commit/abc123
```

#### 2.4 Jira Agent (15 minutes)
- Build containerized Jira agent
- Query issues and projects
- Search using JQL

**Hands-on:**
```
@jiraMcp Get details for issue OSPRH-13100
@jiraMcp Search for issues in project OSPRH assigned to me
```

**Checkpoint:** Run `test-mcp-setup.sh` - all agents should pass ✅

---

### Section 3: Review Workflow Sessions (60-75 minutes)
**Goal:** Master the review assessment and checking workflows

#### Session 3.1: Analyzing a Jira Ticket (15 minutes)

**Scenario:** Product manager asks you to evaluate OSPRH-13100

**Hands-on Steps:**
```bash
# Step 1: Query Jira for ticket details
@jiraMcp Get details for issue OSPRH-13100

# Step 2: Analyze technical feasibility
# Ask: "Based on OSPRH-13100, what technical changes are needed?"

# Step 3: Create analysis document
# AI will generate analysis/analysis_osprh_13100/spike.md
```

**What You'll Learn:**
- How to extract requirements from Jira
- How to use AI to investigate technical implications
- How to structure spike documents

---

#### Session 3.2: First-Time Review Assessment (20 minutes)

**Scenario:** New OpenDev review needs analysis

**Hands-on Steps:**
```bash
# Method 1: Using fetch-review.sh script
cd workspace
./scripts/fetch-review.sh --with-assessment opendev \
  https://review.opendev.org/c/openstack/horizon/+/967773

# Method 2: Using "assess" command
assess review 967773
```

**What You'll Learn:**
- How to trigger full review assessment
- How the AI fetches code and analyzes changes
- How assessment documents are structured
- Where results are saved (workspace/iproject/results/)

**Expected Output:**
```
✅ Assessment created: workspace/iproject/results/review_967773.md

📋 Assessment Summary:
- Recommendation: -1 (Invalid CSS syntax)
- Key findings: Missing border-style parameter
- Suggested fix: Add 'solid #ddd' to CSS
```

---

#### Session 3.3: Daily Check-In Workflow (15 minutes)

**Scenario:** Morning routine - check reviews you're tracking

**Hands-on Steps:**
```bash
# Quick status check
check review 967773
check review 965215
check review 966349
```

**Possible Outputs:**

**A) No changes:**
```
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║   ✓ CHECKED review 967773 - No changes since last check       ║
║                                                                ║
║   • Patchset: 1                                               ║
║   • Status: NEW                                               ║
║   • No new patchsets, comments, or status changes             ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
```

**B) Changes detected:**
```
📋 Check #3 - 2025-11-22

🔔 Changes detected:
  • New patchset: Patchset 2 uploaded
  • 1 new comment from reviewer
  
💡 Next steps:
  Run "check review 967773 latest only" to analyze
```

**What You'll Learn:**
- How to use "check" for quick status updates
- How check history is tracked
- How to decide between "latest only" vs "create patchsets"

---

#### Session 3.4: Multi-Patchset Review Analysis (25 minutes)

**Scenario:** Review with multiple patchsets - want to understand evolution

**Hands-on Steps:**
```bash
# Option A: Analyze only the latest patchset
check review 967773 latest only

# Option B: Create full patchset history
check review 967773 create patchsets
```

**What You'll Get (Option B):**
```
📁 Files created:
   • workspace/iproject/results/review_967773.md (dashboard)
   • workspace/iproject/results/review_967773_patchset_1.md
   • workspace/iproject/results/review_967773_patchset_2.md
   • workspace/iproject/results/review_967773_patchset_3.md

📊 Patchset Evolution:
   PS1 (2025-11-19): Initial submission - Invalid CSS
   ├─ Comment (Owen): "Add solid #ddd"
   PS2 (2025-11-20): Fixed CSS syntax
   ├─ Comment (Ivan): "LGTM"
   PS3 (2025-11-21): Rebased on master
```

**What You'll Learn:**
- Difference between "latest only" and "create patchsets"
- How comment alignment works (by timestamp)
- How to track review evolution
- When to use each approach

---

#### Session 3.5: GitHub PR and GitLab MR Reviews (15 minutes)

**Hands-on: GitHub PR**
```bash
assess review https://github.com/RedHatInsights/rhsm-subscriptions/pull/5232
```

**Hands-on: GitLab MR**
```bash
assess review https://gitlab.cee.redhat.com/group/project/-/merge_requests/123
```

**What You'll Learn:**
- Same workflow works across platforms
- How AI adapts to different review systems
- Platform-specific considerations

---

### Section 4: Feature Planning Workshop (60 minutes)
**Goal:** Plan a real feature from Jira ticket to implementation

#### Choose Your Adventure:

**Option A: Walkthrough of OSPRH-12802** (Recommended for first-time)
- Follow the actual feature development from start to finish
- See how spike.md was created
- Review patchset planning documents
- Understand the structured methodology

**Option B: Plan Your Own Feature** (Advanced)
- Pick a real Jira ticket from your backlog
- Create spike document with AI assistance
- Break down into patchsets
- Estimate complexity and timeline

#### Session 4.1: Feature Planning Spike (20 minutes)

**Scenario:** Product wants you to implement OSPRH-12802 (de-angularize Key Pairs)

**Hands-on Steps:**
```bash
# Step 1: Query Jira for requirements
@jiraMcp Get details for issue OSPRH-12802

# Step 2: Request spike creation
# Ask: "Full spike for OSPRH-12802"
#  or: "Create spike for Jira OSPRH-12802 to analyze what's needed 
#       to de-angularize the Key Pairs create form"
```

**What the AI Creates Automatically:**
- ✅ `analysis/analysis_new_feature_osprh_12802/spike.md`
  - Problem analysis
  - Current implementation review
  - Proposed approach
  - Complexity scoring (Risk, Knowledge, Skill factors)
  - Timeline estimation

**What You'll Learn:**
- How to request spike creation
- What a good spike contains
- How complexity is calculated
- How to identify dependencies

**Review Together:**
```bash
# Open the generated spike
cat analysis/analysis_new_feature_osprh_12802/spike.md
```

---

#### Session 4.2: Breaking Down into Patchsets (25 minutes)

**Continuing from spike:**

**Hands-on Steps:**
```bash
# Ask AI to create patchset documents
# The spike already recommended the breakdown, now request details:
"Create detailed patchset documents for OSPRH-12802"
```

**What the AI Creates:**
- ✅ `patchset_1_generate_key_pair_form.md`
  - Executive summary (goal, files, timeline)
  - Step-by-step implementation
  - Complete code examples
  - Testing checklist (15 scenarios)
  - Commit message template
  - Anticipated reviewer questions

- ✅ `patchset_2_import_key_pair_form.md`
- ✅ `patchset_3_private_key_download.md`
- ✅ `patchset_4_error_handling_polish.md`
- ✅ `patchset_5_tests_pep8.md`

**What You'll Learn:**
- How to structure work into reviewable chunks
- What makes a good patchset document
- How to estimate each patchset
- How to create comprehensive testing checklists

**Review Together:**
```bash
# Examine a patchset document
cat analysis/analysis_new_feature_osprh_12802/patchset_1_generate_key_pair_form.md
```

**Group Discussion:**
- Is this breakdown appropriate?
- Would you split differently?
- Are the testing scenarios comprehensive?

---

#### Session 4.3: Design Document and Code References (15 minutes)

**Scenario:** Before implementing, document the thought process

**What Was Created:**
- ✅ `patchset_1_generate_key_pair_form_design.md`
  - "How did I find this?" for each code reference
  - Links to reference implementations
  - Comparison: 90% reference-driven, 10% custom
  - Architectural decisions explained

**What You'll Learn:**
- How to document design thinking
- How to find and reference similar code
- How to justify design choices
- How to make reviews easier

**Review Together:**
```bash
cat analysis/analysis_new_feature_osprh_12802/patchset_1_generate_key_pair_form_design.md
```

**Key Insight:** Good documentation = faster reviews + better maintainability

---

### Section 5: Advanced Topics & Q&A (30 minutes)

#### Topic 1: Workspace Project System (5 minutes)
- Understanding `workspace/iproject/` vs `workspace/myproject/`
- How to configure your personal workspace
- When to use version control for your workspace

#### Topic 2: Askme Framework (10 minutes)
- How to create YAML keys for repetitive tasks
- Examples: `review_assess.yaml`, `review_check.yaml`
- Creating custom keys for your workflow

#### Topic 3: Context-Aware Storage (5 minutes)
- Saving customer-sensitive assessments separately
- Using `--context` flag
- Configuring `.mymcp-config`

#### Topic 4: Open Q&A (10 minutes)
- Troubleshooting common issues
- Customization requests
- Integration with existing workflows

---

## 📚 Reference Materials

### Quick Start Guides
- **[GET_TOKENS.md](GET_TOKENS.md)** - Authentication setup (read BEFORE workshop)
- **[HOW_TO_ASK.md](../analysis/HOW_TO_ASK.md)** - Asking effective questions
- **[EXECUTE_KEYS_USAGE.md](../askme/EXECUTE_KEYS_USAGE.md)** - Using askme keys
- **[CHECK_FRAMEWORK.md](../askme/CHECK_FRAMEWORK.md)** - Review checking framework

### Deep Dives
- **[analysis/analysis_new_feature_osprh_12802/](../analysis/analysis_new_feature_osprh_12802/)** - Complete feature example
- **[analysis/analysis_new_feature_966349/](../analysis/analysis_new_feature_966349/)** - Another feature example
- **[usecases/analysis_new_feature/README.md](../usecases/analysis_new_feature/README.md)** - Methodology documentation

### Command Reference
```bash
# Review Assessment
assess review <url>                     # Initial assessment
assess review <url> with master         # Include master comparison

# Review Checking
check review <number>                   # Basic status check
check review <number> latest only       # Analyze latest patchset
check review <number> create patchsets  # Full patchset history

# Jira Integration
@jiraMcp Get details for issue <ISSUE-KEY>
@jiraMcp Search for issues in project <PROJECT>

# Feature Planning
"Full spike for <JIRA-KEY>"             # Create spike + patchsets
"Create spike for <JIRA-KEY>"           # Just the spike
```

---

## 🛠️ Troubleshooting

### Common Issues During Workshop

#### "MCP agent not found"
```bash
# Verify agent is configured in Cursor settings
# Check: Settings → Features → MCP Servers
```

#### "Authentication failed"
```bash
# Re-run token validation
./workshop/check_authentication_tokens.sh

# Check specific agent
cd jira-agent && podman run --rm -i --env-file ~/.rh-jira-agent.env jira-agent:latest <<< '{"jsonrpc": "2.0", "method": "exit"}'
```

#### "Virtual environment not found"
```bash
cd opendev-review-agent  # or github-agent, gitlab-rh-agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### "Review template not found"
```bash
# Ensure you're in the correct workspace
cd /path/to/mymcp/workspace
./scripts/fetch-review.sh --help
```

**Full Troubleshooting Guide:** [GET_TOKENS.md](GET_TOKENS.md#troubleshooting)

---

## ✅ Workshop Completion Checklist

By the end of this workshop, you should be able to:

### Authentication & Setup
- [ ] All MCP agents configured and working
- [ ] `test-mcp-setup.sh` passes all checks
- [ ] Understand where tokens are stored

### Review Workflows
- [ ] Perform initial review assessment (`assess review`)
- [ ] Run daily check-ins (`check review`)
- [ ] Understand "latest only" vs "create patchsets"
- [ ] Navigate assessment documents
- [ ] Interpret AI recommendations

### Feature Planning
- [ ] Request spike creation from Jira ticket
- [ ] Understand complexity scoring
- [ ] Break features into patchsets
- [ ] Create comprehensive patchset documents
- [ ] Use code references effectively

### Advanced Usage
- [ ] Configure personal workspace
- [ ] Use askme framework for repetitive tasks
- [ ] Handle multi-patchset reviews
- [ ] Track review evolution

---

## 📝 Workshop Feedback

After the workshop, please provide feedback on:
- What worked well?
- What was confusing?
- What additional topics would you like covered?
- How can we improve the workshop?

---

## 🚀 Next Steps After Workshop

### Continue Learning
1. **Practice with real reviews** - Pick 3-5 reviews from your team's backlog
2. **Plan a small feature** - Use the spike-driven approach on a real ticket
3. **Customize your workflow** - Create askme keys for your common tasks
4. **Join the community** - Share your experiences and learnings

### Resources for Continued Growth
- Main mymcp README: [`../README.md`](../README.md)
- Use case documentation: [`../usecases/`](../usecases/)
- Example analyses: [`../analysis/`](../analysis/)
- Askme framework: [`../askme/`](../askme/)

---

## 👥 Workshop Facilitator Notes

### Setup Checklist (Before Workshop)
- [ ] Confirm all attendees received `GET_TOKENS.md` in advance
- [ ] Set up demo Cursor environment with all agents configured
- [ ] Prepare example reviews/PRs/issues for hands-on sessions
- [ ] Test all commands on a fresh mymcp clone
- [ ] Have backup tokens/accounts ready for attendees who forgot

### Time Management Tips
- Section 1: Can skip if everyone confirmed setup beforehand
- Section 2: Can be shortened if all agents working (just demonstrate each)
- Section 3: This is the core - don't rush
- Section 4: Can use Option A (walkthrough) if short on time
- Section 5: Adjust based on questions during earlier sections

### Common Attendee Questions
1. **"Can I use this with private repos?"** - Yes, with proper token scopes
2. **"How much does this cost?"** - Free for public repos, Cursor subscription for AI
3. **"Do I need DevStack?"** - Only for testing Horizon changes, not for reviews
4. **"Can I customize the templates?"** - Yes, all templates are in `results/`

---

**Workshop Version:** 1.0  
**Last Updated:** 2025-11-22  
**Maintainer:** Owen McGonagle <omcgonag@redhat.com>  
**Feedback:** Create an issue in the mymcp repository

---

**Ready to start?** → Begin with [`GET_TOKENS.md`](GET_TOKENS.md) 🚀

