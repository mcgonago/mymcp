# My MCP Agents Collection

This repository demonstrates how to build custom MCP (Model Context Protocol) agents for Cursor. It contains four MCP agents that I built to analyze different types of code reviews and project management:

- **github-agent**: Analyzes GitHub Pull Requests
- **opendev-review-agent**: Analyzes OpenDev Gerrit reviews
- **gitlab-rh-agent**: Analyzes GitLab Issues, Merge Requests, and Commits from internal Red Hat GitLab
- **jira-agent**: Provides access to Jira issues, projects, and sprints from Cursor

## Table of Contents

- [GitHub Review Agent](#github-review-agent)
- [OpenDev Review Agent](#opendev-review-agent)
- [GitLab RH Agent](#gitlab-rh-agent)
- [Jira Agent](#jira-agent)
- [Complete MCP Configuration](#complete-mcp-configuration)
- [Use Cases](#use-cases)
- [What These Agents Can Do](#what-these-agents-can-do)
- [Next Steps](#next-steps)
- [Additional Resources](#additional-resources)

---

## GitHub Review Agent

An agent for analyzing GitHub Pull Requests with real GitHub API integration.

### Features

- **GitHub API Integration**: Fetches real PR data using PyGithub
- **Authentication**: Uses personal access tokens for API access
- **Comprehensive Data**: Retrieves PR metadata, file changes, comments, and reviews
- **Security**: Environment file for token management (never committed to Git)

**For detailed setup instructions, see [github-agent/README.md](github-agent/README.md).**

---

## OpenDev Review Agent

An agent for analyzing OpenDev Gerrit code reviews for OpenStack projects.

### Features

- **Gerrit API Integration**: Fetches review details from OpenDev's Gerrit REST API
- **Security Prefix Handling**: Strips the `)]}'` prefix that Gerrit adds for security
- **Comprehensive Data**: Retrieves change metadata, file statistics, and comments
- **URL Parsing**: Extracts change numbers from standard OpenDev review URLs

**For detailed setup instructions, see [opendev-review-agent/README.md](opendev-review-agent/README.md).**

---

## GitLab RH Agent

An agent for analyzing GitLab Issues, Merge Requests, and Commits from internal Red Hat GitLab (gitlab.cee.redhat.com).

### Features

- **GitLab API Integration**: Fetches issues, merge requests, and commits from internal Red Hat GitLab
- **Authentication**: Uses personal access tokens with `read_api` scope
- **Supports Issues, MRs, and Commits**: Analyze issues, merge requests, and individual commits
- **Full URL Support**: Paste GitLab URLs directly from your browser
- **Project Path Handling**: Properly URL-encodes project paths for API calls
- **Commit Analysis**: Fetches diffs, file changes, and statistics for security review
- **CVE Detection**: Analyzes commits for security implications and vulnerability fixes
- **Comprehensive Metadata**: Retrieves title, state, description, assignees, labels, and timestamps
- **Security**: Environment file for token management (never committed to Git)

**For detailed setup instructions, see [gitlab-rh-agent/README.md](gitlab-rh-agent/README.md).**

---

## Jira Agent

An agent that provides access to Jira from Cursor with containerized deployment.

> [!NOTE]
> **About the Jira Agent**  
> The `jira-agent` in this repository is based on the excellent work from [redhat-community-ai-tools/jira-mcp](https://github.com/redhat-community-ai-tools/jira-mcp). I followed their well-documented steps as part of my learning journey to build MCP agents.

### Features

- Containerized deployment with Podman
- 20+ Jira tools (issue search, project management, board & sprint management, user management)
- Production-ready setup with proper authentication
- Secure credential management

**For detailed setup instructions, see [jira-agent/README.md](jira-agent/README.md).**

---

## Complete MCP Configuration
Here is what your **MCP Servers** configuration looks like after you are done following the setup and configuration steps for each one.

To see this:
1. Open Cursor Settings (**Ctrl/Cmd + ,**)
2. Search for: **MCP Servers**
3. Click edit on any one of them

```json
{
  "mcpServers": {
    "github-reviewer-agent": {
      "command": "<your-mymcp-cloned-repo-path>/github-agent/server.sh",
      "description": "Analyzes GitHub pull requests to perform automated code review."
    },
    "opendev-reviewer-agent": {
      "command": "<your-mymcp-cloned-repo-path>/opendev-review-agent/server.sh",
      "description": "Analyzes OpenDev Gerrit reviews to perform automated code review."
    },
    "gitlab-cee-agent": {
      "command": "<your-mymcp-cloned-repo-path>/gitlab-rh-agent/server.sh",
      "description": "Agent to fetch and analyze issues/MRs from internal Red Hat GitLab."
    },
    "jiraMcp": {
      "command": "podman",
      "args": [
        "run",
        "--rm",
        "-i",
        "--env-file",
        "/home/username/.rh-jira-mcp.env",
        "jira-agent:latest"
      ],
      "description": "Provides access to Jira issues, projects, boards, and sprints."
    }
  }
}
```

4. **Save your new mcp.json configuration**  
   Go to **File → Save** and then restart Cursor (**Ctrl+Shift+P** → "Developer: Reload Window")
   
   > **Note**: Alternatively, you can fully exit Cursor (**Ctrl+Q**) and restart it, which will also reload the new settings.

### Testing Each Agent

After configuration, test each agent in Cursor:

**GitHub Agent:**
```
@github-reviewer-agent Review https://github.com/openstack-k8s-operators/horizon-operator/pull/402
```

**OpenDev Agent:**
```
@opendev-reviewer-agent Analyze https://review.opendev.org/c/openstack/horizon/+/960204
```

**GitLab Agent:**
```
@gitlab-cee-agent Analyze commit https://gitlab.cee.redhat.com/eng/openstack/python-django/-/commit/848fd870bb51ae6d8ea44512665dab8257f9c27a
```
Or for issues/MRs:
```
@gitlab-cee-agent Analyze issue openstack-konflux/osp-director-operator-17.1/issues/24
```

**Jira Agent:**
```
@jiraMcp Get details for issue OSPRH-13100
```

---

## Use Cases

Practical workflows and examples for using these MCP agents in your development process.

If you come up with different use cases using the MCP agents, please follow the model, add a section and detailed instructions for each new add.

### #1: Review Automation

Automate code review analysis across multiple platforms (OpenDev, GitHub, GitLab) using `fetch_review.sh`.

**For detailed instructions, see [usecases/review_automation/README.md](usecases/review_automation/README.md).**

**Quick Example:**
```bash
cd /home/omcgonag/Work/mymcp/workspace
./fetch-review.sh --with-assessment opendev https://review.opendev.org/c/openstack/horizon/+/965215
```

This workflow:
- ✅ Fetches the review code automatically
- ✅ Creates a structured assessment document
- ✅ Queries the appropriate MCP agent for metadata
- ✅ Provides complete context for code analysis

### #2: Feature Development (Analysis) Workflow Using Cursor

A structured, predictable approach to feature development using Cursor with AI assistance. This workflow systematically breaks down complex features into measurable, time-boxed deliverables with clear complexity rankings and automated story point estimation.

**Core Methodology:**
- **Spike-driven investigation** - Structured technical analysis before implementation
- **Incremental patchsets** - Break features into reviewable, testable chunks
- **Complexity scoring** - Rank technical challenges and knowledge requirements
- **Predictable timelines** - Sprint-aligned deliverables (≤2 weeks per patchset)
- **Parallel development** - Enable feature and test development concurrently
- **AI pattern conformance** - Train LLM on proven "patterns of success" for consistent output

**Proven Results:**
- Review 966349 (Key Pairs): Merged upstream with +2 approval
- Review 967269 (Create Form): 1-day implementation vs. 2-day estimate (50% faster)
- Improved capacity planning through measured complexity scores
- Earlier test planning and parallel test development
- Reduced scope creep through incremental delivery validation

**For detailed instructions, see [usecases/analysis_new_feature/README.md](usecases/analysis_new_feature/README.md).**

**Key Benefits:**
- ✅ Predictable sprint planning with complexity-adjusted story points
- ✅ Earlier detection of scope changes and missed requirements
- ✅ Parallel work streams (feature + tests) for faster delivery
- ✅ Improved team capacity and velocity measurement
- ✅ Structured AI assistance with repeatable patterns
- ✅ Institutional knowledge preservation in git

### #3: Ask Automation System

Generate consistent, well-formatted prompts for AI-assisted development using templates and YAML key files. This system was designed by analyzing patterns from 19 "ask" documents created during Review 966349 development.

**For detailed instructions, see [askme/README.md](askme/README.md).**

**Quick Example:**
```bash
# Generate an ask from a template
./ask_me.sh analysis_doc_create askme/keys/my_investigation.yaml

# Copy output and paste to your AI assistant
```

This system:
- ✅ Standardizes prompt formatting for consistency
- ✅ Separates template structure from content
- ✅ Enables reusable patterns across features
- ✅ Reduces cognitive load when formulating questions
- ✅ Preserves institutional knowledge in version control

**Available Templates:**
- `analysis_doc_create` - Start new investigations
- `code_implement_workspace` - Implement code changes
- `code_review_response` - Address reviewer feedback
- `investigate_patterns` - Research design patterns
- `phase_done` - Wrap up and transition phases

---

## What These Agents Can Do

These MCP agents enable Cursor's AI to seamlessly interact with your development workflow:

✅ **Code Review Analysis**: Fetch and analyze pull requests, merge requests, and Gerrit reviews  
✅ **Commit Investigation**: Deep-dive into individual commits with diffs and change statistics  
✅ **Issue Tracking**: Query and search Jira issues, projects, boards, and sprints  
✅ **Security Analysis**: Identify CVEs and security-related changes in commits  
✅ **Comprehensive Metadata**: Access authors, reviewers, assignees, labels, timestamps, and state  
✅ **Discussion Context**: Review comments, feedback, and technical discussions  
✅ **Multi-Platform Support**: Works with GitHub, GitLab, OpenDev Gerrit, and Jira  
✅ **API Integration**: Official API support with proper authentication and security  
✅ **Private & Public Access**: Support for both public repositories and private/internal systems

## Next Steps

Once you have these agents set up, you can:

- **Analyze Code Changes**: Review PRs, MRs, and commits to understand technical decisions and implementation details
- **Understand Feedback**: Get AI insights on review comments and discussions across platforms
- **Track Development**: Follow project history, feature development, and bug fixes
- **Security Review**: Analyze commits for CVEs and security implications
- **Project Management**: Query Jira for issue status, sprint progress, and project tracking
- **Cross-Platform Analysis**: Combine multiple agents to correlate code changes with issues and reviews
- **Automated Summaries**: Get quick AI-powered summaries of complex reviews and discussions
- **Learn Best Practices**: Study OpenStack coding patterns and enterprise development workflows

> [!NOTE]
> **Explore More MCP Agents**  
> The [redhat-community-ai-tools](https://github.com/redhat-community-ai-tools) organization maintains several high-quality MCP agents and tools. I highly recommend checking out their repositories to discover other useful agents and learn from their implementations. They provide excellent examples of professional MCP agent development.

---

## Additional Resources

### Verification Script

Use `test-mcp-setup.sh` to verify all agents are properly configured:

```bash
./test-mcp-setup.sh
```

This script will:
- Test each agent's server startup
- Verify virtual environments and dependencies
- Check Cursor configuration
- Provide troubleshooting guidance

### Directory Structure

```
mymcp/
├── README.md                           # This file
├── ask_me.sh                           # Ask automation script
├── askme/                              # Ask automation system
│   ├── README.md                       # Ask automation guide
│   ├── templates/                      # Ask templates
│   │   ├── analysis_doc_create.template
│   │   ├── code_implement_workspace.template
│   │   ├── code_review_response.template
│   │   ├── investigate_patterns.template
│   │   └── phase_done.template
│   └── keys/                           # YAML key files (your configs)
│       ├── example_fix_chevron_id.yaml
│       ├── example_implement_chevron_fix.yaml
│       ├── example_review_comment_css_gap.yaml
│       ├── example_template_pattern.yaml
│       └── example_phase_done_gerrit_topic.yaml
├── github-agent/                       # GitHub PR review agent
│   ├── server.py                       # Main MCP server
│   ├── server.sh                       # Launch script
│   ├── README.md                       # Detailed setup guide
│   ├── TROUBLESHOOTING.md              # Troubleshooting guide
│   ├── SETUP.md                        # GitHub authentication guide
│   ├── example.env                     # Environment template
│   └── requirements.txt                # Python dependencies
├── opendev-review-agent/               # OpenDev Gerrit review agent
│   ├── server.py                       # Main MCP server
│   ├── server.sh                       # Launch script
│   ├── README.md                       # Detailed setup guide
│   ├── TROUBLESHOOTING.md              # Troubleshooting guide
│   └── requirements.txt                # Python dependencies
├── gitlab-rh-agent/                    # GitLab issue/MR agent (Red Hat internal)
│   ├── server.py                       # Main MCP server
│   ├── server.sh                       # Launch script
│   ├── README.md                       # Detailed setup guide
│   ├── TROUBLESHOOTING.md              # Troubleshooting guide
│   ├── example.env                     # Environment template
│   └── requirements.txt                # Python dependencies
├── jira-agent/                         # Jira integration agent
│   ├── server.py                       # Main MCP server
│   ├── README.md                       # Detailed setup guide
│   ├── TROUBLESHOOTING.md              # Troubleshooting guide
│   ├── requirements.txt                # Python dependencies
│   ├── Containerfile                   # Container definition
│   ├── Makefile                        # Build and setup automation
│   ├── example.env                     # Environment variables template
│   ├── example.mcp.json                # MCP configuration template
│   └── LICENSE                         # MIT License
├── usecases/                           # Practical use case examples and workflows
│   ├── review_automation/              # Automated review analysis workflow
│   │   └── README.md                   # Review automation guide
│   └── analysis_new_feature/           # Feature development analysis workflow
│       └── README.md                   # Feature development guide
├── images/                             # Screenshots and documentation images
├── workspace/                          # Temporary workspace for code review analysis (gitignored)
│   ├── README.md                       # Workspace usage guide
│   ├── REVIEW_ASSESSMENT_GUIDE.md      # Comprehensive assessment feature guide
│   ├── QUICK_START.md                  # Quick reference commands
│   ├── fetch-review.sh                 # Helper script to fetch reviews/PRs/MRs
│   └── review_template.md              # Template for review assessments
├── results/                            # Review assessment documents (optional git tracking)
│   ├── README.md                       # Results directory guide
│   └── review_*.md                     # Generated assessment documents
├── analysis/                           # Permanent technical analyses and research
│   ├── README.md                       # Analysis directory guide
│   ├── docs/                            # Individual analysis documents
│   │   ├── analysis_template.md        # Template for creating new analyses
│   │   ├── analysis_direct_mode.md     # Horizon/Glance direct mode upload analysis
│   │   └── ...                          # Other analysis documents
└── test-mcp-setup.sh                   # Verification script for all agents
```

### Key Differences Between Agents

**OpenDev, GitHub & GitLab Agents:**
- Simple shell script execution
- Uses `venv` for Python dependencies
- Direct server.py execution
- Environment files for API tokens (.env)

**Jira Agent:**
- Containerized deployment with Podman
- Uses `--env-file` for credentials
- Runs in isolated container environment
- More secure (credentials never in config file)
- 20+ tools for comprehensive Jira integration

### Contributing

This repository is primarily for educational purposes and demonstration. Feel free to fork and adapt for your own MCP agents!

### License

- `jira-agent` is licensed under the MIT License
- Other agents are provided as examples for educational purposes

---

## Questions?

If you have questions during the demonstration or while following along, please feel free to reach out or open an issue in this repository.

**Happy MCP building!** 🚀
