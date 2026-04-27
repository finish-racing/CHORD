# CHORD Release Tracker v1

This tracker is the formal build and release checklist for CHORD and the PRISM Engine. 
Use it to mark each release package complete only when all required items and definitions of done are satisfied.

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
13. **Release Package 13 — Ubuntu Test Cycle Package**

## Tracker

### Release Package 1 — Wave A Lock

**Goal:** Foundation stabilized and aligned to current master handoff

**Status:** ☐ Not started  ☐ In progress  ☐ Complete

**Must be complete**
- [ ] Project structure finalized for Wave A
- [ ] Config system working
- [ ] Debug mode framework present
- [ ] Two-level error handling structure present
- [ ] Logging framework present and tied to debug mode
- [ ] PostgreSQL connection layer working
- [ ] Alembic/migration scaffold working
- [ ] Apple/iTunes TXT import working
- [ ] Top 25 import working
- [ ] Quiz storage working
- [ ] CLI baseline working
- [ ] Minimal API baseline working
**Definition of done**
- [ ] No placeholder modules in Wave A scope
- [ ] No fake/mock/demo logic in Wave A
- [ ] All Wave A commands/routes documented
- [ ] Debug artifacts can be enabled/disabled from config
- [ ] Ready for Ubuntu install and import testing

### Release Package 2 — Wave B1 Behavioral Intelligence

**Goal:** Behavioral feature layer from uploaded data

**Status:** ☐ Not started  ☐ In progress  ☐ Complete

**Must be complete**
- [ ] Top 25 anchor extraction
- [ ] Cross-playlist recurrence metrics
- [ ] Play/skip/rating tension model
- [ ] Artist/era/genre aggregate generation
- [ ] Intake quality score
- [ ] Initial omission scaffolding
- [ ] Initial representation/redundancy scaffolding
- [ ] Initial boundary and role/mood scaffolding from local data only
**Definition of done**
- [ ] Feature tables persisted in PostgreSQL
- [ ] Provenance for locally-derived signals stored
- [ ] Confidence fields present where applicable
- [ ] Debug dumps available for aggregates
- [ ] CLI/API inspection surfaces available

### Release Package 3 — Wave B2 External Enrichment

**Goal:** Real enrichment stack integrated

**Status:** ☐ Not started  ☐ In progress  ☐ Complete

**Must be complete**
- [ ] MusicBrainz client
- [ ] AcousticBrainz client
- [ ] Last.fm official API client
- [ ] Cache tables and cache policy
- [ ] Retry logic
- [ ] API provenance capture
- [ ] Confidence scoring for external results
- [ ] Fallback hierarchy for missing data
**Definition of done**
- [ ] Enrichment can run per track/run
- [ ] Cached enrichment persists across runs
- [ ] Failures degrade gracefully
- [ ] No silent service failures
- [ ] Operator can inspect enrichment status by run

### Release Package 4 — Wave B3 Identity and Similarity Intelligence

**Goal:** Identity engine around duplicates, versions, covers, mood, role, and omission

**Status:** ☐ Not started  ☐ In progress  ☐ Complete

**Must be complete**
- [ ] Same recording logic
- [ ] Same work logic
- [ ] Same-title different-work protection
- [ ] Version classification baseline
- [ ] Candidate-vs-playlist duplicate gate
- [ ] Cover tolerance modeling
- [ ] Representation/redundancy logic
- [ ] Mood-family inference
- [ ] Playlist-role inference
- [ ] Cultural omission intelligence
- [ ] Boundary model integration
- [ ] False-positive prevention inputs
- [ ] Portable curator profile expansion
**Definition of done**
- [ ] Duplicate/cover decisions are persisted
- [ ] Review/allow/block/penalize actions are visible
- [ ] Mood/role assignments are queryable
- [ ] Curator profile is exportable
- [ ] Debug artifacts explain classification decisions

### Release Package 5 — Wave C1 PRISM Engine Core

**Goal:** Actual recommendation engine implemented

**Status:** ☐ Not started  ☐ In progress  ☐ Complete

**Must be complete**
- [ ] Weighted scoring passes
- [ ] Score fusion
- [ ] Confidence scoring
- [ ] Explanation generation
- [ ] Reranking constraints
- [ ] Artist caps
- [ ] Era/decade caps
- [ ] Title-family saturation handling
- [ ] Duplicate-role penalties
- [ ] Safe / balanced / discovery modes
**Definition of done**
- [ ] Ranked recommendations can be generated for a run
- [ ] Each recommendation has score + confidence + explanation
- [ ] Provenance traces major signals
- [ ] Debug mode can dump score snapshots
- [ ] No scoring pass is undocumented

### Release Package 6 — Wave C2 Curated Playlist Builder

**Goal:** Standalone curated-playlist generation

**Status:** ☐ Not started  ☐ In progress  ☐ Complete

**Must be complete**
- [ ] Existing-song pool selection logic
- [ ] New-candidate inclusion logic
- [ ] Diversity balancing
- [ ] Role coverage balancing
- [ ] Era spread balancing
- [ ] Boundary protection
- [ ] Omission rescue integration
- [ ] Redundancy avoidance
- [ ] Final curated-playlist assembly logic
**Definition of done**
- [ ] Tool outputs add recommendations and new curated playlists
- [ ] Output modes are clearly distinct
- [ ] Each curated playlist build is reproducible by run ID and version

### Release Package 7 — Wave C3 Full CLI

**Goal:** Ubuntu CLI fully operable

**Status:** ☐ Not started  ☐ In progress  ☐ Complete

**Must be complete**
- [ ] initdb
- [ ] migrate
- [ ] import
- [ ] import-top25
- [ ] run-analysis
- [ ] list-runs
- [ ] list-playlists
- [ ] show-status
- [ ] show-results
- [ ] export-results
- [ ] export-curated-playlist
- [ ] dump-debug
- [ ] soft-reset
- [ ] hard-reset
**Definition of done**
- [ ] Operator can complete a full run from CLI
- [ ] Help text is complete and ergonomic
- [ ] Debug mode behavior is documented
- [ ] Error messages are clear and actionable

### Release Package 8 — Wave C4 Full Web Interface

**Goal:** Approved Ubuntu web UI implemented

**Status:** ☐ Not started  ☐ In progress  ☐ Complete

**Must be complete**
- [ ] Upload UI
- [ ] Top 25 required intake flow
- [ ] Additional playlist upload flow
- [ ] Quiz UI
- [ ] Run creation flow
- [ ] Progress thermometer
- [ ] Analysis dashboard
- [ ] Recommendation board
- [ ] Curated-playlist board
- [ ] Export/download UI
- [ ] Debug/admin views when enabled
- [ ] Approved CHORD visual style integrated
**Definition of done**
- [ ] Web app matches approved visual direction
- [ ] Progress thermometer tracks real state transitions
- [ ] Results are navigable and understandable
- [ ] No placeholder views in Wave C scope

### Release Package 9 — Wave D1 OpenAI Integration

**Goal:** Required enhanced reasoning layer

**Status:** ☐ Not started  ☐ In progress  ☐ Complete

**Must be complete**
- [ ] Responses API client
- [ ] Config support for OpenAI
- [ ] Function/tool orchestration boundaries
- [ ] Explanation enhancement
- [ ] Optional reranking assistance
- [ ] Deterministic fallback when unavailable
- [ ] Logging/provenance for OpenAI interactions
- [ ] Debug traces/metadata capture
**Definition of done**
- [ ] App works without OpenAI
- [ ] App enhances results with OpenAI when enabled
- [ ] OpenAI failures do not break the core app
- [ ] Operator can tell which outputs used OpenAI

### Release Package 10 — Wave D2 Hardening and Diagnostics

**Goal:** Testable and supportable Ubuntu build

**Status:** ☐ Not started  ☐ In progress  ☐ Complete

**Must be complete**
- [ ] Hardened validation everywhere
- [ ] Hardened error handling everywhere
- [ ] Rich debug artifact generation
- [ ] Log separation and rotation basics
- [ ] State dumps
- [ ] Score snapshots
- [ ] Run-state snapshots
- [ ] Better recovery behavior
- [ ] Operator-facing failure messages
**Definition of done**
- [ ] Any major failure leaves usable artifacts behind
- [ ] Operator can send logs/dumps back for diagnosis
- [ ] App runs cleanly in normal mode or debug mode
- [ ] Debug mode is documented and accessible

### Release Package 11 — Installer and Upgrade System

**Goal:** Real Ubuntu installer and upgrade path

**Status:** ☐ Not started  ☐ In progress  ☐ Complete

**Must be complete**
- [ ] Install script
- [ ] Dependency bootstrap
- [ ] Python environment/bootstrap
- [ ] PostgreSQL setup/init steps
- [ ] App directory creation
- [ ] Config placement
- [ ] Service definitions/start commands
- [ ] Migrate/init commands
- [ ] Versioned release install layout
- [ ] Stable current symlink strategy
- [ ] Upgrade flow
- [ ] Rollback flow
- [ ] Soft reset flow
- [ ] Hard reset flow
- [ ] Artifact/config preservation behavior
**Definition of done**
- [ ] Fresh install works from instructions
- [ ] Upgrade path works from instructions
- [ ] Rollback path works from instructions
- [ ] Config and runtime artifacts are preserved correctly
- [ ] Operator package exists with notes and instructions

### Release Package 12 — Final Documentation and Operator Package

**Goal:** Shipped docs aligned to shipped app

**Status:** ☐ Not started  ☐ In progress  ☐ Complete

**Must be complete**
- [ ] Developer README
- [ ] Operator/admin README
- [ ] Install README
- [ ] Config reference
- [ ] Migration notes
- [ ] Debug mode guide
- [ ] Release notes
- [ ] Known issues
- [ ] Test instructions
- [ ] Artifact collection instructions
- [ ] Build/version/change log
- [ ] Codebase docstrings/comments at expected level
**Definition of done**
- [ ] Docs match actual behavior
- [ ] No stale instructions
- [ ] No undocumented required config keys
- [ ] No undocumented operational steps

### Release Package 13 — Ubuntu Test Cycle Package

**Goal:** First full release for real laptop testing

**Status:** ☐ Not started  ☐ In progress  ☐ Complete

**Must be complete**
- [ ] Installer package
- [ ] Operator package
- [ ] Release notes
- [ ] What-to-test list
- [ ] Known risks list
- [ ] Debug collection instructions
- [ ] Rollback instructions
- [ ] Expected outputs list
**Definition of done**
- [ ] You can install it on Ubuntu
- [ ] You can run a full workflow
- [ ] You can collect artifacts if anything fails
- [ ] Diagnosis is possible from returned artifacts

## Master definition of fully complete

- [ ] All Wave A, B, C, and D packages are done
- [ ] Installer and upgrade/rollback system is done
- [ ] No placeholder business logic remains
- [ ] No demo/mock/fake code remains
- [ ] Web UI matches approved CHORD direction
- [ ] PRISM Engine produces real scored outputs
- [ ] Add recommendations work
- [ ] Curated-playlist builder works
- [ ] OpenAI enhanced mode works
- [ ] Deterministic fallback works
- [ ] Debug mode works
- [ ] Docs match code
- [ ] Ubuntu laptop install and run succeed
- [ ] Issues from Ubuntu testing are resolved into a clean release
