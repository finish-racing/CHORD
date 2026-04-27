from __future__ import annotations
from collections import Counter, defaultdict
from math import log1p
from chord.db import repositories as repo
from chord.utils.debug import write_debug_json

def _bucket_year(year: int | None) -> str:
    if not year:
        return "unknown"
    decade = int(year) // 10 * 10
    return f"{decade}s"

def compute_wave_b1_aggregates(session, settings, *, run_id: int) -> dict:
    canonical_tracks = repo.list_canonical_tracks_for_run(session, run_id)
    playlist_rows = repo.list_playlists_for_run(session, run_id)

    artist_counter = Counter()
    genre_counter = Counter()
    decade_counter = Counter()
    top25_count = 0
    repeated_count = 0
    play_values = []
    skip_values = []
    rated_count = 0

    per_track_payloads = []

    playlist_kinds_present = Counter(p.playlist_kind for p in playlist_rows)

    for ct in canonical_tracks:
        if ct.display_artist:
            artist_counter[ct.display_artist] += 1
        if ct.sample_genre:
            genre_counter[ct.sample_genre] += 1
        decade_counter[_bucket_year(ct.sample_year)] += 1
        if ct.top25_anchor:
            top25_count += 1
        if (ct.playlist_occurrences or 0) > 1:
            repeated_count += 1
        if (ct.total_play_count or 0) > 0:
            play_values.append(ct.total_play_count or 0)
        if (ct.total_skip_count or 0) > 0:
            skip_values.append(ct.total_skip_count or 0)
        if ct.rating_max is not None:
            rated_count += 1

        play = ct.total_play_count or 0
        skip = ct.total_skip_count or 0
        rating = ct.rating_max or 0
        tension_score = round((log1p(play) * 0.5) + (rating / 100 * 0.35) - (log1p(skip) * 0.15), 4)
        payload = {
            "top25_anchor": bool(ct.top25_anchor),
            "playlist_occurrences": ct.playlist_occurrences or 0,
            "cross_playlist_recurrence_score": round(min((ct.playlist_occurrences or 0) / max(1, len(playlist_rows)), 1.0), 4),
            "behavioral_tension_score": tension_score,
            "artist": ct.display_artist,
            "genre": ct.sample_genre,
            "decade_bucket": _bucket_year(ct.sample_year),
            "total_play_count": play,
            "total_skip_count": skip,
            "rating_max": ct.rating_max,
        }
        repo.upsert_canonical_track_aggregate(session, ct.id, payload)
        per_track_payloads.append({"canonical_track_id": ct.id, **payload})

    total_tracks = len(canonical_tracks)
    total_playlists = len(playlist_rows)
    quality = 0.0
    if total_tracks:
        quality += min(top25_count / max(1, total_tracks), 1.0) * 0.30
        quality += min(repeated_count / max(1, total_tracks), 1.0) * 0.20
        quality += min(rated_count / max(1, total_tracks), 1.0) * 0.15
        quality += min(total_playlists / 5, 1.0) * 0.20
        quality += (1.0 if playlist_kinds_present.get("top25", 0) >= 1 else 0.0) * 0.15
    quality = round(quality, 4)

    payload = {
        "run_id": run_id,
        "total_canonical_tracks": total_tracks,
        "total_playlists": total_playlists,
        "playlist_kind_counts": dict(playlist_kinds_present),
        "top25_anchor_count": top25_count,
        "cross_playlist_recurrence_count": repeated_count,
        "rated_track_count": rated_count,
        "top_artists": artist_counter.most_common(15),
        "top_genres": genre_counter.most_common(15),
        "decade_distribution": dict(decade_counter),
        "intake_quality_score": quality,
    }
    repo.upsert_run_aggregate(session, run_id, payload, quality)

    if settings.debug.enabled and settings.debug.dump_run_state:
        path = write_debug_json(settings, "wave_b1_run_aggregates", payload, run_id=run_id)
        if path:
            repo.record_debug_artifact(session, "wave_b1_run_aggregates", path, run_id=run_id)
        path2 = write_debug_json(settings, "wave_b1_track_aggregates", per_track_payloads, run_id=run_id)
        if path2:
            repo.record_debug_artifact(session, "wave_b1_track_aggregates", path2, run_id=run_id)

    return payload
