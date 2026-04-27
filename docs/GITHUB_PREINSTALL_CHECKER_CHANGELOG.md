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

### Current validation target

The checker attempts to verify:

- package installation in a workspace-local venv,
- CI-local config generation,
- PostgreSQL-backed schema initialization,
- source compilation,
- core module imports,
- CLI help,
- run creation,
- fixture playlist import,
- quiz submission,
- aggregate build,
- Uvicorn app startup,
- `/health` response,
- artifact upload from `.ci/runtime`.

### Explicit non-changes

- Production Ubuntu installer was not modified.
- `main` was not modified by checker implementation.
- Release snapshot branch was not used for active checker iteration.
