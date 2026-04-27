from __future__ import annotations
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from chord.config import Settings
from chord.utils.paths import ensure_runtime_dirs

def configure_logging(settings: Settings) -> None:
    dirs = ensure_runtime_dirs(settings)
    log_dir = dirs["logs"]
    root = logging.getLogger()
    if root.handlers:
        return
    root.setLevel(logging.DEBUG if settings.debug.enabled else logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )

    info_handler = RotatingFileHandler(Path(log_dir) / "chord.log", maxBytes=5_000_000, backupCount=5)
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(formatter)

    error_handler = RotatingFileHandler(Path(log_dir) / "chord.error.log", maxBytes=5_000_000, backupCount=5)
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    root.addHandler(info_handler)
    root.addHandler(error_handler)
    root.addHandler(console_handler)

    if settings.debug.enabled:
        debug_handler = RotatingFileHandler(Path(log_dir) / "chord.debug.log", maxBytes=5_000_000, backupCount=5)
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(formatter)
        root.addHandler(debug_handler)


def diagnostic_logger():
    return logging.getLogger("chord.diagnostics")
