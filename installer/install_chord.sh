#!/usr/bin/env bash
set -euo pipefail

APP_USER="${APP_USER:-chord}"
APP_GROUP="${APP_GROUP:-chord}"
APP_ROOT="${APP_ROOT:-/opt/chord}"
RELEASE_VERSION="${RELEASE_VERSION:-0.1.0}"
RELEASE_DIR="$APP_ROOT/releases/$RELEASE_VERSION"
CURRENT_LINK="$APP_ROOT/current"
CONFIG_DIR="${CONFIG_DIR:-/etc/chord}"
DATA_DIR="${DATA_DIR:-/var/lib/chord}"
LOG_DIR="${LOG_DIR:-/var/log/chord}"
ENV_FILE="$CONFIG_DIR/chord.env"
CONFIG_FILE="$CONFIG_DIR/config.toml"

echo "[CHORD] Installing prerequisites..."
sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip postgresql postgresql-contrib nginx

echo "[CHORD] Creating user/group if needed..."
if ! getent group "$APP_GROUP" >/dev/null; then sudo groupadd --system "$APP_GROUP"; fi
if ! id -u "$APP_USER" >/dev/null 2>&1; then sudo useradd --system --gid "$APP_GROUP" --home "$APP_ROOT" --shell /usr/sbin/nologin "$APP_USER"; fi

echo "[CHORD] Creating directories..."
sudo mkdir -p "$APP_ROOT/releases" "$CONFIG_DIR" "$DATA_DIR/uploads" "$DATA_DIR/cache" "$DATA_DIR/exports" "$DATA_DIR/state" "$DATA_DIR/debug" "$LOG_DIR"

echo "[CHORD] Copying release to $RELEASE_DIR ..."
sudo rm -rf "$RELEASE_DIR"
sudo mkdir -p "$RELEASE_DIR"
sudo cp -a . "$RELEASE_DIR"

echo "[CHORD] Creating virtual environment..."
sudo python3 -m venv "$RELEASE_DIR/.venv"
sudo "$RELEASE_DIR/.venv/bin/pip" install --upgrade pip setuptools wheel
sudo "$RELEASE_DIR/.venv/bin/pip" install -e "$RELEASE_DIR"

echo "[CHORD] Installing default config/environment templates if missing..."
if [ ! -f "$ENV_FILE" ]; then sudo cp "$RELEASE_DIR/installer/chord.env.example" "$ENV_FILE"; fi
if [ ! -f "$CONFIG_FILE" ]; then sudo cp "$RELEASE_DIR/config.example.toml" "$CONFIG_FILE"; fi

echo "[CHORD] Linking current release..."
sudo ln -sfn "$RELEASE_DIR" "$CURRENT_LINK"

echo "[CHORD] Setting ownership..."
sudo chown -R "$APP_USER:$APP_GROUP" "$APP_ROOT" "$DATA_DIR" "$LOG_DIR" "$CONFIG_DIR"

echo "[CHORD] Installing systemd service..."
sudo cp "$RELEASE_DIR/installer/chord-web.service" /etc/systemd/system/chord-web.service
sudo systemctl daemon-reload

echo "[CHORD] Install complete."
echo "Next steps:"
echo "1. Edit $ENV_FILE"
echo "2. Edit $CONFIG_FILE"
echo "3. Bootstrap PostgreSQL using installer/postgresql_bootstrap.sql"
echo "4. Start service: sudo systemctl enable --now chord-web"
