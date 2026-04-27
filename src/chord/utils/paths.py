from pathlib import Path
from chord.config import Settings

def ensure_runtime_dirs(settings: Settings) -> dict[str, Path]:
    mapping = {
        "base": Path(settings.app.base_dir),
        "logs": Path(settings.app.log_dir),
        "uploads": Path(settings.paths.upload_dir),
        "cache": Path(settings.paths.cache_dir),
        "exports": Path(settings.paths.export_dir),
        "state": Path(settings.paths.state_dir),
        "debug": Path(settings.debug.artifact_dir),
    }
    for path in mapping.values():
        path.mkdir(parents=True, exist_ok=True)
    return mapping
