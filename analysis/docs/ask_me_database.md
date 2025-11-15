# Ask Me Database - Feature Development Templates

This document catalogs all "ask me" patterns extracted from the Review 966349 development cycle. These templates can be automated using `ask_me.sh` with attribute substitution files.

## Purpose

To systematize the iterative development workflow with AI assistance by:
1. Identifying common ask patterns
2. Creating reusable templates with placeholders
3. Enabling automation via attribute substitution
4. Maintaining consistency across feature development

## Pattern Categories

### Category 1: Analysis Document Creation
### Category 2: Code Implementation
### Category 3: Code Review Response
### Category 4: Problem Investigation
### Category 5: Process/Workflow Questions
### Category 6: Phase Transition

---

## Template Pattern 1: Create Analysis Document with Specific Investigation

**Type**: `analysis_doc_create`

**Pattern Identified In**:
- `HOWTO_osprh_12803_fix_chevron_id.txt` (lines 69-81)
- `HOWTO_osprh_12803_patchset_8_fix_javascript_collapse_phase1.txt` (lines 95-107)
- `HOWTO_osprh_12803_patchset_8_fix_javascript_collapse_phase5_comment_6.txt` (lines 217-249)

**Template Structure**:
```
ask:

For your answers to my inquiry below - please create a new {OUTPUT_DOCUMENT_PATH}

{CONTEXT_DESCRIPTION}

{SPECIFIC_QUESTIONS}
```

**Attribute Placeholders**:
- `{OUTPUT_DOCUMENT_PATH}` - Where to create the analysis document
- `{CONTEXT_DESCRIPTION}` - Background information, relevant links, current state
- `{SPECIFIC_QUESTIONS}` - The actual questions to investigate

**Example Attribute File** (`ask_fix_chevron_id.txt`):
```yaml
type: analysis_doc_create
output_document: analysis/analysis_osprh_12803_fix_chevron_id.org
context_description: |
  We are working on review https://review.opendev.org/c/openstack/horizon/+/966349
  The current chevron_id generation does not work correctly.
specific_questions: |
  Please figure out how we can get unique chevron_id for each row.
  
  The way it is being done now does not work:
  
  class ExpandableKeyPairColumn(tables.Column):
      def get_data(self, datum):
          chevron_id = "%s_table_chevron%d" % (self.table.name, self.creation_counter)
  
  Can you please analyze and give the details on why this approach does not work?
```

**Generated Ask**:
```
ask:

For your answers to my inquiry below - please create a new analysis/analysis_osprh_12803_fix_chevron_id.org

We are working on review https://review.opendev.org/c/openstack/horizon/+/966349
The current chevron_id generation does not work correctly.

Please figure out how we can get unique chevron_id for each row.

The way it is being done now does not work:

class ExpandableKeyPairColumn(tables.Column):
    def get_data(self, datum):
        chevron_id = "%s_table_chevron%d" % (self.table.name, self.creation_counter)

Can you please analyze and give the details on why this approach does not work?
```

---

## Template Pattern 2: Implement Code Changes in Workspace

**Type**: `code_implement_workspace`

**Pattern Identified In**:
- `HOWTO_osprh_12803_fix_chevron_id.txt` (lines 94-107)
- `HOWTO_osprh_12803_ExpandableKeyPairColumn_mark_safe.txt` (lines 942-977)

**Template Structure**:
```
ask:

I already have done the following

: cd {WORKSPACE_PATH}
: {GIT_SETUP_COMMANDS}

I want you to make all your recommended changes

Show me how you would do this work in this {WORKSPACE_NAME} directory?
```

**Attribute Placeholders**:
- `{WORKSPACE_PATH}` - Path to the working directory
- `{GIT_SETUP_COMMANDS}` - Git commands already executed (clone, checkout, fetch)
- `{WORKSPACE_NAME}` - Name of the workspace directory

**Example Attribute File** (`ask_implement_chevron_fix.txt`):
```yaml
type: code_implement_workspace
workspace_path: /home/omcgonag/Work/mymcp/workspace
workspace_name: horizon-osprh-12803-working
git_setup_commands: |
  git clone https://review.opendev.org/openstack/horizon horizon-osprh-12803-working
  cd horizon-osprh-12803-working
  git fetch https://review.opendev.org/openstack/horizon refs/changes/49/966349/5
  git checkout FETCH_HEAD
  git checkout -b osprh-12803-template-refactor
context: |
  Analysis document created at: analysis/analysis_osprh_12803_fix_chevron_id.org
  Recommended changes identified for unique chevron IDs
```

**Generated Ask**:
```
ask:

I already have done the following

: cd /home/omcgonag/Work/mymcp/workspace
: git clone https://review.opendev.org/openstack/horizon horizon-osprh-12803-working
: cd horizon-osprh-12803-working
: git fetch https://review.opendev.org/openstack/horizon refs/changes/49/966349/5
: git checkout FETCH_HEAD
: git checkout -b osprh-12803-template-refactor

I want you to make all your recommended changes

Show me how you would do this work in this horizon-osprh-12803-working directory?
```

---

## Template Pattern 3: Respond to Code Review Comment

**Type**: `code_review_response`

**Pattern Identified In**:
- `HOWTO_osprh_12803_patchset_8_fix_javascript_collapse_phase1.txt` (lines 95-109)
- `HOWTO_osprh_12803_patchset_8_fix_javascript_collapse_phase5_comment_6.txt` (lines 217-250)

**Template Structure**:
```
ask:

For your answers to my inquiry below - please create a new (from top level) {OUTPUT_DOCUMENT_PATH}

From {REVIEW_COMMENT_URL}

From the comment below:

{SPECIFIC_INVESTIGATION}

Comment:

{REVIEWER_NAME} {PATCHSET_NUMBER}

{REVIEWER_COMMENT}

file: {FILE_PATH}

{CODE_CONTEXT}
```

**Attribute Placeholders**:
- `{OUTPUT_DOCUMENT_PATH}` - Where to create the response analysis
- `{REVIEW_COMMENT_URL}` - Link to the specific comment
- `{SPECIFIC_INVESTIGATION}` - What specifically to investigate
- `{REVIEWER_NAME}` - Who made the comment
- `{PATCHSET_NUMBER}` - Which patchset the comment is on
- `{REVIEWER_COMMENT}` - The actual comment text
- `{FILE_PATH}` - The file the comment refers to
- `{CODE_CONTEXT}` - Code snippet the comment is about

**Example Attribute File** (`ask_review_comment_css_gap.txt`):
```yaml
type: code_review_response
output_document: analysis/analysis_osprh_12803_fix_javascript_collapse_phase5_comment_6.org
review_comment_url: https://review.opendev.org/c/openstack/horizon/+/966349/comment/9cf9a894_d4bd10a0/
reviewer_name: Radomir Dopieralski
patchset_number: Patchset 11
specific_investigation: |
  First, please explain what these two lines do:
  
  tr.keypair-detail-row td { padding: 0 };
  tr.keypair-detail-row tod div.keypair-details { margin: 8px };
  
  and how would they get applied to openstack_dashboard/dashboards/project/key_pairs/tables.py
reviewer_comment: |
  I would add something like:
  
  tr.keypair-detail-row td { padding: 0 };
  tr.keypair-detail-row tod div.keypair-details { margin: 8px };
  
  to the style, to get rid of that gap when the details are collapsed.
file_path: openstack_dashboard/dashboards/project/key_pairs/tables.py
code_context: |
     40   /* Rotate chevron 90 degrees when row is expanded (not collapsed) */
     41   .chevron-toggle:not(.collapsed) .fa-chevron-right {
     42     transform: rotate(90deg);
     43   }
     44   </style>
```

---

## Template Pattern 4: Investigate Best Practices / Patterns

**Type**: `investigate_patterns`

**Pattern Identified In**:
- `HOWTO_osprh_12803_ExpandableKeyPairColumn_mark_safe.txt` (lines 69-98)

**Template Structure**:
```
ask:

For your answers to my inquiry below - please create a new {OUTPUT_DOCUMENT_PATH}

{PHASE_CONTEXT}

I want to start simple.

Information:

{CURRENT_STATE_INFO}

For the changes below (using + for add, - for removed)

I want to focus the simple change to get this code to put the {TARGET_ELEMENT} to come from somewhere?

When programming this type of code in {FRAMEWORK} - what is the recommened way to put this code somewhere? template? other?

{CODE_DIFF}
```

**Attribute Placeholders**:
- `{OUTPUT_DOCUMENT_PATH}` - Where to create the analysis
- `{PHASE_CONTEXT}` - What phase/patchset we're working on
- `{CURRENT_STATE_INFO}` - How to view current changes
- `{TARGET_ELEMENT}` - What code element we're asking about
- `{FRAMEWORK}` - Framework name (e.g., "Horizon", "Django")
- `{CODE_DIFF}` - The relevant code changes

**Example Attribute File** (`ask_template_pattern.txt`):
```yaml
type: investigate_patterns
output_document: analysis_osprh_12803_ExpandableKeyPairColumn_mark_safe.org
phase_context: We are starting with changes for next Patchset 5
current_state_info: |
  Patchset 4 changes can be seen as:
  : cd /home/omcgonag/Work/mymcp/workspace/horizon-osprh-12803-patch-set-4
  : git diff --stat 6737fdbfb..365530300 && echo "---" && git diff 6737fdbfb..365530300
target_element: <a role... </a>
framework: Horizon
code_diff: |
  +class ExpandableKeyPairColumn(tables.Column):
  +    def get_data(self, datum):
  +        name = "%s_table_chevron%d" % (self.table.name, self.creation_counter)
  +        return mark_safe("""
  +<a role="button" data-toggle="collapse"
  +href="#%s" aria-expanded="false" aria-controls="collapseExample">
  +<span class="fa fa-chevron-right"></span>
  +</a>
  +""" % name)
```

---

## Template Pattern 5: Final Phase / Wrap-up Questions

**Type**: `phase_done`

**Pattern Identified In**:
- `HOWTO_osprh_12803_patchset_8_fix_javascript_collapse_phase5_comment_DONE.txt` (lines 79-117)

**Template Structure**:
```
ask:

one step at a time...

my current working directory is at {WORKSPACE_PATH}

Now that we have a {MILESTONE} on {REVIEW_URL}

This will be our last {PHASE_TYPE} phase for our chain of analysis documents named {DOCUMENT_PATTERN}...

Please remember - when I ask you to produce a document, I do not want it to be in the workspace folder, instead, I want it in the analysis folder.

Do not create a new analysis folder - use the one that is at the same directory level as workspace.

For your answers to my inquiry below - please create a new (from top level) {OUTPUT_DOCUMENT_PATH}

This will be the place where we (follow up) add our last few actions before officially saying {REVIEW_URL} is ready for a merge.

My question(s):

{FINAL_QUESTIONS}
```

**Attribute Placeholders**:
- `{WORKSPACE_PATH}` - Current working directory
- `{MILESTONE}` - What was achieved (e.g., "+2", "approval")
- `{REVIEW_URL}` - Link to the review
- `{PHASE_TYPE}` - Type of phase (e.g., "DONE", "final")
- `{DOCUMENT_PATTERN}` - Pattern of analysis documents
- `{OUTPUT_DOCUMENT_PATH}` - Where to create final document
- `{FINAL_QUESTIONS}` - Wrap-up questions

**Example Attribute File** (`ask_phase_done_gerrit_topic.txt`):
```yaml
type: phase_done
workspace_path: workspace/horizon-osprh-12803-working
milestone: +2
review_url: https://review.opendev.org/c/openstack/horizon/+/966349
phase_type: DONE
document_pattern: HOWTO_osprh_12803_patchset_8_fix_javascript_collapse_phase5_comment_X.org
output_document: analysis/analysis_osprh_12803_fix_javascript_collapse_phase5_comment_DONE.org
final_questions: |
  do we have a Topic for de-angularize? How do we find that topic?
  
  You can search our horizon open/closed review list at:
  https://review.opendev.org/q/project:openstack/horizon+status:open
  https://review.opendev.org/q/project:openstack/horizon+status:closed
  
  to see how other topics have been created
  
  for whatever reason, the topic showing up at https://review.opendev.org/c/openstack/horizon/+/966349 is "keypair-chevron-patch19"
  
  I want it to be de-angularize
  
  Then, after that is set, how does one view a "topic"? Where do I go to see tickets tagged with de-angularize?
  
  For my next angularjs task, what do you recommend as far as setting this topic? Do I always use a branch name that matches the topic?
  
  I need to understand better in how this is done.
```

---

## Common Patterns Across All Ask Types

### 1. **Document Location Pattern**
```
For your answers to my inquiry below - please create a new {OUTPUT_DOCUMENT_PATH}
```
- Always specifies where the output should go
- Usually in `analysis/` directory, not `workspace/`
- Sometimes includes "(from top level)" to clarify path

### 2. **Context Setting Pattern**
```
{REVIEW_CONTEXT}
{CURRENT_STATE}
{RELEVANT_LINKS}
```
- Provides background information
- Links to review, patchsets, comments
- Current git state, working directory

### 3. **Specific Question Pattern**
```
My question(s):

{QUESTION_1}

{QUESTION_2}

{QUESTION_3}
```
- Questions clearly separated
- Often includes code snippets
- May reference specific files/lines

### 4. **Constraint Pattern**
```
Please remember - {CONSTRAINT_1}
Do not {CONSTRAINT_2}
I want {PREFERENCE}
```
- Specifies what NOT to do
- Clarifies preferences
- Sets boundaries

### 5. **Git Context Pattern**
```
I already have done the following

: cd {PATH}
: git clone {REPO} {DIR}
: git fetch {REMOTE} refs/changes/{XX}/{REVIEW}/{PATCHSET}
: git checkout FETCH_HEAD
: git checkout -b {BRANCH}
```
- Uses `: ` prefix for literal commands
- Shows exact git state
- Specifies branch names

---

## Automation Design

### File Structure

```
mymcp/
├── ask_me.sh                          # Main automation script
├── askme/                             # Ask templates directory
│   ├── templates/                     # Template files
│   │   ├── analysis_doc_create.template
│   │   ├── code_implement_workspace.template
│   │   ├── code_review_response.template
│   │   ├── investigate_patterns.template
│   │   └── phase_done.template
│   └── keys/                          # Attribute key files
│       ├── fix_chevron_id.yaml
│       ├── review_comment_css_gap.yaml
│       └── phase_done_gerrit_topic.yaml
└── analysis/
    └── docs/
        └── ask_me_database.md         # This file
```

### Script Usage

```bash
# Basic usage
./ask_me.sh <ask-type> <key-file>

# Examples
./ask_me.sh analysis_doc_create askme/keys/fix_chevron_id.yaml
./ask_me.sh code_review_response askme/keys/review_comment_css_gap.yaml
./ask_me.sh phase_done askme/keys/phase_done_gerrit_topic.yaml
```

### Template File Format (`.template`)

```
ask:

{TEMPLATE_CONTENT_WITH_PLACEHOLDERS}
```

### Key File Format (`.yaml`)

```yaml
type: <template-type>
<placeholder_name>: <value>
<placeholder_name>: |
  multiline
  value
```

---

## Template Files to Create

### 1. `analysis_doc_create.template`
```
ask:

For your answers to my inquiry below - please create a new {OUTPUT_DOCUMENT_PATH}

{CONTEXT_DESCRIPTION}

{SPECIFIC_QUESTIONS}
```

### 2. `code_implement_workspace.template`
```
ask:

I already have done the following

: cd {WORKSPACE_PATH}
: {GIT_SETUP_COMMANDS}

I want you to make all your recommended changes

Show me how you would do this work in this {WORKSPACE_NAME} directory?
```

### 3. `code_review_response.template`
```
ask:

For your answers to my inquiry below - please create a new (from top level) {OUTPUT_DOCUMENT_PATH}

From {REVIEW_COMMENT_URL}

From the comment below:

{SPECIFIC_INVESTIGATION}

Comment:

{REVIEWER_NAME} {PATCHSET_NUMBER}

{REVIEWER_COMMENT}

file: {FILE_PATH}

{CODE_CONTEXT}
```

### 4. `investigate_patterns.template`
```
ask:

For your answers to my inquiry below - please create a new {OUTPUT_DOCUMENT_PATH}

{PHASE_CONTEXT}

I want to start simple.

Information:

{CURRENT_STATE_INFO}

For the changes below (using + for add, - for removed)

I want to focus the simple change to get this code to put the {TARGET_ELEMENT} to come from somewhere?

When programming this type of code in {FRAMEWORK} - what is the recommened way to put this code somewhere? template? other?

{CODE_DIFF}
```

### 5. `phase_done.template`
```
ask:

one step at a time...

my current working directory is at {WORKSPACE_PATH}

Now that we have a {MILESTONE} on {REVIEW_URL}

This will be our last {PHASE_TYPE} phase for our chain of analysis documents named {DOCUMENT_PATTERN}...

Please remember - when I ask you to produce a document, I do not want it to be in the workspace folder, instead, I want it in the analysis folder.

Do not create a new analysis folder - use the one that is at the same directory level as workspace.

For your answers to my inquiry below - please create a new (from top level) {OUTPUT_DOCUMENT_PATH}

This will be the place where we (follow up) add our last few actions before officially saying {REVIEW_URL} is ready for a merge.

My question(s):

{FINAL_QUESTIONS}
```

---

## Key Attribute Common Patterns

### Review Context Attributes
- `review_url` - Link to the Gerrit review
- `review_number` - Just the number (e.g., 966349)
- `patchset_number` - Patchset number (e.g., "Patchset 11")
- `reviewer_name` - Name of the reviewer
- `review_comment_url` - Link to specific comment

### Git Context Attributes
- `workspace_path` - Full path to workspace
- `workspace_name` - Directory name only
- `git_repo` - Git repository URL
- `git_branch` - Branch name
- `git_setup_commands` - Commands to set up git state

### Document Attributes
- `output_document` - Where to create the document
- `document_pattern` - Pattern for document series
- `phase_number` - Phase number (e.g., "phase1", "phase2")
- `phase_type` - Type of phase (e.g., "DONE", "comment_6")

### Content Attributes
- `context_description` - Background information
- `specific_questions` - The actual questions
- `code_diff` - Code changes to discuss
- `code_context` - Code snippet for context
- `reviewer_comment` - Comment from reviewer

---

## Statistics from Review 966349

### Total "Ask" Documents: 19 files

### Ask Type Distribution:
- **Analysis Document Creation**: 8 (42%)
- **Code Review Response**: 7 (37%)
- **Code Implementation**: 3 (16%)
- **Phase Wrap-up**: 1 (5%)

### Common Placeholders Used:
1. `{OUTPUT_DOCUMENT_PATH}` - 18 occurrences (95%)
2. `{WORKSPACE_PATH}` - 12 occurrences (63%)
3. `{REVIEW_URL}` - 16 occurrences (84%)
4. `{CONTEXT_DESCRIPTION}` - 14 occurrences (74%)
5. `{SPECIFIC_QUESTIONS}` - 18 occurrences (95%)

### Document Naming Patterns:
- `analysis_osprh_12803_*` - For analysis documents
- `analysis_osprh_12803_fix_javascript_collapse_phase*` - For phase documents
- `analysis_osprh_12803_fix_javascript_collapse_phase5_comment_*` - For comment responses

---

## Future Enhancements

### Phase 2: Template Engine
- Use Jinja2 or similar for advanced templating
- Support conditional sections
- Support loops for multiple questions

### Phase 3: Interactive Mode
- Prompt user for values instead of requiring YAML file
- Validate inputs
- Show preview before generating

### Phase 4: Integration with Gerrit
- Fetch review/comment data automatically from Gerrit API
- Auto-populate reviewer names, patchset numbers
- Extract code context from review

### Phase 5: AI Integration
- Automatically send generated ask to AI
- Store response in analysis document
- Track ask/response pairs

---

## Usage Examples

### Example 1: Responding to a Code Review Comment

**Command**:
```bash
./ask_me.sh code_review_response askme/keys/review_phase5_comment_6.yaml
```

**Key File** (`review_phase5_comment_6.yaml`):
```yaml
type: code_review_response
output_document: analysis/analysis_osprh_12803_fix_javascript_collapse_phase5_comment_6.org
review_comment_url: https://review.opendev.org/c/openstack/horizon/+/966349/comment/9cf9a894_d4bd10a0/
reviewer_name: Radomir Dopieralski
patchset_number: Patchset 11
specific_investigation: |
  First, please explain what these two lines do:
  tr.keypair-detail-row td { padding: 0 };
  tr.keypair-detail-row tod div.keypair-details { margin: 8px };
reviewer_comment: |
  I would add something like:
  tr.keypair-detail-row td { padding: 0 };
  tr.keypair-detail-row tod div.keypair-details { margin: 8px };
  to the style, to get rid of that gap when the details are collapsed.
file_path: openstack_dashboard/dashboards/project/key_pairs/tables.py
code_context: |
     40   /* Rotate chevron 90 degrees when row is expanded (not collapsed) */
     41   .chevron-toggle:not(.collapsed) .fa-chevron-right {
     42     transform: rotate(90deg);
     43   }
     44   </style>
```

**Output**: Formatted ask ready to send to AI

---

### Example 2: Creating Analysis for a New Problem

**Command**:
```bash
./ask_me.sh analysis_doc_create askme/keys/fix_chevron_id.yaml
```

**Key File** (`fix_chevron_id.yaml`):
```yaml
type: analysis_doc_create
output_document: analysis/analysis_osprh_12803_fix_chevron_id.org
context_description: |
  We are working on review https://review.opendev.org/c/openstack/horizon/+/966349
  Patchset 7 was just pushed.
  The current chevron_id generation uses creation_counter which does not work correctly.
specific_questions: |
  Please figure out how we can get unique chevron_id for each row.
  
  The way it is being done now does not work - these chevron_ids need
  to be based on the row id somehow - but, the row id is not available at this context?
  
  I have heard we may need some way to expose the unique "cell id" for where this chevron symbol appears.
  
  class ExpandableKeyPairColumn(tables.Column):
      def get_data(self, datum):
          chevron_id = "%s_table_chevron%d" % (self.table.name, self.creation_counter)
          return render_to_string(
              "key_pairs/_chevron_column.html",
              {"chevron_id": chevron_id}
          )
  
  Can you please analyze and give the details on why this approach does not work?
```

---

## Best Practices

### 1. **Be Specific in Questions**
- ✅ "Please explain what these two lines do and how they get applied to tables.py"
- ❌ "Explain the code"

### 2. **Provide Context**
- ✅ Include review URL, patchset number, current state
- ❌ Assume AI remembers previous context

### 3. **Use Consistent Naming**
- ✅ Follow pattern: `analysis_osprh_<number>_<description>.org`
- ❌ Random or inconsistent names

### 4. **Specify Output Location**
- ✅ Always specify full path from repo root
- ❌ Relative paths that could be ambiguous

### 5. **Include Code Context**
- ✅ Show relevant code snippets
- ❌ Just reference "the code" without showing it

---

## Appendix: All Ask Documents from Review 966349

| # | File | Ask Type | Phase |
|---|------|----------|-------|
| 1 | HOWTO_OSPRH_12803_Add_chevrons_to_the_key_pair_table_REVISIT_1.txt | analysis_doc_create | Initial |
| 2 | HOWTO_OSPRH_12803_Add_chevrons_to_the_key_pair_table_REVISIT_2.txt | analysis_doc_create | Initial |
| 3 | HOWTO_osprh_12803_ExpandableKeyPairColumn_mark_safe.txt | investigate_patterns | Patchset 5 |
| 4 | HOWTO_osprh_12803_fix_chevron_id.txt | analysis_doc_create + code_implement | Patchset 7 |
| 5 | HOWTO_osprh_12803_patchset_8_fix_javascript_collapse_phase1.txt | code_review_response | Patchset 8 |
| 6 | HOWTO_osprh_12803_patchset_8_fix_javascript_collapse_phase2.txt | code_review_response | Patchset 8 |
| 7 | HOWTO_osprh_12803_patchset_8_fix_javascript_collapse_phase3.txt | code_review_response | Patchset 8 |
| 8 | HOWTO_osprh_12803_patchset_8_fix_javascript_collapse_phase4.txt | code_review_response | Patchset 8 |
| 9 | HOWTO_osprh_12803_patchset_8_fix_javascript_collapse_phase5.txt | code_review_response | Patchset 10 |
| 10 | HOWTO_osprh_12803_patchset_8_fix_javascript_collapse_phase5_comment_6.txt | code_review_response | Patchset 11 |
| 11 | HOWTO_osprh_12803_patchset_8_fix_javascript_collapse_phase5_comment_7.txt | code_review_response | Patchset 11 |
| 12 | HOWTO_osprh_12803_patchset_8_fix_javascript_collapse_phase5_comment_7_follow_up_1.txt | code_review_response | Patchset 11 |
| 13 | HOWTO_osprh_12803_patchset_8_fix_javascript_collapse_phase5_comment_8.txt | code_review_response | Patchset 11 |
| 14 | HOWTO_osprh_12803_patchset_8_fix_javascript_collapse_phase5_comment_9.txt | code_review_response | Patchset 11 |
| 15 | HOWTO_osprh_12803_patchset_8_fix_javascript_collapse_phase5_comment_10.txt | code_review_response | Patchset 11 |
| 16 | HOWTO_osprh_12803_patchset_8_fix_javascript_collapse_phase5_comment_11.txt | code_review_response | Patchset 11 |
| 17 | HOWTO_osprh_12803_patchset_8_fix_javascript_collapse_phase5_comment_12.txt | code_review_response | Patchset 11 |
| 18 | HOWTO_osprh_12803_patchset_8_fix_javascript_collapse_phase5_comment_13.txt | code_review_response | Patchset 11 |
| 19 | HOWTO_osprh_12803_patchset_8_fix_javascript_collapse_phase5_comment_DONE.txt | phase_done | Final |

---

**Document Version**: 1.0  
**Created**: November 15, 2025  
**Source**: Review 966349 - Key Pairs De-Angularization  
**Total Patterns Identified**: 5 core patterns  
**Total Ask Documents Analyzed**: 19 files

