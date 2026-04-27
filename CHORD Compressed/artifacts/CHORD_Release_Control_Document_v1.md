# CHORD Release Control Document v1

This document converts the release tracker into an active control document. It records the current build state, establishes the controlling baseline, and identifies the next action required before each package can advance.

## Current controlling baseline

- Product: **CHORD**
- Engine: **PRISM Engine**
- Current external handoff baseline: **CHORD / PRISM master handoff v10**
- Current implementation baseline: **CHORD Wave A v3 hardened**
- Current control state: **Release Package 1 (Wave A Lock) is In Progress**

## Package status overview

- **Release Package 1 — Wave A Lock**: In progress
- **Release Package 2 — Wave B1 Behavioral Intelligence**: Not started
- **Release Package 3 — Wave B2 External Enrichment**: Not started
- **Release Package 4 — Wave B3 Identity and Similarity Intelligence**: Not started
- **Release Package 5 — Wave C1 PRISM Engine Core**: Not started
- **Release Package 6 — Wave C2 Curated Playlist Builder**: Not started
- **Release Package 7 — Wave C3 Full CLI**: Not started
- **Release Package 8 — Wave C4 Full Web Interface**: Not started
- **Release Package 9 — Wave D1 OpenAI Integration**: Not started
- **Release Package 10 — Wave D2 Hardening and Diagnostics**: Not started
- **Release Package 11 — Installer and Upgrade System**: Not started
- **Release Package 12 — Final Documentation and Operator Package**: Not started
- **Release Package 13 — Ubuntu Test Cycle Package**: Not started

## Release Package 1 — Wave A Lock

**Goal:** Foundation stabilized and aligned to current master handoff
**Status:** In progress
**Control note:** Wave A codebase exists and has been hardened. This package remains open until Ubuntu-side install/import testing confirms the foundation behaves correctly in the target environment.

### Must-be-complete checkpoints
- [x] Project structure finalized for Wave A
- [x] Config system working
- [x] Debug mode framework present
- [x] Two-level error handling structure present
- [x] Logging framework present and tied to debug mode
- [x] PostgreSQL connection layer working
- [x] Alembic/migration scaffold working
- [x] Apple/iTunes TXT import working
- [x] Top 25 import working
- [x] Quiz storage working
- [x] CLI baseline working
- [x] Minimal API baseline working
### Definition-of-done checkpoints
- [ ] No placeholder modules in Wave A scope
- [x] No fake/mock/demo logic in Wave A
- [x] All Wave A commands/routes documented
- [x] Debug artifacts can be enabled/disabled from config
- [x] Ready for Ubuntu install and import testing
### Next action
- Run Ubuntu-side install/import test and close any defects found there.

## Release Package 2 — Wave B1 Behavioral Intelligence

**Goal:** Behavioral feature layer from uploaded data
**Status:** Not started
**Control note:** Pending start after Wave A Lock is accepted as the controlling baseline.

### Next action
- Begin Top 25 anchors, cross-playlist recurrence, play/skip/rating tension, intake quality score.

## Release Package 3 — Wave B2 External Enrichment

**Goal:** Real enrichment stack integrated
**Status:** Not started
**Control note:** Will follow Wave B1.

### Next action
- Implement MusicBrainz, AcousticBrainz, and official Last.fm clients with caching.

## Release Package 4 — Wave B3 Identity and Similarity Intelligence

**Goal:** Identity engine around duplicates, versions, covers, mood, role, and omission
**Status:** Not started
**Control note:** Will follow Wave B2.

### Next action
- Implement duplicate/variant/cover engine and role/mood/omission intelligence.

## Release Package 5 — Wave C1 PRISM Engine Core

**Goal:** Actual recommendation engine implemented
**Status:** Not started
**Control note:** Will follow Wave B.

### Next action
- Implement scoring passes, fusion, confidence, explanations, and reranking.

## Release Package 6 — Wave C2 Curated Playlist Builder

**Goal:** Standalone curated-playlist generation
**Status:** Not started
**Control note:** Will follow PRISM core.

### Next action
- Implement standalone curated-playlist assembly logic.

## Release Package 7 — Wave C3 Full CLI

**Goal:** Ubuntu CLI fully operable
**Status:** Not started
**Control note:** Will follow recommendation core.

### Next action
- Expand CLI into full operator surface.

## Release Package 8 — Wave C4 Full Web Interface

**Goal:** Approved Ubuntu web UI implemented
**Status:** Not started
**Control note:** Will follow recommendation core.

### Next action
- Build approved CHORD web UI with progress thermometer and result boards.

## Release Package 9 — Wave D1 OpenAI Integration

**Goal:** Required enhanced reasoning layer
**Status:** Not started
**Control note:** Will follow core app behaviors.

### Next action
- Integrate OpenAI Responses API with deterministic fallback.

## Release Package 10 — Wave D2 Hardening and Diagnostics

**Goal:** Testable and supportable Ubuntu build
**Status:** Not started
**Control note:** Will follow major feature completion.

### Next action
- Deepen diagnostics, dumps, recovery, and supportability.

## Release Package 11 — Installer and Upgrade System

**Goal:** Real Ubuntu installer and upgrade path
**Status:** Not started
**Control note:** Will follow app feature maturity.

### Next action
- Build install, upgrade, rollback, reset, and preservation tooling.

## Release Package 12 — Final Documentation and Operator Package

**Goal:** Shipped docs aligned to shipped app
**Status:** Not started
**Control note:** Will follow installer maturity.

### Next action
- Align developer/operator/install/debug docs to shipped behavior.

## Release Package 13 — Ubuntu Test Cycle Package

**Goal:** First full release for real laptop testing
**Status:** Not started
**Control note:** Final packaging gate before broader completion.

### Next action
- Package the first full Ubuntu release for your laptop test cycle.
