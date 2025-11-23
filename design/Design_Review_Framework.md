# Design: Review Assessment Framework

**Document:** How "assess review 967773" orchestrates the creation of review assessments  
**Created:** 2025-11-22  
**Example Output:** `workspace/iproject/results/review_967773.md`

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Component Details](#component-details)
4. [Flow Diagrams](#flow-diagrams)
5. [Data Flow](#data-flow)
6. [Key Orchestration Points](#key-orchestration-points)
7. [Template System](#template-system)
8. [MCP Agent Integration](#mcp-agent-integration)
9. [Example Execution Trace](#example-execution-trace)

---

## Overview

The review assessment framework is a multi-layer orchestration system that combines:
- **Askme Framework** - YAML-based command patterns
- **Bash Scripts** - Code fetching and environment setup
- **MCP Agents** - Review metadata retrieval
- **AI Orchestration** - Template filling and analysis
- **Templates** - Structured documentation patterns

**User Input:** `assess review 967773`

**Final Output:** `workspace/iproject/results/review_967773.md` (complete analysis)

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                              │
│                                                                     │
│  User types: "assess review 967773"                                │
│                                                                     │
└─────────────────┬───────────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      ASKME FRAMEWORK LAYER                          │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────┐     │
│  │ askme/keys/review_assess.yaml                            │     │
│  │                                                           │     │
│  │ type: code_review_full_assessment                        │     │
│  │ script_command: "./scripts/fetch-review.sh               │     │
│  │                  --with-assessment opendev {REVIEW_URL}" │     │
│  │ review_url: "{REVIEW_URL}"                               │     │
│  └──────────────────────────────────────────────────────────┘     │
│                                                                     │
│  Pattern Match: "assess review XXXXX" → Execute script             │
│                                                                     │
└─────────────────┬───────────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       SCRIPT EXECUTION LAYER                        │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────┐     │
│  │ workspace/scripts/fetch-review.sh                        │     │
│  │                                                           │     │
│  │ Actions:                                                 │     │
│  │ 1. Parse review URL → extract review number (967773)    │     │
│  │ 2. Determine review type (opendev/github/gitlab)        │     │
│  │ 3. Clone repository to: workspace/horizon-967773/       │     │
│  │ 4. Checkout review patchset                             │     │
│  │ 5. Create named branch: ws-review-967773                │     │
│  │ 6. Copy template: results/review_template.md →          │     │
│  │                   workspace/iproject/results/review_     │     │
│  │                   967773.md                              │     │
│  └──────────────────────────────────────────────────────────┘     │
│                                                                     │
└─────────────────┬───────────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     MCP AGENT INVOCATION LAYER                      │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────┐     │
│  │ AI automatically invokes:                                │     │
│  │ @opendev-reviewer-agent                                  │     │
│  │                                                           │     │
│  │ Fetches:                                                 │     │
│  │ - Review metadata (author, status, dates)               │     │
│  │ - File change statistics                                │     │
│  │ - Review comments                                        │     │
│  │ - Patchset information                                   │     │
│  └──────────────────────────────────────────────────────────┘     │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────┐     │
│  │ opendev-review-agent/server.py                           │     │
│  │                                                           │     │
│  │ Calls: https://review.opendev.org/changes/967773/detail │     │
│  │ Returns: JSON with review data                          │     │
│  └──────────────────────────────────────────────────────────┘     │
│                                                                     │
└─────────────────┬───────────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       CODE READING LAYER                            │
│                                                                     │
│  AI reads actual code changes:                                     │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────┐     │
│  │ cd workspace/horizon-967773                              │     │
│  │ git show HEAD                                            │     │
│  │                                                           │     │
│  │ Retrieves:                                               │     │
│  │ - Commit message                                         │     │
│  │ - File diffs                                             │     │
│  │ - Line-by-line changes                                   │     │
│  └──────────────────────────────────────────────────────────┘     │
│                                                                     │
└─────────────────┬───────────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      AI ORCHESTRATION LAYER                         │
│                                                                     │
│  AI combines all inputs and fills template:                        │
│                                                                     │
│  Inputs:                          Template Structure:              │
│  ┌────────────────────┐           ┌────────────────────┐          │
│  │ MCP Agent Data     │───────────▶│ Review Info        │          │
│  │ - Metadata         │           │ Executive Summary  │          │
│  │ - Comments         │           │ Decision           │          │
│  └────────────────────┘           │ Change Overview    │          │
│                                    │ Code Quality       │          │
│  ┌────────────────────┐           │ Technical Analysis │          │
│  │ Code Changes       │───────────▶│ Review Checklist   │          │
│  │ - git show HEAD    │           │ Testing            │          │
│  │ - File diffs       │           │ Recommendations    │          │
│  └────────────────────┘           └────────────────────┘          │
│                                             │                       │
│  ┌────────────────────┐                    │                       │
│  │ AI Analysis        │────────────────────┘                       │
│  │ - CSS validation   │                                            │
│  │ - Best practices   │                                            │
│  │ - Recommendations  │                                            │
│  └────────────────────┘                                            │
│                                                                     │
└─────────────────┬───────────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         OUTPUT LAYER                                │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────┐     │
│  │ workspace/iproject/results/review_967773.md              │     │
│  │                                                           │     │
│  │ Complete assessment with:                                │     │
│  │ ✓ Patchset information                                   │     │
│  │ ✓ Review metadata                                        │     │
│  │ ✓ Executive summary                                      │     │
│  │ ✓ Recommendation (-1/0/+1/+2)                            │     │
│  │ ✓ Key findings (e.g., invalid CSS syntax)               │     │
│  │ ✓ Code analysis                                          │     │
│  │ ✓ Testing checklist                                      │     │
│  │ ✓ Reviewer comments analysis                             │     │
│  │ ✓ Recommendations for fix                                │     │
│  │ ✓ Check history tracking                                 │     │
│  │ ✓ Metadata for future checks                             │     │
│  └──────────────────────────────────────────────────────────┘     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. Askme Framework (Pattern Matching)

**File:** `askme/keys/review_assess.yaml`

```yaml
type: code_review_full_assessment
script_command: "./scripts/fetch-review.sh --with-assessment opendev {REVIEW_URL}"
review_url: "{REVIEW_URL}"
```

**Responsibilities:**
- Pattern recognition ("assess review XXXXX")
- URL construction
- Script invocation with correct parameters
- Type detection (opendev/github/gitlab)

**Key Point:** The askme framework acts as a **command router**, translating natural language into structured script execution.

---

### 2. Fetch Script (Environment Setup)

**File:** `workspace/scripts/fetch-review.sh`

**Key Functions:**

```bash
┌─────────────────────────────────────────────────────────────┐
│ Function: parse_review_url()                                │
│                                                              │
│ Input:  https://review.opendev.org/c/openstack/horizon/+/   │
│         967773                                               │
│ Output: REVIEW_TYPE=opendev                                 │
│         PROJECT=horizon                                      │
│         CHANGE=967773                                        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Function: fetch_review_code()                               │
│                                                              │
│ Actions:                                                     │
│ 1. git clone https://review.opendev.org/openstack/horizon  │
│    → workspace/horizon-967773/                              │
│ 2. cd horizon-967773                                        │
│ 3. git fetch origin refs/changes/73/967773/1               │
│ 4. git checkout -b ws-review-967773 FETCH_HEAD             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Function: create_review_assessment()                        │
│                                                              │
│ Actions:                                                     │
│ 1. Determine workspace project dir (iproject)               │
│ 2. Create results directory if needed                       │
│ 3. cp results/review_template.md →                         │
│    workspace/iproject/results/review_967773.md              │
│ 4. Signal AI to complete assessment                        │
└─────────────────────────────────────────────────────────────┘
```

**Responsibilities:**
- URL parsing and validation
- Repository cloning
- Review patchset checkout
- Template copying
- Directory structure management

---

### 3. MCP Agent (Metadata Retrieval)

**File:** `opendev-review-agent/server.py`

**Data Flow:**

```
┌────────────────────────────────────────────────────────────────┐
│ AI Request                                                     │
│ @opendev-reviewer-agent                                        │
│ review_url: "https://review.opendev.org/.../967773"           │
└────────────────┬───────────────────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────────────────┐
│ MCP Server (FastMCP)                                          │
│                                                                │
│ def gerrit_review_fetcher(review_url: str):                  │
│     change_num = extract_change_number(review_url)           │
│     api_url = f"https://review.opendev.org/changes/          │
│                 {change_num}/detail"                          │
│     response = requests.get(api_url)                          │
│     data = parse_gerrit_json(response.text)                  │
│     return formatted_review_data(data)                        │
└────────────────┬───────────────────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────────────────┐
│ Returned Data Structure                                        │
│                                                                │
│ {                                                              │
│   "change_number": "967773",                                   │
│   "title": "Fix inconsistent borders...",                     │
│   "author": "Tatiana Ovchinnikova",                           │
│   "project": "openstack/horizon",                             │
│   "status": "NEW",                                             │
│   "created": "2025-11-19 20:42:59",                           │
│   "files_changed": [".../_keypairs_table.html"],             │
│   "file_stats": [                                              │
│     {"file": "...", "insertions": 2, "deletions": 0}         │
│   ],                                                           │
│   "review_comments": [                                         │
│     {"author": "Owen McGonagle", "message": "..."}           │
│   ]                                                            │
│ }                                                              │
└────────────────────────────────────────────────────────────────┘
```

**Responsibilities:**
- HTTP requests to Gerrit API
- JSON parsing (handling Gerrit's security prefix)
- Data transformation into AI-friendly format
- Error handling and validation

---

### 4. Template System

**File:** `results/review_template.md`

**Template Structure:**

```markdown
# Review Assessment: [Review Number] - [Title]

## Patchset Information
**Patchset Number:** [X]
**Previous Patchsets:** [Links]

## Review Information
**Review URL:** [URL]
**Review Number:** [Number]
**Author:** [Author]
**Status:** [NEW/MERGED/ABANDONED]
[... more metadata fields ...]

## Check History
[Track each time review is checked]

## Executive Summary
[AI fills: What does this change do?]

## Decision
**Recommendation:** ❌ -1 / 🔄 0 / ⚠️ +1 / ✅ +2
[AI fills: Reasoning]

## Code Quality Assessment
[AI fills: Analysis]

## Technical Analysis
[AI fills: Detailed code review]

## Testing Verification
[AI fills: How to test]

## Recommendations
[AI fills: What needs to happen]

## Metadata (for AI tracking)
```yaml
review_metadata:
  review_number: [number]
  current_patchset: [X]
  status: [status]
  last_check_date: [date]
```
```

**Key Features:**
- **Structured sections** - Consistent organization
- **Placeholders** - [Bracketed] values for AI to fill
- **Metadata block** - Machine-readable tracking data
- **Check history** - Cumulative tracking of reviews

---

## Flow Diagrams

### Overall Flow: User Request to Completed Assessment

```
START: User types "assess review 967773"
  │
  ├─ [1] AI Pattern Match
  │    ├─ Detects: "assess review XXXXX"
  │    ├─ Loads: askme/keys/review_assess.yaml
  │    └─ Extracts: review_number=967773
  │
  ├─ [2] AI Invokes Script
  │    ├─ Command: ./scripts/fetch-review.sh
  │    ├─ Args: --with-assessment opendev <url>
  │    └─ Execution: Bash subprocess
  │
  ├─ [3] Script Execution
  │    ├─ Parse URL → type=opendev, project=horizon, change=967773
  │    ├─ Clone repo → workspace/horizon-967773/
  │    ├─ Checkout review → git checkout -b ws-review-967773
  │    ├─ Copy template → workspace/iproject/results/review_967773.md
  │    └─ Return: Template path + directory structure
  │
  ├─ [4] AI Reads Template
  │    ├─ Open: workspace/iproject/results/review_967773.md
  │    ├─ Parse: Identify placeholder sections
  │    └─ Plan: Which data needed to fill each section
  │
  ├─ [5] AI Queries MCP Agent
  │    ├─ Invoke: @opendev-reviewer-agent
  │    ├─ Param: review_url=https://review.opendev.org/.../967773
  │    ├─ Agent: Calls Gerrit API
  │    └─ Returns: JSON with metadata, comments, file stats
  │
  ├─ [6] AI Reads Code Changes
  │    ├─ Command: cd workspace/horizon-967773 && git show HEAD
  │    ├─ Retrieves: Commit message, file diffs
  │    └─ Analyzes: Actual code changes line-by-line
  │
  ├─ [7] AI Performs Analysis
  │    ├─ Review code quality
  │    ├─ Check for issues (e.g., invalid CSS syntax)
  │    ├─ Evaluate against best practices
  │    ├─ Generate recommendations
  │    └─ Formulate decision (-1/0/+1/+2)
  │
  ├─ [8] AI Fills Template
  │    ├─ Patchset Info: From MCP agent data
  │    ├─ Review Info: From MCP agent data
  │    ├─ Executive Summary: AI-generated based on code
  │    ├─ Decision: AI recommendation with reasoning
  │    ├─ Code Analysis: AI evaluation of changes
  │    ├─ Testing: AI-generated test scenarios
  │    ├─ Recommendations: AI suggestions for improvement
  │    └─ Metadata: Tracking data for future checks
  │
  ├─ [9] AI Writes Complete Document
  │    ├─ Write: workspace/iproject/results/review_967773.md
  │    └─ Includes: All sections filled, ~400 lines
  │
  └─ [10] AI Reports to User
       ├─ Summary: Key findings in visual box
       ├─ Recommendation: -1/0/+1/+2 with brief reason
       └─ Location: Path to full assessment
  
END: Complete assessment available
```

---

### Data Flow: Information Sources → Assessment Sections

```
┌──────────────────────────────────────────────────────────────────┐
│                        DATA SOURCES                              │
└──────────────────────────────────────────────────────────────────┘
         │                    │                   │
         │                    │                   │
    ┌────▼────┐        ┌──────▼──────┐      ┌────▼─────┐
    │ MCP     │        │ Git Code    │      │ AI       │
    │ Agent   │        │ Changes     │      │ Analysis │
    └────┬────┘        └──────┬──────┘      └────┬─────┘
         │                    │                   │
         │                    │                   │
┌────────▼────────────────────▼───────────────────▼────────────────┐
│              ASSESSMENT DOCUMENT SECTIONS                         │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ## Patchset Information                                         │
│     ← MCP Agent (current_patchset, total_patchsets)             │
│                                                                   │
│  ## Review Information                                           │
│     ← MCP Agent (author, status, dates, project)                │
│                                                                   │
│  ## Check History                                                │
│     ← AI (timestamp, changes detected, actions taken)           │
│                                                                   │
│  ## Executive Summary                                            │
│     ← MCP Agent (title, file count, line stats)                 │
│     ← Git Code (what changed)                                    │
│     ← AI Analysis (interpretation, impact)                       │
│                                                                   │
│  ## Decision                                                      │
│     ← AI Analysis (recommendation: -1/0/+1/+2)                   │
│     ← AI Analysis (reasoning, conditions)                        │
│                                                                   │
│  ## 👥 Reviewer Comments Analysis                                │
│     ← MCP Agent (review_comments array)                          │
│     ← AI Analysis (interpretation of comments)                   │
│                                                                   │
│  ## Change Overview                                               │
│     ← MCP Agent (files_changed, file_stats)                      │
│     ← Git Code (commit message, diff summary)                    │
│     ← AI Analysis (why this change, impact)                      │
│                                                                   │
│  ## Code Quality Assessment                                       │
│     ← Git Code (actual code changes)                             │
│     ← AI Analysis (strengths, concerns, suggestions)             │
│                                                                   │
│  ## Technical Analysis                                            │
│     ← Git Code (file diffs, line-by-line changes)               │
│     ← AI Analysis (code review, issues, recommendations)         │
│     ← AI Knowledge (CSS spec, best practices)                    │
│                                                                   │
│  ## Review Checklist                                              │
│     ← AI Analysis (evaluated against standards)                  │
│                                                                   │
│  ## Testing Verification                                          │
│     ← AI Knowledge (how to test this type of change)            │
│     ← Git Code (what needs testing)                              │
│                                                                   │
│  ## Recommendations                                               │
│     ← AI Analysis (what must/should/nice-to-have)               │
│                                                                   │
│  ## Metadata                                                      │
│     ← MCP Agent (review state)                                   │
│     ← AI (assessment tracking data)                              │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

---

### Decision Flow: How AI Determines Recommendation

```
START: AI has all data (MCP agent + Git code)
  │
  ├─ [1] Analyze Code Changes
  │    ├─ Parse file diffs
  │    ├─ Identify changed lines
  │    └─ Understand intent
  │
  ├─ [2] Check for Critical Issues
  │    ├─ Syntax errors?
  │    ├─ Security vulnerabilities?
  │    ├─ Breaking changes?
  │    └─ Logic errors?
  │          │
  │          ├─ YES → Recommendation: -1 (Do Not Merge)
  │          └─ NO  → Continue ↓
  │
  ├─ [3] Evaluate Against Best Practices
  │    ├─ Follows language/framework standards?
  │    ├─ Proper error handling?
  │    ├─ Code readability?
  │    ├─ Performance considerations?
  │    └─ Test coverage?
  │          │
  │          ├─ MAJOR ISSUES → -1 (Do Not Merge)
  │          ├─ MODERATE → 0 (Needs Work) or +1 (with comments)
  │          └─ GOOD → Continue ↓
  │
  ├─ [4] Review Comments Analysis
  │    ├─ What did reviewers say?
  │    ├─ Were concerns addressed?
  │    ├─ Premature approvals?
  │    └─ Unresolved issues?
  │          │
  │          └─ Factor into decision ↓
  │
  ├─ [5] Generate Recommendation
  │    │
  │    ├─ -1 (Do Not Merge)
  │    │    ├─ Critical bugs/syntax errors
  │    │    ├─ Security issues
  │    │    ├─ Breaks functionality
  │    │    └─ Requires major rework
  │    │
  │    ├─ 0 (Needs Work)
  │    │    ├─ Multiple moderate issues
  │    │    ├─ Unclear implementation
  │    │    ├─ Missing important aspects
  │    │    └─ Needs discussion
  │    │
  │    ├─ +1 (Looks Good, minor comments)
  │    │    ├─ Generally good approach
  │    │    ├─ Minor improvements suggested
  │    │    ├─ Non-blocking comments
  │    │    └─ Almost ready to merge
  │    │
  │    └─ +2 (Approve)
  │         ├─ Excellent code quality
  │         ├─ No issues found
  │         ├─ Follows all best practices
  │         └─ Ready to merge
  │
  └─ [6] Document Reasoning
       ├─ Why this recommendation?
       ├─ What are the specific issues/strengths?
       ├─ What conditions for approval?
       └─ What next steps?

END: Recommendation with detailed reasoning
```

---

## Key Orchestration Points

### Point 1: Natural Language → Script Execution

**Challenge:** User says "assess review 967773" - how does this become script execution?

**Solution:**

```
User Input: "assess review 967773"
      ↓
AI Pattern Matching:
  - Matches askme/keys/review_assess.yaml
  - Pattern: "assess review {NUMBER}"
  - Extracts: review_number = 967773
      ↓
URL Construction:
  - Assumes OpenDev if just number
  - Constructs: https://review.opendev.org/c/openstack/horizon/+/967773
      ↓
Script Invocation:
  - Command: ./scripts/fetch-review.sh
  - Args: --with-assessment opendev <url>
      ↓
Bash Execution:
  - AI executes script via run_terminal_cmd tool
  - Waits for script completion
  - Reads script output
```

**Key Point:** The AI acts as an **intelligent router**, understanding intent and translating to concrete actions.

---

### Point 2: Template → Filled Document

**Challenge:** How does a template with placeholders become a 400-line assessment?

**Solution:**

```
Template Section:
  ## Executive Summary
  
  **Purpose:** [What does this change do?]
  
  **Scope:**
  - Files changed: [X]
  - Lines added: [+X]
  - Lines deleted: [-X]
  
  **Recommendation:** ✅ APPROVE / ⚠️ NEEDS WORK / ❌ REJECT

AI Processing:
  1. Identify placeholders: [What does...], [X], [+X], [-X]
  2. Map to data sources:
     - "What does this change do?" → Git commit message + code analysis
     - Files changed → MCP agent file_stats
     - Lines added/deleted → MCP agent file_stats
     - Recommendation → AI decision based on analysis
  3. Fill each placeholder:
     - Purpose: "Fix inconsistent borders for expandable rows..."
     - Files: 1
     - Lines: +2 / -0
     - Recommendation: ❌ REJECT (invalid CSS)
  4. Write complete section to file

Result:
  ## Executive Summary
  
  **Purpose:** Fix inconsistent borders for expandable rows with 
  chevrons in the Key Pairs table.
  
  **Scope:**
  - Files changed: 1
  - Lines added: +2
  - Lines deleted: 0
  
  **Recommendation:** ⚠️ NEEDS WORK
  
  This change attempts to fix border inconsistencies...
```

**Key Point:** Templates provide **structure**, AI provides **content intelligence**.

---

### Point 3: Multi-Source Data Synthesis

**Challenge:** Assessment requires data from 3 different sources - how to combine?

**Solution:**

```
For: "Code Quality Assessment" section

Source 1 - MCP Agent:
  {
    "files_changed": ["_keypairs_table.html"],
    "insertions": 2,
    "deletions": 0
  }
  → Tells us: Small change, CSS file

Source 2 - Git Code:
  + border-top: 1px;
  + border-bottom: 1px;
  → Tells us: Adding CSS border properties

Source 3 - AI Knowledge:
  CSS border shorthand requires: width + style + color
  Missing 'style' = invalid CSS
  → Tells us: This code has a critical bug

Synthesis:
  ### ⚠️ Concerns
  1. **Invalid CSS syntax** - Missing required `border-style` parameter
     (critical)
     
     Source: AI's CSS knowledge + Code analysis
     Evidence: Lines show "border-top: 1px" without style
     Impact: Browsers will ignore, defeating purpose of change
```

**Key Point:** AI acts as the **synthesis engine**, combining multiple data sources into cohesive analysis.

---

## Template System

### Template Hierarchy

```
results/
├── review_template.md              # Base template for single review
├── review_dashboard_template.md    # Dashboard for multi-patchset reviews
└── review_patchset_template.md     # Individual patchset assessment

Usage Pattern:

"assess review 967773" (first time)
→ Uses: review_template.md
→ Creates: review_967773.md

"check review 967773" (no changes)
→ Updates: review_967773.md (adds check history)

"check review 967773 latest only" (new patchset detected)
→ Creates: review_967773_patchset_2.md (from patchset_template.md)

"check review 967773 create patchsets" (multiple patchsets)
→ Creates: review_967773.md (from dashboard_template.md)
→ Creates: review_967773_patchset_1.md (from patchset_template.md)
→ Creates: review_967773_patchset_2.md (from patchset_template.md)
→ Creates: review_967773_patchset_3.md (from patchset_template.md)
```

### Template Placeholder Types

```
[Bracketed] Placeholders:
  - [Review Number] → Simple text replacement
  - [Title] → From MCP agent data
  - [Date] → Current date/time
  - [Author] → From MCP agent data

Section Placeholders:
  **Purpose:** [What does this change do?]
  → AI generates narrative explanation

Checklist Placeholders:
  - [ ] Code follows project style guidelines
  → AI evaluates and checks/unchecks

Conditional Sections:
  **Breaking Changes:** YES / NO
  → AI selects appropriate value

Code Block Placeholders:
  ```bash
  # Commands to test this change
  [specific test commands]
  ```
  → AI generates context-specific commands
```

---

## MCP Agent Integration

### Agent Selection Logic

```
Review URL Analysis:
  
  https://review.opendev.org/... 
    → @opendev-reviewer-agent
    → opendev-review-agent/server.py
    → Gerrit API
  
  https://github.com/.../pull/...
    → @github-reviewer-agent
    → github-agent/server.py
    → GitHub API (requires token)
  
  https://gitlab.cee.redhat.com/.../merge_requests/...
    → @gitlab-cee-agent
    → gitlab-rh-agent/server.py
    → GitLab API (requires token)
```

### Agent Data Contract

**What AI Expects from MCP Agents:**

```json
{
  "change_number": "967773",
  "title": "Fix inconsistent borders for rows with chevrons",
  "author": "Tatiana Ovchinnikova",
  "author_email": "t.v.ovtchinnikova@gmail.com",
  "project": "openstack/horizon",
  "branch": "master",
  "status": "NEW",
  "created": "2025-11-19 20:42:59",
  "updated": "2025-11-21 01:52:00",
  "files_changed": [
    "openstack_dashboard/dashboards/project/templates/key_pairs/_keypairs_table.html"
  ],
  "file_stats": [
    {
      "file": "openstack_dashboard/dashboards/project/templates/key_pairs/_keypairs_table.html",
      "insertions": 2,
      "deletions": 0,
      "net_changes": 2
    }
  ],
  "total_files": 1,
  "total_insertions": 2,
  "total_deletions": 0,
  "review_comments": [
    {
      "file": "/PATCHSET_LEVEL",
      "line": 0,
      "message": "LGTM, trivial.",
      "author": "Ivan Anfimov"
    },
    {
      "file": ".../_keypairs_table.html",
      "line": 55,
      "message": "...",
      "author": "Owen McGonagle"
    }
  ]
}
```

**How AI Uses This Data:**

```
change_number → Review Number field
title → Document title
author → Review Information section
status → Current status tracking
files_changed → Technical Analysis section
file_stats → Change Overview metrics
review_comments → Reviewer Comments Analysis section
total_insertions/deletions → Scope statistics
```

---

## Example Execution Trace

### Actual Execution: "assess review 967773"

```
[00:00.000] User Input
  Input: "assess review 967773"
  
[00:00.100] AI Pattern Match
  Matched: askme/keys/review_assess.yaml
  Extracted: review_number=967773
  URL: https://review.opendev.org/c/openstack/horizon/+/967773
  
[00:00.200] Script Invocation
  Tool: run_terminal_cmd
  Command: cd <mymcp-repo-path>/workspace && \
           ./scripts/fetch-review.sh --with-assessment opendev \
           https://review.opendev.org/c/openstack/horizon/+/967773
  
[00:01.500] Script Execution (fetch-review.sh)
  [00:01.500] Parse URL
    Type: opendev
    Project: horizon
    Change: 967773
  
  [00:01.600] Check existing directory
    Path: workspace/horizon-967773/
    Exists: Yes
    Action: Reuse existing
  
  [00:01.700] Load workspace config
    Config: workspace/.workspace-config
    Project: iproject
  
  [00:01.800] Create assessment template
    Source: results/review_template.md
    Destination: workspace/iproject/results/review_967773.md
    Action: Copy template
  
  [00:01.900] Script Complete
    Exit code: 0
    Output: "Assessment template ready: workspace/iproject/results/review_967773.md"
  
[00:02.000] AI Reads Script Output
  Template path: workspace/iproject/results/review_967773.md
  Review code: workspace/horizon-967773/
  
[00:02.100] MCP Agent Invocation
  Tool: mcp_opendev-reviewer-agent_gerrit_review_fetcher
  Params: review_url=https://review.opendev.org/c/openstack/horizon/+/967773
  
[00:03.500] MCP Agent Response
  Received: JSON with review metadata (see Data Contract above)
  
[00:03.600] Read Code Changes
  Tool: run_terminal_cmd
  Command: cd workspace/horizon-967773 && git show HEAD
  
[00:04.000] Git Output
  Commit: 9863f8bd5fa7feeb73b0945db89bb278331f99a4
  Author: Tatiana Ovchinnikova
  Date: Wed Nov 19 14:41:23 2025
  
  Diff:
  +  border-top: 1px;
  +  border-bottom: 1px;
  
[00:04.100] AI Analysis
  [00:04.100] Parse diff
    File: _keypairs_table.html
    Changes: 2 lines added
    Type: CSS addition
  
  [00:04.200] Validate CSS
    Line: "border-top: 1px;"
    Issue: Missing border-style (required parameter)
    Severity: Critical (browsers will ignore)
  
  [00:04.300] Review comments
    Ivan: "LGTM, trivial"
    Analysis: Premature approval, missed CSS error
    
    Owen: "border-top: 1px solid #ddd;"
    Analysis: Correctly identified fix
  
  [00:04.400] Generate recommendation
    Decision: -1 (Do Not Merge)
    Reason: Invalid CSS syntax will not work
    Conditions: Fix syntax, add 'solid #ddd'
  
[00:05.000] Fill Template
  Tool: write (or search_replace)
  File: workspace/iproject/results/review_967773.md
  
  Sections filled:
  ✓ Patchset Information (from MCP agent)
  ✓ Review Information (from MCP agent)
  ✓ Check History (AI-generated, first check)
  ✓ Executive Summary (AI synthesis)
  ✓ Decision (AI recommendation: -1)
  ✓ Key Findings (AI analysis: Invalid CSS)
  ✓ Reviewer Comments Analysis (AI interpretation)
  ✓ Change Overview (from MCP + Git)
  ✓ Code Quality Assessment (AI evaluation)
  ✓ Technical Analysis (AI detailed review)
  ✓ Review Checklist (AI evaluation)
  ✓ Testing Verification (AI-generated)
  ✓ Recommendations (AI suggestions)
  ✓ Metadata (tracking data)
  
  Result: 419 lines written
  
[00:06.000] Report to User
  Output:
    ✅ Assessment Complete: Review 967773
    
    📋 Assessment Summary:
    Review: 967773 - Fix inconsistent borders
    Recommendation: ❌ -1 (Do Not Merge)
    Issue: Invalid CSS syntax
    Location: workspace/iproject/results/review_967773.md
  
[00:06.100] COMPLETE
  Total time: ~6 seconds
  Files created: 1 (review_967773.md)
  Lines written: 419
```

---

## Summary

### The Orchestration Stack

```
Layer 1: User Intent
  "assess review 967773"

Layer 2: Askme Framework (Pattern Recognition)
  review_assess.yaml → Script command with parameters

Layer 3: Script Execution (Environment Setup)
  fetch-review.sh → Clone code, create template

Layer 4: MCP Agents (Metadata Retrieval)
  @opendev-reviewer-agent → Review data from Gerrit API

Layer 5: Code Reading (Direct Analysis)
  git show HEAD → Actual code changes

Layer 6: AI Orchestration (Synthesis & Analysis)
  Combine all sources → Analyze → Generate recommendations

Layer 7: Template Filling (Documentation)
  Fill placeholders → Write complete assessment

Layer 8: User Output (Communication)
  Summary → Recommendation → File location
```

### Key Principles

1. **Separation of Concerns**
   - Scripts handle environment/setup
   - MCP agents handle external data
   - AI handles analysis and synthesis

2. **Template-Driven**
   - Structure defined in templates
   - Content generated dynamically
   - Consistent output format

3. **Multi-Source Intelligence**
   - MCP agents: Structured metadata
   - Git: Code changes
   - AI: Analysis and recommendations

4. **Cumulative Tracking**
   - Check history in documents
   - Metadata for future checks
   - Patchset evolution tracking

5. **Natural Language Interface**
   - Simple user commands
   - Complex orchestration hidden
   - Intelligent interpretation

---

**Document Version:** 1.0  
**Created:** 2025-11-22  
**Example:** Review 967773 assessment  
**Framework:** mymcp askme system

---

## See Also

- [askme/keys/review_assess.yaml](../askme/keys/review_assess.yaml) - Command definition
- [workspace/scripts/fetch-review.sh](../workspace/scripts/fetch-review.sh) - Script implementation
- [results/review_template.md](../results/review_template.md) - Template structure
- [opendev-review-agent/server.py](../opendev-review-agent/server.py) - MCP agent code
- [askme/EXECUTE_KEYS_USAGE.md](../askme/EXECUTE_KEYS_USAGE.md) - Usage guide
- [askme/CHECK_FRAMEWORK.md](../askme/CHECK_FRAMEWORK.md) - Check workflow details

