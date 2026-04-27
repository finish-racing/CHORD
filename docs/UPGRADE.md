# CHORD Upgrade Guide

## Deploy a new release
1. Copy the new release package to Ubuntu.
2. Extract it.
3. Run:
   `RELEASE_VERSION=<new-version> bash installer/deploy_release.sh`
4. Verify:
   - service status
   - health endpoint
   - run `chord show-status` for a known run if desired

## Preservation behavior
The following should remain preserved across upgrades:
- PostgreSQL data
- `/etc/chord/config.toml`
- `/etc/chord/chord.env`
- `/var/lib/chord/uploads`
- `/var/lib/chord/cache`
- `/var/lib/chord/exports`
- `/var/lib/chord/debug`
- `/var/log/chord`
