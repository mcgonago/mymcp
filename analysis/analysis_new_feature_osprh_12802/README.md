# OSPRH-12802: Implement Key Pair Create Form in Python

**Jira**: [OSPRH-12802](https://issues.redhat.com/browse/OSPRH-12802)  
**Epic**: [OSPRH-12801](https://issues.redhat.com/browse/OSPRH-12801) - Remove angular.js from Horizon  
**Status**: 🚀 In Progress - Patchset 1 Submitted  
**Estimated Effort**: 7 days (1.5 sprints)

---

## 🚀 Current Status: Patchset 1 Submitted for Review

**Review**: [967269 - De-angularize Key Pairs: Add Django-based Create form](https://review.opendev.org/c/openstack/horizon/+/967269)  
**Submitted**: November 17, 2025  
**Topic**: [`de-angularize`](https://review.opendev.org/q/topic:de-angularize) (grouped with related de-angularization work)  
**Depends-On**: [Review 966349](https://review.opendev.org/c/openstack/horizon/+/966349) (Approved +2, awaiting merge)

This patchset implements the core "Generate Key Pair" form infrastructure, replacing the AngularJS client-side implementation with Django server-side forms. It is the first of five planned patchsets to complete the de-angularization of the Key Pairs panel.

**Implementation Time**: 1 day (faster than 2-day estimate)  
**Lines Added**: 144 lines across 6 files  
**Testing**: 6 manual test scenarios completed successfully  

---

## Overview

This directory contains complete documentation for implementing the Key Pair creation forms (Generate and Import) using Python/Django, replacing the AngularJS implementation as part of the Horizon de-angularization effort.

## Quick Links

### Documentation
- **[spike.md](spike.md)** - Initial investigation and planning
- **[Patchset 1: Generate Form](patchset_1_generate_key_pair_form.md)** - 2 days ✅ **Submitted**
- **[Patchset 1: Design Document](patchset_1_generate_key_pair_form_design.md)** - Detailed design rationale ✅ **Complete**
- **[Patchset 2: Import Form](patchset_2_import_key_pair_form.md)** - 2 days
- **[Patchset 3: Download Page](patchset_3_private_key_download.md)** - 1.5 days
- **[Patchset 4: Error Handling](patchset_4_error_handling_polish.md)** - 1 day
- **[Patchset 5: Tests & PEP8](patchset_5_tests_pep8.md)** - 2 days

### Upstream Reviews
- **[Review 967269](https://review.opendev.org/c/openstack/horizon/+/967269)** - Patchset 1: Generate Key Pair Form 🚀 **Active**
  - Topic: [`de-angularize`](https://review.opendev.org/q/topic:de-angularize)
  - Depends on: [Review 966349](https://review.opendev.org/c/openstack/horizon/+/966349) (Key Pairs expandable rows - Approved +2 ⏳)

## Implementation Phases

### Phase 1: Planning (Complete)
- [x] Spike document created
- [x] Patchset documents created
- [x] Timeline estimated
- [x] Dependencies identified

### Phase 2: Implementation (In Progress)

Follow these documents in order:

```
1. spike.md              → ✅ Complete - Understand the problem and approach
2. patchset_1_*.md       → 🚀 SUBMITTED - Implement Generate Key Pair form (Review 967269)
3. patchset_2_*.md       → 📋 Next - Implement Import Key Pair form  
4. patchset_3_*.md       → 📋 Pending - Implement private key download page
5. patchset_4_*.md       → 📋 Pending - Polish error handling and UX
6. patchset_5_*.md       → 📋 Pending - Add tests and ensure PEP8 compliance
```

**Current Status**: Patchset 1 submitted for review. Awaiting CI results and reviewer feedback.

### Phase 3: Review & Merge

#### Patchset 1 (In Progress)
- [x] Submit to Gerrit with topic: `de-angularize`
- [x] Link dependency: Review 966349
- [ ] Wait for Review 966349 to merge (has +2 approval)
- [ ] CI tests pass
- [ ] Address reviewer feedback
- [ ] Achieve +2 approval
- [ ] Merge upstream

#### Future Patchsets
- [ ] Submit remaining patchsets (2-5)
- [ ] Iterative review and refinement
- [ ] Final integration testing
- [ ] Complete feature merge

---

## Document Structure

Each patchset document follows this comprehensive format:

### 📋 Executive Summary
- Goal, approach, files affected, expected result

### 🔧 Implementation Details
- Problem statement
- Step-by-step instructions with complete code examples
- Key technical decisions explained

### ✅ Testing Checklist
- Manual testing scenarios (10-15 per patchset)
- Command-line verification
- Edge cases and error scenarios

### 📝 Commit Message Template
- Complete, ready-to-use git commit message
- Follows OpenStack standards

### ❓ Expected Reviewer Questions
- Anticipated questions with prepared answers
- Based on Review 966349 experience

### 📚 Dependencies & References
- Required APIs, libraries, related work

---

## Key Features

### Generate Key Pair
- User provides name and optional key type (SSH or X509)
- Server generates both public and private keys via Nova
- Private key returned to user for download
- Public key stored in Nova

### Import Key Pair
- User provides name and existing SSH public key
- Comprehensive validation (algorithm, format, encoding)
- Public key stored in Nova
- User already has private key locally

### Private Key Download
- Secure, one-time display of generated private key
- Copy to clipboard functionality
- Download as .pem file
- Step-by-step usage instructions
- Security best practices

---

## Timeline

### Actual vs. Estimated

| Patchset | Estimated | Actual | Review | Status |
|----------|-----------|--------|--------|--------|
| Patchset 1 | 2 days | 1 day | [967269](https://review.opendev.org/c/openstack/horizon/+/967269) | 🚀 Submitted (Nov 17, 2025) |
| Patchset 2 | 2 days | TBD | - | 📋 Pending |
| Patchset 3 | 1.5 days | TBD | - | 📋 Pending |
| Patchset 4 | 1 day | TBD | - | 📋 Pending |
| Patchset 5 | 2 days | TBD | - | 📋 Pending |
| **Total** | **8.5 days** | **1 day / 8.5** | - | 🚀 In Progress |

**Patchset 1 Highlights**:
- Implementation: 1 day (Nov 17, 2025)
- Files modified: 4 (forms.py, views.py, urls.py, tables.py)
- Files created: 2 (create.html, _create.html)
- Total lines: 144 lines added
- Design document: Complete with full reference analysis
- Dependency: Built on Review 966349 (expandable rows)

*Note: Timeline will be updated as work progresses*

---

## Development Environment

### Prerequisites

```bash
# Set up working directory
cd /home/omcgonag/Work/mymcp/workspace
git clone https://review.opendev.org/openstack/horizon horizon-osprh-12802-working
cd horizon-osprh-12802-working

# Configure git
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Install git-review
pip install git-review
git review -s

# Create working branch
git checkout -b osprh-12802-generate-form
```

### DevStack Access

You'll need access to a running DevStack instance for testing:

- See: [analysis/analysis_new_feature_966349/HOWTO_install_devstack_on_psi.org](../analysis_new_feature_966349/HOWTO_install_devstack_on_psi.org)
- Or: [analysis/analysis_new_feature_966349/HOWTO_install_devstack_on_laptop.org](../analysis_new_feature_966349/HOWTO_install_devstack_on_laptop.org)

---

## Success Criteria

### Planning & Documentation
- [x] Spike document complete
- [x] All patchset documents created
- [x] Design document with code references complete

### Implementation Progress
- [x] Patchset 1: Generate Key Pair form implemented
- [x] Patchset 1: Submitted to Gerrit (Review 967269)
- [ ] Patchset 1: CI tests passing
- [ ] Patchset 1: +2 approval received
- [ ] Import Key Pair form implemented (Patchset 2)
- [ ] Private key download page implemented (Patchset 3)
- [ ] Error handling polish (Patchset 4)
- [ ] Unit tests and PEP8 (Patchset 5)

### Quality Assurance
- [x] Patchset 1: Manual testing complete (6 scenarios)
- [ ] All forms validated and functional
- [ ] Error handling comprehensive
- [ ] Unit tests written and passing
- [ ] PEP8 compliant
- [ ] Complete manual testing (30+ scenarios)

### Upstream Delivery
- [x] First patchset submitted upstream
- [ ] All patchsets reviewed and approved
- [ ] Feature merged to master

---

## Code Metrics (Projected)

### Files to Create/Modify

```
openstack_dashboard/dashboards/project/key_pairs/
├── forms.py                     (~200 lines added)
├── views.py                     (~120 lines added)
├── urls.py                      (~10 lines added)
├── tables.py                    (~15 lines modified)
├── templates/key_pairs/
│   ├── create.html              (~50 lines new)
│   ├── import.html              (~70 lines new)
│   └── download.html            (~200 lines new)
└── tests/
    ├── test_forms.py            (~300 lines added)
    └── test_views.py            (~150 lines added)

Total: ~1,115 lines of new/modified code
```

### Test Coverage Goal

- Forms: >90% coverage
- Views: >85% coverage
- Overall: >85% coverage for new code

---

## Related Work

### Dependencies

- **Review 966349** (Key Pairs expandable rows) - ⏳ Awaiting Merge
  - Link: https://review.opendev.org/c/openstack/horizon/+/966349
  - Provides foundation (custom row rendering, chevron functionality)
  - Reference: [analysis/analysis_new_feature_966349/](../analysis_new_feature_966349/)
  - Status: Approved +2 (Nov 2025), waiting for merge

### Downstream Work

After completing OSPRH-12802, the Key Pairs panel will be fully de-angularized and ready for the Angular removal in:

- **OSPRH-16644**: Deprecate and remove angular.js from Horizon

### Related Tickets

See [analysis/docs/ANGULAR_JS_TICKETS.md](../docs/ANGULAR_JS_TICKETS.md) for the complete list of de-angularization tickets.

---

## Best Practices Applied

This implementation follows best practices identified from Review 966349:

1. ✅ **Use framework features first** - Django forms, Bootstrap modals
2. ✅ **Comprehensive validation** - Client and server-side
3. ✅ **User-friendly errors** - Actionable guidance, not just "failed"
4. ✅ **Security focus** - One-time private key display, session management
5. ✅ **Accessibility** - ARIA labels, keyboard navigation, screen reader friendly
6. ✅ **Test coverage** - Unit tests for all paths
7. ✅ **PEP8 compliance** - Clean, maintainable code
8. ✅ **Documentation** - Comprehensive commit messages and code comments
9. ✅ **Iterative development** - Small, reviewable patchsets
10. ✅ **Reviewer-friendly** - Clear commit messages, anticipated questions

See: [analysis/docs/BEST_PRACTICES_FEATURE_DEV.md](../docs/BEST_PRACTICES_FEATURE_DEV.md)

---

## Resources

### Internal Documentation

- [Best Practices](../docs/BEST_PRACTICES_FEATURE_DEV.md) - Feature development patterns
- [AngularJS Tickets](../docs/ANGULAR_JS_TICKETS.md) - All de-angularization work
- [Review 966349 Analysis](../analysis_new_feature_966349/) - Completed expandable rows feature
- [Ask Automation](../../askme/README.md) - Generate "ask" prompts for AI assistance

### Upstream Resources

- [Nova API Documentation](https://docs.openstack.org/api-ref/compute/)
- [Nova Keypairs API](https://docs.openstack.org/api-ref/compute/#keypairs-keypairs)
- [Horizon Forms Documentation](https://docs.openstack.org/horizon/latest/contributor/topics/forms.html)
- [Horizon Testing Guide](https://docs.openstack.org/horizon/latest/contributor/topics/testing.html)
- [OpenStack Coding Guidelines](https://docs.openstack.org/hacking/latest/)

---

## Getting Started

### For Implementation

1. **Read the spike**: [spike.md](spike.md) - Understand the full scope
2. **Set up environment**: Follow "Development Environment" section above
3. **Start with Patchset 1**: [patchset_1_generate_key_pair_form.md](patchset_1_generate_key_pair_form.md)
4. **Follow the testing checklists**: Each patchset has comprehensive tests
5. **Update this README**: Mark items complete as you progress

### For Review

1. **Check the spike**: Understanding the overall approach
2. **Review patchsets in order**: Each builds on the previous
3. **Verify testing**: Each patchset has 10-15 manual tests documented
4. **Check commit messages**: Should match templates in documents

---

## Questions?

### Using Ask Automation

Generate formatted "asks" for AI assistance:

```bash
cd /home/omcgonag/Work/mymcp

# Example: Create an ask for investigating a specific issue
cat > askme/keys/osprh_12802_issue.yaml <<EOF
type: investigate_patterns
output_document: analysis/analysis_osprh_12802_issue.md
phase_context: Working on OSPRH-12802 Patchset 2
target_element: public key validation
framework: Horizon
current_state_info: |
  Having issues with base64 validation...
code_diff: |
  def clean_public_key(self):
      # Code here...
EOF

./ask_me.sh investigate_patterns askme/keys/osprh_12802_issue.yaml
```

See: [askme/README.md](../../askme/README.md) for complete guide.

---

## Recent Updates

### November 17, 2025
- ✅ **Patchset 1 Submitted**: Review 967269 created and pushed to Gerrit
- ✅ **Design Document Complete**: Full reference analysis with GitHub links
- ✅ **WIP Documentation**: Complete development log in `analysis_new_feature_osprh_12802_wip/`
- 🎯 **Next**: Monitor CI results and prepare for reviewer feedback

### November 15, 2025
- ✅ **Planning Complete**: All patchset documents created
- ✅ **Spike Complete**: Investigation and approach defined
- ✅ **Environment Setup**: DevStack ready, workspace configured

---

**Created**: November 15, 2025  
**Last Updated**: November 17, 2025  
**Status**: 🚀 In Progress - Patchset 1 Under Review  
**Next Action**: Monitor Review 967269, prepare Patchset 2


