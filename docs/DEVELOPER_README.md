# CHORD Developer README

## Product naming
- **CHORD** = **Curation Heuristics for Omission, Redundancy, and Discovery**
- **PRISM Engine** = **Playlist Recommendation and Identity Scoring Model**

## Architecture summary
CHORD is an Ubuntu-first playlist intelligence system with:
- FastAPI web application
- Typer-based CLI
- PostgreSQL persistence
- PRISM Engine scoring/reranking
- external enrichment clients for Last.fm, MusicBrainz, and AcousticBrainz
- optional OpenAI Responses API enhancement
- installer, upgrade, rollback, and reset support

## Current source layout
- `src/chord/config.py` — config loader and environment overrides
- `src/chord/db/` — SQLAlchemy base, models, session, repositories
- `src/chord/domain/` — quiz and domain-level definitions
- `src/chord/ingest/` — Apple/iTunes TXT parsing and normalization
- `src/chord/integrations/` — external API clients
- `src/chord/services/` — pipeline services and operator services
- `src/chord/web/` — FastAPI API, HTML UI templates, CSS, UI helpers
- `installer/` — deployment, service, and database bootstrap assets
- `docs/` — operator and release documentation

## Pipeline order
1. create run
2. import Top 25 and playlist files
3. capture quiz
4. build aggregates
5. enrich run
6. build identity
7. run PRISM
8. build curated playlist
9. optionally run OpenAI enhancement

## Development rules
- No mock/demo-only code
- Standard and debug error handling must both exist
- Validation must remain hardened
- Logging, error handling, and debugging remain connected
- CLI/API surfaces should remain ergonomic
- The Ubuntu laptop is the real target runtime
- The final Ubuntu test cycle is the only real acceptance test

## Notes for further implementation
The current codebase already includes the main pipeline, web interface, and installer scaffolding. Any remaining work should refine correctness, add missing export formats, and close documentation/code drift.
