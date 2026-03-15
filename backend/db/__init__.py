"""Database module for GenAI-Genesis-2026."""

from .firebase_client import get_db, init_firebase
from .queries import (
    save_entry,
    get_recent_entries,
    get_all_entries,
    save_mood,
    save_notification,
)

__all__ = [
    "get_db",
    "init_firebase",
    "save_entry",
    "get_recent_entries",
    "get_all_entries",
    "save_mood",
    "save_notification",
]
