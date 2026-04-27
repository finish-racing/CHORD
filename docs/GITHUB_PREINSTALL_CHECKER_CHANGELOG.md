# GitHub Pre-Install Checker Changelog

Branch: `testing/github-preinstall-checker`

## 2026-04-26

### Branch and release isolation

- Created isolated release snapshot branch: `release/chord-ubuntu-testcycle-v1-experimental`.
- Created future development branch: `develop`.
- Created experiment branch: `testing/github-preinstall-checker`.
- Added `RELEASE_STATUS.md` on the release snapshot branch.
- Added `docs/BRANCHING_MODEL.md` on `develop` and this experiment branch.
- Added `docs/GITHUB_PREINSTALL_CHECKER_PLAN.md` on this experiment branch.
- No experiment files were merged into `main`.

### GitHub pre-install checker implementation

Added on `testing/github-preinstall-checker` only:

- `installer/install_chord_github_actions.sh`
- `.github/workflows/github-preinstall-checker.yml`
- `scripts/github_preinstall_smoke_test.sh`
- `tests/fixtures/top25_sample.txt`
- `tests/fixtures/playlist_sample.txt`

### Dependency repair discovered by checker

- First observed run failed because `httpx` was imported by `chord.integrations.http_client` but was not listed in `pyproject.toml`.
- Added missing runtime dependencies on this branch only: `httpx>=0.27` and `jinja2>=3.1`.

### Successful checker run

Workflow run `24971955865` completed successfully.

Validated in GitHub Actions:

- PostgreSQL service container initialization,
- package installation in a workspace-local venv,
- CI-local config generation,
- source compilation,
- core module imports,
- CLI help,
- database schema initialization,
- run creation,
- fixture Top 25 import,
- fixture playlist import,
- quiz submission,
- aggregate build,
- Uvicorn app startup,
- `/health` response,
- `/runs` response,
- artifact upload from `.ci/runtime`.

### Current validation limit

This proves GitHub Actions can perform a pre-install smoke check. It does not prove production Ubuntu installer behavior, systemd behavior, nginx behavior, or the final Ubuntu laptop acceptance cycle.

### Explicit non-changes

- Production Ubuntu installer was not modified.
- `main` was not modified by checker implementation.
- Release snapshot branch was not used for active checker iteration.
