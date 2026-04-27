# CHORD Continuity

Last updated: 2026-04-26
Repository: `finish-racing/CHORD`
Default branch: `main`

## Purpose

CHORD is a music playlist analysis and creation project for GenX. The repository is being synchronized from the extracted CHORD project handoff archive.

## Current authority model

Use this continuity file with the full handoff archive.

Primary archive:

- `CHORD_Project_Full_Handoff.zip`

Start here when restoring or continuing work:

1. Extract the archive.
2. Read `artifacts/MANIFEST.json`.
3. Identify the newest CHORD package snapshot for code continuation.
4. Identify the newest printed-report/spec documentation for design authority.
5. Preserve CHORD v1.0 as the locked baseline unless the user explicitly says otherwise.
6. Treat later changes as v1.1+ work.

## Locked baseline and forward direction

- CHORD v1.0 is the locked baseline.
- v1.1 adds the Settings Control Panel framework and Printed Report Output direction.
- Printed Report Output is its own report-design family, not just generic PDF export.
- The tool should remain fun and music-forward even when premium.

## Continuity rules

- Do not re-invent CHORD when the established process already exists.
- Do not silently simplify the analysis.
- Do not replace the real process with a “similar” one.
- Keep scope tight unless the user approves expansion.
- Be honest about scaffolding vs fully finished implementation.
- No shortcuts.
- No pretending.
- No hidden simplifications.
- No scope creep without permission.
- Preserve locked behavior exactly once agreed.

## Conflict resolution

If artifacts conflict:

1. Prefer newer versioned artifacts over older ones.
2. Prefer explicit locked decisions over loose drafts.
3. Prefer faithful continuity over clever reinvention.
4. If something is incomplete, say so plainly.
5. Continue from the strongest real baseline.
6. Do not overstate completion.

## Runtime and deployment target

- Ubuntu laptop runtime is the real deployment target.
- In-line/local runs should preserve CHORD logic, only changing runtime environment details.

## Compact project guidance status

No separate confirmed ≤800-character CHORD guidance file has been recovered in the available continuity material. The available authoritative guidance is represented by this consolidated file, derived from the CHORD bootstrap and handoff message.

## Current sync workflow decision

Codespaces ZIP extraction is paused because of terminal/font display friction. The fastest practical path is now the ChatGPT GitHub connector route:

1. Inspect repo state through the GitHub connector.
2. Make the smallest useful file changes directly through the connector.
3. Prefer consolidated files when they reduce commit count without damaging continuity.
4. Use branches/PRs only when the scope or risk justifies it.
5. Avoid the GitHub mobile app for multi-file repo reconstruction.

## Source continuity packet summarized here

This file consolidates the operational content from:

- `CHORD_BOOTSTRAP_FOR_NEW_CONTINUITY.txt`
- `CHORD_MESSAGE_TO_NEW_CONTINUITY.txt`

It is intended as a durable root-level restoration/resume marker, not a substitute for the full handoff archive when the archive is available.
