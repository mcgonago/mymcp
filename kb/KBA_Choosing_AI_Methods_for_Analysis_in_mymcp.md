# KBA: Choosing AI Methods for Analysis in mymcp

**Knowledge Base Article ID**: KBA-001  
**Topic**: AI Interaction Methods for Documentation Generation  
**Audience**: mymcp users (from beginners to advanced)  
**Last Updated**: 2025-11-23

---

## Table of Contents

1. [Overview](#overview)
2. [The Four Methods](#the-four-methods)
3. [Method 1: AI Natural Language](#method-1-ai-natural-language)
4. [Method 2: Manual with Templates](#method-2-manual-with-templates)
5. [Method 3: Reference Examples](#method-3-reference-examples)
6. [Method 4: askme Templates](#method-4-askme-templates)
5. [Decision Framework](#decision-framework)
6. [How AI Interprets Your Requests](#how-ai-interprets-your-requests)
7. [AI/LLM Concepts Explained](#aillm-concepts-explained)
8. [Out-of-the-Box Experience](#out-of-the-box-experience)
9. [Further Learning Resources](#further-learning-resources)

---

## Overview

The `mymcp` repository provides **four distinct methods** for generating analysis, documentation, and feature planning artifacts. Each method leverages different AI capabilities and serves different use cases.

### Why Multiple Methods?

Different tasks require different levels of:
- **AI autonomy** - How much does the AI decide vs. you?
- **Structure enforcement** - How strictly is the format controlled?
- **Repeatability** - How consistent are the results across runs?
- **Context provision** - How much domain knowledge is pre-loaded?

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Method Spectrum                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Low Structure ◄──────────────────────────► High Structure  │
│  High AI Freedom                         Strict Format      │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │ 
│  │ Method 1 │  │ Method 3 │  │ Method 4 │  │ Method 2 │     │
│  │ Natural  │  │Reference │  │  askme   │  │ Manual   │     │
│  │ Language │  │ Examples │  │ Templates│  │Templates │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## The Four Methods

### Quick Comparison Table

| Method | User Effort | AI Autonomy | Structure | Repeatability | Best For |
|--------|-------------|-------------|-----------|---------------|----------|
| **1. Natural Language** | Low | High | Flexible | Medium | Quick exploration, spikes |
| **2. Manual Templates** | High | None | Strict | High | Precise control, learning |
| **3. Reference Examples** | Medium | Medium | Guided | Medium-High | Complex features, consistency |
| **4. askme Templates** | Low-Medium | Medium | Strict | High | Standardized workflows, automation |

---

## Method 1: AI Natural Language

### What It Is

You give the AI a **natural language request** without referencing specific templates or examples. The AI uses its **internalized knowledge** of documentation patterns to generate appropriate artifacts.

### Example Request

```
Full spike for OSPRH-16421
```

### How AI Processes This

```
┌─────────────────────────────────────────────────────────────┐
│  User Request: "Full spike for OSPRH-16421"                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  AI Pattern Recognition (Zero-Shot Learning)                │
├─────────────────────────────────────────────────────────────┤
│  1. Identifies "spike" as a Scrum/Agile artifact            │
│  2. Recognizes "OSPRH-XXXXX" as a JIRA ticket pattern       │
│  3. Retrieves internalized spike structure from training    │
│  4. Infers need for: spike.md, patchsets, design docs       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Codebase Context Gathering (In-Context Learning)           │
├─────────────────────────────────────────────────────────────┤
│  1. Searches for existing spikes in analysis/ directory     │
│  2. Reads similar feature analysis (e.g., OSPRH-12803)      │
│  3. Identifies templates in analysis/ if available          │
│  4. Reviews README.md for repository conventions            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Structure Synthesis (Few-Shot Learning)                    │
├─────────────────────────────────────────────────────────────┤
│  - Combines: LLM training + codebase examples + templates   │
│  - Adapts structure to match repository patterns            │
│  - Generates: spike.md, patchset_X.md, design.md, README.md │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────┐
│  Output: Generated artifacts in workspace/iproject/analysis/ │
└──────────────────────────────────────────────────────────────┘
```

### AI Internals

**LLM Capabilities Used:**
1. **Zero-Shot Learning** - Understanding "spike" without explicit examples
2. **Pattern Matching** - Recognizing JIRA ticket formats (OSPRH-XXXXX)
3. **Semantic Search** - Finding relevant existing documentation
4. **Structure Inference** - Deriving document organization from context
5. **Template Synthesis** - Combining multiple patterns into coherent output

**What the AI "Knows":**
- Industry-standard documentation patterns (from training data)
- Agile/Scrum terminology (spike, patchset, epic, story)
- Common software analysis structures
- Markdown formatting conventions
- Your repository's existing patterns (from codebase context)

### When to Use

✅ **Use Method 1 when:**
- You want **fast results** without specifying every detail
- Exploring a new feature and need a starting point
- The AI has access to similar examples in the codebase
- You trust the AI to choose appropriate structure

❌ **Avoid Method 1 when:**
- You need **exact** section headings or formats
- Working on a novel document type with no precedent
- Multiple people need identical structure (use askme instead)
- You're learning the documentation structure yourself

### Example Workflow

```bash
# User says:
"Full spike for OSPRH-16421"

# AI does:
1. Searches codebase for "spike" examples
2. Finds analysis/spike_template.md (if exists)
3. Finds analysis/analysis_new_feature_966349/spike.md (reference)
4. Generates new spike using combined patterns
5. Creates in workspace/iproject/analysis/analysis_new_feature_osprh_16421/
6. Follows mymcp conventions (workspace policy)
```

### Advantages

- **Speed** - Fastest method for experienced users
- **Flexibility** - AI adapts to context
- **Low cognitive load** - Just describe what you want
- **Natural** - Feels like talking to a colleague

### Disadvantages

- **Variability** - Results may differ between runs
- **Black box** - Less visibility into AI's reasoning
- **Dependency** - Requires AI to have learned patterns
- **Unpredictable** - May miss specific requirements

---

## Method 2: Manual with Templates

### What It Is

You **manually copy** template files from `analysis/` directory and fill them in yourself. **No AI involvement** in generation—you're in complete control.

### Example Workflow

```bash
# Step 1: Copy template
cp analysis/spike_template.md \
   workspace/iproject/analysis/analysis_new_feature_osprh_16421/spike.md

# Step 2: Edit manually
vim workspace/iproject/analysis/analysis_new_feature_osprh_16421/spike.md

# Step 3: Fill in sections
# ... (you do all the writing)
```

### Available Templates

| Template File | Purpose | Sections |
|---------------|---------|----------|
| `analysis/spike_template.md` | Initial investigation | Context, Goals, Approach, Findings, Risks |
| `analysis/patchset_template.md` | Implementation plan | Overview, Changes, Testing, Migration |
| `analysis/design_template.md` | Design rationale | Architecture, Decisions, Tradeoffs |

### AI Role

**During Creation:** None - You're the author.

**After Creation:** AI can:
- Review your completed document
- Suggest improvements
- Fill in missing sections (if requested)
- Cross-reference with code

### When to Use

✅ **Use Method 2 when:**
- You **know exactly** what you want to write
- Learning the documentation structure
- Maximum control is required
- No AI assistance is desired
- Working offline or without AI access

❌ **Avoid Method 2 when:**
- You want AI to draft content
- Time is limited
- You're unfamiliar with the domain
- The task is repetitive (use askme instead)

### Advantages

- **Total control** - You decide every word
- **Predictable** - No AI surprises
- **Educational** - Learn the structure deeply
- **Offline** - No AI/network required
- **Privacy** - No data sent to AI

### Disadvantages

- **Time-consuming** - Slowest method
- **Requires expertise** - You must know the content
- **No assistance** - AI can't help with drafting
- **Manual errors** - No automated validation

---

## Method 3: Reference Examples

### What It Is

You **explicitly direct the AI** to use specific existing documents as structural references. This is **few-shot learning** at work.

### Example Request

```
Create a spike for OSPRH-16421 using the same structure as 
analysis/analysis_new_feature_966349/spike.md
```

### How AI Processes This

```
┌─────────────────────────────────────────────────────────────┐
│  User Request: "...using same structure as 966349/spike.md" │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Few-Shot Learning Pipeline                                 │
├─────────────────────────────────────────────────────────────┤
│  1. Read reference: analysis/.../966349/spike.md            │
│  2. Extract structure:                                      │
│     - Section headings                                      │
│     - Subsection hierarchy                                  │
│     - Content patterns (tables, lists, code blocks)         │
│     - Markdown formatting conventions                       │
│  3. Identify "template patterns" from reference             │
│  4. Create "mental template" for new document               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Content Generation (Constrained by Reference)              │
├─────────────────────────────────────────────────────────────┤
│  - Apply structure from 966349/spike.md                     │
│  - Fill with content relevant to OSPRH-16421                │
│  - Maintain same section depth, ordering, style             │
│  - Preserve table/list formats                              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Output: New spike matching reference structure             │
└─────────────────────────────────────────────────────────────┘
```

### AI Internals

**LLM Capabilities Used:**
1. **Few-Shot Learning** - Learning from 1-3 examples provided
2. **Pattern Extraction** - Identifying structural elements
3. **Transfer Learning** - Applying structure to new content
4. **Constrained Generation** - Staying within reference format

**What Makes This Powerful:**
- **Explicit instruction** reduces AI guessing
- **Concrete example** provides clear expectations
- **Consistency** - Multiple documents share structure
- **Quality inheritance** - Good examples → good outputs

### When to Use

✅ **Use Method 3 when:**
- You have a **reference document** you like
- Consistency across multiple features is critical
- The reference represents your desired standard
- Working on a similar feature to an existing one

❌ **Avoid Method 3 when:**
- No suitable reference exists
- You want AI to choose optimal structure
- Reference is outdated or poorly structured
- Need automation (askme is better)

### Example Workflow

```bash
# User says:
"Create spike for OSPRH-16421 matching the structure of 
 workspace/iproject/analysis/analysis_new_feature_966349/spike.md"

# AI does:
1. read_file(workspace/iproject/analysis/.../966349/spike.md)
2. Analyzes:
   ## Context and Background
   ## Goals
   ## Approach
   ### Phase 1: Investigation
   ### Phase 2: Implementation
   ## Findings
   ## Risks
   ## Next Steps
3. Generates new spike.md with SAME headings
4. Fills content relevant to OSPRH-16421
5. Saves to workspace/iproject/analysis/analysis_new_feature_osprh_16421/
```

### Advantages

- **Consistency** - Guaranteed structural match
- **Quality control** - Choose your reference carefully
- **Clarity** - AI knows exactly what you want
- **Team alignment** - Everyone uses same structure

### Disadvantages

- **Reference dependency** - Needs good examples
- **Less flexibility** - Locked to reference structure
- **Manual specification** - Must identify reference each time
- **Not automatable** - Can't easily script this

---

## Method 4: askme Templates

### What It Is

The **askme framework** is mymcp's **prompt automation system**. You define **YAML keys** with:
- Template files (with placeholders)
- Configuration (paths, variables)
- Instructions (for AI)

Then generate prompts with `./ask_me.sh <key>`.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    askme System Architecture                │
└─────────────────────────────────────────────────────────────┘

┌───────────────────┐
│  YAML Key File    │  (askme/keys/my_feature.yaml)
│  ┌─────────────┐  │
│  │ name:       │  │  Defines:
│  │ template:   │  │  - Which template to use
│  │ variables:  │  │  - Values to inject
│  │ output_dir: │  │  - Where to save results
│  │ instructions│  │  - AI guidance
│  └─────────────┘  │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  Template File    │  (askme/templates/feature_analysis.template)
│  ┌─────────────┐  │
│  │ # Analysis  │  │  Contains:
│  │ for {JIRA}  │  │  - Markdown structure
│  │             │  │  - Placeholders: {JIRA}, {FEATURE}, etc.
│  │ ## Context  │  │  - Standard sections
│  │ {CONTEXT}   │  │  - Instructions for AI
│  └─────────────┘  │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  ./ask_me.sh      │  (generates prompt)
│  ┌─────────────┐  │
│  │ 1. Read YAML│  │  Process:
│  │ 2. Read tmpl│  │  - Merge YAML + template
│  │ 3. Substitute│  │  - Replace placeholders
│  │ 4. Output   │  │  - Expand paths ({WORKSPACE_PATH})
│  │    prompt   │  │  - Generate final ask
│  └─────────────┘  │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  Generated Prompt │  (stdout or file)
│  ┌─────────────┐  │
│  │ Complete    │  │  Contains:
│  │ instructions│  │  - Filled template
│  │ for AI with │  │  - All context
│  │ all values  │  │  - Precise instructions
│  │ filled in   │  │  - File paths
│  └─────────────┘  │
└────────┬──────────┘
         │
         ▼  (paste into Cursor)
┌───────────────────┐
│  AI Executes      │
│  ┌─────────────┐  │
│  │ Reads files │  │  AI:
│  │ Analyzes    │  │  - Follows structured instructions
│  │ Generates   │  │  - Creates artifacts
│  │ Saves docs  │  │  - Minimal ambiguity
│  └─────────────┘  │
└───────────────────┘
```

### Example: askme Key File

```yaml
# askme/keys/osprh_16421.yaml
name: "Analysis for OSPRH-16421: Expandable Rows"
template: "feature_spike.template"
variables:
  JIRA_TICKET: "OSPRH-16421"
  FEATURE_NAME: "Add expandable rows to Images table"
  REFERENCE_REVIEW: "966349"
  REFERENCE_TICKET: "OSPRH-12803"
  PROJECT: "horizon"
workspace_path: "{WORKSPACE_PATH}/analysis/analysis_new_feature_osprh_16421"
instructions: |
  Create a complete spike analysis for this feature.
  Use the structure from analysis_new_feature_966349 as reference.
  Include all phases: investigation, design, implementation, testing.
```

### Example: Template File

```markdown
# askme/templates/feature_spike.template

# Spike: {FEATURE_NAME}

**JIRA**: {JIRA_TICKET}
**Reference**: Review {REFERENCE_REVIEW} ({REFERENCE_TICKET})
**Project**: {PROJECT}
**Created**: {DATE}

## Context and Background

{CONTEXT}

## Goals

- Investigate feasibility of {FEATURE_NAME}
- Identify dependencies on {REFERENCE_TICKET}
- Plan implementation approach

## Reference Implementation

Review the following for structural guidance:
- analysis/analysis_new_feature_{REFERENCE_REVIEW}/

## Deliverables

1. spike.md (this document)
2. patchset_1_*.md
3. design.md
4. README.md

---
**AI Instructions:**
{instructions}
```

### Usage

```bash
# Generate the prompt
./ask_me.sh osprh_16421

# Output (to terminal or file):
# Complete prompt with all placeholders filled
# Ready to paste into Cursor

# Paste into Cursor, AI executes
```

### How AI Processes askme Prompts

```
┌─────────────────────────────────────────────────────────────┐
│  AI Receives: Fully-formed prompt from askme                │
├─────────────────────────────────────────────────────────────┤
│  Prompt contains:                                           │
│  1. Exact file paths (workspace, references)                │
│  2. Specific instructions (from YAML)                       │
│  3. Template structure (from .template file)                │
│  4. All variables filled in (JIRA, feature name, etc.)      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  AI Processing (Instruction-Following Mode)                 │
├─────────────────────────────────────────────────────────────┤
│  - No guessing required (paths provided)                    │
│  - Structure pre-defined (template)                         │
│  - References explicit (YAML)                               │
│  - Output location specified (workspace_path)               │
│  - Minimal decision-making overhead                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Execution: High-precision, low-variance                    │
└─────────────────────────────────────────────────────────────┘
```

### When to Use

✅ **Use Method 4 when:**
- You have **repeatable workflows**
- Multiple people need to generate same docs
- Standardization is critical
- You want **automation** (CI/CD, scripts)
- Onboarding new team members
- Complex prompts with many parameters

❌ **Avoid Method 4 when:**
- One-off tasks (overhead not worth it)
- Exploratory work (too rigid)
- You don't want to maintain YAML/templates
- Simple requests (Method 1 is faster)

### Advantages

- **Repeatability** - Identical results every time
- **Standardization** - Team-wide consistency
- **Automation** - Script-friendly
- **Onboarding** - New users run same commands
- **Version control** - Templates evolve with repo
- **Low error rate** - Less ambiguity for AI

### Disadvantages

- **Setup overhead** - Must create YAML + templates
- **Maintenance** - Update templates when structure changes
- **Less flexible** - Locked to defined patterns
- **Learning curve** - Users must understand askme system

---

## Decision Framework

### Flowchart: Which Method Should I Use?

```
                    START: Need to create documentation
                                    |
                                    ▼
                    ┌───────────────────────────────┐
                    │ Do you know EXACTLY what      │
                    │ content/structure you want?   │
                    └───────────┬───────────────────┘
                                │
                ┌───────────────┴───────────────┐
                │                               │
               YES                             NO
                │                               │
                ▼                               ▼
    ┌───────────────────────┐      ┌───────────────────────┐
    │ Want AI to help       │      │ Want AI to decide     │
    │ write content?        │      │ structure?            │
    └───────┬───────────────┘      └───────┬───────────────┘
            │                               │
    ┌───────┴────────┐              ┌──────┴─────────┐
   YES              NO              YES              NO
    │                │               │                │
    ▼                ▼               ▼                ▼
┌─────────┐   ┌──────────┐   ┌─────────┐     ┌──────────┐
│ Method 3│   │ Method 2 │   │ Method 1│     │ Method 4 │
│Reference│   │ Manual   │   │ Natural │     │  askme   │
│Examples │   │Templates │   │Language │     │ Templates│
└─────────┘   └──────────┘   └─────────┘     └──────────┘
    │                │             │                │
    └────────────────┴─────────────┴────────────────┘
                          │
                          ▼
            ┌──────────────────────────┐
            │ Additional Considerations │
            └──────────┬───────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
  ┌──────────┐  ┌──────────┐  ┌──────────┐
  │Repeatabil│  │  Speed   │  │   Team   │
  │ity needed│  │ matters  │  │alignment │
  │    ?     │  │    ?     │  │ needed?  │
  └────┬─────┘  └────┬─────┘  └────┬─────┘
       │             │              │
      YES           YES            YES
       │             │              │
       └─────────────┴──────────────┘
                     │
                     ▼
              ┌──────────┐
              │ Method 4 │
              │  askme   │
              └──────────┘
```

### Decision Matrix

Use this table to quickly decide:

| Your Situation | Recommended Method | Why |
|----------------|-------------------|-----|
| Quick spike, vague idea | Method 1 (Natural) | Fast, exploratory |
| Learning doc structure | Method 2 (Manual) | Educational, hands-on |
| Similar to existing feature | Method 3 (Reference) | Proven structure |
| Team standard workflow | Method 4 (askme) | Consistency, automation |
| First time using mymcp | Method 1 or 4 | Guided experience |
| Complex multi-phase feature | Method 3 or 4 | Structure matters |
| One-off analysis | Method 1 | Overhead not justified |
| Weekly status reports | Method 4 | Repeatable automation |
| Novel document type | Method 2 | AI has no reference |
| Teaching others | Method 4 | Reproducible commands |

---

## How AI Interprets Your Requests

### Natural Language Processing (NLP) Pipeline

When you give the AI a request, here's what happens under the hood:

```
┌─────────────────────────────────────────────────────────────┐
│  Stage 1: Intent Classification                             │
├─────────────────────────────────────────────────────────────┤
│  Input: "Full spike for OSPRH-16421"                        │
│  ↓                                                          │
│  Tokenization: ["Full", "spike", "for", "OSPRH", "-", ...]  │
│  ↓                                                          │
│  Intent: CREATE_DOCUMENTATION                               │
│  Sub-intent: SPIKE_ANALYSIS                                 │
│  Entity: OSPRH-16421 (JIRA ticket)                          │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  Stage 2: Context Retrieval (RAG - Retrieval Augmented Gen) │
├─────────────────────────────────────────────────────────────┤
│  Semantic Search in Codebase:                               │
│  - Query: "spike analysis feature documentation"            │
│  - Results:                                                 │
│    1. analysis/spike_template.md (relevance: 0.95)          │
│    2. analysis/analysis_new_feature_966349/ (relevance: 0.87│
│    3. README.md sections (relevance: 0.72)                  │
│  ↓                                                          │
│  Read relevant files into context window                    │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  Stage 3: Plan Generation (Chain-of-Thought Reasoning)      │
├─────────────────────────────────────────────────────────────┤
│  AI Reasoning (internal monologue):                         │
│  1. "User wants spike → need spike.md"                      │
│  2. "'Full' implies complete → patchsets + design + README" │
│  3. "Found template → use as base structure"                │
│  4. "Found 966349 example → learn patterns from it"         │
│  5. "Workspace policy → create in iproject/"                │
│  ↓                                                          │
│  Plan:                                                      │
│  [ ] Create workspace/iproject/analysis/...16421/           │
│  [ ] Generate spike.md                                      │
│  [ ] Generate patchset_1.md                                 │
│  [ ] Generate design.md                                     │
│  [ ] Generate README.md                                     │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  Stage 4: Tool Selection & Execution                        │
├─────────────────────────────────────────────────────────────┤
│  Available tools:                                           │
│  - read_file, write, search_replace, codebase_search, ...   │
│  ↓                                                          │
│  Selected tool sequence:                                    │
│  1. codebase_search("spike template structure")             │
│  2. read_file("analysis/spike_template.md")                 │
│  3. read_file("analysis/.../966349/spike.md")               │
│  4. write("workspace/iproject/analysis/.../spike.md")       │
│  5. write(...patchset_1.md)                                 │
│  6. ... (continue for all files)                            │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  Stage 5: Self-Correction & Validation                      │
├─────────────────────────────────────────────────────────────┤
│  AI checks:                                                 │
│  ✓ Files created in correct location?                       │
│  ✓ Structure matches template?                              │
│  ✓ All sections present?                                    │
│  ✓ Markdown syntax valid?                                   │
│  ✓ Cross-references correct?                                │
│  ↓                                                          │
│  If errors detected → fix them                              │
│  If missing content → fill it in                            │
└─────────────────────────────────────────────────────────────┘
```

### Key AI Concepts in Action

#### 1. **Zero-Shot Learning**
   - **What it is**: AI performs a task without seeing examples
   - **Example**: "Create a spike for OSPRH-16421" (no template shown)
   - **How**: LLM training data includes similar documentation patterns

#### 2. **Few-Shot Learning**
   - **What it is**: AI learns from 1-3 examples provided in the prompt
   - **Example**: "Use structure from 966349/spike.md"
   - **How**: AI extracts patterns from example, applies to new task

#### 3. **Retrieval-Augmented Generation (RAG)**
   - **What it is**: AI retrieves relevant docs before generating
   - **Example**: Searching codebase for "spike" before creating one
   - **How**: `codebase_search` tool provides context

#### 4. **Chain-of-Thought (CoT) Reasoning**
   - **What it is**: AI breaks complex tasks into sequential steps
   - **Example**: "Full spike" → plan → execute → validate
   - **How**: Internal reasoning before tool calls

#### 5. **In-Context Learning**
   - **What it is**: AI learns from the current conversation/codebase
   - **Example**: Reading your repository's patterns, then applying them
   - **How**: Files read during session inform AI's understanding

### Trigger Words and Patterns

The AI recognizes certain **keywords** that activate specific behaviors:

| Keyword/Phrase | AI Interprets As | Action Triggered |
|----------------|------------------|------------------|
| "Full spike" | Complete analysis required | Create all docs (spike, patchsets, design, README) |
| "OSPRH-XXXXX" | JIRA ticket reference | Search for related tickets in codebase |
| "using structure from X" | Few-shot learning request | Read X as template |
| "based on template Y" | Template-guided generation | Use Y as strict structure |
| "similar to Z" | Reference learning | Analyze Z for patterns, adapt |
| "create analysis" | Documentation task | Look for analysis/ templates |
| "assess review" | Code review task | Fetch from MCP agent, analyze |

---

## AI/LLM Concepts Explained

### What is an LLM?

**LLM** = **Large Language Model**

A neural network trained on massive text datasets (books, code, web) to:
- Predict next words in a sequence
- Understand semantic meaning
- Generate coherent text
- Follow instructions
- Reason about problems

**In mymcp context**: Claude Sonnet 4.5 powers Cursor AI

### Key LLM Capabilities

#### 1. **Transformer Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│  Transformer Model (Simplified)                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Input: "Full spike for OSPRH-16421"                        │
│    ↓                                                        │
│  ┌────────────────────────────────────────┐                 │
│  │  Tokenization                          │                 │
│  │  ["Full", "spike", "for", "OSPRH",...] │                 │
│  └────────────┬───────────────────────────┘                 │
│               ↓                                             │
│  ┌────────────────────────────────────────┐                 │
│  │  Embedding Layer                       │                 │
│  │  (Convert tokens to vectors)           │                 │
│  │  [0.23, -0.45, ...], [0.89, 0.12, ...] │                 │
│  └────────────┬───────────────────────────┘                 │
│               ↓                                             │
│  ┌────────────────────────────────────────┐                 │
│  │  Self-Attention Mechanism              │                 │
│  │  (Relate "spike" ↔ "OSPRH-16421")     │                  │
│  │  Weight: "spike" + "for" + JIRA       │                  │
│  └────────────┬───────────────────────────┘                 │
│               ↓                                             │
│  ┌────────────────────────────────────────┐                 │
│  │  Feed-Forward Network                  │                 │
│  │  (Deep reasoning layers)               │                 │
│  └────────────┬───────────────────────────┘                 │
│               ↓                                             │
│  Output: Intent="CREATE_SPIKE"                              │
│          Entity="OSPRH-16421"                               │
│          Action="generate_documentation"                    │
└─────────────────────────────────────────────────────────────┘
```

#### 2. **Attention Mechanism**

How AI "focuses" on relevant parts of input:

```
User: "Create spike for OSPRH-16421 similar to review 966349"

Attention Weights (what AI focuses on):
┌──────────────────────────────────────────────┐
│ Token        Attention Weight  Meaning       │  
├──────────────────────────────────────────────┤ 
│ "Create"     0.92           HIGH - Action    │
│ "spike"      0.95           HIGH - Type      │
│ "OSPRH-16421" 0.88          HIGH - Target    │
│ "similar"    0.85           HIGH - Method    │
│ "966349"     0.90           HIGH - Reference │
│ "to"         0.12           LOW - Grammar    │
│ "review"     0.65           MED - Context    │
└──────────────────────────────────────────────┘
                                                
Result: AI knows to:                            
1. CREATE (action)                              
2. SPIKE document (type)                        
3. For OSPRH-16421 (target)                     
4. Using 966349 as structural reference (method)
```                                             
                                                
#### 3. **Context Window**                      
                                                
The amount of text AI can "remember" in one session:
                                                
```                                             
┌─────────────────────────────────────────────────────────────┐
│  Claude Sonnet 4.5 Context Window: ~1M tokens               │
│  (≈ 750,000 words, or ≈ 3,000 pages)                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────────┐               │
│  │ Your Conversation History                │ 5%            │
│  ├──────────────────────────────────────────┤               │
│  │ Repository Files Read                    │ 30%           │
│  ├──────────────────────────────────────────┤               │
│  │ Tool Results (codebase_search, etc.)     │ 15%           │
│  ├──────────────────────────────────────────┤               │
│  │ Available Space for Generation           │ 50%           │
│  └──────────────────────────────────────────┘               │
│                                                             │
│  Why this matters:                                          │
│  - Can read ENTIRE spike + patchsets + design in one go     │
│  - No need to "forget" earlier conversation                 │
│  - Can reference any part of long documents                 │
└─────────────────────────────────────────────────────────────┘
```                                                            
                                                               
#### 4. **Temperature and Sampling**                           
                                                               
Controls how "creative" vs "deterministic" AI output is:       
                                                               
```                                                            
Temperature Scale:                                             
┌─────────────────────────────────────────────────────────────┐
│ 0.0                    0.5                    1.0           │
│ Deterministic          Balanced               Creative      │
│ Same output every time                        Varies widely │
│ ├──────────────────────┼──────────────────────┤             │ 
│ Method 4 (askme)       Method 3              Method 1       │
│ Repeatable             Consistent            Flexible       │
└─────────────────────────────────────────────────────────────┘

Example with Temperature=0.0 (Method 4):
  Request: "Generate spike for OSPRH-16421"
  Run 1: [spike.md with sections A, B, C, D]
  Run 2: [spike.md with sections A, B, C, D] ← IDENTICAL
  Run 3: [spike.md with sections A, B, C, D] ← IDENTICAL

Example with Temperature=0.7 (Method 1):
  Request: "Full spike for OSPRH-16421"
  Run 1: [spike.md with sections A, B, C, D, examples X, Y]
  Run 2: [spike.md with sections A, B, D, E, examples Z, W] ← DIFFERENT
  Run 3: [spike.md with sections A, C, D, F, examples Q, R] ← DIFFERENT
```

#### 5. **Prompt Engineering**

The art of crafting effective instructions for AI:

**Poor Prompt:**
```
Create docs for OSPRH-16421
```
- Ambiguous ("docs" = what kind?)
- No structure guidance
- No output location

**Good Prompt (Method 1):**
```
Full spike for OSPRH-16421
```
- Clear intent ("Full spike")
- Specific target (OSPRH-16421)
- AI knows "full" means all artifacts

**Excellent Prompt (Method 4 - askme generated):**
```
Create a complete spike analysis for OSPRH-16421: Add expandable rows to Images table.

Structure:
- Use template: analysis/spike_template.md
- Reference implementation: analysis/analysis_new_feature_966349/
- Include sections: Context, Goals, Approach, Findings, Risks

Files to create:
1. workspace/iproject/analysis/analysis_new_feature_osprh_16421/spike.md
2. workspace/iproject/analysis/analysis_new_feature_osprh_16421/patchset_1_add_expandable_rows.md
3. workspace/iproject/analysis/analysis_new_feature_osprh_16421/patchset_1_add_expandable_rows_design.md
4. workspace/iproject/analysis/analysis_new_feature_osprh_16421/README.md

Reference for structure:
- OSPRH-12803 (Key Pairs chevrons) - Review 966349

Context:
The Images table needs expandable row functionality similar to Key Pairs.
Users should click chevrons to view image details without navigating away.
```
- Extremely specific
- All paths provided
- Structure defined
- References explicit
- Minimal ambiguity

### Learning Paradigms

```
┌─────────────────────────────────────────────────────────────┐
│  How AI "Learns" During Inference (Not Training)            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌────────────────────────────────────────┐                 │
│  │ Pre-Training (OpenAI/Anthropic did)    │                 │
│  │ Billions of documents, years of work   │                 │
│  │ AI learned: language, code, patterns   │                 │
│  └────────────┬───────────────────────────┘                 │
│               ↓                                             │
│               Your session starts                           │
│               ↓                                             │
│  ┌────────────────────────────────────────┐                 │
│  │ In-Context Learning                    │                 │
│  │ (During your conversation)             │                 │
│  │                                        │                 │
│  │ You: "Full spike for OSPRH-16421"      │                 │
│  │ AI reads: spike_template.md            │                 │
│  │ AI reads: 966349/spike.md              │                 │
│  │ AI "learns": Your repo's style         │                 │
│  │                                        │                 │
│  │ This is NOT permanent training         │                 │
│  │ This is temporary context adaptation   │                 │
│  └────────────┬───────────────────────────┘                 │
│               ↓                                             │
│  ┌────────────────────────────────────────┐                 │
│  │ Few-Shot Learning                      │                 │
│  │ (You provide 1-3 examples)             │                 │
│  │                                        │                 │
│  │ You: "Use structure from 966349"       │                 │
│  │ AI: Reads 966349, extracts pattern     │                 │
│  │     Applies pattern to new document    │                 │
│  └────────────┬───────────────────────────┘                 │
│               ↓                                             │
│  ┌────────────────────────────────────────┐                 │
│  │ Zero-Shot Learning                     │                 │
│  │ (No examples, just instructions)       │                 │
│  │                                        │                 │
│  │ You: "Create spike for OSPRH-16421"    │                 │
│  │ AI: Uses pre-trained knowledge of      │                 │
│  │     what "spike" means in Agile dev    │                 │
│  └────────────────────────────────────────┘                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Out-of-the-Box Experience

### For New mymcp Users

When someone clones `mymcp` for the first time, what do they get?

#### Available Immediately (No Setup)

1. **Method 1: Natural Language**
   - ✅ Works instantly
   - ✅ AI finds templates in `analysis/`
   - ✅ Follows `docs/WORKSPACE_POLICY.md`
   - ✅ Generates in `workspace/iproject/`
   
   **First command:** `"Full spike for MYPROJECT-123"`

2. **Method 2: Manual Templates**
   - ✅ Templates in `analysis/`
   - ✅ Just copy and edit
   - ✅ No AI required
   
   **First command:** `cp analysis/spike_template.md my_spike.md`

#### Requires Minimal Setup

3. **Method 3: Reference Examples**
   - ⚠️ Need at least one example
   - ✅ Repository includes `analysis_new_feature_966349/`
   - ✅ Can use immediately
   
   **First command:** `"Create spike using structure from analysis_new_feature_966349/spike.md"`

4. **Method 4: askme Templates**
   - ⚠️ Requires creating YAML key
   - ✅ Examples in `askme/keys/`
   - ✅ System ready, just add your keys
   
   **Setup:** Copy `askme/keys/example_*.yaml`, customize
   **First command:** `./ask_me.sh my_key`

### AI Behavior for New Users

```
┌─────────────────────────────────────────────────────────────┐
│  Scenario: Brand new user, first time using mymcp           │
└─────────────────────────────────────────────────────────────┘

User: "I need to analyze a new feature PROJ-456"

AI Process:
1. Searches codebase for "analysis" patterns
   → Finds: analysis/spike_template.md ✓
   → Finds: analysis/analysis_new_feature_966349/ ✓
   → Finds: docs/WORKSPACE_POLICY.md ✓

2. Reads README.md to understand repo structure
   → Learns: workspace/iproject/ is for new work ✓
   → Learns: analysis/ contains templates ✓
   → Learns: MCP agents available ✓

3. Infers user wants:
   → Spike document (investigation)
   → Following repository patterns
   → In correct location

4. Generates:
   workspace/iproject/analysis/analysis_new_feature_proj_456/
   ├── spike.md (using spike_template.md structure)
   ├── README.md
   └── ... (additional docs as needed)

5. Explains to user what was created and where

Result: User gets properly structured output even with vague request
```

### Repository Design for Discoverability

mymcp is designed for AI to **discover** patterns:

| Discoverable Element | Location | AI Uses For | Example |
|---------------------|----------|-------------|---------|
| Templates | `analysis/*_template.md` | Structure guidance | [`analysis/spike_template.md`](https://github.com/mcgonago/mymcp/blob/main/analysis/spike_template.md) |
| Examples | `analysis/analysis_new_feature_*/` | Pattern learning | [`workspace/iproject/analysis/analysis_new_feature_966349/`](https://github.com/mcgonago/mymcp/tree/main/workspace/iproject/analysis/analysis_new_feature_966349) |
| Policies | `docs/WORKSPACE_POLICY.md` | Where to create files | [`docs/WORKSPACE_POLICY.md`](https://github.com/mcgonago/mymcp/blob/main/docs/WORKSPACE_POLICY.md) |
| Configuration | `.mymcp-config` | Path resolution | [`.mymcp-config`](https://github.com/mcgonago/mymcp/blob/main/.mymcp-config) |
| askme Examples | `askme/keys/example_*.yaml` | Workflow patterns | [`askme/keys/example_implement_chevron_fix.yaml`](https://github.com/mcgonago/mymcp/blob/main/askme/keys/example_implement_chevron_fix.yaml) |
| Agent README | `*-agent/README.md` | How to use agents | [`activity-tracker-agent/README.md`](https://github.com/mcgonago/mymcp/blob/main/activity-tracker-agent/README.md) |

**AI Self-Sufficiency:**
The repository is structured so AI can:
1. Find templates automatically
2. Learn conventions from examples
3. Follow policies without being told
4. Generate appropriate artifacts

---

## Further Learning Resources

### Understanding LLMs

#### Foundational Concepts

1. **"Attention Is All You Need" (Transformer Paper)**
   - Original paper introducing transformer architecture
   - Link: https://arxiv.org/abs/1706.03762
   - Key concept: Self-attention mechanism

2. **Anthropic's Claude Documentation**
   - https://docs.anthropic.com/
   - Explains Claude's capabilities (the model powering Cursor)
   - Prompt engineering guide

3. **OpenAI's Prompt Engineering Guide**
   - https://platform.openai.com/docs/guides/prompt-engineering
   - Best practices for instructing LLMs
   - Few-shot learning examples

#### Interactive Learning

4. **"LLM Visualization" by Jay Alammar**
   - https://jalammar.github.io/illustrated-transformer/
   - Visual explanation of how transformers work
   - Intuitive diagrams

5. **"The Illustrated GPT-2"**
   - https://jalammar.github.io/illustrated-gpt2/
   - Step-by-step walkthrough of language generation
   - Accessible for non-ML experts

### Prompt Engineering

6. **Learn Prompting**
   - https://learnprompting.org/
   - Free course on prompt engineering
   - Covers zero-shot, few-shot, chain-of-thought

7. **Cursor AI Documentation**
   - https://docs.cursor.com/
   - How Cursor uses Claude
   - Best practices for AI pair programming

### Retrieval-Augmented Generation (RAG)

8. **"Retrieval-Augmented Generation for LLMs"**
   - https://arxiv.org/abs/2005.11401
   - How AI combines search + generation
   - What `codebase_search` does

9. **LangChain Documentation**
   - https://docs.langchain.com/
   - Framework for building LLM applications
   - RAG implementation patterns

### MCP (Model Context Protocol)

10. **FastMCP Documentation**
    - https://github.com/jlowin/fastmcp
    - How mymcp agents are built
    - Creating custom tools for AI

11. **Anthropic's MCP Announcement**
    - https://www.anthropic.com/news/model-context-protocol
    - Why MCP exists
    - How it enables AI-tool integration

### Advanced Topics

12. **"Chain-of-Thought Prompting"**
    - https://arxiv.org/abs/2201.11903
    - How AI breaks down complex reasoning
    - Used in Method 1 (Natural Language)

13. **"Few-Shot Learning in Practice"**
    - https://arxiv.org/abs/2005.14165
    - Theory behind Method 3 (Reference Examples)

14. **Temperature and Sampling Methods**
    - https://huggingface.co/blog/how-to-generate
    - How to control AI creativity vs consistency

### mymcp-Specific Learning

15. **This Repository's Documentation**
    - [`README.md`](https://github.com/mcgonago/mymcp/blob/main/README.md) - Overview of all agents
    - [`docs/WORKSPACE_POLICY.md`](https://github.com/mcgonago/mymcp/blob/main/docs/WORKSPACE_POLICY.md) - Where files go
    - [`docs/CENTRAL_CONFIGURATION.md`](https://github.com/mcgonago/mymcp/blob/main/docs/CENTRAL_CONFIGURATION.md) - Path system
    - [`design/Design_MCP_Standup.md`](https://github.com/mcgonago/mymcp/blob/main/design/Design_MCP_Standup.md) - Example design process
    - [`analysis/TEMPLATES_README.md`](https://github.com/mcgonago/mymcp/blob/main/analysis/TEMPLATES_README.md) - How templates work

16. **Example Workflows**
    - [`askme/keys/example_implement_chevron_fix.yaml`](https://github.com/mcgonago/mymcp/blob/main/askme/keys/example_implement_chevron_fix.yaml) - askme example
    - [`askme/keys/example_template_pattern.yaml`](https://github.com/mcgonago/mymcp/blob/main/askme/keys/example_template_pattern.yaml) - Another askme example
    - [`workspace/iproject/analysis/analysis_new_feature_966349/`](https://github.com/mcgonago/mymcp/tree/main/workspace/iproject/analysis/analysis_new_feature_966349) - Full feature analysis
    - [`activity-tracker-agent/`](https://github.com/mcgonago/mymcp/tree/main/activity-tracker-agent) - Complete MCP agent implementation

---

## Practical Examples

### Example 1: First-Time User - Natural Language

**User (new to mymcp):**
```
I need to plan implementation for ticket DEMO-101: Add dark mode toggle
```

**AI Response:**
1. Searches codebase, finds templates
2. Creates `workspace/iproject/analysis/analysis_new_feature_demo_101/`
3. Generates:
   - `spike.md` (investigation)
   - `patchset_1_add_dark_mode_toggle.md` (implementation)
   - `design.md` (architecture decisions)
   - `README.md` (overview)
4. Uses structure from `spike_template.md`

**Outcome:** User gets complete analysis without knowing internal structure

---

### Example 2: Team Lead - askme for Standardization

**Setup (one time):**
```yaml
# askme/keys/feature_analysis_template.yaml
name: "Standard Feature Analysis"
template: "feature_complete.template"
variables:
  JIRA_TICKET: "{USER_INPUT}"
  FEATURE_NAME: "{USER_INPUT}"
  PROJECT: "{USER_INPUT}"
workspace_path: "{WORKSPACE_PATH}/analysis/analysis_new_feature_{JIRA_TICKET_LOWER}"
instructions: |
  Generate complete feature analysis including:
  - Spike (investigation)
  - Patchset plans (implementation)
  - Design document (architecture)
  - README (overview)
  Use analysis/spike_template.md, patchset_template.md, design_template.md
```

**Usage (every feature):**
```bash
./ask_me.sh feature_analysis_template
# Prompts for JIRA_TICKET, FEATURE_NAME, PROJECT
# Generates full prompt
# Paste into Cursor
```

**Outcome:** Every team member generates identical structure

---

### Example 3: Experienced Developer - Reference Examples

**User (knows exactly what they want):**
```
Create analysis for BACKEND-555 using the same structure as 
workspace/iproject/analysis/analysis_new_feature_966349/
but focus on backend API changes instead of UI
```

**AI Response:**
1. Reads `analysis_new_feature_966349/` thoroughly
2. Extracts structure:
   - 5 patchset documents
   - Design doc with specific sections
   - README with phase breakdown
3. Generates identical structure for BACKEND-555
4. Fills content with backend-specific details

**Outcome:** Proven structure, customized content

---

### Example 4: Solo Developer - Manual Control

**User (learning process, wants hands-on):**
```bash
# Copy template
cp analysis/spike_template.md \
   workspace/iproject/analysis/my_feature/spike.md

# Edit manually
vim workspace/iproject/analysis/my_feature/spike.md

# Fill in sections over several days
# Ask AI for specific help:
"Review my spike.md and suggest improvements to the Risks section"
```

**Outcome:** Deep understanding of structure, full control

---

## Summary: Method Selection Guide

### Quick Decision Table

| If you value... | Use this method | Trade-off |
|-----------------|-----------------|-----------|
| **Speed** | Method 1 (Natural) | Less control |
| **Precision** | Method 2 (Manual) | More time |
| **Consistency** | Method 4 (askme) | Setup overhead |
| **Learning** | Method 2 or 3 | Slower initially |
| **Flexibility** | Method 1 | Less repeatability |
| **Automation** | Method 4 (askme) | Requires templates |
| **Team alignment** | Method 4 | Must maintain YAML |

### The Golden Rule

**Start with Method 1 (Natural Language) for exploration.**  
**Evolve to Method 4 (askme) for production workflows.**

As you learn what works:
1. **Explore** with Method 1 (fast, flexible)
2. **Refine** with Method 3 (reference good examples)
3. **Standardize** with Method 4 (automate the proven pattern)
4. **Teach** others with Method 4 (reproducible commands)

---

## Glossary

| Term | Definition | Example |
|------|------------|---------|
| **LLM** | Large Language Model - AI trained on text | Claude Sonnet 4.5 |
| **RAG** | Retrieval-Augmented Generation - search before generating | `codebase_search` |
| **CoT** | Chain-of-Thought - breaking tasks into steps | Planning → Execution → Validation |
| **Few-Shot** | Learning from 1-3 examples | "Use structure from file X" |
| **Zero-Shot** | Performing task without examples | "Create spike for Y" |
| **MCP** | Model Context Protocol - AI tool integration | activity-tracker-agent |
| **askme** | mymcp's prompt automation system | `./ask_me.sh key` |
| **Temperature** | Controls AI randomness (0=deterministic, 1=creative) | askme uses low temperature |
| **Context Window** | How much text AI can remember | ~1M tokens for Claude |
| **Prompt Engineering** | Crafting effective AI instructions | askme templates are pre-engineered |

---

## Questions & Troubleshooting

### FAQ

**Q: Which method is "best"?**  
A: Depends on context. Method 1 for speed, Method 4 for repeatability. See [Decision Framework](#decision-framework).

**Q: Can I mix methods?**  
A: Absolutely! Use Method 1 to explore, then refine with Method 3, then automate with Method 4.

**Q: How does AI know mymcp conventions?**  
A: It reads `docs/WORKSPACE_POLICY.md`, templates, and examples during execution.

**Q: What if AI generates wrong structure?**  
A: Be more specific:
- Method 1: Add "using spike_template.md"
- Method 3: Reference a specific example
- Method 4: Use askme for guaranteed structure

**Q: Why does Method 1 give different results each time?**  
A: Higher "temperature" (AI creativity). Use Method 4 for consistency.

**Q: Can I create my own templates?**  
A: Yes! Add to `analysis/` and AI will discover them. See [Manual Templates](#method-2-manual-with-templates).

**Q: What's the difference between template and reference?**  
A: 
- **Template**: Empty structure to fill in (Method 2)
- **Reference**: Complete example to learn from (Method 3)

**Q: How do I know if askme is working?**  
A: Run `./ask_me.sh example_implement_chevron_fix` - you should see a generated prompt.

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-23 | Initial creation |

---

**See Also:**
- [`README.md`](https://github.com/mcgonago/mymcp/blob/main/README.md) - Repository overview
- [`docs/WORKSPACE_POLICY.md`](https://github.com/mcgonago/mymcp/blob/main/docs/WORKSPACE_POLICY.md) - Where to create files
- [`analysis/TEMPLATES_README.md`](https://github.com/mcgonago/mymcp/blob/main/analysis/TEMPLATES_README.md) - Template system explained
- [`design/Design_MCP_Standup.md`](https://github.com/mcgonago/mymcp/blob/main/design/Design_MCP_Standup.md) - Example of design process

**Feedback:**  
For questions or improvements to this KBA, create an issue or update this document directly.

