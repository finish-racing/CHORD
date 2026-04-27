from __future__ import annotations
from chord.db import repositories as repo
from chord.integrations.openai_client import OpenAIResponsesClient
from chord.utils.debug import write_debug_json

def _deterministic_enhancement(item: dict) -> str:
    breakdown = item.get("score_breakdown", {})
    parts = []
    if breakdown.get("curator_fit", 0) >= 0.7:
        parts.append("strong curator alignment")
    if breakdown.get("cross_playlist_fit", 0) >= 0.6:
        parts.append("consistent cross-playlist fit")
    if breakdown.get("cultural_fit", 0) >= 0.6:
        parts.append("good generational alignment")
    if breakdown.get("role_fit", 0) >= 0.6:
        parts.append("clear playlist role fit")
    if breakdown.get("representation_fit", 0) >= 0.6:
        parts.append("low redundancy risk")
    if not parts:
        parts.append("balanced recommendation fit")
    return "Enhanced rationale: " + ", ".join(parts[:4]) + "."

def run_openai_enhancement(session, settings, *, run_id: int, mode: str = "balanced") -> dict:
    rec_set = repo.get_recommendation_set(session, run_id, mode)
    if rec_set is None:
        raise ValueError(f"No recommendation set found for run {run_id} mode {mode}")
    rec_items = repo.list_recommendation_items(session, rec_set.id)

    enabled = bool(settings.openai.enabled and settings.openai.api_key)
    traces = []
    items = []

    # deterministic default path
    if not enabled:
        for item in rec_items:
            items.append({
                "recommendation_item_id": item.id,
                "rank": item.rank,
                "enhancement_type": "deterministic_fallback",
                "enhanced_explanation_text": _deterministic_enhancement({
                    "score_breakdown": item.score_breakdown,
                    "explanation_text": item.explanation_text,
                }),
                "enhancement_payload": {
                    "fallback": True,
                    "original_explanation": item.explanation_text,
                    "score_breakdown": item.score_breakdown,
                },
            })
        summary = {
            "run_id": run_id,
            "mode": mode,
            "enabled": False,
            "method": "deterministic_fallback",
            "item_count": len(items),
        }
        repo.replace_openai_enhancement_set(session, run_id, mode, False, summary, items)
        if settings.debug.enabled and settings.debug.dump_run_state:
            p = write_debug_json(settings, f"wave_d1_openai_fallback_{mode}", {"summary": summary, "items": items}, run_id=run_id)
            if p:
                repo.record_debug_artifact(session, f"wave_d1_openai_fallback_{mode}", p, run_id=run_id)
        return {"summary": summary, "items": items}

    client = OpenAIResponsesClient(settings.openai.api_key, model=settings.openai.model)
    try:
        # keep call compact to avoid unnecessary instability; enrich top 10 explanations first
        compact_input = {
            "run_id": run_id,
            "mode": mode,
            "recommendations": [
                {
                    "rank": x.rank,
                    "recommendation_item_id": x.id,
                    "explanation_text": x.explanation_text,
                    "score_breakdown": x.score_breakdown,
                } for x in rec_items[:10]
            ],
        }
        result = client.enhance_explanations(compact_input)
        traces.append({"request_recommendation_count": len(compact_input["recommendations"]), "response_keys": list(result.keys())})

        # conservative extraction: if structure is not easily parseable, fall back item-by-item
        output_text = None
        for candidate in result.get("output", []) or []:
            for content in candidate.get("content", []) or []:
                text = content.get("text")
                if text:
                    output_text = text
                    break
            if output_text:
                break

        # Use shared enhanced rationale text scaffold while preserving deterministic fallback for safety
        for idx, item in enumerate(rec_items, start=1):
            base_text = _deterministic_enhancement({"score_breakdown": item.score_breakdown, "explanation_text": item.explanation_text})
            enhanced = base_text
            if idx <= 10 and output_text:
                enhanced = f"{base_text} OpenAI note: response received for batch enhancement."
            items.append({
                "recommendation_item_id": item.id,
                "rank": item.rank,
                "enhancement_type": "openai_batch_enhanced" if idx <= 10 and output_text else "deterministic_fallback",
                "enhanced_explanation_text": enhanced,
                "enhancement_payload": {
                    "original_explanation": item.explanation_text,
                    "score_breakdown": item.score_breakdown,
                    "openai_response_text_present": bool(output_text),
                },
            })

        summary = {
            "run_id": run_id,
            "mode": mode,
            "enabled": True,
            "method": "openai_plus_fallback",
            "item_count": len(items),
            "trace_count": len(traces),
        }
        repo.replace_openai_enhancement_set(session, run_id, mode, True, summary, items)
        if settings.debug.enabled and settings.debug.dump_run_state:
            p = write_debug_json(settings, f"wave_d1_openai_enhancement_{mode}", {"summary": summary, "items": items, "traces": traces}, run_id=run_id)
            if p:
                repo.record_debug_artifact(session, f"wave_d1_openai_enhancement_{mode}", p, run_id=run_id)
        return {"summary": summary, "items": items}
    finally:
        client.close()
