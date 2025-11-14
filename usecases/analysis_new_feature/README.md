# Feature Development (Analysis) Workflow Using Cursor

## Overview

This use case demonstrates how to use Cursor with MCP agents to perform systematic feature development analysis. The `analysis/` directory provides a permanent knowledge base for documenting research, methodology, and findings during feature development work.

This workflow was successfully used during the development of the expandable Key Pairs table feature that was merged upstream: [Review 966349](https://review.opendev.org/c/openstack/horizon/+/966349).

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

## How to Use

### Step 1: Create a New Analysis Document

```bash
# Create a new analysis from template
cd analysis
cp analysis_template.md analysis_<topic>.md
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

- ✅ **Permanent knowledge base** (tracked in git)
- ✅ **All queries and sources documented**
- ✅ **Reproducible research methodology**
- ✅ **Easy onboarding for new team members**
- ✅ **Historical context for future work**
- ✅ **Institutional memory preservation**

## Directory Structure

The analysis directory is organized at the top level:

```
/home/omcgonag/Work/mymcp/
├── analysis/                           # Permanent research documents
│   ├── README.md                       # Analysis directory guide
│   ├── analysis_template.md            # Template for new analyses
│   ├── analysis_template_random_topics.md  # Template for Q&A style analyses
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
- [Analysis Template](../../analysis/analysis_template.md) - Standard template
- [Analysis Template (Random Topics)](../../analysis/analysis_template_random_topics.md) - Q&A style template
- [Review Automation Use Case](../review_automation/README.md) - Automated review workflow
- [Main Repository README](../../README.md) - Repository overview

## See Also

- [OpenDev Review Agent](../../opendev-review-agent/README.md) - Analyze Gerrit reviews
- [GitHub Review Agent](../../github-agent/README.md) - Analyze GitHub PRs
- [GitLab Agent](../../gitlab-rh-agent/README.md) - Analyze GitLab issues/MRs
- [Jira Agent](../../jira-agent/README.md) - Query Jira issues

