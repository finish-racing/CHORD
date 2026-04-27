#!/usr/bin/env bash
set -euo pipefail

APP_ROOT="${APP_ROOT:-/opt/chord}"
TARGET_VERSION="${TARGET_VERSION:?Set TARGET_VERSION}"
TARGET_DIR="$APP_ROOT/releases/$TARGET_VERSION"
CURRENT_LINK="$APP_ROOT/current"

if [ ! -d "$TARGET_DIR" ]; then
  echo "[CHORD] Target release does not exist: $TARGET_DIR" >&2
  exit 1
fi

echo "[CHORD] Rolling back to $TARGET_VERSION ..."
sudo ln -sfn "$TARGET_DIR" "$CURRENT_LINK"
sudo systemctl restart chord-web
echo "[CHORD] Rollback complete."
