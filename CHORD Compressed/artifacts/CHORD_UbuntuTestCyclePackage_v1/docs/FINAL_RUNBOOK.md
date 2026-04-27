# CHORD Final Ubuntu Runbook

## Install
1. Extract package on Ubuntu
2. Run installer
3. Edit `/etc/chord/chord.env`
4. Edit `/etc/chord/config.toml`
5. Bootstrap PostgreSQL
6. Initialize schema
7. Start `chord-web`

## Execute a full run
1. Open CHORD in browser
2. Create new run
3. Upload Top 25 and playlists
4. Complete quiz
5. Run pipeline
6. Review dashboard
7. Export outputs

## If something fails
1. Capture logs from `/var/log/chord/`
2. Capture debug artifacts from `/var/lib/chord/debug/<run_id>/`
3. Run `chord diagnose-run --run-id <id>`
4. Run `chord export-debug-index --run-id <id> --out /tmp/chord_debug_index.json`
5. If needed, rollback to prior release

## Rollback
- `TARGET_VERSION=<old-version> bash installer/rollback_release.sh`
