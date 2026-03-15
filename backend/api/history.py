from typing import Any, Dict, List, Optional
import re

from fastapi import APIRouter, Depends, HTTPException, Query

from backend.api.auth import get_current_user_id
from backend.db.firebase_client import get_db

router = APIRouter(prefix="/history", tags=["History"])


def _strip_html_tags(text: str) -> str:
    if not text:
        return ""
    cleaned = re.sub(r"<[^>]+>", " ", text)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def _iso_timestamp(value) -> Optional[str]:
    if value is None:
        return None

    if hasattr(value, "isoformat"):
        return value.isoformat()

    return str(value)


def _get_user_diary_entries(user_id: str) -> List[Dict[str, Any]]:
    db = get_db()

    query = db.collection("diary_entries").where("user_id", "==", user_id)
    docs = query.stream()

    entries: List[Dict[str, Any]] = []

    for doc in docs:
        entry = doc.to_dict()
        entry["entry_id"] = doc.id
        entries.append(entry)

    # Most recent first
    entries.sort(key=lambda x: _iso_timestamp(x.get("timestamp")) or "", reverse=True)
    return entries


def _get_user_mood_history(user_id: str) -> List[Dict[str, Any]]:
    db = get_db()

    query = db.collection("mood_history").where("user_id", "==", user_id)
    docs = query.stream()

    moods: List[Dict[str, Any]] = []

    for doc in docs:
        mood = doc.to_dict()
        mood["mood_id"] = doc.id
        moods.append(mood)

    # Most recent first
    moods.sort(key=lambda x: _iso_timestamp(x.get("timestamp")) or "", reverse=True)
    return moods


def _build_diary_preview(entry: Dict[str, Any], preview_length: int = 140) -> Dict[str, Any]:
    plain_text = _strip_html_tags(entry.get("text", ""))
    preview = plain_text[:preview_length].strip()

    if len(plain_text) > preview_length:
        preview += "..."

    return {
        "entry_id": entry.get("entry_id"),
        "preview": preview,
        "text": plain_text,
        "timestamp": _iso_timestamp(entry.get("timestamp")),
        "user_id": entry.get("user_id"),
    }


def _build_mood_preview(mood: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "mood_id": mood.get("mood_id"),
        "mood": mood.get("mood"),
        "intensity": mood.get("intensity"),
        "note": mood.get("note"),
        "date": mood.get("date"),
        "timestamp": _iso_timestamp(mood.get("timestamp")),
        "user_id": mood.get("user_id"),
    }


@router.get("/diary")
async def list_diary_entries(user_id: str = Depends(get_current_user_id)):
    """
    Return all diary entries for the logged-in user in reverse chronological order.
    Most recent entry comes first.
    """
    entries = _get_user_diary_entries(user_id)

    return {
        "success": True,
        "total": len(entries),
        "entries": [_build_diary_preview(entry) for entry in entries],
    }


@router.get("/diary/nav")
async def navigate_diary_entry(
    current_entry_id: Optional[str] = Query(default=None),
    direction: str = Query(default="current", pattern="^(current|next|previous)$"),
    user_id: str = Depends(get_current_user_id),
):
    """
    Return the current, next, or previous diary entry for the logged-in user.

    Behaviour:
    - no current_entry_id -> returns the most recent entry
    - direction=next -> next older entry
    - direction=previous -> previous newer entry
    - direction=current -> current entry if provided
    """
    entries = _get_user_diary_entries(user_id)

    if not entries:
        raise HTTPException(status_code=404, detail="No diary entries found")

    entry_ids = [entry["entry_id"] for entry in entries]

    if current_entry_id is None:
        target_index = 0
    else:
        if current_entry_id not in entry_ids:
            raise HTTPException(status_code=404, detail="Diary entry not found")

        current_index = entry_ids.index(current_entry_id)

        if direction == "next":
            target_index = min(current_index + 1, len(entries) - 1)
        elif direction == "previous":
            target_index = max(current_index - 1, 0)
        else:
            target_index = current_index

    entry = entries[target_index]

    return {
        "success": True,
        "entry": {
            "entry_id": entry.get("entry_id"),
            "text": entry.get("text"),
            "plain_text": _strip_html_tags(entry.get("text", "")),
            "timestamp": _iso_timestamp(entry.get("timestamp")),
            "user_id": entry.get("user_id"),
        },
        "position": target_index,
        "total": len(entries),
        "has_previous": target_index > 0,
        "has_next": target_index < len(entries) - 1,
        "previous_entry_id": entries[target_index - 1]["entry_id"] if target_index > 0 else None,
        "next_entry_id": entries[target_index + 1]["entry_id"] if target_index < len(entries) - 1 else None,
    }


@router.get("/moods")
async def list_mood_history(user_id: str = Depends(get_current_user_id)):
    """
    Return all mood history records for the logged-in user in reverse chronological order.
    Most recent entry comes first.
    """
    moods = _get_user_mood_history(user_id)

    return {
        "success": True,
        "total": len(moods),
        "moods": [_build_mood_preview(mood) for mood in moods],
    }


@router.get("/moods/nav")
async def navigate_mood_entry(
    current_mood_id: Optional[str] = Query(default=None),
    direction: str = Query(default="current", pattern="^(current|next|previous)$"),
    user_id: str = Depends(get_current_user_id),
):
    """
    Return the current, next, or previous mood history item for the logged-in user.

    Behaviour:
    - no current_mood_id -> returns the most recent mood entry
    - direction=next -> next older mood item
    - direction=previous -> previous newer mood item
    - direction=current -> current mood item if provided
    """
    moods = _get_user_mood_history(user_id)

    if not moods:
        raise HTTPException(status_code=404, detail="No mood history found")

    mood_ids = [mood["mood_id"] for mood in moods]

    if current_mood_id is None:
        target_index = 0
    else:
        if current_mood_id not in mood_ids:
            raise HTTPException(status_code=404, detail="Mood history item not found")

        current_index = mood_ids.index(current_mood_id)

        if direction == "next":
            target_index = min(current_index + 1, len(moods) - 1)
        elif direction == "previous":
            target_index = max(current_index - 1, 0)
        else:
            target_index = current_index

    mood = moods[target_index]

    return {
        "success": True,
        "mood": {
            "mood_id": mood.get("mood_id"),
            "mood": mood.get("mood"),
            "intensity": mood.get("intensity"),
            "note": mood.get("note"),
            "date": mood.get("date"),
            "timestamp": _iso_timestamp(mood.get("timestamp")),
            "user_id": mood.get("user_id"),
        },
        "position": target_index,
        "total": len(moods),
        "has_previous": target_index > 0,
        "has_next": target_index < len(moods) - 1,
        "previous_mood_id": moods[target_index - 1]["mood_id"] if target_index > 0 else None,
        "next_mood_id": moods[target_index + 1]["mood_id"] if target_index < len(moods) - 1 else None,
    }