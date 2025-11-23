# Design: [Feature Name] - Code References & Decisions

**Feature**: [JIRA-KEY] - [Feature name]  
**Patchset**: N of M  
**Created**: [Date]  
**Status**: 📐 **DESIGN DOCUMENTATION**

---

## Table of Contents

1. [Code References: Discovery & Analysis](#code-references-discovery--analysis)
2. [Summary: Reference vs New Code](#summary-reference-vs-new-code)
3. [Architectural Decisions](#architectural-decisions)
4. [Flow Diagrams](#flow-diagrams) (optional)

---

## Code References: Discovery & Analysis

This section documents the **thought process** and **discovery journey** for implementing [feature name].

**Purpose**: Show HOW you found the code to reference, not just WHAT you found.

---

### Thought #1: [First Question You Asked]

**Question**: [The question that started your investigation]

**Investigation**:
Searched for: "[What you searched for]"

**Found**:
- **[Component Name]** - [Brief description]
  - GitHub: [Link to code]
  - Review: [Link to review if applicable]

**Pattern Identified**:
```python
# Code example showing the pattern you found
class ExamplePattern:
    def example_method(self):
        # ...
```

**How I Used This**:
- ✅ **Copied**: [What you copied exactly]
- ✅ **Adapted**: [What you changed]
- ⚠️ **Modified**: [What you had to modify and why]
- ⚠️ **Added**: [What you added beyond the reference]

**% Reference vs Custom**:
- **X% reference** - [Description]
- **Y% custom** - [Description]

**Code Diff** (optional but helpful):
```diff
- old_code_from_reference
+ new_code_in_your_implementation
```

---

### Thought #2: [Second Question]

**Question**: [Next question in your discovery process]

**Investigation**:
[What you looked at next]

**Found**:
[What you discovered]

**Pattern Identified**:
```python
# Code pattern
```

**How I Used This**:
- ✅ [How you adapted it]

**% Reference vs Custom**:
- **X% reference**
- **Y% custom**

---

### Thought #N: [Continue for each major discovery]

[Repeat the structure for each significant piece of code you referenced]

**Typical thoughts to document**:
- How does [component X] work?
- Where is [pattern Y] defined?
- What's the best way to [do Z]?
- How do similar features handle [scenario]?

---

## Summary: Reference vs New Code

### Overall Breakdown

| Component | Reference Source | % Ref | % Custom | Notes |
|-----------|------------------|-------|----------|-------|
| **[Component 1]** | [Source] | X% | Y% | [Brief note] |
| **[Component 2]** | [Source] | X% | Y% | [Brief note] |
| **[Component 3]** | [Source] | X% | Y% | [Brief note] |
| **[Component N]** | [Source] | X% | Y% | [Brief note] |
| **Overall** | **[Primary Source]** | **X%** | **Y%** | [Summary] |

### Interpretation

**This implementation is X% reference-driven:**

- **Core pattern**: [Percentage and description]
- **Templates**: [Percentage and description]
- **Logic**: [Percentage and description]
- **Custom code**: [Percentage and description]

**Reviewer Benefit**:
By understanding that X% follows [proven pattern], reviewers can focus their attention on the Y% custom code:
1. [Custom piece 1]
2. [Custom piece 2]
3. [Custom piece 3]

**Confidence Level**: **[Very High/High/Medium]**
- [Rationale for confidence level]

---

## Architectural Decisions

### Decision 1: [Decision Name]

**Context**: [What was the situation requiring a decision?]

**Options**:
1. **[Option A]** - [Description]
2. **[Option B]** - [Description]
3. **[Option C]** - [Description]

**Decision**: [Which option was chosen]

**Reasoning**:
- ✅ **Reason 1**: [Why this is good]
- ✅ **Reason 2**: [Another advantage]
- ⚠️ **Trade-off**: [What you gave up]

**Trade-offs**:
- ✅ **Pros**: [Advantages of this choice]
- ⚠️ **Cons**: [Disadvantages of this choice]

**Impact**: [How significant is this decision? Low/Medium/High]

---

### Decision 2: [Another Key Decision]

[Repeat the same structure]

**Context**: [Situation]

**Options**:
1. [Option A]
2. [Option B]

**Decision**: [Choice]

**Reasoning**:
- [Reasons]

**Trade-offs**:
- [Pros and cons]

**Impact**: [Significance]

---

### Decision N: [Continue for all major decisions]

[Typical architectural decisions to document]:
- Technology/framework choices
- Pattern selections
- Data structure choices
- API design decisions
- UI/UX approach decisions

---

## Flow Diagrams

*Optional but highly recommended for complex features*

### User Interaction Flow

```
User [action]
  │
  ├─ [System response 1]
  │    └─ [Details]
  │
  ├─ [System response 2]
  │    └─ [Details]
  │
  └─ [Final state]
```

### Code Execution Flow

```
Entry Point: [Where code starts]
  │
  ├─ [Step 1]
  │    ├─ [Substep 1a]
  │    └─ [Substep 1b]
  │
  ├─ [Step 2]
  │    └─ [Details]
  │
  └─ [Exit point]
```

### Data Flow

```
[Data Source 1] ──┐
                  │
[Data Source 2] ──┼──→ [Processing] ──→ [Output]
                  │
[Data Source 3] ──┘
```

### State Machine (if applicable)

```
Initial State
    │
    ├─ [Event 1] → [State A]
    │                │
    │                └─ [Event 2] → [State B]
    │
    └─ [Event 3] → [State C]
```

---

## Key Lessons from [Reference Implementation]

*Document what you learned from the reference implementation*

### Technical Lessons

1. **[Lesson 1]**
   - ❌ Don't: [Anti-pattern]
   - ✅ Do: [Best practice]
   - **Why**: [Explanation]

2. **[Lesson 2]**
   - [Key insight]
   - [How this applies]

### Process Lessons

1. **[Process lesson 1]**
   - [What you learned about the development process]

2. **[Process lesson 2]**
   - [Another process insight]

---

**Design Document Status**: ✅ **COMPLETE** / 🔄 **IN PROGRESS**  
**Next Document**: `[Next document name]`  
**Code Confidence**: **[Level]** ([X]% reference-driven)

---

*Document Version: 1.0*  
*Created: [Date]*  
*Reference: [Primary reference implementation]*  
*AI-assisted design: mymcp framework*

