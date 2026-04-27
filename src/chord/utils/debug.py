from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from chord.config import Settings
from chord.utils.paths import ensure_runtime_dirs

def write_debug_json(settings: Settings, artifact_type: str, payload: Any, *, run_id: int | None = None) -> str | None:
    if not settings.debug.enabled:
        return None
    dirs = ensure_runtime_dirs(settings)
    base = dirs["debug"]
    if run_id is not None:
        base = base / str(run_id)
        base.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = base / f"{stamp}_{artifact_type}.json"
    with path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False, default=str)
    return str(path)
