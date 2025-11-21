# Workspace Scripts Directory

This directory contains scripts for automating code review and verification workflows.

## Script Index

| Script | Purpose | Usage |
|--------|---------|-------|
| [fetch-review.sh](fetch-review.sh) | 🔄 **Review Fetcher** | Automatically fetch code reviews from OpenDev, GitHub, or GitLab and create assessment templates |
| [verify-pr-483.sh](verify-pr-483.sh) | ✅ **PR Verifier** | Verify that PR #483 changes are included in RHOSO 1.0 operator builds |

## Detailed Descriptions

### fetch-review.sh

**Purpose**: Streamline the code review analysis workflow by automatically fetching review code and creating structured assessment documents.

**Features**:
- Fetches reviews from OpenDev (Gerrit), GitHub, or GitLab
- Creates git clones in workspace for code analysis
- Generates assessment templates in `results/` directory
- Supports `--with-assessment` flag for automatic template creation
- Integrates with MCP agents for metadata retrieval

**Usage**:
```bash
# OpenDev review
./fetch-review.sh --with-assessment opendev https://review.opendev.org/c/openstack/horizon/+/965215

# GitHub PR
./fetch-review.sh --with-assessment github https://github.com/openstack-k8s-operators/horizon-operator/pull/483

# GitLab MR
./fetch-review.sh --with-assessment gitlab <gitlab-mr-url>
```

**Options**:
- `--with-assessment` - Create assessment template automatically
- First argument: Platform type (`opendev`, `github`, `gitlab`)
- Second argument: Review URL

**Output**:
- Git clone in `workspace/<project>-<review-number>/`
- Assessment document in `results/review_<number>.md` (if using `--with-assessment`)

**Documentation**: See [../docs/REVIEW_ASSESSMENT_GUIDE.md](../docs/REVIEW_ASSESSMENT_GUIDE.md)

---

### verify-pr-483.sh

**Purpose**: Runtime verification that PR #483 (horizon-operator IncludeOptional support) is correctly included in deployments.

**Features**:
- Checks for IncludeOptional directive in httpd configuration
- Verifies conf.d directory structure
- Tests configuration file inclusion
- Provides detailed verification output

**Usage**:
```bash
# Run in deployed environment
./verify-pr-483.sh
```

**What it checks**:
1. Presence of `IncludeOptional` directive in base httpd.conf
2. Existence of `/etc/httpd/conf.d/` directory
3. Loading of custom configuration files from conf.d/
4. Proper Apache configuration syntax

**Documentation**: See [../docs/PR-483-VERIFICATION-GUIDE.md](../docs/PR-483-VERIFICATION-GUIDE.md)

---

## Adding New Scripts

When adding new scripts to this directory:

1. **Make executable**: `chmod +x script-name.sh`
2. **Add shebang**: Start with `#!/usr/bin/env bash`
3. **Add usage function**: Include `usage()` function with help text
4. **Update this README**: Add entry to the table above with description
5. **Document in workspace/docs/**: Create detailed guide if needed

## Related Resources

- [Workspace README](../README.md) - Overview of workspace structure
- [Review Automation Use Case](../../usecases/review_automation/README.md) - Complete workflow documentation
- [Workspace Documentation](../docs/) - Related guides and summaries

---

**Total Scripts**: 2 files  
**Last Updated**: November 15, 2025

