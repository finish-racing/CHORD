# CHORD Expected Outputs

## Installation phase
- `/opt/chord/releases/<version>/`
- `/opt/chord/current`
- `/etc/chord/config.toml`
- `/etc/chord/chord.env`
- `/var/lib/chord/uploads`
- `/var/lib/chord/cache`
- `/var/lib/chord/exports`
- `/var/lib/chord/state`
- `/var/lib/chord/debug`
- `/var/log/chord/chord.log`
- `/var/log/chord/chord.error.log`
- `/var/log/chord/chord.debug.log` when debug mode is enabled

## Runtime outputs
For a completed run, expect:
- run record in PostgreSQL
- uploads and playlists recorded
- canonical tracks recorded
- run aggregate payload
- track enrichment payloads
- identity profile
- recommendation set
- curated playlist set
- optional OpenAI enhancement set
- debug artifacts if enabled

## Export outputs
- recommendation results JSON
- curated playlist JSON
- debug index JSON
- diagnostics snapshot JSON when exported manually
