#!/usr/bin/env bash
set -euo pipefail
RUN_ID="${RUN_ID:?Set RUN_ID}"
CONFIG_FILE="${CONFIG_FILE:-/etc/chord/config.toml}"
/opt/chord/current/.venv/bin/chord hard-reset --run-id "$RUN_ID" --config "$CONFIG_FILE"
