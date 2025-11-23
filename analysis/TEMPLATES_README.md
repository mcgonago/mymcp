# Analysis Templates - How They Work

**Created**: 2025-11-22  
**Purpose**: Provide consistent structure for feature analysis documents

---

## 📚 Available Templates

```
analysis/
├── spike_template.md       # Investigation & planning document
├── patchset_template.md    # Implementation guide for each patchset
├── design_template.md      # Design rationale & code references
└── TEMPLATES_README.md     # This file
```

---

## 🎯 What These Templates Are For

### For Humans Using mymcp

These templates provide **structure and guidance** for creating feature analysis documents:

1. **spike_template.md** - Start here when investigating a new feature
   - Problem statement
   - Current state analysis
   - Proposed approach
   - Complexity scoring
   - Breakdown into patchsets

2. **patchset_template.md** - For each implementation patchset
   - Step-by-step implementation guide
   - Complete code examples
   - Testing checklist
   - Commit message template
   - Expected reviewer Q&A

3. **design_template.md** - Document your thought process
   - Code discovery journey ("Thoughts")
   - Reference vs custom code breakdown
   - Architectural decisions
   - Flow diagrams

---

## 🤖 The Truth: How AI Currently Uses These

### Short Answer: **I DON'T USE THEM (yet)**

When you say:
```
Full spike for OSPRH-16421
```

I create the spike.md, patchsets, and design docs **WITHOUT using these templates**.

### How I Actually Work

**What I use**:
1. **Natural Language Understanding** - Parse your intent
2. **Reference Examples** - Study existing analysis documents:
   - `analysis/analysis_new_feature_966349/` (complete example)
   - `analysis/analysis_new_feature_osprh_12802/` (in-progress)
3. **Design Frameworks** - Follow patterns documented in:
   - `design/Design_New_Feature_Framework.md` (just created!)
   - My training on structured documentation
4. **Internalized Structure** - I've learned the spike → patchset → design pattern

**What I create**:
```
analysis/analysis_new_feature_osprh_16421/
├── spike.md (581 lines)                    # Generated from examples, not template
├── patchset_1_*.md (739 lines)            # Generated from examples, not template
├── patchset_1_*_design.md (893 lines)     # Generated from examples, not template
└── README.md (576 lines)                   # Generated from examples, not template
```

**Why this works for me**:
- ✅ I have access to all example documents
- ✅ I can analyze patterns across multiple examples
- ✅ I can adapt structure to specific needs
- ✅ I understand the relationships between sections

**Why this is a problem**:
- ❌ Humans can't easily see the structure I'm following
- ❌ No explicit template to guide manual document creation
- ❌ Not discoverable - users don't know what sections to include

---

## 💡 How You SHOULD Use These Templates

### Option 1: Manual Document Creation

**Use case**: You want to create analysis documents yourself (without AI)

**Steps**:
1. Copy template to your feature directory:
   ```bash
   cp analysis/spike_template.md \
      analysis/analysis_new_feature_osprh_16421/spike.md
   ```

2. Fill in the placeholders:
   - Replace `[JIRA-KEY]` with actual Jira number
   - Replace `[Feature Name]` with actual name
   - Fill in each section following the structure

3. Use as checklist - each section guides what to document

### Option 2: AI-Assisted with Template Reference

**Use case**: Ask AI to fill in template structure

**Steps**:
1. Point AI to the template:
   ```
   Please create spike.md for OSPRH-16421 following the structure 
   in analysis/spike_template.md
   ```

2. AI reads template and generates content following that structure

3. Review and refine the generated content

### Option 3: Natural Language (Current Approach)

**Use case**: Let AI figure out structure from examples

**Steps**:
1. Simple request:
   ```
   Full spike for OSPRH-16421
   ```

2. AI generates all documents using internalized structure

3. Documents follow template structure implicitly

---

## 🔄 Templates vs Examples

### Templates (Structural Guide)

**Purpose**: Show WHAT sections to include

**Content**: Placeholders like `[JIRA-KEY]`, `[Feature Name]`

**Usage**: Copy and fill in

**Location**: `analysis/spike_template.md`

### Examples (Real Implementation)

**Purpose**: Show HOW to fill in sections with real content

**Content**: Actual analysis of real features

**Usage**: Reference for ideas and patterns

**Locations**:
- `analysis/analysis_new_feature_966349/` ✅ Complete, merged
- `analysis/analysis_new_feature_osprh_12802/` 🔄 In progress
- `analysis/analysis_new_feature_osprh_16421/` 📋 Just planned

---

## 📊 Template Structure Overview

### spike_template.md Structure

```markdown
# Spike: [Feature Name] ([JIRA-KEY])

## Problem Statement
   - What, Why, Impact

## Current Implementation Analysis
   - Current system
   - What's missing

## Proposed Approach
   - Architecture
   - Reference implementation
   - Key patterns

## Technical Decisions
   - Decision 1: [Choice + reasoning]
   - Decision 2: [Choice + reasoning]

## Complexity Analysis
   - Risk factors (multiplier)
   - Knowledge factors (multiplier)
   - Skill factors (multiplier)
   - Story point calculation

## Recommended Breakdown
   - Patchset 1: [Description]
   - Patchset 2: [Description]
   - ...

## Success Criteria
   - Functional requirements
   - Non-functional requirements

## Implementation Strategy
   - Phase 1: Investigation
   - Phase 2: Implementation
   - Phase 3: Review

## Risks and Mitigation

## Reference Documentation

## Next Steps
```

### patchset_template.md Structure

```markdown
# Patchset N: [Patchset Name]

## 📋 Executive Summary
   - Goal, Approach, Files, Timeline

## 🔧 Implementation Details
   - Step 1: [Code changes]
   - Step 2: [Code changes]
   - ...

## ✅ Testing Checklist
   - Happy path tests
   - Validation tests
   - Error cases
   - Integration tests
   - Edge cases
   - Code quality

## 📝 Commit Message Template

## ❓ Expected Reviewer Questions
   - Q1: [Question] A: [Answer]
   - Q2: [Question] A: [Answer]
   - ...

## 🔗 Reference Links

## 🚀 Implementation Checklist
```

### design_template.md Structure

```markdown
# Design: [Feature Name] - Code References & Decisions

## Code References: Discovery & Analysis
   - Thought #1: [Question → Investigation → Found → How used]
   - Thought #2: [Question → Investigation → Found → How used]
   - ...

## Summary: Reference vs New Code
   - Table showing % breakdown
   - Overall interpretation

## Architectural Decisions
   - Decision 1: [Context → Options → Choice → Reasoning]
   - Decision 2: [Context → Options → Choice → Reasoning]
   - ...

## Flow Diagrams (optional)
   - User interaction flow
   - Code execution flow
   - Data flow
   - State machine

## Key Lessons from [Reference]
```

---

## 🔧 Future: Making AI Use Templates

### Why AI Should Use Templates

1. **Consistency** - Every spike looks the same
2. **Discoverability** - Users can see the template
3. **Validation** - Easy to check if sections are complete
4. **Evolution** - Template improvements benefit everyone

### How to Make This Work

**Option A: Explicit Template Loading**

```python
# In AI processing
if user_says("Full spike for OSPRH-16421"):
    template = read_file("analysis/spike_template.md")
    content = fill_template_with_investigation_results(template, osprh_16421_data)
    write_file("analysis/analysis_new_feature_osprh_16421/spike.md", content)
```

**Option B: Template as Checklist**

```python
# AI reads template to ensure all sections covered
template_sections = extract_sections("analysis/spike_template.md")
generated_doc = create_spike(osprh_16421_data)
verify_all_sections_present(generated_doc, template_sections)
```

**Option C: Hybrid (Current)**

```python
# AI has internalized the structure but doesn't explicitly load template
# Humans can reference template for manual creation
```

---

## 📖 Usage Examples

### Example 1: Manual Spike Creation

```bash
# 1. Copy template
cp analysis/spike_template.md \
   analysis/analysis_new_feature_osprh_16999/spike.md

# 2. Open in editor
vim analysis/analysis_new_feature_osprh_16999/spike.md

# 3. Fill in placeholders
# - Replace [JIRA-KEY] with OSPRH-16999
# - Replace [Feature Name] with actual feature name
# - Fill in each section with investigation results
```

### Example 2: AI-Assisted with Template

```
You: Please create spike.md for OSPRH-16999 following the structure 
     in analysis/spike_template.md. The feature is adding filtering 
     to the Volumes table.

AI: [Reads spike_template.md]
    [Investigates Volumes table]
    [Generates spike.md following template structure]
```

### Example 3: Natural Language (Current)

```
You: Full spike for OSPRH-16999

AI: [Uses internalized structure from examples]
    [Generates spike.md, patchsets, design docs]
    [Structure matches templates but not explicitly loaded]
```

---

## 🎓 Best Practices

### When Creating Analysis Documents

1. **Start with Spike**
   - Always create spike.md first
   - Use template to guide investigation
   - Don't skip complexity analysis

2. **One Patchset, One Document**
   - Each patchset gets its own document
   - Use consistent naming: `patchset_N_[name].md`
   - Include all sections from template

3. **Design Docs Are Key**
   - Document the "why" not just the "what"
   - Show your discovery process ("Thoughts")
   - Include reference vs custom breakdown

4. **Keep Templates Updated**
   - If you find sections are missing, add to template
   - If sections aren't useful, mark as optional
   - Templates evolve based on real usage

### Template Customization

**Feel free to**:
- ✅ Add sections specific to your domain
- ✅ Mark sections as optional if not always needed
- ✅ Adapt structure to your team's needs
- ✅ Create domain-specific templates

**Try to keep**:
- ✅ Consistent section ordering
- ✅ Clear section headers
- ✅ Placeholder format `[DESCRIPTION]`
- ✅ Emoji icons for visual scanning

---

## 📝 Template Maintenance

### When to Update Templates

1. **New Section Needed**
   - You discover a section that should always be included
   - Add to template with placeholder

2. **Section Never Used**
   - Mark as `(Optional)` rather than removing
   - Or move to a separate "extended template"

3. **Better Structure Found**
   - Reorganize sections for better flow
   - Update all three templates consistently

4. **New Pattern Discovered**
   - Add to template with example
   - Document in this README

### Versioning

Templates should have version numbers:
```markdown
*Template Version: 1.0*
*Last Updated: 2025-11-22*
```

When making breaking changes, increment version and document changes.

---

## 🔗 Related Documentation

- **Design Framework**: `design/Design_New_Feature_Framework.md` - How AI orchestrates feature planning
- **Workflow Guide**: `usecases/analysis_new_feature/README.md` - Complete methodology
- **How to Ask**: `analysis/HOW_TO_ASK.md` - How to request analysis from AI
- **Examples**: `analysis/analysis_new_feature_*/` - Real implementations

---

## ❓ FAQ

### Q: Does AI actually use these templates?

**A**: Not yet explicitly. AI currently uses internalized structure from examples. These templates are primarily for humans and could be used by AI in the future.

### Q: Should I copy the template or ask AI to create the document?

**A**: Depends on your needs:
- **Manual control**: Copy template and fill in
- **AI assistance**: Ask AI to create following template
- **Quick generation**: Natural language request (AI uses internalized structure)

### Q: What if template doesn't fit my feature?

**A**: Templates are guides, not rules:
- Add sections you need
- Skip sections that don't apply (mark N/A)
- Customize to your domain
- Consider contributing improvements back

### Q: How do I know if I've covered everything?

**A**: Use template as checklist:
- Each section header is a required topic
- Fill in all `[PLACEHOLDERS]`
- If section doesn't apply, write "N/A - [reason]"
- Review against example documents

---

**Status**: ✅ Templates created, ready to use  
**Next**: Consider making AI explicitly load templates  
**Feedback**: Submit issues/PRs to improve templates

---

*Document Version: 1.0*  
*Created: 2025-11-22*  
*Purpose: Explain analysis templates and their usage*

