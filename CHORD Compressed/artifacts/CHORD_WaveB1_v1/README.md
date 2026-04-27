# CHORD Wave B1 v1

**CHORD** = **Curation Heuristics for Omission, Redundancy, and Discovery**  
**PRISM Engine** = **Playlist Recommendation and Identity Scoring Model**

This package continues directly from the Wave A locked baseline and begins **Wave B1 Behavioral Intelligence**.

## Included in Wave B1 v1
- Top 25 anchor extraction
- Cross-playlist recurrence metrics
- Play/skip/rating tension metrics
- Artist / era / genre aggregate generation
- Intake quality score
- Aggregate persistence tables
- CLI/API inspection surfaces for aggregates
- Debug dumps for derived aggregate payloads

## New CLI commands
- `chord build-aggregates --run-id <id>`
- `chord show-aggregates --run-id <id>`

## New API routes
- `POST /runs/{run_id}/aggregates`
- `GET /runs/{run_id}/aggregates`

## Process note
Wave B remains an internal build checkpoint toward the final CHORD Ubuntu release. It is not a separate field-test milestone.
