from __future__ import annotations
import re

def _clean(value: str | None) -> str:
    return (value or "").strip()

def normalize_text(value: str | None) -> str:
    value = _clean(value).lower()
    value = re.sub(r"\s+", " ", value)
    value = re.sub(r"[\(\)\[\]\{\}\.,'\"!?:;]", "", value)
    return value.strip()

def normalize_track_row(row: dict) -> dict:
    def as_int(value):
        if value in (None, ""):
            return None
        try:
            return int(str(value).strip())
        except ValueError:
            return None

    normalized = {
        "title": _clean(row.get("title") or row.get("name")),
        "artist": _clean(row.get("artist")),
        "album": _clean(row.get("album")),
        "genre": _clean(row.get("genre")),
        "year": as_int(row.get("year")),
        "rating": as_int(row.get("rating")),
        "play_count": as_int(row.get("play_count")),
        "skip_count": as_int(row.get("skip_count")),
        "date_added": _clean(row.get("date_added")),
        "media_kind": _clean(row.get("media_kind") or row.get("kind")),
        "source_row_number": row.get("source_row_number"),
        "raw_payload": row,
    }
    normalized["canonical_title"] = normalize_text(normalized["title"])
    normalized["canonical_artist"] = normalize_text(normalized["artist"])
    return normalized

def dedupe_exact_rows(rows: list[dict]) -> list[dict]:
    seen = set()
    deduped = []
    for row in rows:
        key = (
            row.get("title"),
            row.get("artist"),
            row.get("album"),
            row.get("year"),
            row.get("media_kind"),
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)
    return deduped
