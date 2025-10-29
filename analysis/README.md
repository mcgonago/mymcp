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

1. **Identify the topic** you want to research
2. **Query the relevant MCP agents** (@github-reviewer-agent, @opendev-reviewer-agent, @gitlab-cee-agent, @jiraMcp)
3. **Document the inquiry** - Save the exact query used
4. **Capture the results** - Include all relevant information returned
5. **Create the analysis file** - Name it descriptively (e.g., `analysis_direct_mode.md`)
6. **Include reproduction steps** - Document how to recreate the research

### Analysis File Template

```markdown
# Analysis: [Topic Title]

## Original Inquiry

**Date:** YYYY-MM-DD
**Asked to:** @agent-name
**Query:**
```
[exact query text]
```

## Data Sources

- [ ] GitHub PRs
- [ ] OpenDev Reviews
- [ ] GitLab MRs
- [ ] Jira Issues
- [ ] Other: [specify]

## Executive Summary

[Brief overview of findings]

## Detailed Findings

[Comprehensive analysis]

## Code References

- PR/Review links
- Commit SHAs
- File paths

## Related Work

- Links to related analyses
- Cross-references

## Reproduction Steps

[Commands to verify or reproduce the findings]

## Conclusions

[Key takeaways]
```

## Current Analyses

- **[analysis_direct_mode.md](analysis_direct_mode.md)** - Horizon/Glance direct mode upload changes (CORS, httpd.conf, etc.)

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

