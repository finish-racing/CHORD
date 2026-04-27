# CHORD Artifact Collection Guide

When diagnosing issues on the Ubuntu laptop, collect:

## Logs
- `/var/log/chord/chord.log`
- `/var/log/chord/chord.error.log`
- `/var/log/chord/chord.debug.log` (if debug enabled)

## Debug artifacts
- `/var/lib/chord/debug/<run_id>/...`

## Exported indexes
- output from `chord export-debug-index --run-id <id> --out /path/file.json`
- output from `chord diagnose-run --run-id <id>`

## Optional output artifacts
- exported recommendation JSON
- exported curated playlist JSON
