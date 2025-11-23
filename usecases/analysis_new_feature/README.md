# Feature Development (Analysis) Workflow Using Cursor

## Features Completed

This section tracks OpenStack Horizon features that were successfully developed and merged upstream using this systematic analysis workflow.

### Review 966349: Expandable Key Pairs Table

**Link**: [analysis/analysis_new_feature_966349](../../analysis/analysis_new_feature_966349/)

**Feature**: De-angularized the Key Pairs table by implementing a Bootstrap-based expandable row system that displays detailed key pair information (fingerprint, type, creation date) on demand. This feature replaced the AngularJS implementation with Django templates and CSS-driven interactions, improving maintainability and aligning with Horizon's modernization efforts. The implementation uses Bootstrap's native collapse component with Font Awesome chevron icons to provide a clean, accessible user experience.

**Upstream Review**: [https://review.opendev.org/c/openstack/horizon/+/966349](https://review.opendev.org/c/openstack/horizon/+/966349)

**Status**: ✅ Merged (+2 approval, Nov 2025)

---

## Overview

This workflow provides a **structured, predictable methodology** for feature development using Cursor with AI assistance. It systematically breaks down complex technical challenges into measurable deliverables with clear complexity rankings, knowledge requirements, and time estimates - enabling accurate sprint planning, parallel development, and continuous learning.

### The Challenge: Predictable Software Delivery

How do you:
- Determine technical challenges of a task in a structured way?
- Predict time needed based on knowledge requirements?
- Break large tasks into sprint-aligned (≤2 weeks) deliverables?
- Enable multiple developers to work in parallel?
- Detect scope changes and missed requirements early?
- Improve team capacity and velocity measurement?
- Harness AI assistance consistently with proven patterns?

### The Solution: Structured Spike + Patchset Methodology

This workflow answers these questions through:

1. **Complexity Analysis** - Systematic technical challenge assessment
2. **Knowledge Scoring** - Rate required expertise for accurate time estimates
3. **Incremental Delivery** - Break features into reviewable patchsets
4. **Pattern-Driven AI** - Train LLM on proven "patterns of success"
5. **Measured Artifacts** - Track complexity, time, and story points per deliverable
6. **Parallel Workflows** - Enable concurrent feature and test development

**Proven Success:** This methodology successfully delivered Review 966349 (merged upstream with +2) and Review 967269 (50% faster than estimated).

## Analysis Directory for Permanent Research

The `analysis/` directory stores permanent technical analyses and research findings:

### Purpose

- Document research methodology and findings
- Preserve institutional knowledge
- Provide reproducible research
- Cross-reference related work

### Example Analyses

- Horizon/Glance direct mode upload implementation
- CORS configuration changes
- Feature migrations and deprecations
- Integration test architecture decisions
- Key Pairs expandable row feature development (OSPRH-12803)

## The Structured Methodology

### Phase 1: Spike - Structured Technical Investigation

**Purpose**: Determine technical challenges, complexity, and knowledge requirements **before** implementation.

**Key Activities:**
1. **Technical Challenge Analysis**
   - Identify all areas of knowledge required (framework, API, UI, testing)
   - Score each area: Novice (1) → Expert (5)
   - Calculate weighted complexity score

2. **Patchset Planning**
   - Break feature into ≤2 week incremental deliverables
   - Each patchset: independent, reviewable, testable
   - Define success criteria for each increment

3. **Time Estimation**
   - Base estimate on similar work (historical data)
   - Adjust by knowledge/skill factor: `story_points = base_complexity * (6 - avg_knowledge_score)`
   - Validate: Can each patchset fit in one sprint?

4. **Test Strategy**
   - Plan test development in parallel with features
   - Define test scenarios per patchset (not just at the end)
   - Enable separate developers for feature vs. test implementation

**Deliverable**: Spike document with complexity table, patchset breakdown, and time estimates.

---

### Phase 2: Patchset Development - Incremental Delivery

**Purpose**: Implement each patchset using proven patterns, track actual vs. estimated time.

**Key Activities:**
1. **Pattern-Driven Implementation**
   - Use design documents that show code reference discovery process
   - Force AI to follow "frame of progression" (proven patterns)
   - Document: "What was copied" vs. "What was new"

2. **Parallel Development**
   - Feature implementation (Patchset N)
   - Test development (Patchset N tests)
   - Enable different developers to work concurrently

3. **Continuous Validation**
   - Test each patchset independently
   - Validate time estimates vs. actuals
   - Detect scope changes early (compare to spike)

4. **WIP Documentation**
   - Real-time development log (all issues, solutions, decisions)
   - Enables reproducibility and onboarding

**Deliverable**: Working code + tests + design document + WIP log per patchset.

---

### Phase 3: Retrospective - Continuous Improvement

**Purpose**: Update complexity table, refine estimation model, capture lessons learned.

**Key Activities:**
1. **Update Complexity Table**
   - Add "Actual Days" column
   - Compare to predicted time
   - Adjust knowledge scores if needed

2. **Story Point Validation**
   - Did story points accurately predict effort?
   - Update formula if systematic over/under-estimation

3. **Pattern Capture**
   - What new "patterns of success" emerged?
   - Update best practices document
   - Feed back into AI training for next feature

4. **Team Metrics**
   - Calculate actual capacity (story points / sprint)
   - Measure velocity trend
   - Identify knowledge gaps for training

**Deliverable**: Updated complexity table, lessons learned, refined estimation model.

---

## How AI Assistance is Structured

### Training the LLM on "Patterns of Success"

Instead of ad-hoc prompts, this methodology enforces **structured progression**:

1. **Spike Phase Patterns**
   - "Find similar code in same panel first"
   - "Check 3 other panels for consistency"
   - "Document reference code with GitHub links"
   - "Calculate 90% adapted vs. 10% new ratio"

2. **Implementation Phase Patterns**
   - "Copy, Don't Invent" - adapt existing patterns
   - "Two-template pattern for modals"
   - "Use framework features before custom code"
   - "Document every design decision with reference"

3. **Documentation Phase Patterns**
   - "Show discovery process (Thought #1-6)"
   - "Create component-by-component analysis"
   - "Track all code references with links"
   - "Separate WIP log from polished docs"

**Result**: The LLM learns to provide consistent, high-quality output that follows proven patterns, reducing variation and improving predictability.

---

## Complexity Scoring Framework

### Knowledge/Skill Factors (1-5 Scale)

| Score | Level | Description | Time Multiplier |
|-------|-------|-------------|-----------------|
| 1 | Novice | First time working with this technology | 5x base |
| 2 | Beginner | Limited experience, needs guidance | 4x base |
| 3 | Intermediate | Comfortable with basics, occasional lookup | 3x base |
| 4 | Advanced | Deep understanding, rare lookup | 2x base |
| 5 | Expert | Complete mastery, can teach others | 1x base |

### Story Point Calculation

```
Base Complexity = Estimated days for expert (score 5)
Skill Multiplier = (6 - Average Knowledge Score)
Story Points = Base Complexity * Skill Multiplier

Example:
  Base: 2 days (expert estimate)
  Knowledge: 3 (intermediate)
  Story Points = 2 * (6 - 3) = 2 * 3 = 6 points
```

### Complexity Table Template (Updated After Each Patchset)

| Patchset | Base Days | Knowledge Areas | Avg Score | Story Points | Actual Days | Variance |
|----------|-----------|-----------------|-----------|--------------|-------------|----------|
| Spike | 1 | Django(4), Horizon(3), API(4) | 3.7 | 2.3 | 1.5 | -35% |
| PS1: Generate Form | 2 | Django(4), Templates(3), JS(2) | 3.0 | 6 | 1 | **-50%** ✅ |
| PS2: Import Form | 2 | Django(4), Validation(3) | 3.5 | 5 | TBD | - |
| PS3: Download | 1.5 | Django(4), Security(3), JS(2) | 3.0 | 4.5 | TBD | - |
| PS4: Polish | 1 | CSS(4), UX(4) | 4.0 | 2 | TBD | - |
| PS5: Tests | 2 | Testing(4), Mock(3) | 3.5 | 5 | TBD | - |
| **Total** | **9.5** | - | **3.4 avg** | **24.8** | **2.5 / 9.5** | - |

**Key Insights from Table:**
- ✅ Patchset 1 completed 50% faster than predicted
- 📊 Knowledge score refinement needed (over-conservative estimate)
- 🎯 Sprint capacity: ~25 story points validated
- 📈 Velocity trend: Improving as patterns learned

---

## How to Use

For more info on guidelines and templates please see [Analysis directory README](../../analysis/README.md)

### Step 1: Create a New Analysis Document

```bash
# Create a new analysis from template
cd analysis
cp docs/analysis_template.md docs/analysis_<topic>.md
```

### Step 2: Query MCP Agents for Information

Use the MCP agents to gather information about your feature:

```bash
# Query GitHub for related PRs
@github-reviewer-agent search for [topic]

# Analyze OpenDev reviews
@opendev-reviewer-agent analyze [review]

# Check GitLab for related work
@gitlab-cee-agent analyze commit [commit-url]

# Query Jira for issue context
@jiraMcp Get details for issue [ISSUE-KEY]
```

### Step 3: Document Findings

Document your research in the analysis file:

```bash
# Edit your analysis document
vim analysis_<topic>.md
```

### Step 4: Organize Your Research

Use the analysis document to:
- Track your questions and findings
- Document decisions and rationale
- Link to relevant reviews, commits, and issues
- Provide examples and code references
- Note future work and follow-ups

## Real-World Example: Key Pairs Expandable Rows

The development of expandable rows for the Key Pairs table (OSPRH-12803) demonstrates this workflow in action:

### Analysis Documents Created

Multiple analysis documents tracked the development:
- `analysis_osprh_12803_fix_javascript_collapse_phase5_comment_1.md` through `comment_11.md`
- `HOWTO_osprh_12803_patchset_8_fix_javascript_collapse_phase5_comment_X.org` series
- `analysis_osprh_12803_fix_javascript_collapse_phase5_comment_DONE.org` (final phase)

### Research Process

1. **Initial Investigation**: Used MCP agents to understand existing AngularJS implementation
2. **Incremental Development**: Created phase-by-phase analysis documents
3. **Problem Solving**: Documented each issue encountered (spacing, borders, JavaScript execution)
4. **Solution Documentation**: Preserved the working solutions and explanations
5. **Final Assessment**: Completed with full context for future reference

### Upstream Success

The feature was successfully merged upstream with a +2 approval:
- **Review**: https://review.opendev.org/c/openstack/horizon/+/966349
- **Result**: De-angularized Key Pairs table with expandable row details
- **Benefit**: Complete historical record of the development process

## Benefits

### For Developers
- ✅ **Structured guidance** - Clear "frame of progression" for solving problems
- ✅ **Pattern library** - Proven "patterns of success" for consistent results
- ✅ **Reduced cognitive load** - Framework handles the "how to break it down"
- ✅ **Faster onboarding** - New developers follow documented patterns
- ✅ **Parallel work** - Feature and test development concurrent

### For Teams
- ✅ **Predictable planning** - Complexity scores enable accurate sprint planning
- ✅ **Measurable capacity** - Track story points per sprint, calculate velocity
- ✅ **Early risk detection** - Catch scope changes and missed requirements sooner
- ✅ **Improved estimation** - Refine model after each feature (actual vs. predicted)
- ✅ **Knowledge sharing** - All research and decisions documented in git

### For Organizations
- ✅ **Institutional memory** - Permanent knowledge base tracked in version control
- ✅ **Reproducible methodology** - New teams can replicate success patterns
- ✅ **Continuous improvement** - Learn from every feature, refine the process
- ✅ **Higher throughput** - Parallel development + accurate planning = faster delivery
- ✅ **Automated story points** - Complexity scoring reduces estimation meetings

## Directory Structure

The analysis directory is organized at the top level:

```
<mymcp-repo-path>/
├── analysis/                           # Permanent research documents
│   ├── README.md                       # Analysis directory guide
│   ├── docs/                            # Individual analysis documents
│   │   ├── analysis_template.md        # Template for new analyses
│   │   ├── analysis_template_random_topics.md  # Template for Q&A style analyses
│   ├── analysis_osprh_12803_*.md       # Key Pairs feature development docs
│   └── HOWTO_osprh_12803_*.org         # Phase-by-phase development guides
├── workspace/                          # Temporary code checkout (gitignored)
├── results/                            # Review assessments (can commit)
└── usecases/                           # Use case documentation
```

## Workflow Tips

### When to Create Analysis Documents

Create analysis documents when:
- Starting a new feature or significant change
- Researching how existing code works
- Investigating a complex bug
- Documenting architectural decisions
- Learning a new part of the codebase

### Document Naming Conventions

Use clear, descriptive names:
- `analysis_<feature_name>.md` - For feature development
- `analysis_<issue_key>.md` - For bug investigations
- `HOWTO_<topic>.org` - For step-by-step guides
- `analysis_<topic>_phase<N>.md` - For multi-phase work

### What to Include

Good analysis documents include:
- **Context**: What problem are you solving?
- **Questions**: What did you need to learn?
- **Methodology**: How did you investigate?
- **Findings**: What did you discover?
- **Decisions**: What choices did you make and why?
- **References**: Links to reviews, commits, issues, documentation
- **Code Examples**: Relevant snippets and references
- **Future Work**: What's left to do or investigate?

### Org Mode vs Markdown

Both formats work well:
- **Markdown (.md)**: Better GitHub integration, universal support
- **Org Mode (.org)**: Powerful Emacs features, folding, TODO tracking

Choose based on your preferred editor and workflow.

## Answering Key Planning Questions

### Can each patchset be done in one two-week sprint?

**Yes** - This is a core design principle:

1. **During Spike**: Break feature into patchsets where each:
   - Has ≤10 story points (2 weeks for intermediate developer)
   - Is independently reviewable and testable
   - Has clear success criteria

2. **Validation**: Use complexity table to check:
   ```
   Story Points = Base Days * (6 - Avg Knowledge Score)
   If Story Points > 10 → Split patchset further
   ```

3. **Example (OSPRH-12802)**:
   - Patchset 1: 6 story points → ✅ Fits in sprint
   - Patchset 5: 5 story points → ✅ Fits in sprint
   - Original monolithic: 24.8 points → ❌ Would require 3 sprints

**Result**: Sprint-aligned delivery with predictable completion dates.

---

### Can we automate story points based on spike and planned patchsets?

**Yes** - The complexity scoring framework enables semi-automated estimation:

1. **Automated Inputs**:
   - Base complexity (days) from spike breakdown
   - Knowledge areas identified from code references
   - Historical data (actual vs. predicted from previous features)

2. **Manual Inputs** (per developer/team):
   - Knowledge scores (1-5) for each area
   - These become more accurate over time

3. **Formula**:
   ```python
   def calculate_story_points(base_days, knowledge_areas):
       avg_score = sum(knowledge_areas.values()) / len(knowledge_areas)
       return base_days * (6 - avg_score)
   
   # Example:
   ps1 = calculate_story_points(2, {"Django": 4, "Templates": 3, "JS": 2})
   # Returns: 2 * (6 - 3.0) = 6 story points
   ```

4. **Future Enhancement**:
   - Script to generate complexity table from spike document
   - Pull knowledge scores from team profile
   - Auto-calculate story points per patchset

**Result**: Reduced estimation meetings, consistent scoring across teams.

---

### How to get tests written earlier?

**Strategy**: Plan tests **per patchset** during spike, develop **in parallel** with features.

1. **During Spike**:
   - Define test scenarios for each patchset (not just at the end)
   - Example (Patchset 1):
     - Unit tests: `GenerateKeyPairForm`, `CreateView`
     - Integration test: Form submission → Nova API call
     - UI test: Modal opens, fields validate, success message
   - Estimate test development time separately

2. **During Implementation**:
   - Assign different developers to feature vs. tests
   - Feature developer: Implements `forms.py`, `views.py`, `templates/`
   - Test developer: Implements `tests/test_forms.py`, `tests/test_views.py` in parallel
   - Both reference the same spike and design documents

3. **Patchset Structure**:
   ```
   Patchset 1 (Feature): forms.py, views.py, templates/
   Patchset 1 (Tests): tests/test_forms.py, tests/test_views.py
   ```
   Or combine into single patchset if small.

4. **Test-First Variant**:
   - Write failing tests first (TDD)
   - Feature developer makes tests pass
   - Requires very detailed spike/design docs

**Result**: Tests complete as feature develops, not as an afterthought.

---

### How to enable feature and test development in parallel?

**Prerequisites**:
1. **Detailed Design Document** - Shows exact implementation
2. **Clear API Contracts** - Function signatures, expected inputs/outputs
3. **Shared Spike** - Both developers understand the feature

**Workflow**:

```
┌─────────────────────────────────────────────────────────────┐
│ Spike Complete (Day 0)                                      │
│ - Patchset 1 Design: GenerateKeyPairForm                   │
│ - API: handle(request, data) → keypair | False             │
│ - Success criteria defined                                  │
└─────────────────────────────────────────────────────────────┘
                    │
          ┌─────────┴──────────┐
          │                    │
┌─────────▼─────────┐  ┌───────▼──────────┐
│ Developer A       │  │ Developer B      │
│ Feature           │  │ Tests            │
│ (Day 1-2)         │  │ (Day 1-2)        │
├───────────────────┤  ├──────────────────┤
│ - forms.py        │  │ - test_forms.py  │
│ - views.py        │  │ - test_views.py  │
│ - templates/      │  │ - mock API calls │
└─────────┬─────────┘  └───────┬──────────┘
          │                    │
          └─────────┬──────────┘
                    │
          ┌─────────▼──────────┐
          │ Integration        │
          │ (Day 3)            │
          │ - Merge branches   │
          │ - Run full tests   │
          │ - Fix any issues   │
          └────────────────────┘
```

**Communication**:
- Daily sync: "I changed function signature" → Test dev updates mocks
- Shared design doc: Single source of truth
- Feature branch + test branch → merge for review

**Result**: 2 developers complete in 3 days what 1 developer would need 4-5 days for.

---

### How to enable test planning earlier in development cycle?

**Shift Test Planning to Spike Phase**:

Traditional:
```
Spike (2 days) → Implement (7 days) → Oh no, need tests! (3 days)
Total: 12 days
```

This Methodology:
```
Spike (2 days, includes test planning) → Implement + Test in parallel (7 days)
Total: 9 days (25% faster)
```

**Spike Document Sections for Test Planning**:

1. **Test Scenarios (Per Patchset)**:
   ```markdown
   ### Patchset 1: Generate Key Pair Form
   
   #### Unit Tests (test_forms.py)
   - test_generate_keypair_form_valid()
   - test_generate_keypair_form_invalid_name()
   - test_generate_keypair_form_api_failure()
   - test_clean_name_validation()
   
   #### Integration Tests (test_views.py)
   - test_create_view_get()
   - test_create_view_post_success()
   - test_create_view_post_quota_exceeded()
   
   #### Manual Tests
   - Open modal, verify fields render
   - Submit valid form, verify success message
   - Test with quota at limit
   ```

2. **Test Data Requirements**:
   - Mock API responses
   - Test fixtures
   - DevStack configuration

3. **Test Complexity Scoring**:
   - Include test development in story points
   - Example: Feature (4 points) + Tests (2 points) = 6 points total

**Result**: No surprises, tests are first-class citizens in planning.

---

## Integration with Other Workflows

### Combined with Review Automation

The analysis workflow complements review automation:

1. Use review automation to fetch and analyze code
2. Create analysis documents to track your research
3. Document decisions and rationale in analysis files
4. Reference analysis documents in commit messages
5. Preserve institutional knowledge for future developers

### Combined with MCP Agents

MCP agents enhance the analysis process:
- Query multiple platforms for related work
- Gather context from issues, reviews, and commits
- Document all sources for reproducibility
- Cross-reference related changes
- Build comprehensive understanding

## Additional Resources

- [Analysis Directory README](../../analysis/README.md) - Detailed guidelines and templates
- [Analysis Template](../../analysis/docs/analysis_template.md) - Standard template
- [Analysis Template (Random Topics)](../../analysis/docs/analysis_template_random_topics.md) - Q&A style template
- [Review Automation Use Case](../review_automation/README.md) - Automated review workflow
- [Main Repository README](../../README.md) - Repository overview

## See Also

- [OpenDev Review Agent](../../opendev-review-agent/README.md) - Analyze Gerrit reviews
- [GitHub Review Agent](../../github-agent/README.md) - Analyze GitHub PRs
- [GitLab Agent](../../gitlab-rh-agent/README.md) - Analyze GitLab issues/MRs
- [Jira Agent](../../jira-agent/README.md) - Query Jira issues

