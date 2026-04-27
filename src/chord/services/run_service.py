from __future__ import annotations
import hashlib, logging
from pathlib import Path
from chord.constants import QUIZ_VERSION
from chord.db import repositories as repo
from chord.domain.quiz import build_profile_seed
from chord.ingest.apple_txt import parse_apple_txt
from chord.ingest.normalize import normalize_track_row, dedupe_exact_rows
from chord.utils.debug import write_debug_json

logger = logging.getLogger(__name__)

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def ingest_playlist_file(session, settings, *, run_id: int, file_path: str, playlist_name: str, playlist_kind: str, source_order: int = 0):
    path = Path(file_path)
    upload = repo.create_upload(
        session,
        run_id=run_id,
        source_kind=playlist_kind,
        original_filename=path.name,
        stored_path=str(path),
        file_size_bytes=path.stat().st_size,
        sha256=sha256_file(path),
    )
    playlist = repo.create_playlist(
        session,
        run_id=run_id,
        upload_id=upload.id,
        playlist_name=playlist_name,
        playlist_kind=playlist_kind,
        source_order=source_order,
    )

    parsed_rows = parse_apple_txt(path)
    if settings.debug.enabled and settings.debug.dump_parsed_rows:
        artifact_path = write_debug_json(settings, f"{playlist_kind}_parsed_rows", parsed_rows, run_id=run_id)
        if artifact_path:
            repo.record_debug_artifact(session, "parsed_rows", artifact_path, run_id=run_id)

    normalized_rows = [normalize_track_row(row) for row in parsed_rows]
    normalized_rows = dedupe_exact_rows(normalized_rows)

    if settings.debug.enabled and settings.debug.dump_normalized_rows:
        artifact_path = write_debug_json(settings, f"{playlist_kind}_normalized_rows", normalized_rows, run_id=run_id)
        if artifact_path:
            repo.record_debug_artifact(session, "normalized_rows", artifact_path, run_id=run_id)

    for row in normalized_rows:
        track = repo.create_track(
            session,
            playlist_id=playlist.id,
            source_row_number=row["source_row_number"],
            title=row["title"] or None,
            artist=row["artist"] or None,
            album=row["album"] or None,
            genre=row["genre"] or None,
            year=row["year"],
            rating=row["rating"],
            play_count=row["play_count"],
            skip_count=row["skip_count"],
            date_added=row["date_added"] or None,
            media_kind=row["media_kind"] or None,
            raw_payload=row["raw_payload"],
        )
        canonical, created = repo.get_or_create_canonical_track(
            session,
            run_id=run_id,
            canonical_title=row["canonical_title"],
            canonical_artist=row["canonical_artist"],
            defaults={
                "display_title": row["title"] or None,
                "display_artist": row["artist"] or None,
                "sample_album": row["album"] or None,
                "sample_genre": row["genre"] or None,
                "sample_year": row["year"],
                "top25_anchor": (playlist_kind == "top25"),
                "playlist_occurrences": 0,
                "total_play_count": 0,
                "total_skip_count": 0,
                "rating_max": row["rating"],
                "first_seen_playlist_kind": playlist_kind,
            },
        )
        canonical.playlist_occurrences = (canonical.playlist_occurrences or 0) + 1
        canonical.total_play_count = (canonical.total_play_count or 0) + (row["play_count"] or 0)
        canonical.total_skip_count = (canonical.total_skip_count or 0) + (row["skip_count"] or 0)
        if row["rating"] is not None:
            canonical.rating_max = max(canonical.rating_max or 0, row["rating"])
        if playlist_kind == "top25":
            canonical.top25_anchor = True
        repo.link_track(session, canonical.id, track.id)
    session.commit()
    logger.info("Imported playlist '%s' (%s)", playlist_name, playlist_kind)
    return {"upload_id": upload.id, "playlist_id": playlist.id, "rows": len(normalized_rows)}

def submit_quiz_answers(session, *, run_id: int, answers: dict[str, str]):
    repo.add_quiz_answers(session, run_id, QUIZ_VERSION, answers)
    profile = repo.upsert_curator_profile_seed(session, run_id, QUIZ_VERSION, build_profile_seed(answers))
    return profile
