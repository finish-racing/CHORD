# CHORD Release Tracker v2

This tracker is the formal build and release checklist for CHORD and the PRISM Engine.

## Build policy note

Release packages are **internal construction and checkpoint boundaries**. They are **not** mandatory Ubuntu field-test milestones. The only real-world test cycle that counts for project acceptance is the **final completed Ubuntu app** running on the user's laptop.

## Current sequence

1. **Release Package 1 — Wave A Lock**
2. **Release Package 2 — Wave B1 Behavioral Intelligence**
3. **Release Package 3 — Wave B2 External Enrichment**
4. **Release Package 4 — Wave B3 Identity and Similarity Intelligence**
5. **Release Package 5 — Wave C1 PRISM Engine Core**
6. **Release Package 6 — Wave C2 Curated Playlist Builder**
7. **Release Package 7 — Wave C3 Full CLI**
8. **Release Package 8 — Wave C4 Full Web Interface**
9. **Release Package 9 — Wave D1 OpenAI Integration**
10. **Release Package 10 — Wave D2 Hardening and Diagnostics**
11. **Release Package 11 — Installer and Upgrade System**
12. **Release Package 12 — Final Documentation and Operator Package**
13. **Release Package 13 — Final Ubuntu Test Cycle Package**

## Current status summary

- Release Package 1 — **Code-complete checkpoint**
- Release Packages 2–13 — **Not started or pending**

## Acceptance rule

A package can be marked complete as an internal build milestone once its scoped code and docs are complete, even if no Ubuntu laptop test has been run yet.

## Final project acceptance

The project is only considered fully accepted when:
- all release packages are complete,
- the final installer exists,
- the final Ubuntu app runs on the user's laptop,
- and issues from that final laptop run have been resolved.
