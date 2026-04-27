# CHORD Debug Mode Guide

## Purpose
Debug mode provides deep operational visibility during real Ubuntu laptop testing.

## Enable debug mode
Use one of:
- `app.debug = true` in config
- `debug.enabled = true` in config
- `CHORD_DEBUG=1` in `/etc/chord/chord.env`

## What debug mode adds
- `chord.debug.log`
- JSON artifacts for parsed imports
- normalized row dumps
- aggregate dumps
- enrichment result dumps
- identity profile dumps
- PRISM score snapshots
- curated playlist snapshots
- OpenAI enhancement snapshots
- diagnostic snapshots

## CLI helpers
- `chord list-debug-artifacts --run-id <id>`
- `chord export-debug-index --run-id <id> --out /path/file.json`
- `chord diagnose-run --run-id <id>`
