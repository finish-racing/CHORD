from __future__ import annotations
import json
from pathlib import Path
from chord.db import repositories as repo

def get_run_status_payload(session, run_id: int) -> dict:
    run = repo.get_run(session, run_id)
    if run is None:
        raise ValueError(f"Run not found: {run_id}")
    playlists = repo.list_playlists_for_run(session, run_id)
    aggregate = repo.get_run_aggregate(session, run_id)
    enrich = repo.get_run_enrichment_summary(session, run_id)
    identity = repo.get_identity_profile(session, run_id)
    rec_bal = repo.get_recommendation_set(session, run_id, "balanced")
    curated_bal = repo.get_curated_playlist_set(session, run_id, "balanced")
    return {
        "run_id": run.id,
        "status": run.status,
        "mode": run.mode,
        "debug_enabled": run.debug_enabled,
        "playlist_count": len(playlists),
        "has_aggregates": aggregate is not None,
        "has_enrichment": enrich is not None,
        "has_identity": identity is not None,
        "has_balanced_recommendations": rec_bal is not None,
        "has_balanced_curated_playlist": curated_bal is not None,
    }

def export_results_payload(session, run_id: int, mode: str) -> dict:
    rec_set = repo.get_recommendation_set(session, run_id, mode)
    if rec_set is None:
        raise ValueError(f"No recommendation set found for run {run_id} mode {mode}")
    items = repo.list_recommendation_items(session, rec_set.id)
    return {
        "summary": rec_set.summary_payload,
        "items": [
            {
                "rank": x.rank,
                "canonical_track_id": x.canonical_track_id,
                "final_score": x.final_score,
                "confidence_score": x.confidence_score,
                "mode": x.mode,
                "explanation_text": x.explanation_text,
                "score_breakdown": x.score_breakdown,
            } for x in items
        ]
    }

def export_curated_payload(session, run_id: int, mode: str) -> dict:
    cp_set = repo.get_curated_playlist_set(session, run_id, mode)
    if cp_set is None:
        raise ValueError(f"No curated playlist found for run {run_id} mode {mode}")
    items = repo.list_curated_playlist_items(session, cp_set.id)
    return {
        "summary": cp_set.summary_payload,
        "items": [
            {
                "rank": x.rank,
                "canonical_track_id": x.canonical_track_id,
                "source_type": x.source_type,
                "role_label": x.role_label,
                "inclusion_reason": x.inclusion_reason,
                "score_payload": x.score_payload,
            } for x in items
        ]
    }

def write_json_export(payload: dict, out_path: str):
    path = Path(out_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return str(path)

def soft_reset(session, run_id: int):
    repo.delete_run_outputs(session, run_id)
    repo.update_run_status(session, run_id, "imported")

def hard_reset(session, run_id: int):
    repo.delete_run_everything(session, run_id)
