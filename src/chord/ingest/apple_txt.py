from __future__ import annotations
import csv
from pathlib import Path
from chord.utils.validation import validate_upload_file

COMMON_HEADERS = {
    "name": "title",
    "artist": "artist",
    "album": "album",
    "genre": "genre",
    "year": "year",
    "rating": "rating",
    "plays": "play_count",
    "play count": "play_count",
    "skips": "skip_count",
    "skip count": "skip_count",
    "date added": "date_added",
    "kind": "media_kind",
}

def _read_text(path: Path) -> str:
    raw = path.read_bytes()
    for encoding in ("utf-16", "utf-8-sig", "utf-8", "latin-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")

def parse_apple_txt(path: str | Path) -> list[dict]:
    p = Path(path)
    validate_upload_file(p)
    text = _read_text(p)
    reader = csv.DictReader(text.splitlines(), delimiter="\t")
    rows = []
    for idx, row in enumerate(reader, start=1):
        mapped = {"source_row_number": idx}
        for key, value in row.items():
            if key is None:
                continue
            nk = key.strip().lower()
            mapped_key = COMMON_HEADERS.get(nk, nk.replace(" ", "_"))
            mapped[mapped_key] = value.strip() if isinstance(value, str) else value
        rows.append(mapped)
    return rows
