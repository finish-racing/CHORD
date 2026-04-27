from __future__ import annotations
from chord.db import repositories as repo
from chord.services.operator_service import get_run_status_payload
from chord.utils.debug import write_debug_json

def collect_run_diagnostics(session, settings, *, run_id: int) -> dict:
    status = get_run_status_payload(session, run_id)
    aggregate = repo.get_run_aggregate(session, run_id)
    enrichment = repo.get_run_enrichment_summary(session, run_id)
    identity = repo.get_identity_profile(session, run_id)
    rec_set = repo.get_recommendation_set(session, run_id, "balanced")
    curated_set = repo.get_curated_playlist_set(session, run_id, "balanced")
    openai_set = repo.get_openai_enhancement_set(session, run_id, "balanced")
    debug_items = repo.list_debug_artifacts_for_run(session, run_id)

    diagnostics = {
        "run_status": status,
        "has_aggregate_payload": aggregate is not None,
        "has_enrichment_summary": enrichment is not None,
        "has_identity_profile": identity is not None,
        "has_balanced_recommendations": rec_set is not None,
        "has_balanced_curated_playlist": curated_set is not None,
        "has_balanced_openai_enhancement": openai_set is not None,
        "debug_artifact_count": len(debug_items),
        "debug_artifacts": [
            {"id": x.id, "artifact_type": x.artifact_type, "artifact_path": x.artifact_path}
            for x in debug_items
        ],
        "summary_payloads": {
            "aggregate": getattr(aggregate, "aggregate_payload", None),
            "enrichment": getattr(enrichment, "summary_payload", None),
            "identity": getattr(identity, "profile_payload", None),
            "recommendation": getattr(rec_set, "summary_payload", None),
            "curated": getattr(curated_set, "summary_payload", None),
            "openai": getattr(openai_set, "summary_payload", None),
        },
    }

    if settings.debug.enabled and settings.debug.dump_run_state:
        p = write_debug_json(settings, "wave_d2_diagnostics", diagnostics, run_id=run_id)
        if p:
            repo.record_debug_artifact(session, "wave_d2_diagnostics", p, run_id=run_id)

    return diagnostics

def export_debug_index(session, *, run_id: int) -> dict:
    items = repo.list_debug_artifacts_for_run(session, run_id)
    return {
        "run_id": run_id,
        "artifact_count": len(items),
        "artifacts": [
            {
                "id": x.id,
                "artifact_type": x.artifact_type,
                "artifact_path": x.artifact_path,
            }
            for x in items
        ],
    }
