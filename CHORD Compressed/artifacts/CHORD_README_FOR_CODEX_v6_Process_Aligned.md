# CHORD README for Codex v6 (Process-Aligned)

This README updates the build policy for CHORD.

## Critical process rule

Build **directly toward the final Ubuntu release app**.

Do **not** interpret Waves A/B/C/D or release packages as separate customer-facing or separately tested Ubuntu releases unless the controlling documentation explicitly requires it.

## What waves mean

Waves and release packages are:
- internal implementation boundaries,
- checkpoint/save boundaries,
- time-out/crash prevention boundaries for the build process.

They are **not**:
- mandatory per-wave Ubuntu installers,
- mandatory per-wave laptop test milestones,
- interim release candidates unless explicitly packaged that way later.

## Real testing rule

No testing done inside the build environment counts as project acceptance testing.

The only real test cycle that matters is:
- the final CHORD Ubuntu application
- installed on the user's laptop
- run there with real inputs
- debugged using the built-in logs, dumps, and state artifacts

## Coding rule

Every wave still adds real product code to the final CHORD codebase.  
No demo-only code.  
No fake placeholder business logic.  
No mock app shells pretending to be complete.

## Installer rule

The installer, upgrade path, rollback path, and reset tooling should be built for the **final release**, not rebuilt as separate per-wave deliverables unless explicitly requested later.

## Current implementation posture

- Use the latest CHORD master handoff as the build contract.
- Use the release tracker and control document as internal progress controls.
- Continue from the current Wave A locked codebase toward Wave B and beyond.
