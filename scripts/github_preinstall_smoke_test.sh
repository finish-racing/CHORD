#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="${GITHUB_WORKSPACE:-$(pwd)}"
CI_DIR="${CHORD_CI_DIR:-$ROOT_DIR/.ci}"
RUNTIME_DIR="${CHORD_RUNTIME_DIR:-$CI_DIR/runtime}"
VENV_DIR="${CHORD_VENV_DIR:-$CI_DIR/venv}"
CONFIG_FILE="${CHORD_CONFIG_FILE:-$RUNTIME_DIR/config.toml}"
RESULT_FILE="$RUNTIME_DIR/smoke_test_result.json"
LOG_DIR="$RUNTIME_DIR/logs"
UVICORN_LOG="$LOG_DIR/uvicorn.log"

mkdir -p "$LOG_DIR"

export CHORD_DATABASE_URL="${CHORD_DATABASE_URL:-postgresql+psycopg://chord:change_me@localhost:5432/chord}"
export PATH="$VENV_DIR/bin:$PATH"

cd "$ROOT_DIR"

echo "[CHORD CI] Compile source"
python -m compileall src

echo "[CHORD CI] Import core modules"
python - <<'PY'
import importlib
modules = [
    'chord',
    'chord.cli',
    'chord.config',
    'chord.db.models',
    'chord.db.repositories',
    'chord.services.run_service',
    'chord.services.feature_service',
    'chord.services.enrichment_service',
    'chord.services.identity_service',
    'chord.services.prism_service',
    'chord.services.curated_playlist_service',
    'chord.services.openai_service',
    'chord.services.diagnostics_service',
    'chord.web.api',
]
for name in modules:
    importlib.import_module(name)
print('CHORD imports OK')
PY

echo "[CHORD CI] CLI help"
chord --help >/tmp/chord_help.txt
cat /tmp/chord_help.txt

echo "[CHORD CI] Initialize database"
chord initdb --config "$CONFIG_FILE"

echo "[CHORD CI] Create run"
CREATE_RUN_JSON="$(chord create-run --config "$CONFIG_FILE" --mode analysis --notes "GitHub preinstall smoke test")"
echo "$CREATE_RUN_JSON"
RUN_ID="$(python -c 'import json,sys; print(json.load(sys.stdin)["run_id"])' <<< "$CREATE_RUN_JSON")"
echo "[CHORD CI] RUN_ID=$RUN_ID"

echo "[CHORD CI] Import fixture playlists"
chord import-playlists \
  --config "$CONFIG_FILE" \
  --run-id "$RUN_ID" \
  --top25 tests/fixtures/top25_sample.txt \
  --playlist tests/fixtures/playlist_sample.txt

echo "[CHORD CI] Submit quiz"
QUIZ_JSON='{"project_type":"generation_soundtrack","recommendation_mistake":"same_artist","recommendation_goal":"tasteful_surprises","belonging_rule":"same_kind_of_person","balance_preference":"balanced","avoid_false_positive":"technically_similar_but_wrong"}'
chord submit-quiz --config "$CONFIG_FILE" --run-id "$RUN_ID" --answers-json "$QUIZ_JSON"

echo "[CHORD CI] Build aggregates"
chord build-aggregates --config "$CONFIG_FILE" --run-id "$RUN_ID"

echo "[CHORD CI] Show status"
chord show-status --config "$CONFIG_FILE" --run-id "$RUN_ID"

echo "[CHORD CI] Start web app"
uvicorn chord.web.api:api --host 127.0.0.1 --port 8000 > "$UVICORN_LOG" 2>&1 &
UVICORN_PID=$!
trap 'kill "$UVICORN_PID" >/dev/null 2>&1 || true' EXIT

for attempt in $(seq 1 30); do
  if curl -fsS http://127.0.0.1:8000/health >/tmp/chord_health.json; then
    break
  fi
  sleep 1
  if ! kill -0 "$UVICORN_PID" >/dev/null 2>&1; then
    echo "[CHORD CI] Uvicorn exited early"
    cat "$UVICORN_LOG" || true
    exit 1
  fi
  if [ "$attempt" -eq 30 ]; then
    echo "[CHORD CI] Health check timed out"
    cat "$UVICORN_LOG" || true
    exit 1
  fi
done

echo "[CHORD CI] Health check"
cat /tmp/chord_health.json

echo "[CHORD CI] Web run list"
curl -fsS http://127.0.0.1:8000/runs > "$RUNTIME_DIR/web_runs.json"
cat "$RUNTIME_DIR/web_runs.json"

python - <<PY
import json
from pathlib import Path
payload = {
    'status': 'passed',
    'run_id': int('$RUN_ID'),
    'health': json.loads(Path('/tmp/chord_health.json').read_text()),
    'artifacts': {
        'runtime_dir': '$RUNTIME_DIR',
        'uvicorn_log': '$UVICORN_LOG',
        'config_file': '$CONFIG_FILE',
    },
}
Path('$RESULT_FILE').write_text(json.dumps(payload, indent=2))
print(json.dumps(payload, indent=2))
PY
