from __future__ import annotations
from collections import Counter, defaultdict
from math import log1p
from chord.db import repositories as repo
from chord.utils.debug import write_debug_json

ROLE_ORDER = [
    "anchor_song",
    "replay_core_song",
    "bridge_song",
    "memory_trigger_song",
    "social_singalong_song",
    "comfort_background_song",
    "emotional_centerpiece",
    "generational_touchstone",
    "curated_outlier",
]

def _extract_lastfm_tags(enrichments: list[dict]) -> list[str]:
    tags = []
    for item in enrichments:
        if item.get("source_name") != "lastfm":
            continue
        tag_rows = ((((item.get("data_payload") or {}).get("tags") or {}).get("toptags") or {}).get("tag")) or []
        if isinstance(tag_rows, dict):
            tag_rows = [tag_rows]
        for tag in tag_rows:
            name = (tag.get("name") or "").strip()
            if name:
                tags.append(name.lower())
    return tags

def _extract_mb_recording_id(enrichments: list[dict]) -> str | None:
    for item in enrichments:
        if item.get("source_name") == "musicbrainz" and item.get("source_key"):
            return item.get("source_key")
    return None

def _guess_mood(tags: list[str], genre: str | None, decade_bucket: str, play_count: int, skip_count: int) -> str:
    tagset = set(tags)
    g = (genre or "").lower()
    if {"soft rock", "folk", "americana", "acoustic", "singer-songwriter"} & tagset or "folk" in g or "singer" in g:
        return "warm_nostalgia" if decade_bucket in {"1970s", "1980s"} else "reflective_bridge"
    if {"indie", "alternative", "indie rock", "indie folk"} & tagset or "alternative" in g:
        return "modern_replay_core" if play_count >= max(skip_count, 1) else "reflective_bridge"
    if {"pop", "dance", "disco", "new wave"} & tagset or "pop" in g:
        return "social_singalong"
    if play_count > 0 and skip_count == 0:
        return "comfort_groove"
    return "eclectic_drive"

def _guess_role(top25_anchor: bool, recurrence: float, tension: float, decade_bucket: str, tags: list[str], play_count: int) -> str:
    if top25_anchor:
        return "anchor_song"
    if play_count >= 20 or tension >= 2.2:
        return "replay_core_song"
    if recurrence >= 0.5:
        return "bridge_song"
    if decade_bucket in {"1970s", "1980s"} and ("classic rock" in tags or "70s" in tags or "80s" in tags):
        return "generational_touchstone"
    if "driving" in tags or "pop" in tags:
        return "social_singalong_song"
    if "acoustic" in tags or "folk" in tags:
        return "comfort_background_song"
    return "memory_trigger_song"

def build_identity_profile(session, settings, *, run_id: int) -> dict:
    canonical_tracks = repo.list_canonical_tracks_for_run(session, run_id)
    enrichments = repo.list_track_enrichments_for_run(session, run_id)
    aggregate = repo.get_run_aggregate(session, run_id)
    quiz_profile = None
    try:
        quiz_profile = session.execute(__import__("sqlalchemy").select(__import__("chord.db.models", fromlist=["CuratorProfile"]).CuratorProfile).where(__import__("chord.db.models", fromlist=["CuratorProfile"]).CuratorProfile.run_id == run_id)).scalar_one_or_none()
    except Exception:
        quiz_profile = None

    enrich_by_track = defaultdict(list)
    for item in enrichments:
        enrich_by_track[item.canonical_track_id].append({
            "source_name": item.source_name,
            "source_key": item.source_key,
            "status": item.status,
            "data_payload": item.data_payload,
            "confidence_score": item.confidence_score,
        })

    title_family_counter = Counter()
    artist_counter = Counter()
    mood_counter = Counter()
    role_counter = Counter()
    top25_anchors = 0
    duplicate_like_families = 0

    per_track_identity = []

    for ct in canonical_tracks:
        track_enrich = enrich_by_track.get(ct.id, [])
        tags = _extract_lastfm_tags(track_enrich)
        decade_bucket = f"{(ct.sample_year // 10) * 10}s" if ct.sample_year else "unknown"
        tension = round((log1p(ct.total_play_count or 0) * 0.5) + (((ct.rating_max or 0) / 100) * 0.35) - (log1p(ct.total_skip_count or 0) * 0.15), 4)
        recurrence = round(min((ct.playlist_occurrences or 0) / max(len(canonical_tracks), 1) * 5, 1.0), 4)
        mood = _guess_mood(tags, ct.sample_genre, decade_bucket, ct.total_play_count or 0, ct.total_skip_count or 0)
        role = _guess_role(bool(ct.top25_anchor), recurrence, tension, decade_bucket, tags, ct.total_play_count or 0)

        title_key = ct.canonical_title
        artist_key = ct.canonical_artist
        title_family_counter[title_key] += 1
        artist_counter[artist_key] += 1
        mood_counter[mood] += 1
        role_counter[role] += 1
        if ct.top25_anchor:
            top25_anchors += 1

        version_like = any(x in (ct.display_title or "").lower() for x in ["live", "acoustic", "remaster", "edit", "demo", "mix"])
        mbid = _extract_mb_recording_id(track_enrich)

        payload = {
            "canonical_title": ct.canonical_title,
            "canonical_artist": ct.canonical_artist,
            "display_title": ct.display_title,
            "display_artist": ct.display_artist,
            "top25_anchor": bool(ct.top25_anchor),
            "cross_playlist_recurrence_score": recurrence,
            "behavioral_tension_score": tension,
            "mood_family": mood,
            "playlist_role": role,
            "lastfm_tags": tags[:15],
            "decade_bucket": decade_bucket,
            "genre": ct.sample_genre,
            "representation_inputs": {
                "playlist_occurrences": ct.playlist_occurrences or 0,
                "total_play_count": ct.total_play_count or 0,
                "total_skip_count": ct.total_skip_count or 0,
                "rating_max": ct.rating_max,
            },
            "identity_flags": {
                "version_like_title": version_like,
                "musicbrainz_recording_mbid_present": bool(mbid),
                "same_title_family_size": title_family_counter[title_key],
            },
        }
        repo.upsert_canonical_track_identity(session, ct.id, payload)
        per_track_identity.append({"canonical_track_id": ct.id, **payload})

    # Recompute family counters after pass
    probable_cover_tolerance = round(min(sum(1 for k, v in title_family_counter.items() if v > 1) / max(len(title_family_counter), 1), 1.0), 4)
    duplicate_like_families = sum(1 for _, v in title_family_counter.items() if v > 1)

    profile_payload = {
        "run_id": run_id,
        "top25_anchor_count": top25_anchors,
        "mood_family_distribution": dict(mood_counter),
        "playlist_role_distribution": dict(role_counter),
        "title_family_duplicate_like_count": duplicate_like_families,
        "cover_tolerance_profile": {
            "probable_cover_tolerance": probable_cover_tolerance,
            "interpretation": "moderate" if probable_cover_tolerance >= 0.2 else "low",
        },
        "boundary_model": {
            "avoid_same_artist_overweight": True,
            "avoid_same_era_trap": True,
            "avoid_technically_similar_but_wrong": True,
            "avoid_repeat_of_existing": True,
        },
        "cultural_omission_scaffold": {
            "enabled": True,
            "target_generational_lane": "genx_lifetime_soundtrack",
        },
        "curator_profile_seed": getattr(quiz_profile, "profile_seed", None),
        "aggregate_summary": getattr(aggregate, "aggregate_payload", None),
    }

    repo.upsert_identity_profile(session, run_id, profile_payload)
    session.commit()

    if settings.debug.enabled and settings.debug.dump_run_state:
        p1 = write_debug_json(settings, "wave_b3_identity_profile", profile_payload, run_id=run_id)
        if p1:
            repo.record_debug_artifact(session, "wave_b3_identity_profile", p1, run_id=run_id)
        p2 = write_debug_json(settings, "wave_b3_track_identity", per_track_identity, run_id=run_id)
        if p2:
            repo.record_debug_artifact(session, "wave_b3_track_identity", p2, run_id=run_id)

    return profile_payload
