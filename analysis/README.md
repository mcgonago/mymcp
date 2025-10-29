# Analysis Directory

## Purpose

This directory contains detailed technical analyses of various OpenStack Horizon and related projects. Each analysis is created by querying our MCP agents (GitHub, OpenDev, GitLab, Jira) to gather comprehensive information about specific features, changes, or issues.

## Structure

Each analysis document includes:
- **Original Query/Inquiry** - The exact question or search terms used
- **Data Sources** - Which MCP agents were consulted
- **Findings** - Detailed technical information discovered
- **Code References** - Links to commits, PRs, reviews
- **Context** - Background and rationale for the changes
- **Commands Used** - Exact commands to reproduce the research

## How to Use This Directory

### Creating a New Analysis

The template includes sections for:
- Original inquiry and data sources
- Executive summary and background
- Detailed findings with categories
- Code references (PRs, reviews, commits)
- Implementation timeline
- Testing and verification
- Configuration examples
- Known issues and workarounds
- Related work and cross-references
- Reproduction steps
- Conclusions and recommendations

1. **Copy the template**
   ```bash
   cd <your-mymcp-cloned-repo-path>/analysis
   cp analysis_template.md analysis_<topic-name>.md
   ```
2. Ask Cursor a question - example question for analysis_direct_mode.md

   Create a new analysis_direct_mode.md from analysis_template.md (copy) and fill in with your answer to:
   search for any work done with respect to Horizon/Glance and the changes made (CORS, httpd.conf, ..) to support direct mode upload by default

## Current Analyses

- **[analysis_template.md](analysis_template.md)** - 📝 Template for creating new analyses (copy this to start)
- **[analysis_direct_mode.md](analysis_direct_mode.md)** - Horizon/Glance direct mode upload changes (CORS, httpd.conf, etc.) [✅ Complete - awaiting PR/review searches]

## Benefits of This Approach

1. ✅ **Reproducible Research** - All queries and commands documented
2. ✅ **Knowledge Preservation** - Technical context captured
3. ✅ **Cross-referencing** - Easy to link related analyses
4. ✅ **Onboarding** - New team members can understand historical decisions
5. ✅ **Audit Trail** - Clear record of research methodology

## Tips for Good Analysis Documents

- **Be specific** - Include exact queries, URLs, commit SHAs
- **Show your work** - Include all commands and outputs
- **Provide context** - Explain why the research was needed
- **Link liberally** - Cross-reference related analyses and external resources
- **Update regularly** - Add follow-up findings as they emerge
- **Tag appropriately** - Use clear file naming conventions

## File Naming Convention

```
analysis_<topic-name>.md
```

Examples:
- `analysis_direct_mode.md`
- `analysis_integration_tests_removal.md`
- `analysis_django5_migration.md`
- `analysis_cors_configuration.md`

## Integration with Workspace

This analysis directory complements the `workspace/` directory:
- **workspace/** - For temporary code checkouts and active review analysis
- **analysis/** - For permanent documentation of research and findings

Together, they provide a complete code review and research workflow.

---

**Note:** This directory is tracked in git to preserve institutional knowledge. Ensure sensitive information (tokens, passwords, internal-only data) is not committed.

