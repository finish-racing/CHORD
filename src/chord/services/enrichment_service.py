from __future__ import annotations
import logging
from collections import Counter
from chord.db import repositories as repo
from chord.integrations.lastfm import LastFMClient
from chord.integrations.musicbrainz import MusicBrainzClient
from chord.integrations.acousticbrainz import AcousticBrainzClient
from chord.utils.debug import write_debug_json

logger = logging.getLogger(__name__)

def _confidence_from_lastfm(info: dict, tags: dict) -> float:
    listeners = 0
    track = info.get("track") or {}
    try:
        listeners = int(track.get("listeners") or 0)
    except Exception:
        listeners = 0
    tag_count = len((((tags.get("toptags") or {}).get("tag")) or []))
    score = min((listeners / 250000), 1.0) * 0.7 + min((tag_count / 10), 1.0) * 0.3
    return round(score, 4)

def enrich_run(session, settings, *, run_id: int) -> dict:
    canonical_tracks = repo.list_canonical_tracks_for_run(session, run_id)
    lastfm = LastFMClient(settings.lastfm.api_root, settings.lastfm.api_key, user_agent="CHORD/0.1.0")
    mb = MusicBrainzClient(settings.musicbrainz.api_root, user_agent=settings.musicbrainz.user_agent)
    ab = AcousticBrainzClient(settings.acousticbrainz.api_root)
    source_counter = Counter()
    status_counter = Counter()
    results = []

    try:
        for ct in canonical_tracks:
            if not ct.display_title or not ct.display_artist:
                continue

            # Last.fm
            lf_status = "disabled" if not settings.lastfm.enabled or not settings.lastfm.api_key else "missing"
            lf_payload = {}
            lf_prov = {"source": "lastfm", "artist": ct.display_artist, "title": ct.display_title}
            lf_conf = None
            if settings.lastfm.enabled and settings.lastfm.api_key:
                try:
                    info = lastfm.track_info(artist=ct.display_artist, track=ct.display_title)
                    tags = lastfm.track_top_tags(artist=ct.display_artist, track=ct.display_title)
                    lf_payload = {"info": info, "tags": tags}
                    lf_conf = _confidence_from_lastfm(info, tags)
                    lf_status = "resolved"
                except Exception as exc:
                    lf_status = "error"
                    lf_payload = {"error": str(exc)}
            repo.upsert_track_enrichment(
                session, ct.id, "lastfm",
                source_key=f"{ct.display_artist}::{ct.display_title}",
                status=lf_status,
                confidence_score=lf_conf,
                provenance_payload=lf_prov,
                data_payload=lf_payload,
            )
            source_counter["lastfm"] += 1
            status_counter[f"lastfm:{lf_status}"] += 1

            # MusicBrainz
            mb_status = "disabled" if not settings.musicbrainz.enabled else "missing"
            mb_payload = {}
            mb_prov = {"source": "musicbrainz", "artist": ct.display_artist, "title": ct.display_title}
            mb_conf = None
            recording_mbid = None
            if settings.musicbrainz.enabled:
                try:
                    data = mb.search_recording(artist=ct.display_artist, title=ct.display_title)
                    recs = data.get("recordings") or []
                    mb_payload = data
                    if recs:
                        recording_mbid = recs[0].get("id")
                        mb_status = "resolved"
                        mb_conf = round(min(len(recs) / 5, 1.0), 4)
                    else:
                        mb_status = "missing"
                except Exception as exc:
                    mb_status = "error"
                    mb_payload = {"error": str(exc)}
            repo.upsert_track_enrichment(
                session, ct.id, "musicbrainz",
                source_key=recording_mbid,
                status=mb_status,
                confidence_score=mb_conf,
                provenance_payload=mb_prov,
                data_payload=mb_payload,
            )
            source_counter["musicbrainz"] += 1
            status_counter[f"musicbrainz:{mb_status}"] += 1

            # AcousticBrainz
            ab_status = "disabled" if not settings.acousticbrainz.enabled else "missing"
            ab_payload = {}
            ab_prov = {"source": "acousticbrainz", "recording_mbid": recording_mbid}
            ab_conf = None
            if settings.acousticbrainz.enabled and recording_mbid:
                try:
                    data = ab.by_mbid(recording_mbid)
                    ab_payload = data
                    ab_status = "resolved"
                    ab_conf = 0.8
                except Exception as exc:
                    ab_status = "error"
                    ab_payload = {"error": str(exc)}
            repo.upsert_track_enrichment(
                session, ct.id, "acousticbrainz",
                source_key=recording_mbid,
                status=ab_status,
                confidence_score=ab_conf,
                provenance_payload=ab_prov,
                data_payload=ab_payload,
            )
            source_counter["acousticbrainz"] += 1
            status_counter[f"acousticbrainz:{ab_status}"] += 1

            results.append({
                "canonical_track_id": ct.id,
                "display_title": ct.display_title,
                "display_artist": ct.display_artist,
                "lastfm_status": lf_status,
                "musicbrainz_status": mb_status,
                "acousticbrainz_status": ab_status,
                "recording_mbid": recording_mbid,
            })

        summary = {
            "run_id": run_id,
            "total_tracks_considered": len(results),
            "source_counter": dict(source_counter),
            "status_counter": dict(status_counter),
        }
        repo.upsert_run_enrichment_summary(session, run_id, summary)

        if settings.debug.enabled and settings.debug.dump_run_state:
            path = write_debug_json(settings, "wave_b2_enrichment_results", results, run_id=run_id)
            if path:
                repo.record_debug_artifact(session, "wave_b2_enrichment_results", path, run_id=run_id)

        return summary
    finally:
        lastfm.close()
        mb.close()
        ab.close()
