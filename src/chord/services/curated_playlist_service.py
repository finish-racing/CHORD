from __future__ import annotations
from collections import defaultdict
from chord.db import repositories as repo
from chord.utils.debug import write_debug_json

def _role_target_mix(requested_length: int) -> dict[str, int]:
    return {
        "anchor_song": max(6, int(requested_length * 0.12)),
        "replay_core_song": max(8, int(requested_length * 0.16)),
        "bridge_song": max(6, int(requested_length * 0.10)),
        "memory_trigger_song": max(6, int(requested_length * 0.10)),
        "social_singalong_song": max(8, int(requested_length * 0.12)),
        "comfort_background_song": max(5, int(requested_length * 0.08)),
        "emotional_centerpiece": max(4, int(requested_length * 0.06)),
        "generational_touchstone": max(6, int(requested_length * 0.10)),
    }

def build_curated_playlist(session, settings, *, run_id: int, mode: str = "balanced", requested_length: int = 60) -> dict:
    rec_set = repo.get_recommendation_set(session, run_id, mode)
    if rec_set is None:
        raise ValueError(f"No PRISM recommendation set found for run {run_id} and mode {mode}")

    rec_items = repo.list_recommendation_items(session, rec_set.id)
    canonical_tracks = repo.list_canonical_tracks_for_run(session, run_id)
    identity_rows = repo.list_canonical_track_identity_for_run(session, run_id)

    canonical_by_id = {ct.id: ct for ct in canonical_tracks}
    identity_by_ct = {row.canonical_track_id: row.identity_payload for row in identity_rows}

    role_targets = _role_target_mix(requested_length)
    role_counts = defaultdict(int)
    decade_counts = defaultdict(int)
    artist_counts = defaultdict(int)

    selected = []
    used_ids = set()

    # 1) seed with strong existing tracks from canonical library
    seeded = []
    for ct in canonical_tracks:
        ip = identity_by_ct.get(ct.id, {})
        role = ip.get("playlist_role", "memory_trigger_song")
        decade = ip.get("decade_bucket", "unknown")
        artist = (ct.display_artist or "").lower()

        existing_strength = (
            (1.0 if ct.top25_anchor else 0.0) * 0.45
            + min((ct.total_play_count or 0) / 50.0, 1.0) * 0.30
            + min((ct.playlist_occurrences or 0) / 5.0, 1.0) * 0.15
            + min((ct.rating_max or 0) / 100.0, 1.0) * 0.10
        )
        seeded.append({
            "canonical_track_id": ct.id,
            "source_type": "existing",
            "role_label": role,
            "decade_bucket": decade,
            "artist_key": artist,
            "score_payload": {"existing_strength": round(existing_strength, 6)},
            "inclusion_reason": f"Existing core library selection for {role.replace('_', ' ')} coverage",
            "priority": round(existing_strength, 6),
        })

    seeded.sort(key=lambda x: x["priority"], reverse=True)

    for item in seeded:
        if len(selected) >= max(30, requested_length // 2):
            break
        role = item["role_label"]
        if role_counts[role] >= role_targets.get(role, 6):
            continue
        if artist_counts[item["artist_key"]] >= 2:
            continue
        if decade_counts[item["decade_bucket"]] >= max(10, requested_length // 5):
            continue
        selected.append(item)
        used_ids.add(item["canonical_track_id"])
        role_counts[role] += 1
        artist_counts[item["artist_key"]] += 1
        decade_counts[item["decade_bucket"]] += 1

    # 2) fill remaining from PRISM recommendation items
    for rec in rec_items:
        if len(selected) >= requested_length:
            break
        if rec.canonical_track_id in used_ids:
            continue
        ct = canonical_by_id.get(rec.canonical_track_id)
        if not ct:
            continue
        ip = identity_by_ct.get(rec.canonical_track_id, {})
        role = ip.get("playlist_role", "memory_trigger_song")
        decade = ip.get("decade_bucket", "unknown")
        artist = (ct.display_artist or "").lower()

        # boundary protection + diversity
        if artist_counts[artist] >= 2:
            continue
        if decade_counts[decade] >= max(12, requested_length // 4):
            continue

        selected.append({
            "canonical_track_id": rec.canonical_track_id,
            "source_type": "recommended",
            "role_label": role,
            "decade_bucket": decade,
            "artist_key": artist,
            "score_payload": {
                "prism_final_score": rec.final_score,
                "prism_confidence_score": rec.confidence_score,
                "prism_score_breakdown": rec.score_breakdown,
            },
            "inclusion_reason": f"PRISM recommendation added for {role.replace('_', ' ')} coverage",
            "priority": rec.final_score,
        })
        used_ids.add(rec.canonical_track_id)
        role_counts[role] += 1
        artist_counts[artist] += 1
        decade_counts[decade] += 1

    # 3) sort final list by blended priority and assign ranks
    selected.sort(key=lambda x: (1 if x["source_type"] == "existing" else 0, x["priority"]), reverse=True)
    items = []
    for rank, item in enumerate(selected[:requested_length], start=1):
        items.append({
            "canonical_track_id": item["canonical_track_id"],
            "rank": rank,
            "source_type": item["source_type"],
            "role_label": item["role_label"],
            "inclusion_reason": item["inclusion_reason"],
            "score_payload": item["score_payload"],
        })

    summary = {
        "run_id": run_id,
        "mode": mode,
        "requested_length": requested_length,
        "selected_count": len(items),
        "existing_count": sum(1 for x in items if x["source_type"] == "existing"),
        "recommended_count": sum(1 for x in items if x["source_type"] == "recommended"),
        "role_distribution": dict(role_counts),
        "decade_distribution": dict(decade_counts),
        "artist_count": len(artist_counts),
    }

    repo.replace_curated_playlist_set(session, run_id, mode, requested_length, summary, items)

    if settings.debug.enabled and settings.debug.dump_score_snapshots:
        p1 = write_debug_json(settings, f"wave_c2_curated_playlist_{mode}", {"summary": summary, "items": items}, run_id=run_id)
        if p1:
            repo.record_debug_artifact(session, f"wave_c2_curated_playlist_{mode}", p1, run_id=run_id)

    return {"summary": summary, "items": items}
