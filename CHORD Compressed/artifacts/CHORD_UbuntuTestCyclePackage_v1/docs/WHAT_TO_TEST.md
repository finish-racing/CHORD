# CHORD What-To-Test List

## 1. Installation and startup
- Run the installer script successfully
- Confirm the virtual environment is created
- Confirm the systemd service file is installed
- Confirm PostgreSQL bootstrap steps succeed
- Confirm `chord-web` starts
- Confirm `/health` responds

## 2. Configuration behavior
- Confirm config file is read from `/etc/chord/config.toml`
- Confirm env overrides from `/etc/chord/chord.env` work
- Confirm debug mode can be toggled on/off

## 3. Web UI basics
- Home page loads
- New run page loads
- Run detail page loads after creation
- Upload form accepts Top 25 + one or more playlists
- Quiz form submits
- Dashboard updates after pipeline completion

## 4. Core pipeline
- Create run
- Upload Top 25 + playlist set
- Save quiz
- Run pipeline
- Confirm status progresses through stages
- Confirm progress thermometer updates
- Confirm aggregates panel populates
- Confirm enrichment panel populates
- Confirm identity panel populates
- Confirm PRISM recommendation board populates
- Confirm curated playlist board populates

## 5. CLI workflow
- `chord create-run`
- `chord import-playlists`
- `chord submit-quiz`
- `chord build-aggregates`
- `chord enrich-run`
- `chord build-identity`
- `chord run-prism`
- `chord build-curated`
- `chord diagnose-run`

## 6. Exports
- Export recommendations JSON
- Export curated playlist JSON
- Export debug index JSON
- Confirm exported files are written where expected

## 7. Debugging and diagnostics
- Enable debug mode
- Confirm `chord.debug.log` is written
- Confirm debug artifacts appear under `/var/lib/chord/debug/<run_id>/`
- Confirm diagnostics route and command return useful information

## 8. Maintenance and recovery
- Soft reset a run
- Re-run pipeline after soft reset
- Hard reset a run
- Upgrade flow
- Rollback flow
