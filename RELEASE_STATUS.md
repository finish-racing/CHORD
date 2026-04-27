# CHORD Ubuntu Test Cycle v1 — Experimental Release Snapshot

Branch: `release/chord-ubuntu-testcycle-v1-experimental`
Base commit: `2e0fd764a6ae549e7017f27f814a2caf898ab080`
Created: 2026-04-26

## Status

This branch is a locked snapshot of the synchronized CHORD Ubuntu Test Cycle v1 repository state after handoff extraction and current release sync.

## Classification

**Experimental / install at own risk.**

This branch preserves the synchronized release candidate as received and extracted. It is not yet proven by a successful install, import, full pipeline run, or Ubuntu laptop validation cycle.

## What is considered locked here

- Extracted handoff archive contents under `CHORD Compressed/`
- Current root-level CHORD app tree
- Installer scripts from the synchronized package
- Documentation, SQL, Alembic scaffold, CLI, web app, and service code

## What is not proven yet

- Production Ubuntu installer success
- GitHub Actions install/test success
- PostgreSQL runtime behavior under real workflow load
- Full playlist upload/import/pipeline execution
- Web UI end-to-end usability
- Final Ubuntu laptop acceptance

## Required next step

Do not modify this release snapshot directly for GitHub pre-release testing. Use:

- `develop` for normal future app development
- `testing/github-preinstall-checker` for the GitHub pre-release installer/checker experiment

## Release warning

This snapshot exists to preserve the synchronized CHORD state. Any install or test should be treated as experimental until a validation run proves the app installs, starts, initializes its database, and completes at least a smoke workflow.
