"""Pygrad configuration and constants."""

import logging
import os
import sys
from pathlib import Path

# Default storage paths
PYGRAD_HOME = Path.home() / ".pygrad"
REPO_STORAGE = PYGRAD_HOME / "repos"


def ensure_storage_exists() -> Path:
    """Ensure the repository storage directory exists."""
    REPO_STORAGE.mkdir(parents=True, exist_ok=True)
    return REPO_STORAGE


def configure_logging_from_env() -> None:
    """Apply root logging level from ``PYGRAD_LOG_LEVEL`` (e.g. DEBUG, INFO, WARNING).

    If unset or empty, leaves logging configuration unchanged (default root level
    remains WARNING unless the host app configured it).
    """
    raw = os.getenv("PYGRAD_LOG_LEVEL", "").strip()
    if not raw:
        return
    name = raw.upper()
    level = getattr(logging, name, None)
    if not isinstance(level, int):
        print(
            f"pygrad: invalid PYGRAD_LOG_LEVEL={raw!r} (use DEBUG, INFO, WARNING, ERROR, CRITICAL); ignoring",
            file=sys.stderr,
        )
        return
    logging.basicConfig(
        level=level,
        format="%(levelname)s %(name)s: %(message)s",
    )
