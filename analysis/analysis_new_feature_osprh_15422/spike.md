# Spike: OSPRH-15422 - Explore DFG:UI Contribution for De-Angularization

**Jira**: [OSPRH-15422](https://issues.redhat.com/browse/OSPRH-15422)  
**Epic**: [OSPRH-12801](https://issues.redhat.com/browse/OSPRH-12801) - Remove angular.js from Horizon  
**Type**: Research/Planning  
**Estimated Complexity**: Low (Documentation/Coordination)  
**Date Created**: November 15, 2025

---

## Overview

This ticket is about exploring and documenting potential contributions from the DFG:UI (Distributed Field Guide: UI) team to support the de-angularization effort in OpenStack Horizon.

## Problem Statement

The de-angularization initiative involves significant UI/UX work across multiple Horizon panels. The DFG:UI team may have:
- Relevant expertise in UI modernization
- Resources to contribute to the effort
- Standards and patterns that should be followed
- Testing and validation capabilities

We need to identify:
1. What contributions the DFG:UI team can make
2. How to coordinate with them effectively
3. What standards/patterns they recommend
4. How to leverage their expertise

## Success Criteria

- [ ] Document has been created outlining DFG:UI team capabilities
- [ ] Coordination plan established with DFG:UI team
- [ ] UI/UX standards and patterns documented
- [ ] Contribution areas identified
- [ ] Communication channels established

## Key Questions to Answer

### Stakeholder Questions
1. Who are the key contacts in the DFG:UI team?
2. What is their capacity for this initiative?
3. What is their preferred collaboration model?
4. What timelines are they working with?

### Technical Questions
1. What UI frameworks/standards does DFG:UI recommend?
2. Are there existing UI component libraries we should use?
3. What testing standards should be applied?
4. Are there accessibility requirements we must meet?

### Process Questions
1. How should code reviews be coordinated?
2. What documentation standards are required?
3. How should UI/UX decisions be escalated?
4. What approval process is needed for UI changes?

## Investigation Plan

### Phase 1: Stakeholder Identification (1 day)
1. Identify DFG:UI team leads
2. Schedule initial meeting
3. Document team structure and responsibilities

### Phase 2: Capability Assessment (2 days)
1. Document DFG:UI team's expertise areas
2. Identify available resources
3. Assess capacity for de-angularization work
4. Document existing UI standards

### Phase 3: Coordination Plan (2 days)
1. Define collaboration model
2. Establish communication channels
3. Create escalation process
4. Document decision-making framework

### Phase 4: Documentation (1 day)
1. Create comprehensive stakeholder guide
2. Document UI/UX standards
3. Publish coordination plan
4. Update related tickets with findings

**Total Estimated Time**: 6 days (1 sprint)

## Code Areas (N/A for Research)

This is a research/coordination task with no direct code changes. However, the findings will inform all other de-angularization tickets.

## Dependencies

### Upstream Dependencies
- None (this is the first step)

### Downstream Dependencies
- All other de-angularization tickets (OSPRH-16421-16644) benefit from this research

## Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| DFG:UI team unavailable | High | Medium | Document minimum standards ourselves, seek approval later |
| Conflicting standards | Medium | Low | Early alignment meetings, document tradeoffs |
| Limited capacity | Medium | Medium | Prioritize most critical panels first |
| Communication gaps | High | Medium | Establish clear channels and regular check-ins |

## Deliverables

1. **Stakeholder Map** (`stakeholders.md`)
   - DFG:UI team structure
   - Key contacts
   - Responsibilities

2. **UI/UX Standards Guide** (`ui_ux_standards.md`)
   - Component patterns
   - Accessibility requirements
   - Browser compatibility
   - Testing standards

3. **Coordination Plan** (`coordination_plan.md`)
   - Communication channels
   - Review process
   - Escalation paths
   - Decision framework

4. **Contribution Matrix** (`contribution_matrix.md`)
   - Ticket assignments
   - DFG:UI involvement level
   - Timeline alignment

## Proposed Work Items

### Week 1: Discovery
1. Identify and contact DFG:UI team leads
2. Schedule kickoff meeting
3. Gather existing documentation
4. Document current state

### Week 2: Planning
1. Conduct capability assessment
2. Define collaboration model
3. Create coordination plan
4. Document UI/UX standards

### Week 3: Documentation
1. Write comprehensive guides
2. Update Jira tickets with findings
3. Present to stakeholders
4. Get approval to proceed

## Lessons from Review 966349

While this is a research ticket, learnings from the completed Key Pairs work (Review 966349) are relevant:

### What We Did Well
- Documented decisions thoroughly
- Followed iterative development
- Responded to reviewer feedback

### What We Should Standardize
- **Bootstrap usage patterns** - When to use native collapse vs. custom JS?
- **CSS methodology** - Specificity vs. `!important`, SCSS organization
- **JavaScript patterns** - jQuery usage, event handling standards
- **Template structure** - Django template best practices
- **Testing approach** - What constitutes sufficient testing?

These should be addressed in the UI/UX Standards Guide.

## Next Steps After Spike

1. Create the four deliverable documents listed above
2. Update all related tickets (OSPRH-16421-16644) with relevant findings
3. Schedule kickoff meetings for individual panel work
4. Begin implementation of highest-priority panel (likely Images - OSPRH-16421)

---

## References

- [OSPRH-12801: Remove angular.js from Horizon](https://issues.redhat.com/browse/OSPRH-12801)
- [Review 966349: Key Pairs De-Angularization](https://review.opendev.org/c/openstack/horizon/+/966349)
- [Complete Documentation: Review 966349](../analysis_new_feature_966349/)
- [Best Practices for Feature Development](../docs/BEST_PRACTICES_FEATURE_DEV.md)
- [AngularJS Tickets Overview](../docs/ANGULAR_JS_TICKETS.md)

---

**Status**: 📋 Planning  
**Assigned To**: TBD  
**Target Completion**: TBD

