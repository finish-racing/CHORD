from __future__ import annotations
import os, tomllib
from pathlib import Path
from typing import Any
from pydantic import BaseModel, Field
from chord.constants import DEFAULT_CONFIG_PATHS

class AppSection(BaseModel):
    name: str = "CHORD"
    environment: str = "development"
    debug: bool = False
    base_dir: str = "/var/lib/chord"
    log_dir: str = "/var/log/chord"
    config_dir: str = "/etc/chord"
    release_version: str = "0.1.0"

class DatabaseSection(BaseModel):
    url: str = "postgresql+psycopg://chord:change_me@localhost:5432/chord"
    connect_timeout_seconds: int = 10
    pool_size: int = 5
    max_overflow: int = 10

class DebugSection(BaseModel):
    enabled: bool = False
    artifact_dir: str = "/var/lib/chord/debug"
    dump_parsed_rows: bool = True
    dump_normalized_rows: bool = True
    dump_run_state: bool = True
    dump_score_snapshots: bool = True
    http_trace: bool = False

class PathsSection(BaseModel):
    upload_dir: str = "/var/lib/chord/uploads"
    cache_dir: str = "/var/lib/chord/cache"
    export_dir: str = "/var/lib/chord/exports"
    state_dir: str = "/var/lib/chord/state"

class WebSection(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: list[str] = Field(default_factory=lambda: ["*"])

class OpenAISection(BaseModel):
    enabled: bool = False
    api_key: str = ""
    model: str = "gpt-5.4"

class LastFMSection(BaseModel):
    enabled: bool = False
    api_key: str = ""
    shared_secret: str = ""
    api_root: str = "https://ws.audioscrobbler.com/2.0"

class MusicBrainzSection(BaseModel):
    enabled: bool = False
    api_root: str = "https://musicbrainz.org/ws/2"
    user_agent: str = "CHORD/0.1.0 (ubuntu build)"

class AcousticBrainzSection(BaseModel):
    enabled: bool = False
    api_root: str = "https://acousticbrainz.org/api/v1"

class Settings(BaseModel):
    app: AppSection = Field(default_factory=AppSection)
    database: DatabaseSection = Field(default_factory=DatabaseSection)
    debug: DebugSection = Field(default_factory=DebugSection)
    paths: PathsSection = Field(default_factory=PathsSection)
    web: WebSection = Field(default_factory=WebSection)
    openai: OpenAISection = Field(default_factory=OpenAISection)
    lastfm: LastFMSection = Field(default_factory=LastFMSection)
    musicbrainz: MusicBrainzSection = Field(default_factory=MusicBrainzSection)
    acousticbrainz: AcousticBrainzSection = Field(default_factory=AcousticBrainzSection)

def _as_bool(value: str | None):
    if value is None:
        return None
    return value.strip().lower() in {"1", "true", "yes", "on"}

def resolve_config_path(explicit_path: str | None = None) -> Path:
    if explicit_path:
        return Path(explicit_path)
    for candidate in DEFAULT_CONFIG_PATHS:
        p = Path(candidate)
        if p.exists():
            return p
    return Path(DEFAULT_CONFIG_PATHS[-1])

def _load_toml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("rb") as fh:
        return tomllib.load(fh)

def load_settings(config_path: str | None = None) -> Settings:
    path = resolve_config_path(config_path)
    payload = _load_toml(path)
    overrides = {
        ("app", "debug"): _as_bool(os.getenv("CHORD_DEBUG")),
        ("debug", "enabled"): _as_bool(os.getenv("CHORD_DEBUG")),
        ("database", "url"): os.getenv("CHORD_DATABASE_URL"),
        ("openai", "api_key"): os.getenv("CHORD_OPENAI_API_KEY"),
        ("lastfm", "api_key"): os.getenv("CHORD_LASTFM_API_KEY"),
        ("lastfm", "shared_secret"): os.getenv("CHORD_LASTFM_SHARED_SECRET"),
    }
    for (section, key), value in overrides.items():
        if value is None or value == "":
            continue
        payload.setdefault(section, {})
        payload[section][key] = value
    settings = Settings.model_validate(payload)
    if settings.app.debug and not settings.debug.enabled:
        settings.debug.enabled = True
    return settings
