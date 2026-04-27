# CHORD Wave D2 v1

**CHORD** = **Curation Heuristics for Omission, Redundancy, and Discovery**  
**PRISM Engine** = **Playlist Recommendation and Identity Scoring Model**

This package continues from Wave D1 and implements **Wave D2 Hardening and Diagnostics**.

## Included in Wave D2 v1
- expanded exception model
- standard vs debug error responses
- diagnostic snapshot service
- run-state snapshots
- score snapshot helpers
- debug artifact index export
- richer operator-facing failure messages
- CLI/API diagnostics surfaces

## New CLI commands
- `chord diagnose-run --run-id <id>`
- `chord export-debug-index --run-id <id> --out /path/file.json`

## New API routes
- `GET /runs/{run_id}/diagnostics`
- `GET /runs/{run_id}/debug-index`
