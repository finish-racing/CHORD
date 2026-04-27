# CHORD Wave C2 v1

**CHORD** = **Curation Heuristics for Omission, Redundancy, and Discovery**  
**PRISM Engine** = **Playlist Recommendation and Identity Scoring Model**

This package continues from Wave C1 and implements **Wave C2 Curated Playlist Builder**.

## Included in Wave C2 v1
- curated playlist set/item persistence
- standalone curated-playlist assembly logic
- existing-song pool selection logic
- candidate inclusion from PRISM outputs
- diversity / era / role balancing
- omission rescue integration
- boundary protection
- CLI/API surfaces for curated playlist generation and inspection

## New CLI commands
- `chord build-curated --run-id <id> [--mode balanced] [--length 60]`
- `chord show-curated --run-id <id> [--mode balanced]`

## New API routes
- `POST /runs/{run_id}/curated`
- `GET /runs/{run_id}/curated`

## Process note
Wave C remains an internal build checkpoint toward the final CHORD Ubuntu release.
