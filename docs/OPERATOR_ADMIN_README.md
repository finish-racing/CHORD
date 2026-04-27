# CHORD Operator / Admin README

## Main runtime locations
- Code releases: `/opt/chord/releases/<version>/`
- Current release symlink: `/opt/chord/current`
- Config: `/etc/chord/config.toml`
- Environment file: `/etc/chord/chord.env`
- Data: `/var/lib/chord/`
- Logs: `/var/log/chord/`

## Common commands
### Service
- `sudo systemctl status chord-web`
- `sudo systemctl restart chord-web`

### CLI
- `chord create-run`
- `chord import-playlists`
- `chord submit-quiz`
- `chord build-aggregates`
- `chord enrich-run`
- `chord build-identity`
- `chord run-prism`
- `chord build-curated`
- `chord run-openai-enhancement`
- `chord diagnose-run`

## Debug mode
Enable debug mode in config or via `CHORD_DEBUG=1`.

When debug mode is active, CHORD writes:
- standard logs
- error logs
- debug logs
- JSON debug artifacts
- diagnostics snapshots
- score snapshots
- OpenAI trace snapshots where applicable

## Maintenance commands
- soft reset a run: `chord soft-reset --run-id <id>`
- hard reset a run: `chord hard-reset --run-id <id>`

## Artifact collection
Useful locations:
- `/var/log/chord/`
- `/var/lib/chord/debug/`
- exported JSON results created by CLI export commands
