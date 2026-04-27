# CHORD v1.0 Ubuntu Build README for Codex

This README is the required first-read companion to the handoff DOCX.

## Locked names
- Product: **CHORD** = **Curation Heuristics for Omission, Redundancy, and Discovery**
- Engine: **PRISM Engine** = **Playlist Recommendation and Identity Scoring Model**

## Mission
Build the final Ubuntu v1.0 application exactly according to the handoff specification. Do not create a generic music recommender. Implement the deterministic curator-intelligence system described in the DOCX.

## Primary deliverables
1. Ubuntu web application
2. Ubuntu CLI
3. PostgreSQL-backed persistence layer
4. Installer/bootstrap for Ubuntu
5. Deterministic recommendation engine
6. OpenAI-enhanced reasoning layer with deterministic fallback
7. Exportable recommendation and curated-playlist outputs

## Mandatory implementation order
1. Read the DOCX handoff and this README completely.
2. Create the Ubuntu project structure and installer bootstrap.
3. Implement configuration loading and environment validation.
4. Implement PostgreSQL schema, migrations, and storage layout.
5. Implement upload intake, run records, source provenance, and file persistence.
6. Implement Apple/iTunes playlist parsing plus Top 25 ingestion.
7. Implement canonicalization and exact/loose duplicate handling.
8. Build the unified analysis universe.
9. Implement MusicBrainz, AcousticBrainz, and Last.fm clients with local caching.
10. Implement candidate generation.
11. Implement multi-pass scoring and reranking exactly per the handoff.
12. Implement duplicate / version / cover logic exactly per the handoff.
13. Implement standalone curated-playlist builder mode.
14. Implement explanations, confidence, provenance, and diagnostics.
15. Implement Ubuntu web UI using the approved CHORD visual language from the handoff.
16. Implement the live progress thermometer in both web and CLI surfaces.
17. Add OpenAI Responses API integration as an augmentation layer, not a replacement for deterministic ranking.
18. Run validation and acceptance tests.

## Non-negotiable build rules
- Do not over-weight mood.
- Do not collapse the system into same-artist or same-era similarity.
- Treat Top 25 Most Played as the strongest replay-core signal.
- Treat the uploaded playlist set as the broader accepted curation universe.
- Preserve duplicate/variant/cover logic and representation/redundancy logic.
- Preserve confidence, explanation, and provenance outputs.
- Preserve deterministic fallback when OpenAI is unavailable.
- Use Last.fm over HTTPS in runtime implementation.
- The Ubuntu web UI must inherit the approved visual language from the accepted CHORD mobile concept and associated brand boards.

## Final acceptance
The build is not complete until a user can:
1. Upload Top 25 + one or more playlists
2. Answer the short quiz
3. Watch live progress through completion
4. Receive add recommendations and a standalone curated playlist
5. Review explanations, confidence, provenance, and diagnostics
6. Export results from the Ubuntu app

If there is any conflict between compact summaries and the detailed algorithm sections in the DOCX, the detailed algorithm sections govern.
