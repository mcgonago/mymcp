# OSPRH Analysis Guide: Spike vs. Full Package

This guide explains the two methods for generating OSPRH feature analysis using the `ask_me.sh` framework.

---

## Quick Reference

| Goal | Command | Output | Size |
|------|---------|--------|------|
| **Spike Only** | `./ask_me.sh analysis_doc_create askme/keys/osprh_template.yaml TICKET_NUMBER=... FEATURE_NAME="..."` | spike.md | ~20-30K |
| **Full Package** | `./ask_me.sh analysis_full_package askme/keys/osprh_full_template.yaml TICKET_NUMBER=... FEATURE_NAME="..."` | spike.md + patchsets + design.md + README.md | ~100-150K |

---

## Method 1: Spike Only (Quick Investigation)

### When to Use

- ✅ Initial feasibility check
- ✅ Quick complexity assessment
- ✅ Deciding whether to proceed with feature
- ✅ Need answer within minutes
- ✅ Don't need implementation details yet

### Command

```bash
./ask_me.sh analysis_doc_create askme/keys/osprh_template.yaml \
    TICKET_NUMBER=16421 \
    FEATURE_NAME="Add expandable rows to Images table" \
    REFERENCE_TICKET=12803 \
    REFERENCE_REVIEW=966349
```

### Output Structure

```
workspace/iproject/analysis/analysis_new_feature_osprh_16421/
└── spike.md                (~20-30K)
```

### What spike.md Contains

- ✅ Context and background
- ✅ Technical approach overview
- ✅ Complexity assessment (Low/Medium/High)
- ✅ Key risks identified
- ✅ Rough breakdown into patchsets
- ✅ Timeline estimate
- ✅ Go/no-go decision
- ❌ NO detailed implementation code
- ❌ NO patchset-by-patchset guides
- ❌ NO design document

### Time to Generate

- **~2-5 minutes** (AI processing time)

### Follow-Up

After reviewing the spike, if you decide to proceed, you can:

1. **Option A**: Run the full package command (Method 2)
2. **Option B**: Ask in natural language:
   ```
   Now create the remaining documents for OSPRH-16421:
   - patchset_1_*.md
   - patchset_2_*.md
   - patchset_3_*.md
   - patchset_4_*.md
   - design.md
   - README.md
   ```

---

## Method 2: Full Package (Complete Analysis)

### When to Use

- ✅ Ready to implement the feature
- ✅ Need detailed implementation guides
- ✅ Want comprehensive documentation
- ✅ Planning to submit for code review soon
- ✅ Reference material for other developers
- ✅ Complete project from spike to merge

### Command

```bash
./ask_me.sh analysis_full_package askme/keys/osprh_full_template.yaml \
    TICKET_NUMBER=16421 \
    FEATURE_NAME="Add expandable rows to Images table" \
    REFERENCE_TICKET=12803 \
    REFERENCE_REVIEW=966349
```

### Output Structure

```
workspace/iproject/analysis/analysis_new_feature_osprh_16421/
├── README.md                           (~13K)  ← Start here!
├── spike.md                            (~29K)  ← Investigation
├── patchset_1_mvp_implementation.md    (~16K)  ← Core feature
├── patchset_2_extended_metadata.md     (~10K)  ← Enhancements
├── patchset_3_css_refinement.md        (~11K)  ← Polish
├── patchset_4_final_polish.md          (~15K)  ← Merge prep
└── design.md                           (~31K)  ← Architecture
                                        -------
Total:                                  ~125K
```

### What the Full Package Contains

#### 1. **README.md** (Project Hub)
- Feature overview
- Quick navigation to all documents
- Timeline and status tracking
- Key decisions summary
- Testing strategy
- Success criteria

#### 2. **spike.md** (Investigation)
- Comprehensive technical analysis
- Complexity breakdown
- Risk assessment
- Reference implementation analysis
- Decision rationale

#### 3. **Patchset Documents** (Implementation Guides)
Each patchset document includes:
- Objectives (what this phase accomplishes)
- Files to modify (specific paths and line numbers)
- **Actual code examples** (copy-paste ready)
- Testing procedures (unit + manual)
- Commit message templates
- Expected reviewer feedback
- Success criteria

**Typical breakdown**:
- **Patchset 1**: MVP (minimal viable product)
- **Patchset 2**: Extended features
- **Patchset 3**: CSS/polish/optimization
- **Patchset 4**: Final refinements and merge prep

#### 4. **design.md** (Architecture)
- Problem statement (current vs. desired state)
- Goals and non-goals
- Architecture diagrams
- Key design decisions with rationale
- Data models
- User experience flows
- Accessibility considerations
- Performance analysis
- Security considerations
- Alternative designs (and why rejected)
- References to related work

### Time to Generate

- **~5-15 minutes** (AI processing time for complete package)

### Usage Flow

1. Run command → generates all 7 documents
2. Read README.md first (navigation hub)
3. Review spike.md (understand the approach)
4. Read design.md (understand architectural decisions)
5. Implement following patchset_1, 2, 3, 4 in order
6. Use commit messages from patchset docs
7. Submit to Gerrit following patchset guides

---

## Comparison: Spike vs. Full Package

| Aspect | Spike Only | Full Package |
|--------|-----------|--------------|
| **Files Created** | 1 | 7 |
| **Total Size** | ~20-30K | ~100-150K |
| **Generation Time** | 2-5 minutes | 5-15 minutes |
| **Purpose** | Feasibility check | Implementation guide |
| **Code Examples** | Minimal/conceptual | Detailed/copy-paste ready |
| **Implementation Details** | High-level | Line-by-line |
| **Testing Guidance** | Overview | Step-by-step |
| **Use Case** | Decision making | Actual development |

---

## Template Variables Reference

Both templates support the same variables:

### Required Variables

| Variable | Example | Description |
|----------|---------|-------------|
| `TICKET_NUMBER` | `16421` | OSPRH ticket number |
| `FEATURE_NAME` | `"Add expandable rows to Images table"` | Brief feature description |

### Optional Variables

| Variable | Example | Description |
|----------|---------|-------------|
| `REFERENCE_TICKET` | `12803` | Related OSPRH ticket (if applicable) |
| `REFERENCE_REVIEW` | `966349` | Related OpenDev review (if applicable) |

**Notes**:
- Quote the `FEATURE_NAME` if it contains spaces
- Optional variables can be omitted (template handles gracefully)
- Variables are case-sensitive (use ALL_CAPS)

---

## Examples

### Example 1: Spike Only (Initial Investigation)

```bash
./ask_me.sh analysis_doc_create askme/keys/osprh_template.yaml \
    TICKET_NUMBER=16421 \
    FEATURE_NAME="Add expandable rows to Images table" \
    REFERENCE_TICKET=12803 \
    REFERENCE_REVIEW=966349
```

**Output**:
```
✅ Generated: workspace/iproject/analysis/analysis_new_feature_osprh_16421/spike.md
```

**Review the spike, then decide**:
- If complex/risky → maybe don't proceed
- If feasible → proceed to full package (Example 2)

---

### Example 2: Full Package (Ready to Implement)

```bash
./ask_me.sh analysis_full_package askme/keys/osprh_full_template.yaml \
    TICKET_NUMBER=16421 \
    FEATURE_NAME="Add expandable rows to Images table" \
    REFERENCE_TICKET=12803 \
    REFERENCE_REVIEW=966349
```

**Output**:
```
✅ Generated complete package:
   - README.md (start here)
   - spike.md
   - patchset_1_mvp_implementation.md
   - patchset_2_extended_metadata.md
   - patchset_3_css_refinement.md
   - patchset_4_final_polish.md
   - design.md
```

**Next steps**:
1. Read README.md
2. Implement patchset 1
3. Submit to Gerrit
4. Iterate through patchsets 2-4

---

### Example 3: No Reference Implementation

```bash
./ask_me.sh analysis_full_package askme/keys/osprh_full_template.yaml \
    TICKET_NUMBER=99999 \
    FEATURE_NAME="Add network topology visualization"
```

**Note**: Omitted `REFERENCE_TICKET` and `REFERENCE_REVIEW` (totally fine)

**Output**: Same structure, but analysis will note "no reference implementation"

---

## Workflow Recommendations

### Recommended: Two-Phase Approach

**Phase 1: Spike** (5 minutes)
```bash
./ask_me.sh analysis_doc_create askme/keys/osprh_template.yaml \
    TICKET_NUMBER=<num> \
    FEATURE_NAME="..."
```

Review spike.md:
- ✅ Feasible? → Proceed to Phase 2
- ❌ Too complex/risky? → Don't proceed (or revise approach)

**Phase 2: Full Package** (if proceeding)
```bash
./ask_me.sh analysis_full_package askme/keys/osprh_full_template.yaml \
    TICKET_NUMBER=<num> \
    FEATURE_NAME="..." \
    REFERENCE_TICKET=... \
    REFERENCE_REVIEW=...
```

Implement following the patchset documents.

---

### Alternative: One-Shot Full Package

If you're **confident** the feature is feasible (e.g., similar to past work):

```bash
# Skip spike, go straight to full package
./ask_me.sh analysis_full_package askme/keys/osprh_full_template.yaml \
    TICKET_NUMBER=... \
    FEATURE_NAME="..." \
    REFERENCE_TICKET=... \
    REFERENCE_REVIEW=...
```

**Pros**: Saves 5 minutes  
**Cons**: Risk of wasted effort if feature is infeasible

---

## Natural Language Alternative

If you prefer not to use the `ask_me.sh` framework, you can always use natural language:

### For Spike Only:
```
Quick spike for OSPRH-16421: Add expandable rows to Images table
```

### For Full Package:
```
Full spike for OSPRH-16421: Add expandable rows to Images table
Reference: OSPRH-12803 (Review 966349)
```

or

```
Create complete feature analysis for OSPRH-16421: Add expandable rows to Images table
Reference: Key Pairs (OSPRH-12803, Review 966349)
Include: spike, patchsets, design, README
```

**Pros**: Flexible, conversational  
**Cons**: Less reproducible, less explicit

---

## Files Reference

| File | Purpose | Template Type |
|------|---------|---------------|
| `askme/templates/analysis_doc_create.template` | Spike-only template | `analysis_doc_create` |
| `askme/templates/analysis_full_package.template` | Full package template | `analysis_full_package` |
| `askme/keys/osprh_template.yaml` | OSPRH spike YAML | Use with `analysis_doc_create` |
| `askme/keys/osprh_full_template.yaml` | OSPRH full package YAML | Use with `analysis_full_package` |

---

## Troubleshooting

### Problem: "Template not found"

**Error**: `ERROR: Template file not found: askme/templates/analysis_full_package.template`

**Solution**: Ensure you're using the correct template type:
- Spike: `analysis_doc_create`
- Full: `analysis_full_package`

---

### Problem: "Only got spike.md, where are the patchsets?"

**Cause**: You used `analysis_doc_create` instead of `analysis_full_package`

**Solution**: Use the full package command:
```bash
./ask_me.sh analysis_full_package askme/keys/osprh_full_template.yaml ...
```

---

### Problem: "Variable not substituted"

**Error**: Output contains `{TICKET_NUMBER}` instead of `16421`

**Cause**: Variable not passed on command line

**Solution**: Check your command:
```bash
./ask_me.sh ... TICKET_NUMBER=16421 FEATURE_NAME="..."
                ^^^^^^^^^^^^^^^^^^  ^^^^^^^^^^^^^^^^^^^
                Must include all required variables
```

---

## Summary

### ✅ Use Spike Only When:
- Initial investigation
- Feasibility check
- Quick complexity assessment
- Decision: go/no-go

**Command**:
```bash
./ask_me.sh analysis_doc_create askme/keys/osprh_template.yaml \
    TICKET_NUMBER=... FEATURE_NAME="..."
```

### ✅ Use Full Package When:
- Ready to implement
- Need detailed guides
- Want complete documentation
- Reference for other developers

**Command**:
```bash
./ask_me.sh analysis_full_package askme/keys/osprh_full_template.yaml \
    TICKET_NUMBER=... FEATURE_NAME="..."
```

---

**Created**: 2025-11-23  
**Location**: `askme/OSPRH_ANALYSIS_GUIDE.md`  
**Related Docs**:
- `askme/TEMPLATE_VARIABLES.md` - Template variables guide
- `docs/USE_CASE_ASK_ME.md` - How ask_me.sh works internally
- `kb/KBA_Choosing_AI_Methods_for_Analysis_in_mymcp.md` - All 4 AI methods

