# CHORD Wave B2 v1

**CHORD** = **Curation Heuristics for Omission, Redundancy, and Discovery**  
**PRISM Engine** = **Playlist Recommendation and Identity Scoring Model**

This package continues from the Wave B1 baseline and implements the **Wave B2 External Enrichment** layer.

## Included in Wave B2 v1
- official Last.fm API client
- MusicBrainz client
- AcousticBrainz client
- enrichment cache tables
- provenance and confidence capture
- retry-aware HTTP helper
- fallback routing scaffold
- CLI/API surfaces to enrich and inspect runs

## New CLI commands
- `chord enrich-run --run-id <id>`
- `chord show-enrichment --run-id <id>`

## New API routes
- `POST /runs/{run_id}/enrich`
- `GET /runs/{run_id}/enrichment`

## Process note
Wave B remains an internal build checkpoint toward the final CHORD Ubuntu release.
