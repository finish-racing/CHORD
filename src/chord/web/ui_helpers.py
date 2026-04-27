from __future__ import annotations

PIPELINE_STEPS = [
    ("created", "Run created"),
    ("importing", "Importing playlists"),
    ("imported", "Imports complete"),
    ("quiz_captured", "Quiz captured"),
    ("aggregates_built", "Behavioral aggregates built"),
    ("enriched", "External enrichment complete"),
    ("identity_built", "Identity profile complete"),
    ("prism_scored", "PRISM recommendations complete"),
    ("curated_built", "Curated playlist complete"),
]

def progress_for_status(status: str) -> dict:
    status = (status or "created").strip().lower()
    step_names = [x[0] for x in PIPELINE_STEPS]
    if status not in step_names:
        return {"percent": 0, "label": "Unknown", "steps": [{"key":k,"label":l,"done":False,"current":False} for k,l in PIPELINE_STEPS]}
    idx = step_names.index(status)
    total = len(PIPELINE_STEPS) - 1
    percent = int((idx / total) * 100) if total > 0 else 0
    steps = []
    for i, (key, label) in enumerate(PIPELINE_STEPS):
        steps.append({
            "key": key,
            "label": label,
            "done": i < idx,
            "current": i == idx,
        })
    return {"percent": percent, "label": PIPELINE_STEPS[idx][1], "steps": steps}

def truthy(value) -> bool:
    return bool(value)
