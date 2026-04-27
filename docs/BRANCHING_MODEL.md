# CHORD Branching Model

Created: 2026-04-26

## Purpose

This branching model keeps the synchronized CHORD release baseline separate from development and GitHub-based test experiments.

## Branches

### `main`

Current public/default branch. Contains the synchronized CHORD handoff and current Ubuntu test cycle release content.

Rules:
- Do not use `main` for experimental installer work.
- Keep `main` stable unless intentionally promoting verified changes.
- Prefer PR-based promotion from `develop` or release branches.

### `release/chord-ubuntu-testcycle-v1-experimental`

Locked release snapshot branch created from cleaned `main` at commit `2e0fd764a6ae549e7017f27f814a2caf898ab080`.

Rules:
- Treat as experimental / install at own risk.
- Preserve synchronized release state.
- Do not use for active GitHub Actions installer iteration.
- Use only for reference, reproduction, or emergency comparison.

### `develop`

Primary future development integration branch.

Rules:
- New CHORD app development should branch from `develop`.
- Merge to `main` only after validation.
- Keep release snapshot branches separate from active development.

### `testing/github-preinstall-checker`

Experimental branch for building a GitHub Actions pre-release installer and app checker.

Rules:
- All GitHub pre-install checker work starts here.
- CI harness changes, test-specific config, and GitHub-only installer scripts belong here first.
- Do not merge to `main` until the experiment is proven useful and intentionally promoted.

## Promotion flow

Recommended flow:

1. Preserve release snapshot branch.
2. Build GitHub test harness on `testing/github-preinstall-checker`.
3. When stable, merge useful test harness pieces into `develop`.
4. After development validation, promote from `develop` into `main`.
5. Create a new release snapshot branch for any future release candidate.

## Safety rule

Do not mix GitHub pre-release test harness changes into the synchronized release baseline without an explicit promotion decision.
