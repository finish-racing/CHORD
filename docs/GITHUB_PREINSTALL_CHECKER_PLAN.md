# GitHub Pre-Install Checker Experiment Plan

Created: 2026-04-26
Branch: `testing/github-preinstall-checker`

## Purpose

Create a GitHub Actions-based installer and smoke-test harness that can install and exercise CHORD before any Ubuntu laptop installation.

This is an experiment to determine whether GitHub can serve as a fast testing iteration tool for CHORD.

## Non-goals

- Do not replace real Ubuntu laptop testing.
- Do not certify production readiness.
- Do not modify the locked synchronized release snapshot.
- Do not assume GitHub Actions is equivalent to the final Ubuntu runtime.

## Isolation rule

All experiment files and changes must remain on `testing/github-preinstall-checker` until explicitly promoted.

The existing synchronized CHORD release remains preserved on:

- `main`
- `release/chord-ubuntu-testcycle-v1-experimental`

## Required implementation steps

### 1. Create a CI-specific installer entry point

Add a new script rather than altering the production installer first:

- `installer/install_chord_github_actions.sh`

The script should:

- use workspace-local paths by default,
- avoid `systemctl`,
- avoid Nginx,
- avoid permanent system user creation,
- avoid required writes to `/opt/chord`, `/etc/chord`, `/var/lib/chord`, and `/var/log/chord`,
- create a Python virtual environment in a temporary or workspace-local directory,
- install the package with `pip install -e .`,
- generate a CI-local `config.toml`,
- initialize runtime directories,
- emit an install summary artifact.

### 2. Add GitHub Actions workflow

Add:

- `.github/workflows/github-preinstall-checker.yml`

The workflow should:

1. Check out the repository.
2. Set up Python 3.11.
3. Start PostgreSQL using either:
   - a GitHub Actions service container, or
   - the runner PostgreSQL package if preferred.
4. Create CHORD database/user or use a postgres superuser connection for CI.
5. Run the GitHub-specific installer.
6. Run `chord initdb --config <ci-config>`.
7. Run `chord --help`.
8. Compile `src` with `python -m compileall src`.
9. Import core modules.
10. Start Uvicorn with `chord.web.api:api` against the CI config.
11. Poll `/health`.
12. Create a smoke run through CLI or API.
13. Optionally upload minimal fixture playlist data.
14. Export logs, config summary, and diagnostics as workflow artifacts.

### 3. Add CI-local config generation

The CI installer should generate something like:

- `.ci/runtime/config.toml`
- `.ci/runtime/uploads/`
- `.ci/runtime/cache/`
- `.ci/runtime/exports/`
- `.ci/runtime/state/`
- `.ci/runtime/debug/`
- `.ci/runtime/logs/`

Database URL should come from environment:

- `CHORD_DATABASE_URL`

### 4. Add smoke-test fixture data

Add minimal test fixtures under:

- `tests/fixtures/top25_sample.txt`
- `tests/fixtures/playlist_sample.txt`

These should be tiny, synthetic, and safe to keep in the repo.

### 5. Add smoke test script

Add:

- `scripts/github_preinstall_smoke_test.sh`

It should test:

- package import,
- CLI help,
- database initialization,
- run creation,
- Top 25 + playlist import,
- quiz submission,
- aggregate build,
- optional pipeline stages that do not require external API keys,
- web app `/health`.

### 6. Add Python-level smoke tests if useful

Optional later addition:

- `tests/test_ci_smoke.py`

This can use `pytest` once the shell-based harness is proven.

### 7. Capture artifacts

The workflow should upload:

- generated config summary with secrets redacted,
- install summary,
- CLI output logs,
- Uvicorn logs,
- CHORD debug directory if enabled,
- smoke test result JSON.

### 8. Define pass/fail gates

Minimum pass gate:

- package installs,
- core modules import,
- DB schema initializes,
- CLI help works,
- web app starts,
- `/health` returns success.

Expanded pass gate:

- run can be created,
- fixture files can be imported,
- quiz can be submitted,
- aggregates can be built,
- diagnostic/export commands work.

Full future gate:

- full pipeline completes with deterministic fallback and no external credentials.

## Required documentation changes

All changes made for this experiment must be tracked in:

- `docs/GITHUB_PREINSTALL_CHECKER_CHANGELOG.md`
- `docs/GITHUB_PREINSTALL_CHECKER_PLAN.md`

Do not merge experiment files into `main` until the experiment is reviewed and explicitly promoted.

## Risks

- GitHub Actions is not a full substitute for the target Ubuntu laptop.
- Service behavior under `systemd` is not tested by CI-local Uvicorn execution.
- Path and permission behavior differs from `/opt`, `/etc`, and `/var` production install paths.
- Database lifecycle is disposable in CI.
- External APIs should remain disabled unless secrets are intentionally configured.

## Success definition for the experiment

The experiment is successful if GitHub Actions can repeatedly install CHORD from a clean checkout, initialize its database, start the app, pass health checks, and execute at least a minimal deterministic smoke workflow before Ubuntu laptop installation.
