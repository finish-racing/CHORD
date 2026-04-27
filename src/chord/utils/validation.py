from __future__ import annotations
from pathlib import Path
from chord.constants import ALLOWED_UPLOAD_SUFFIXES, MAX_UPLOAD_BYTES

def validate_upload_file(path: Path) -> None:
    if not path.exists():
        raise ValueError(f"File does not exist: {path}")
    if not path.is_file():
        raise ValueError(f"Not a file: {path}")
    if path.suffix.lower() not in ALLOWED_UPLOAD_SUFFIXES:
        raise ValueError(f"Unsupported file type: {path.suffix}")
    size = path.stat().st_size
    if size <= 0:
        raise ValueError(f"File is empty: {path}")
    if size > MAX_UPLOAD_BYTES:
        raise ValueError(f"File is too large: {path} ({size} bytes)")

def validate_quiz_answers(answers: dict[str, str]) -> None:
    if not answers:
        raise ValueError("Quiz answers cannot be empty")
    seen = set()
    for key, value in answers.items():
        if not key or len(key) > 100:
            raise ValueError("Invalid quiz question key")
        if key in seen:
            raise ValueError(f"Duplicate quiz question key: {key}")
        seen.add(key)
        if value is None or str(value).strip() == "":
            raise ValueError(f"Empty answer for question: {key}")
        if len(str(value)) > 1000:
            raise ValueError(f"Answer too long for question: {key}")


def require_positive_int(value: int, name: str) -> None:
    if value is None or int(value) <= 0:
        raise ValueError(f"{name} must be a positive integer")
