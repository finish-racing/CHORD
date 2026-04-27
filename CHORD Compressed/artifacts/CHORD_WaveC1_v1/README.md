# CHORD Wave C1 v1

**CHORD** = **Curation Heuristics for Omission, Redundancy, and Discovery**  
**PRISM Engine** = **Playlist Recommendation and Identity Scoring Model**

This package continues from Wave B3 and implements **Wave C1 PRISM Engine Core**.

## Included in Wave C1 v1
- candidate generation from canonical tracks
- weighted scoring passes
- score fusion
- confidence scoring
- recommendation explanation generation
- reranking constraints
- safe / balanced / discovery modes
- recommendation persistence tables
- CLI/API surfaces to build and inspect PRISM recommendations

## New CLI commands
- `chord run-prism --run-id <id> [--mode safe|balanced|discovery]`
- `chord show-prism --run-id <id>`

## New API routes
- `POST /runs/{run_id}/prism`
- `GET /runs/{run_id}/prism`

## Process note
Wave C remains an internal build checkpoint toward the final CHORD Ubuntu release.
