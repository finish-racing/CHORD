#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="${GITHUB_WORKSPACE:-$(pwd)}"
CI_DIR="${CHORD_CI_DIR:-$ROOT_DIR/.ci}"
RUNTIME_DIR="${CHORD_RUNTIME_DIR:-$CI_DIR/runtime}"
VENV_DIR="${CHORD_VENV_DIR:-$CI_DIR/venv}"
CONFIG_FILE="${CHORD_CONFIG_FILE:-$RUNTIME_DIR/config.toml}"
RESULT_DIR="${CHORD_REALDATA_RESULT_DIR:-$RUNTIME_DIR/real_data_result}"
LOG_DIR="$RUNTIME_DIR/logs"
UVICORN_LOG="$LOG_DIR/uvicorn-real-data.log"

REAL_DATA_DIR="${CHORD_REALDATA_DIR:-$ROOT_DIR/tests/real_data}"
TOP25_FILE="${CHORD_REALDATA_TOP25:-$REAL_DATA_DIR/top25_real.txt}"
PLAYLIST_DIR="${CHORD_REALDATA_PLAYLIST_DIR:-$REAL_DATA_DIR/playlists}"
SINGLE_PLAYLIST_FILE="${CHORD_REALDATA_PLAYLIST:-$REAL_DATA_DIR/playlist_real.txt}"
QUIZ_FILE="${CHORD_REALDATA_QUIZ:-$REAL_DATA_DIR/quiz_answers.json}"
ALLOW_SINGLE_AS_TOP25="${CHORD_REALDATA_ALLOW_SINGLE_FILE_AS_TOP25:-1}"

mkdir -p "$LOG_DIR" "$RESULT_DIR"

export CHORD_DATABASE_URL="${CHORD_DATABASE_URL:-postgresql+psycopg://chord:change_me@localhost:5432/chord}"
export PATH="$VENV_DIR/bin:$PATH"

cd "$ROOT_DIR"

if [ ! -f "$QUIZ_FILE" ]; then
  echo "Missing real-data quiz file: $QUIZ_FILE" >&2
  echo "Create tests/real_data/quiz_answers.json from the user's real quiz answers." >&2
  exit 2
fi

PLAYLIST_ARGS=()
PLAYLIST_INPUTS=()

if [ -f "$TOP25_FILE" ]; then
  SELECTED_TOP25="$TOP25_FILE"
elif [ "$ALLOW_SINGLE_AS_TOP25" = "1" ] && [ -f "$SINGLE_PLAYLIST_FILE" ]; then
  SELECTED_TOP25="$SINGLE_PLAYLIST_FILE"
else
  echo "Missing Top 25 file: $TOP25_FILE" >&2
  echo "For fallback, provide $SINGLE_PLAYLIST_FILE and keep CHORD_REALDATA_ALLOW_SINGLE_FILE_AS_TOP25=1." >&2
  exit 2
fi

if [ -d "$PLAYLIST_DIR" ]; then
  shopt -s nullglob
  for file in "$PLAYLIST_DIR"/*.txt "$PLAYLIST_DIR"/*.csv "$PLAYLIST_DIR"/*.tsv; do
    PLAYLIST_ARGS+=(--playlist "$file")
    PLAYLIST_INPUTS+=("$file")
  done
  shopt -u nullglob
fi

if [ "${#PLAYLIST_ARGS[@]}" -eq 0 ] && [ -f "$SINGLE_PLAYLIST_FILE" ]; then
  PLAYLIST_ARGS+=(--playlist "$SINGLE_PLAYLIST_FILE")
  PLAYLIST_INPUTS+=("$SINGLE_PLAYLIST_FILE")
fi

if [ "${#PLAYLIST_ARGS[@]}" -eq 0 ]; then
  echo "Missing playlist input. Provide files under $PLAYLIST_DIR or $SINGLE_PLAYLIST_FILE." >&2
  exit 2
fi

python -m compileall src
python - <<'PY'
import importlib
for name in ['chord', 'chord.cli', 'chord.web.api']:
    importlib.import_module(name)
print('Real-data smoke imports OK')
PY

chord initdb --config "$CONFIG_FILE" | tee "$RESULT_DIR/initdb.log"

CREATE_RUN_JSON="$(chord create-run --config "$CONFIG_FILE" --mode analysis --notes "GitHub real-data smoke test")"
echo "$CREATE_RUN_JSON" | tee "$RESULT_DIR/create_run.json"
RUN_ID="$(python -c 'import json,sys; print(json.load(sys.stdin)["run_id"])' <<< "$CREATE_RUN_JSON")"
echo "$RUN_ID" > "$RESULT_DIR/run_id.txt"

chord import-playlists \
  --config "$CONFIG_FILE" \
  --run-id "$RUN_ID" \
  --top25 "$SELECTED_TOP25" \
  "${PLAYLIST_ARGS[@]}" | tee "$RESULT_DIR/import_playlists.log"

QUIZ_JSON="$(python -c 'import json,sys; print(json.dumps(json.load(open(sys.argv[1]))))' "$QUIZ_FILE")"
chord submit-quiz --config "$CONFIG_FILE" --run-id "$RUN_ID" --answers-json "$QUIZ_JSON" | tee "$RESULT_DIR/submit_quiz.json"

chord build-aggregates --config "$CONFIG_FILE" --run-id "$RUN_ID" | tee "$RESULT_DIR/aggregates.json"
chord build-identity --config "$CONFIG_FILE" --run-id "$RUN_ID" | tee "$RESULT_DIR/identity.json"
chord run-prism --config "$CONFIG_FILE" --run-id "$RUN_ID" --mode balanced | tee "$RESULT_DIR/prism_summary.json"
chord build-curated --config "$CONFIG_FILE" --run-id "$RUN_ID" --mode balanced --length 25 | tee "$RESULT_DIR/curated_summary.json"
chord show-status --config "$CONFIG_FILE" --run-id "$RUN_ID" | tee "$RESULT_DIR/run_status.json"
chord show-prism --config "$CONFIG_FILE" --run-id "$RUN_ID" --mode balanced | tee "$RESULT_DIR/prism_results.json"
chord show-curated --config "$CONFIG_FILE" --run-id "$RUN_ID" --mode balanced | tee "$RESULT_DIR/curated_playlist.json"
chord diagnose-run --config "$CONFIG_FILE" --run-id "$RUN_ID" | tee "$RESULT_DIR/diagnostics.json"
chord export-debug-index --config "$CONFIG_FILE" --run-id "$RUN_ID" --out "$RESULT_DIR/debug_index.json" | tee "$RESULT_DIR/debug_index_export.json"

uvicorn chord.web.api:api --host 127.0.0.1 --port 8000 > "$UVICORN_LOG" 2>&1 &
UVICORN_PID=$!
trap 'kill "$UVICORN_PID" >/dev/null 2>&1 || true' EXIT

for attempt in $(seq 1 30); do
  if curl -fsS http://127.0.0.1:8000/health > "$RESULT_DIR/health.json"; then
    break
  fi
  sleep 1
  if ! kill -0 "$UVICORN_PID" >/dev/null 2>&1; then
    cat "$UVICORN_LOG" || true
    exit 1
  fi
  if [ "$attempt" -eq 30 ]; then
    cat "$UVICORN_LOG" || true
    exit 1
  fi
done

curl -fsS http://127.0.0.1:8000/runs > "$RESULT_DIR/web_runs.json"
curl -fsS "http://127.0.0.1:8000/runs/$RUN_ID/status" > "$RESULT_DIR/web_run_status.json"
curl -fsS "http://127.0.0.1:8000/runs/$RUN_ID/aggregates" > "$RESULT_DIR/web_aggregates.json"

python - <<PY
import json, hashlib
from pathlib import Path
result_dir = Path('$RESULT_DIR')
selected_top25 = Path('$SELECTED_TOP25')
playlist_inputs = [Path(p) for p in ${PLAYLIST_INPUTS[@]@Q}]

def fingerprint(path):
    h = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            h.update(chunk)
    return {
        'name': path.name,
        'size_bytes': path.stat().st_size,
        'sha256': h.hexdigest(),
    }

summary = {
    'status': 'passed',
    'run_id': int('$RUN_ID'),
    'top25_input': fingerprint(selected_top25),
    'playlist_inputs': [fingerprint(p) for p in playlist_inputs],
    'result_files': sorted(p.name for p in result_dir.iterdir() if p.is_file()),
}
(result_dir / 'real_data_smoke_summary.json').write_text(json.dumps(summary, indent=2))
print(json.dumps(summary, indent=2))
PY
