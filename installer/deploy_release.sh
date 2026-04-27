#!/usr/bin/env bash
set -euo pipefail

APP_ROOT="${APP_ROOT:-/opt/chord}"
RELEASE_VERSION="${RELEASE_VERSION:?Set RELEASE_VERSION}"
RELEASE_DIR="$APP_ROOT/releases/$RELEASE_VERSION"
CURRENT_LINK="$APP_ROOT/current"

echo "[CHORD] Deploying release $RELEASE_VERSION ..."
sudo mkdir -p "$APP_ROOT/releases"
sudo rm -rf "$RELEASE_DIR"
sudo mkdir -p "$RELEASE_DIR"
sudo cp -a . "$RELEASE_DIR"
sudo python3 -m venv "$RELEASE_DIR/.venv"
sudo "$RELEASE_DIR/.venv/bin/pip" install --upgrade pip setuptools wheel
sudo "$RELEASE_DIR/.venv/bin/pip" install -e "$RELEASE_DIR"
sudo ln -sfn "$RELEASE_DIR" "$CURRENT_LINK"
sudo cp "$RELEASE_DIR/installer/chord-web.service" /etc/systemd/system/chord-web.service
sudo systemctl daemon-reload
echo "[CHORD] Running database schema initialization..."
sudo -u chord "$CURRENT_LINK/.venv/bin/chord" initdb --config /etc/chord/config.toml || true
echo "[CHORD] Restarting service..."
sudo systemctl restart chord-web
echo "[CHORD] Deployment complete."
