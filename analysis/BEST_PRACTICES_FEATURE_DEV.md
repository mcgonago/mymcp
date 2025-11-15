# Best Practices for Feature Development Using Cursor and MCP Agents

**Purpose**: This document captures proven best practices for systematically developing OpenStack Horizon features using Cursor, MCP agents, and comprehensive analysis documentation.

**Audience**: Developers using this repository's workflow for feature development

**Last Updated**: November 15, 2025

---

## Table of Contents

1. [Best Practices Overview](#best-practices-overview)
2. [Practice Adoption Tracking Table](#practice-adoption-tracking-table)
3. [Detailed Practice Descriptions](#detailed-practice-descriptions)
4. [How to Use This Document](#how-to-use-this-document)
5. [Contributing New Practices](#contributing-new-practices)

---

## Best Practices Overview

These practices emerged from successful development of [Review 966349: Expandable Key Pairs Table](analysis_new_feature_966349/README.md), which was merged upstream with +2 approval in November 2025.

### Practice Categories

1. **Investigation & Planning** - Practices for initial feature research
2. **Development Environment** - Setup and tooling practices
3. **Implementation** - Code development and architecture practices
4. **Code Review & Iteration** - Collaboration and feedback practices
5. **Documentation** - Analysis and knowledge preservation practices
6. **Git & Gerrit Workflow** - Version control and review system practices
7. **Quality Assurance** - Testing and verification practices

---

## Practice Adoption Tracking Table

This table tracks which features have used each best practice, with links to specific documentation showing how the practice was applied.

| # | Practice | Category | Review 966349 | Future Features |
|---|----------|----------|---------------|-----------------|
| 1 | **Create Spike Document** | Investigation | ✅ [spike.md](analysis_new_feature_966349/spike.md) | |
| 2 | **Document Two Dev Environments** | Dev Environment | ✅ [PSI](analysis_new_feature_966349/HOWTO_install_devstack_on_psi.org), [Laptop](analysis_new_feature_966349/HOWTO_install_devstack_on_laptop.org) | |
| 3 | **Create Phase-Based Analysis Documents** | Documentation | ✅ [PS001](analysis_new_feature_966349/patchset_001_initial_implementation.md), [PS008](analysis_new_feature_966349/patchset_008_bootstrap_refactor_phases_1to4.md), [PS018](analysis_new_feature_966349/patchset_018_css_refinement.md), [PS020](analysis_new_feature_966349/patchset_020_final_polish_and_merge.md) | |
| 4 | **Keep WIP Analysis Separate** | Documentation | ✅ [analysis_new_feature_966349_wip/](analysis_new_feature_966349_wip/) (24 docs) | |
| 5 | **Check Framework Solutions First** | Implementation | ✅ [Bootstrap over custom JS](analysis_new_feature_966349/patchset_008_bootstrap_refactor_phases_1to4.md#phase-2-bootstrap-native-collapse) | |
| 6 | **Use Helper Functions (DRY)** | Implementation | ✅ [get_chevron_id()](analysis_new_feature_966349/patchset_008_bootstrap_refactor_phases_1to4.md#phase-1-unique-chevron-id-generation) | |
| 7 | **Test with Multiple Items (3+)** | Quality Assurance | ✅ [3+ key pairs](analysis_new_feature_966349_wip/PHASE_1_TO_4_COMPLETE_SUMMARY.md#testing-checklist) | |
| 8 | **Use datum for Unique IDs** | Implementation | ✅ [datum usage](analysis_new_feature_966349/patchset_001_initial_implementation.md#issue-1-duplicate-chevron-ids-critical) | |
| 9 | **Prefer CSS over !important** | Implementation | ✅ [CSS specificity](analysis_new_feature_966349/patchset_018_css_refinement.md) | |
| 10 | **Accept Feedback Gracefully** | Code Review | ✅ [~20 patchsets](analysis_new_feature_966349/README.md#development-journey), [feedback summary](analysis_new_feature_966349/patchset_020_final_polish_and_merge.md#key-success-factors) | |
| 11 | **Use Consistent Topics** | Git & Gerrit | ✅ [de-angularize topic](analysis_new_feature_966349/patchset_020_final_polish_and_merge.md#phase-topic-management) | |
| 12 | **Write Detailed Commit Messages** | Git & Gerrit | ✅ [commit message improvement](analysis_new_feature_966349/patchset_020_final_polish_and_merge.md#phase-commit-message-improvement) | |
| 13 | **Create README Index** | Documentation | ✅ [README](analysis_new_feature_966349/README.md) | |
| 14 | **Document Git Commands** | Documentation | ✅ [View patchset changes](analysis_new_feature_966349/README.md#how-to-view-patchset-changes) | |
| 15 | **Run PEP8/Lint After Each Change** | Quality Assurance | ✅ [PEP8 phase](analysis_new_feature_966349/patchset_008_bootstrap_refactor_phases_1to4.md#phase-4-pep8-compliance) | |
| 16 | **Document Technical Decisions** | Documentation | ✅ [Key decisions](analysis_new_feature_966349/README.md#key-technical-decisions) | |
| 17 | **Learn from Maintainers** | Code Review | ✅ [CSS simplification](analysis_new_feature_966349/README.md#reviewer-feedback-highlights) | |
| 18 | **Break Work into Logical Phases** | Investigation | ✅ [4 phases](analysis_new_feature_966349/patchset_008_bootstrap_refactor_phases_1to4.md) | |
| 19 | **Use MCP Agents for Metadata** | Dev Environment | ✅ [@opendev-reviewer-agent](../README.md#1-review-automation) | |
| 20 | **Create Comparison Documents** | Documentation | ✅ [Evolution metrics](analysis_new_feature_966349/README.md#evolution-metrics), [patchset comparisons](analysis_new_feature_966349_wip/PHASE_1_TO_4_COMPLETE_SUMMARY.md) | |
| 21 | **Document "What Worked Well"** | Documentation | ✅ [What worked well](analysis_new_feature_966349/patchset_001_initial_implementation.md#what-worked-well) | |
| 22 | **Document "Issues Discovered"** | Documentation | ✅ [Issues discovered](analysis_new_feature_966349/patchset_001_initial_implementation.md#issues-discovered) | |
| 23 | **Capture Reviewer Quotes** | Documentation | ✅ [Feedback highlights](analysis_new_feature_966349/README.md#reviewer-feedback-highlights) | |
| 24 | **Track Code Metrics** | Documentation | ✅ [Code metrics](analysis_new_feature_966349/README.md#code-metrics), [Evolution](analysis_new_feature_966349/README.md#evolution-metrics) | |
| 25 | **Create "Lessons Learned"** | Documentation | ✅ [Lessons learned](analysis_new_feature_966349/README.md#lessons-learned), [Each phase](analysis_new_feature_966349/patchset_001_initial_implementation.md#lessons-learned) | |

---

## Detailed Practice Descriptions

### Investigation & Planning Practices

#### Practice #1: Create Spike Document

**What**: Create a comprehensive spike document that investigates the feature before implementation.

**Why**: 
- Reduces implementation risk by answering key questions upfront
- Documents decision rationale for future reference
- Identifies potential blockers early
- Provides time estimates

**How**:
1. Document what you're trying to understand
2. Evaluate multiple approaches (with pros/cons)
3. Make explicit decisions with rationale
4. Estimate complexity and time
5. List risks and mitigation strategies

**Example**: [spike.md](analysis_new_feature_966349/spike.md)

**Key Sections**:
- Executive Summary
- Development Environment Setup
- Options Evaluated
- Final Design Decision
- Complexity Assessment
- Success Criteria
- Next Steps

---

#### Practice #18: Break Work into Logical Phases

**What**: Divide complex features into discrete, logical phases that can be implemented and tested independently.

**Why**:
- Makes code review easier (smaller, focused changes)
- Allows incremental progress
- Reduces risk of massive rewrites
- Each phase can be verified before moving forward

**How**:
1. Identify natural breakpoints in the work
2. Order phases by dependency (foundational first)
3. Make each phase independently testable
4. Document phase goals clearly

**Example**: Review 966349 had 4 phases:
- [Phase 1: Fix Unique IDs](analysis_new_feature_966349/patchset_008_bootstrap_refactor_phases_1to4.md#phase-1-unique-chevron-id-generation)
- [Phase 2: Bootstrap Collapse](analysis_new_feature_966349/patchset_008_bootstrap_refactor_phases_1to4.md#phase-2-bootstrap-native-collapse)
- [Phase 3: Chevron Rotation](analysis_new_feature_966349/patchset_008_bootstrap_refactor_phases_1to4.md#phase-3-automatic-chevron-rotation)
- [Phase 4: PEP8 Compliance](analysis_new_feature_966349/patchset_008_bootstrap_refactor_phases_1to4.md#phase-4-pep8-compliance)

---

### Development Environment Practices

#### Practice #2: Document Two Dev Environments

**What**: Document setup for both cloud-based (PSI) and local (laptop VM) development environments.

**Why**:
- Flexibility: Work remotely or offline
- Backup: If one environment breaks, use the other
- Different use cases: PSI for stable/always-on, laptop for fast iteration
- Team enablement: Others can choose their preferred setup

**How**:
1. Document PSI cloud setup with screenshots
2. Document local VM setup with virt-manager
3. Include troubleshooting sections
4. Reference both from spike document

**Examples**:
- [HOWTO_install_devstack_on_psi.org](analysis_new_feature_966349/HOWTO_install_devstack_on_psi.org)
- [HOWTO_install_devstack_on_laptop.org](analysis_new_feature_966349/HOWTO_install_devstack_on_laptop.org)

---

#### Practice #19: Use MCP Agents for Metadata

**What**: Use MCP agents (`@opendev-reviewer-agent`, `@github-reviewer-agent`, `@gitlab-cee-agent`) to fetch review metadata automatically.

**Why**:
- Faster than manual lookups
- Comprehensive data in structured format
- Includes reviewer comments, CI status, merge conflicts
- Enables systematic review analysis

**How**:
1. Run `fetch-review.sh --with-assessment <type> <URL>`
2. Use appropriate MCP agent in Cursor
3. Agent fetches metadata and creates assessment template
4. Read actual code with `git show HEAD`

**Example**: See [usecases/review_automation/README.md](../usecases/review_automation/README.md)

---

### Implementation Practices

#### Practice #5: Check Framework Solutions First

**What**: Before writing custom code, check if the framework (Bootstrap, Horizon, Django) already provides a solution.

**Why**:
- Framework solutions are battle-tested
- Better maintained (updates flow through)
- More accessible (framework handles ARIA)
- Less code to maintain
- Faster implementation

**How**:
1. Read framework documentation for similar features
2. Search codebase for existing patterns
3. Ask maintainers if unsure
4. Only write custom code if no framework solution exists

**Example**: Review 966349 initially used custom JavaScript for collapse, then switched to Bootstrap's native collapse:
- Before: 30 lines custom JS
- After: 0 lines (Bootstrap `data-toggle="collapse"`)
- **Result**: Better accessibility, less maintenance

**Reference**: [Bootstrap refactor documentation](analysis_new_feature_966349/patchset_008_bootstrap_refactor_phases_1to4.md#phase-2-bootstrap-native-collapse)

---

#### Practice #6: Use Helper Functions (DRY)

**What**: Extract duplicated logic into helper functions with clear names and documentation.

**Why**:
- Single source of truth
- Easier to test
- Reduces bugs from inconsistent implementations
- Improves code readability

**How**:
1. Identify duplicated logic
2. Extract to helper function
3. Add clear docstring
4. Call from all locations

**Example**: Review 966349 created `get_chevron_id(table, datum)`:
```python
def get_chevron_id(table, datum):
    """Generate unique chevron ID for a given key pair row.
    
    Args:
        table: The DataTable instance
        datum: The Keypair object for this row
    
    Returns:
        str: Unique ID like "keypairs_chevron_test1"
    """
    object_id = table.get_object_id(datum)
    return "%s_chevron_%s" % (table.name, object_id)
```

**Reference**: [Phase 1 documentation](analysis_new_feature_966349/patchset_008_bootstrap_refactor_phases_1to4.md#phase-1-unique-chevron-id-generation)

---

#### Practice #8: Use datum for Unique IDs

**What**: When working with table rows, use the `datum` parameter (row data object) to generate unique per-row identifiers.

**Why**:
- `self.creation_counter` is class-level (same for all rows)
- `datum` contains row-specific data (e.g., name, ID)
- Ensures unique IDs for each row
- Predictable and debuggable IDs

**How**:
```python
# ❌ Wrong: Class-level counter (same for all rows)
chevron_id = "%s_table_chevron%d" % (self.table.name, self.creation_counter)

# ✅ Correct: Row-specific data
chevron_id = "%s_chevron_%s" % (table.name, table.get_object_id(datum))
```

**Example**: Review 966349 bug where all rows had same ID, causing only first row to expand.

**Reference**: [Issue analysis](analysis_new_feature_966349/patchset_001_initial_implementation.md#issue-1-duplicate-chevron-ids-critical)

---

#### Practice #9: Prefer CSS Specificity over !important

**What**: Use specific CSS selectors to override styles instead of `!important` flags.

**Why**:
- More maintainable (follows CSS cascade)
- Easier to debug
- Framework updates don't conflict
- Professional code quality

**How**:
```css
/* ❌ Bad: Using !important */
.chevron-toggle .fa {
  color: #0088cc !important;
}

/* ✅ Good: High specificity selector */
.table > tbody > tr > td .chevron-toggle .fa {
  color: #0088cc;
}
```

**Example**: Review 966349 maintainer simplified CSS from 14 `!important` flags to 0.

**Reference**: [CSS refinement phase](analysis_new_feature_966349/patchset_018_css_refinement.md)

---

### Code Review & Iteration Practices

#### Practice #10: Accept Feedback Gracefully

**What**: Treat code review feedback as learning opportunities, not criticism. Iterate based on feedback.

**Why**:
- Each iteration improves code quality
- Maintainers have deep framework knowledge
- Builds collaborative relationships
- Results in better final implementation

**How**:
1. Read feedback carefully
2. Ask clarifying questions if needed
3. Implement suggested improvements
4. Thank reviewers for their time
5. Document what you learned

**Example**: Review 966349 went through ~20 patchsets:
- PS 1-7: Initial implementation
- PS 8-14: Bootstrap refactor (after feedback)
- PS 18-19: CSS optimization (maintainer improvements)
- PS 20+: Final polish

**Reference**: [Success factors](analysis_new_feature_966349/patchset_020_final_polish_and_merge.md#key-success-factors)

---

#### Practice #17: Learn from Maintainers

**What**: Study maintainer improvements to your code - they're master classes in framework usage.

**Why**:
- Maintainers know the framework deeply
- Their simplifications reveal better patterns
- Learning improves future contributions
- Builds expertise

**How**:
1. When maintainer modifies your code, study the diff carefully
2. Understand *why* their approach is better
3. Document the learning in your analysis
4. Apply the pattern to future work

**Example**: Review 966349 maintainer (Radomir) simplified CSS:
- Before: 14 `!important` flags, complex selectors
- After: 0 `!important`, 29% code reduction, higher specificity
- **Learning**: Use `.table>tbody>tr.class>td` specificity instead of brute force

**Reference**: [Reviewer feedback highlights](analysis_new_feature_966349/README.md#reviewer-feedback-highlights)

---

### Documentation Practices

#### Practice #3: Create Phase-Based Analysis Documents

**What**: Create separate markdown documents for each major phase of development, organized by patchset groups.

**Why**:
- Easier to navigate than one huge document
- Clear progression through development
- Each phase tells a complete story
- Future reference for similar work

**How**:
1. Create document per major milestone/phase
2. Name by patchset number: `patchset_XXX_description.md`
3. Include git commands to view those patchsets
4. Link documents together

**Example Structure**:
```
analysis_new_feature_966349/
├── README.md (index)
├── spike.md (investigation)
├── patchset_001_initial_implementation.md
├── patchset_008_bootstrap_refactor_phases_1to4.md
├── patchset_018_css_refinement.md
└── patchset_020_final_polish_and_merge.md
```

**Reference**: [Review 966349 organization](analysis_new_feature_966349/README.md)

---

#### Practice #4: Keep WIP Analysis Separate

**What**: Create a separate `_wip` directory for all work-in-progress analysis documents.

**Why**:
- Preserves complete development history
- Polished documents can reference WIP details
- No need to delete original analysis
- Shows authentic, unedited thought process

**How**:
1. Create `analysis_new_feature_XXXXXX_wip/` directory
2. Keep all original, chronological analysis documents
3. Create `README.md` explaining WIP purpose
4. Link from polished docs when showing details

**Example**: Review 966349 has:
- `analysis_new_feature_966349/` - 6 polished documents
- `analysis_new_feature_966349_wip/` - 24 original WIP documents

**Reference**: [WIP directory](analysis_new_feature_966349_wip/)

---

#### Practice #13: Create README Index

**What**: Create a comprehensive `README.md` in the feature directory that serves as the main index and overview.

**Why**:
- Single entry point for understanding the feature
- Quick navigation to all documents
- Executive summary for stakeholders
- Provides context and metrics

**How**:
1. Start with feature overview and quick reference
2. Add "Quick Navigation" section with links to phase documents
3. Include metrics (timeline, code stats, iterations)
4. Document key technical decisions
5. Add "How to View Patchset Changes" section
6. Include lessons learned and impact

**Example**: [analysis_new_feature_966349/README.md](analysis_new_feature_966349/README.md)

**Key Sections**:
- Feature Overview
- Quick Navigation (phase documents)
- Development Journey (timeline table)
- Code Evolution (metrics)
- Key Technical Decisions
- Lessons Learned
- How to View Patchset Changes
- Code Metrics
- Reviewer Feedback Highlights

---

#### Practice #14: Document Git Commands

**What**: Include git/gerrit commands in each phase document showing how to view those specific patchsets.

**Why**:
- Makes documentation actionable
- Others can easily review code changes
- Useful for future reference
- Demonstrates transparency

**How**:
```markdown
## View Patchset Changes

### Compare with baseline:
```bash
git review -d 966349,7
git diff origin/master
```

### View specific patchset:
```bash
git fetch origin refs/changes/49/966349/7
git checkout FETCH_HEAD
```

### Compare patchsets online:
```
https://review.opendev.org/c/openstack/horizon/+/966349/1..7
```
```

**Example**: Every phase document in review 966349 starts with git commands

**Reference**: [Example from patchset 001](analysis_new_feature_966349/patchset_001_initial_implementation.md#view-patchset-changes)

---

#### Practice #16: Document Technical Decisions

**What**: Create a dedicated section documenting key technical decisions with rationale and trade-offs.

**Why**:
- Preserves decision context
- Prevents future "why did we do this?" questions
- Helps others learn decision-making process
- Documents alternatives that were considered

**How**:
```markdown
## Key Technical Decisions

### 1. Decision Title

**Decision**: What was decided

**Reasoning**:
- Why this approach was chosen
- What problem it solves

**Trade-off**:
- ✅ Benefits
- ⚠️ Costs or limitations

**Alternatives Considered**:
- Option A: Why not chosen
- Option B: Why not chosen
```

**Example**: [Key technical decisions section](analysis_new_feature_966349/README.md#key-technical-decisions)

---

#### Practice #20: Create Comparison Documents

**What**: Create documents that compare different states (before/after, patchset ranges, approaches).

**Why**:
- Shows evolution clearly
- Quantifies improvements
- Demonstrates value
- Educational for others

**How**:
1. Create "before" and "after" sections
2. Use tables for metrics comparison
3. Include code snippets showing key differences
4. Quantify improvements (lines of code, performance, etc.)

**Example**: [Evolution metrics table](analysis_new_feature_966349/README.md#evolution-metrics)

| Metric | Initial | Final | Change |
|--------|---------|-------|--------|
| Total lines | 230 | 200 | -30 (-13%) |
| JavaScript | 30 | 0 | -30 (-100%) |
| CSS with `!important` | 14 | 0 | -14 (-100%) |

**Reference**: [PHASE_1_TO_4_COMPLETE_SUMMARY.md](analysis_new_feature_966349_wip/PHASE_1_TO_4_COMPLETE_SUMMARY.md)

---

#### Practice #21: Document "What Worked Well"

**What**: In each phase document, include a section on what worked well, not just problems.

**Why**:
- Reinforces successful patterns
- Builds confidence
- Balances problem-focused documentation
- Identifies reusable approaches

**How**:
```markdown
## What Worked Well

### ✅ Pattern Name

Description of what worked and why it was successful.

**Why it worked**: Explanation

**Reusable**: Yes/No and in what contexts
```

**Example**: [What worked well section](analysis_new_feature_966349/patchset_001_initial_implementation.md#what-worked-well)

---

#### Practice #22: Document "Issues Discovered"

**What**: Create detailed documentation of issues discovered, including root cause, impact, and resolution.

**Why**:
- Prevents similar issues in future
- Documents debugging process
- Helps others learn from mistakes
- Shows authentic development process

**How**:
```markdown
## Issues Discovered

### Issue #: Title (Severity)

**Problem**: Clear description of the issue

**Root Cause**: Why it happened

**Impact**: 
- ❌ Effect on functionality
- Severity rating

**Status**: How it was resolved

**Reference**: Link to fix documentation
```

**Example**: [Issues discovered section](analysis_new_feature_966349/patchset_001_initial_implementation.md#issues-discovered)

---

#### Practice #23: Capture Reviewer Quotes

**What**: Preserve actual reviewer comments as quotes in your documentation.

**Why**:
- Authentic feedback from experts
- Shows collaborative process
- Preserves maintainer wisdom
- Provides context for changes

**How**:
```markdown
## Reviewer Feedback

**Reviewer Name** (Role):
> "Exact quote from review comment"

**Location**: File, line number

**Action Taken**: How you addressed it
```

**Example**: [Reviewer feedback highlights](analysis_new_feature_966349/README.md#reviewer-feedback-highlights)

---

#### Practice #24: Track Code Metrics

**What**: Track quantitative metrics throughout development (lines of code, complexity, performance).

**Why**:
- Demonstrates improvement objectively
- Provides data for discussions
- Shows value of refactoring
- Tracks technical debt

**How**:
1. Create metrics table in README
2. Track key metrics: LOC, file counts, complexity
3. Calculate before/after differences
4. Include in executive summaries

**Example**: [Code metrics section](analysis_new_feature_966349/README.md#code-metrics)

```markdown
### Evolution Metrics

| Metric | Initial | Final | Change |
|--------|---------|-------|--------|
| Total lines | 230 | 200 | -30 (-13%) |
| JavaScript | 30 | 0 | -30 (-100%) |
| Helper functions | 0 | 1 | +1 (DRY) |
```

---

#### Practice #25: Create "Lessons Learned"

**What**: End each phase document and the main README with a "Lessons Learned" section.

**Why**:
- Explicit knowledge transfer
- Makes learning actionable
- Improves future work
- Shows growth

**How**:
```markdown
## Lessons Learned

### Technical Lessons

1. **Lesson**: Description
   **Applied**: How to use this learning

### Process Lessons

1. **Lesson**: Description
   **Applied**: How to use this learning

### Collaboration Lessons

1. **Lesson**: Description
   **Applied**: How to use this learning
```

**Example**: [Lessons learned sections](analysis_new_feature_966349/README.md#lessons-learned)

---

### Git & Gerrit Workflow Practices

#### Practice #11: Use Consistent Topics

**What**: Set meaningful Gerrit topics that group related reviews together (e.g., `de-angularize`).

**Why**:
- Makes reviews discoverable
- Provides context about initiative
- Helps track related work
- Shows scope of effort

**How**:
1. Choose descriptive topic for the initiative
2. Set topic on first review: `git review -t <topic>`
3. Use same topic for all related reviews
4. Search by topic: `project:X topic:Y`

**Example**: Review 966349 uses `de-angularize` topic
- Query: `project:openstack/horizon topic:de-angularize`
- Groups all de-angularization work together

**Reference**: [Topic management](analysis_new_feature_966349/patchset_020_final_polish_and_merge.md#phase-topic-management)

---

#### Practice #12: Write Detailed Commit Messages

**What**: Write comprehensive commit messages that explain what, how, and why.

**Why**:
- Future developers understand context
- Code review is faster
- Git history is meaningful
- Shows professionalism

**How**:
```
Subject line: What was added/changed (50 chars)

Detailed description explaining:
- What the change does
- How it works
- Why it was needed

Implementation details:
- Key approach taken
- Important patterns used

Change-Id: <gerrit-change-id>
Signed-off-by: Your Name <email>
```

**Example**: [Commit message improvement](analysis_new_feature_966349/patchset_020_final_polish_and_merge.md#phase-commit-message-improvement)

**Bad**:
```
de-angularize Key Pairs
```

**Good**:
```
Add expandable row details to Key Pairs table

Implement expandable rows with collapsible details for the Key Pairs table,
allowing users to view key pair information inline without navigating to a
separate detail page. Users can click a chevron icon to expand/collapse
row details.

This achieves feature parity with the AngularJS version of the Key Pairs
panel and de-angularizes this part of the interface.

Implementation:
- Custom row rendering with summary and detail rows
- Bootstrap collapse for expand/collapse functionality
- Chevron icons with automatic rotation
- Responsive detail layout with definition list
```

---

### Quality Assurance Practices

#### Practice #7: Test with Multiple Items (3+)

**What**: Always test table/list features with at least 3 items, not just 1 or 2.

**Why**:
- Edge cases appear with multiple items
- Uniqueness issues become obvious
- Performance issues may surface
- Real-world usage simulation

**How**:
1. Create 3+ test items
2. Test all operations on each
3. Test interactions between items
4. Verify uniqueness (IDs, names, etc.)

**Example**: Review 966349 discovered duplicate ID bug only when testing with 3+ key pairs

**Reference**: [Testing checklist](analysis_new_feature_966349_wip/PHASE_1_TO_4_COMPLETE_SUMMARY.md#testing-checklist)

---

#### Practice #15: Run PEP8/Lint After Each Change

**What**: Run linting tools (`tox -e pep8`) after every code change, not just at the end.

**Why**:
- Catches issues early
- Prevents linter fix commits
- Maintains code quality
- Shows professionalism

**How**:
```bash
# After each code change:
tox -e pep8

# Fix any issues immediately
# Commit only when lint-clean
```

**Example**: Review 966349 had dedicated Phase 4 for PEP8 compliance

**Reference**: [PEP8 phase](analysis_new_feature_966349/patchset_008_bootstrap_refactor_phases_1to4.md#phase-4-pep8-compliance)

**Better Approach**: Run after each change to avoid this.

---

## How to Use This Document

### When Starting a New Feature

1. **Review relevant practices** - Read practices in categories that apply
2. **Check the tracking table** - See how Review 966349 applied each practice
3. **Set up your structure** - Create directories following these patterns:
   ```
   analysis/
   ├── analysis_new_feature_XXXXXX/     (polished docs)
   │   ├── README.md
   │   ├── spike.md
   │   ├── patchset_XXX_*.md
   │   └── HOWTO_*.org
   └── analysis_new_feature_XXXXXX_wip/  (original WIP docs)
       ├── README.md
       └── analysis_*.md/org
   ```
4. **Start with spike** - Create `spike.md` to investigate the feature
5. **Document as you go** - Don't wait until the end

### During Development

1. **Create WIP docs** - Write analysis docs in real-time as you work
2. **Follow implementation practices** - Check framework first, use helpers, etc.
3. **Test incrementally** - Use Practice #7 (test with 3+ items)
4. **Run lint frequently** - Practice #15 (PEP8 after each change)
5. **Accept feedback** - Practice #10 (iterate based on review)

### After Feature Completion

1. **Create polished docs** - Synthesize WIP docs into phase-based documents
2. **Write comprehensive README** - Practice #13 (README index)
3. **Document lessons** - Practice #25 (lessons learned)
4. **Update this document** - Add your feature to the tracking table
5. **Add new practices** - If you discovered new patterns

---

## Contributing New Practices

### When to Add a New Practice

Add a practice to this document when:
- ✅ You've used it successfully in a feature
- ✅ It's generally applicable to other features
- ✅ It's not already covered by existing practices
- ✅ It improved code quality, process, or outcomes

### How to Add a New Practice

1. **Add to tracking table** - Add row with practice name and initial feature
2. **Add to detailed section** - Create full description with:
   - **What**: Clear description
   - **Why**: Rationale and benefits
   - **How**: Step-by-step guide
   - **Example**: Link to where you used it
   - **Reference**: Link to detailed documentation
3. **Update category count** - Increment practice numbers
4. **Link from your feature README** - Show how you applied it

### Practice Template

```markdown
#### Practice #X: Practice Name

**What**: Brief description of the practice

**Why**:
- Benefit 1
- Benefit 2
- Benefit 3

**How**:
1. Step 1
2. Step 2
3. Step 3

**Example**: [Link to example in your feature](path/to/doc.md#section)

**Reference**: [Detailed documentation](path/to/reference.md)
```

---

## Summary

These 25 best practices emerged from successful development of [Review 966349](https://review.opendev.org/c/openstack/horizon/+/966349), which achieved:

- ✅ **+2 approval** from project maintainer
- ✅ **Merged upstream** in November 2025
- ✅ **9-day development** from investigation to approval
- ✅ **~20 patchsets** of iterative improvement
- ✅ **Zero custom JavaScript** in final implementation
- ✅ **13% code reduction** with same functionality
- ✅ **Comprehensive documentation** for future reference

**Key Insight**: Systematic documentation during development, not after, creates better features and preserves institutional knowledge.

---

**Next Steps**:
1. Use these practices for your next feature
2. Update the tracking table when you apply them
3. Add new practices you discover
4. Share improvements with the team

**Questions or Suggestions**: Add them to this document as you work!

---

**Document History**:
- November 15, 2025: Initial version based on Review 966349 experience
- Future: Will be updated as new features are developed


