# CHORD Rollback Guide

## Roll back to a previous release
1. Identify the previous version under `/opt/chord/releases/`
2. Run:
   `TARGET_VERSION=<old-version> bash installer/rollback_release.sh`

## Notes
Rollback changes the active code release by updating `/opt/chord/current`.
It does not delete PostgreSQL data, config, uploads, cache, exports, or debug artifacts.
