#!/usr/bin/env bash
set -euo pipefail

# GitHub Actions / CI-only installer for CHORD.
# This intentionally avoids systemd, nginx, permanent system users, /opt, /etc, and /var paths.

ROOT_DIR="${GITHUB_WORKSPACE:-$(pwd)}"
CI_DIR="${CHORD_CI_DIR:-$ROOT_DIR/.ci}"
RUNTIME_DIR="${CHORD_RUNTIME_DIR:-$CI_DIR/runtime}"
VENV_DIR="${CHORD_VENV_DIR:-$CI_DIR/venv}"
CONFIG_FILE="$RUNTIME_DIR/config.toml"
ROOT_CONFIG_FILE="$ROOT_DIR/config.toml"
SUMMARY_FILE="$RUNTIME_DIR/install_summary.json"

DATABASE_URL="${CHORD_DATABASE_URL:-postgresql+psycopg://chord:change_me@localhost:5432/chord}"

mkdir -p \
  "$RUNTIME_DIR/uploads" \
  "$RUNTIME_DIR/cache" \
  "$RUNTIME_DIR/exports" \
  "$RUNTIME_DIR/state" \
  "$RUNTIME_DIR/debug" \
  "$RUNTIME_DIR/logs"

python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/python" -m pip install --upgrade pip setuptools wheel
"$VENV_DIR/bin/python" -m pip install -e "$ROOT_DIR"

cat > "$CONFIG_FILE" <<EOF
[app]
name = "CHORD"
environment = "github-actions"
debug = true
base_dir = "$RUNTIME_DIR"
log_dir = "$RUNTIME_DIR/logs"
config_dir = "$RUNTIME_DIR"
release_version = "0.1.0-ci"

[database]
url = "$DATABASE_URL"
connect_timeout_seconds = 10
pool_size = 2
max_overflow = 2

[debug]
enabled = true
artifact_dir = "$RUNTIME_DIR/debug"
dump_parsed_rows = true
dump_normalized_rows = true
dump_run_state = true
dump_score_snapshots = true
http_trace = false

[paths]
upload_dir = "$RUNTIME_DIR/uploads"
cache_dir = "$RUNTIME_DIR/cache"
export_dir = "$RUNTIME_DIR/exports"
state_dir = "$RUNTIME_DIR/state"

[web]
host = "127.0.0.1"
port = 8000
cors_origins = ["*"]

[lastfm]
enabled = false
api_key = ""
shared_secret = ""
api_root = "https://ws.audioscrobbler.com/2.0"

[musicbrainz]
enabled = false
api_root = "https://musicbrainz.org/ws/2"
user_agent = "CHORD/0.1.0-ci (github actions)"

[acousticbrainz]
enabled = false
api_root = "https://acousticbrainz.org/api/v1"

[openai]
enabled = false
api_key = ""
model = "gpt-5.4"
EOF

# The web app calls load_settings(None) at import time, which checks ./config.toml.
# Copy the CI config there inside the ephemeral workflow checkout only.
cp "$CONFIG_FILE" "$ROOT_CONFIG_FILE"

cat > "$SUMMARY_FILE" <<EOF
{
  "installer": "installer/install_chord_github_actions.sh",
  "mode": "github-actions",
  "root_dir": "$ROOT_DIR",
  "ci_dir": "$CI_DIR",
  "runtime_dir": "$RUNTIME_DIR",
  "venv_dir": "$VENV_DIR",
  "config_file": "$CONFIG_FILE",
  "root_config_file": "$ROOT_CONFIG_FILE",
  "database_url_source": "CHORD_DATABASE_URL or default",
  "production_installer_modified": false
}
EOF

cat "$SUMMARY_FILE"
