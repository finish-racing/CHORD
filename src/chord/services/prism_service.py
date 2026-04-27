from __future__ import annotations
from math import log1p
from chord.db import repositories as repo
from chord.utils.debug import write_debug_json

MODE_TOP_N = {"safe": 15, "balanced": 25, "discovery": 35}

def _clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, v))

def _first_lastfm_tags(track_identity_payload: dict) -> list[str]:
    return [str(x).lower() for x in (track_identity_payload.get("lastfm_tags") or [])]

def _role_bonus(role: str, mode: str) -> float:
    if mode == "safe":
        return {"anchor_song": 0.10, "replay_core_song": 0.09, "generational_touchstone": 0.08, "bridge_song": 0.06}.get(role, 0.03)
    if mode == "discovery":
        return {"curated_outlier": 0.10, "bridge_song": 0.08, "memory_trigger_song": 0.06}.get(role, 0.04)
    return {"anchor_song": 0.08, "replay_core_song": 0.08, "bridge_song": 0.07, "generational_touchstone": 0.07}.get(role, 0.04)

def _explain(display_title: str, display_artist: str, parts: dict, role: str, mood: str) -> str:
    reasons = []
    if parts.get("top25_anchor_fit", 0) >= 0.7:
        reasons.append("strong Top 25 anchor fit")
    if parts.get("cross_playlist_fit", 0) >= 0.5:
        reasons.append("cross-playlist recurrence")
    if parts.get("cultural_fit", 0) >= 0.6:
        reasons.append("cultural / generational alignment")
    if parts.get("mood_fit", 0) >= 0.6:
        reasons.append(f"{mood.replace('_', ' ')} lane fit")
    if parts.get("role_fit", 0) >= 0.6:
        reasons.append(f"{role.replace('_', ' ')} role fit")
    if parts.get("false_positive_penalty", 0) <= 0.1:
        reasons.append("low false-positive risk")
    if not reasons:
        reasons.append("balanced overall fit")
    return f"{display_title} — {display_artist}: " + ", ".join(reasons[:4]) + "."

def run_prism(session, settings, *, run_id: int, mode: str = "balanced") -> dict:
    mode = mode.lower()
    if mode not in MODE_TOP_N:
        raise ValueError(f"Unsupported PRISM mode: {mode}")

    canonical_tracks = repo.list_canonical_tracks_for_run(session, run_id)
    track_identity_rows = repo.list_canonical_track_identity_for_run(session, run_id)
    run_aggregate = repo.get_run_aggregate(session, run_id)
    identity_profile = repo.get_identity_profile(session, run_id)

    # index
    identity_by_ct = {row.canonical_track_id: row.identity_payload for row in track_identity_rows}
    agg_payload = getattr(run_aggregate, "aggregate_payload", {}) or {}
    identity_payload = getattr(identity_profile, "profile_payload", {}) or {}
    top_artists = {k.lower(): v for k, v in agg_payload.get("top_artists", [])}
    top_genres = {k.lower(): v for k, v in agg_payload.get("top_genres", [])}
    decade_dist = agg_payload.get("decade_distribution", {}) or {}
    title_family_duplicate_like_count = identity_payload.get("title_family_duplicate_like_count", 0)

    scored = []
    artist_taken = {}
    decade_taken = {}

    for ct in canonical_tracks:
        ip = identity_by_ct.get(ct.id, {})
        role = ip.get("playlist_role", "memory_trigger_song")
        mood = ip.get("mood_family", "eclectic_drive")
        tags = _first_lastfm_tags(ip)
        genre = (ip.get("genre") or "").lower()
        decade_bucket = ip.get("decade_bucket", "unknown")
        top25_anchor = 1.0 if ip.get("top25_anchor") else 0.0
        cross_playlist = float(ip.get("cross_playlist_recurrence_score") or 0.0)
        tension = float(ip.get("behavioral_tension_score") or 0.0)
        tension_norm = _clamp(tension / 3.0)
        cultural_fit = _clamp((1.0 if decade_bucket in decade_dist else 0.3) * (1.0 if "classic rock" in tags or "70s" in tags or "80s" in tags or "pop" in tags or "alternative" in tags else 0.75))
        mood_fit = _clamp(0.8 if mood in {"warm_nostalgia", "social_singalong", "modern_replay_core", "reflective_bridge", "comfort_groove", "eclectic_drive"} else 0.5)
        role_fit = _clamp(0.6 + _role_bonus(role, mode))
        artist_weight = _clamp((top_artists.get((ct.display_artist or "").lower(), 0) / max(1, len(canonical_tracks))) * 6)
        genre_weight = _clamp((top_genres.get(genre, 0) / max(1, len(canonical_tracks))) * 6)
        top25_anchor_fit = _clamp(0.7 + top25_anchor * 0.3)
        cross_playlist_fit = _clamp(0.45 + cross_playlist * 0.55)
        representation_fit = _clamp(1.0 - min((ct.playlist_occurrences or 0) / 10.0, 0.4) + (0.1 if role in {"bridge_song", "generational_touchstone"} else 0.0))
        false_positive_penalty = _clamp(0.15 if ip.get("identity_flags", {}).get("version_like_title") else 0.03)
        if title_family_duplicate_like_count > 0 and ip.get("identity_flags", {}).get("same_title_family_size", 1) > 1:
            false_positive_penalty = _clamp(false_positive_penalty + 0.12)
        novelty_bonus = {"safe": 0.02, "balanced": 0.04, "discovery": 0.08}[mode]
        if role == "curated_outlier":
            novelty_bonus += 0.05
        if mood == "modern_replay_core":
            novelty_bonus += 0.03

        # weighted scoring per current design direction
        score_parts = {
            "curator_fit": round(_clamp((top25_anchor_fit * 0.55) + (tension_norm * 0.45)), 4),
            "top25_anchor_fit": round(top25_anchor_fit, 4),
            "engagement_fit": round(tension_norm, 4),
            "cross_playlist_fit": round(cross_playlist_fit, 4),
            "cultural_fit": round(cultural_fit, 4),
            "mood_fit": round(mood_fit, 4),
            "role_fit": round(role_fit, 4),
            "omission_fit": round(_clamp(0.55 + (0.15 if role == "generational_touchstone" else 0.0) + (0.10 if decade_bucket in {"1970s", "1980s", "1990s", "2000s", "2010s"} else 0.0)), 4),
            "representation_fit": round(representation_fit, 4),
            "adjacency_fit": round(_clamp((artist_weight * 0.5) + (genre_weight * 0.5)), 4),
            "novelty_bonus": round(_clamp(novelty_bonus, 0.0, 0.2), 4),
            "false_positive_penalty": round(false_positive_penalty, 4),
        }

        final_score = (
            score_parts["curator_fit"] * 0.18
            + score_parts["top25_anchor_fit"] * 0.12
            + score_parts["engagement_fit"] * 0.10
            + score_parts["cross_playlist_fit"] * 0.10
            + score_parts["cultural_fit"] * 0.10
            + score_parts["mood_fit"] * 0.08
            + score_parts["role_fit"] * 0.10
            + score_parts["omission_fit"] * 0.08
            + score_parts["representation_fit"] * 0.08
            + score_parts["adjacency_fit"] * 0.04
            + score_parts["novelty_bonus"]
            - score_parts["false_positive_penalty"] * 0.12
        )
        confidence = _clamp((score_parts["curator_fit"] * 0.30) + (score_parts["cross_playlist_fit"] * 0.15) + (score_parts["cultural_fit"] * 0.15) + (score_parts["representation_fit"] * 0.15) + (score_parts["role_fit"] * 0.15) + (0.10 if ip.get("identity_flags", {}).get("musicbrainz_recording_mbid_present") else 0.0))

        scored.append({
            "canonical_track_id": ct.id,
            "display_title": ct.display_title,
            "display_artist": ct.display_artist,
            "decade_bucket": decade_bucket,
            "final_score": round(final_score, 6),
            "confidence_score": round(confidence, 6),
            "score_breakdown": score_parts,
            "explanation_text": _explain(ct.display_title or "", ct.display_artist or "", score_parts, role, mood),
        })

    # sort before rerank
    scored.sort(key=lambda x: (x["final_score"], x["confidence_score"]), reverse=True)

    # rerank constraints: artist caps / decade softness
    selected = []
    top_n = MODE_TOP_N[mode]
    for item in scored:
        artist_key = (item["display_artist"] or "").lower()
        decade_key = item["decade_bucket"]
        artist_limit = 1 if mode == "safe" else (2 if mode == "balanced" else 3)
        decade_soft_limit = 5 if mode == "safe" else 7
        if artist_taken.get(artist_key, 0) >= artist_limit:
            continue
        if decade_taken.get(decade_key, 0) >= decade_soft_limit:
            continue
        selected.append(item)
        artist_taken[artist_key] = artist_taken.get(artist_key, 0) + 1
        decade_taken[decade_key] = decade_taken.get(decade_key, 0) + 1
        if len(selected) >= top_n:
            break

    for idx, item in enumerate(selected, start=1):
        item["rank"] = idx

    summary = {
        "run_id": run_id,
        "mode": mode,
        "total_candidates": len(scored),
        "selected_count": len(selected),
        "artist_distribution": artist_taken,
        "decade_distribution": decade_taken,
        "top_score": selected[0]["final_score"] if selected else None,
    }

    repo.replace_recommendation_set(session, run_id, mode, summary, selected)

    if settings.debug.enabled and settings.debug.dump_score_snapshots:
        p1 = write_debug_json(settings, f"wave_c1_scored_candidates_{mode}", scored, run_id=run_id)
        if p1:
            repo.record_debug_artifact(session, f"wave_c1_scored_candidates_{mode}", p1, run_id=run_id)
        p2 = write_debug_json(settings, f"wave_c1_selected_recommendations_{mode}", selected, run_id=run_id)
        if p2:
            repo.record_debug_artifact(session, f"wave_c1_selected_recommendations_{mode}", p2, run_id=run_id)

    return {"summary": summary, "items": selected}
