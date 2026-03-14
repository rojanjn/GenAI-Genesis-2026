"""
Backboard Memory Layer
======================
Calls the Backboard REST API directly via httpx.
Bypasses the broken backboard-sdk (v1.5.5).

Confirmed API shape:
  POST /assistants/{id}/memories
    body: {"content": str, "metadata": {}}
    response: {"success": true, "memory_id": str, "content": str}

  GET /assistants/{id}/memories
    response: {"memories": [{"id": str, "content": str, "metadata": {}, ...}], "total_count": int}

Tags are stored in metadata as {"tag": str} since the API has no native tag field.
"""

import asyncio
import logging
import os

import httpx

from .schemas import UserProfileMemory

logger = logging.getLogger(__name__)

BASE_URL = "https://app.backboard.io/api"

TAG_STRESSOR        = "stressor"
TAG_EMOTION         = "emotion"
TAG_STRATEGY        = "strategy"
TAG_SUPPORT_STYLE   = "support_style"
TAG_PATTERN         = "pattern"
TAG_SESSION_SUMMARY = "session_summary"


def _headers() -> dict:
    api_key = os.getenv("BACKBOARD_API_KEY")
    if not api_key:
        raise RuntimeError("BACKBOARD_API_KEY environment variable is not set")
    return {"X-API-Key": api_key, "Content-Type": "application/json"}


# ── Assistant management ──────────────────────────────────────────────────────

async def get_or_create_assistant(user_id: str) -> str:
    """
    Return the assistant_id for this user, creating one if needed.
    Store the returned ID in your user DB.
    """
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/assistants", headers=_headers())
        r.raise_for_status()
        for asst in r.json():
            if asst.get("name") == f"arc-{user_id}":
                return asst["assistant_id"]

        r = await client.post(
            f"{BASE_URL}/assistants",
            headers=_headers(),
            json={
                "name": f"arc-{user_id}",
                "system_prompt": (
                    "You are an AI mental wellness companion. "
                    "You help users reflect on their emotions through journalling. "
                    "You are warm, non-judgmental, and use motivational interviewing principles."
                ),
            },
        )
        r.raise_for_status()
        assistant_id = r.json()["assistant_id"]
        logger.info("Created assistant %s for user %s", assistant_id, user_id)
        return assistant_id


# ── Write ─────────────────────────────────────────────────────────────────────

async def store_profile_update(assistant_id: str, profile: UserProfileMemory) -> None:
    """Write a UserProfileMemory to Backboard. Each item stored as a separate memory."""

    writes: list[tuple[str, str]] = []  # (content, tag)

    for item in profile.common_stressors:
        writes.append((item, TAG_STRESSOR))
    for item in profile.recurring_emotions:
        writes.append((item, TAG_EMOTION))
    for item in profile.helpful_strategies:
        writes.append((item, TAG_STRATEGY))
    for item in profile.support_preferences:
        writes.append((item, TAG_SUPPORT_STYLE))
    for item in profile.recent_patterns:
        writes.append((item, TAG_PATTERN))
    if profile.summary:
        writes.append((profile.summary, TAG_SESSION_SUMMARY))

    if not writes:
        return

    async with httpx.AsyncClient() as client:
        tasks = [
            client.post(
                f"{BASE_URL}/assistants/{assistant_id}/memories",
                headers=_headers(),
                json={"content": content, "metadata": {"tag": tag}},
            )
            for content, tag in writes
        ]
        responses = await asyncio.gather(*tasks)
        for r in responses:
            r.raise_for_status()

    logger.info("Stored %d memories for assistant %s", len(writes), assistant_id)


# ── Read ──────────────────────────────────────────────────────────────────────

async def load_user_profile(assistant_id: str) -> UserProfileMemory:
    """
    Fetch all memories and reassemble into a UserProfileMemory.
    Returns an empty UserProfileMemory for first-time users.
    """
    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{BASE_URL}/assistants/{assistant_id}/memories",
            headers=_headers(),
        )
        r.raise_for_status()
        memories = r.json().get("memories", [])

    common_stressors: list[str] = []
    recurring_emotions: list[str] = []
    helpful_strategies: list[str] = []
    support_preferences: list[str] = []
    recent_patterns: list[str] = []
    summaries: list[str] = []

    for memory in memories:
        content = (memory.get("content") or "").strip()
        tag = (memory.get("metadata") or {}).get("tag", "")
        if not content:
            continue

        if tag == TAG_STRESSOR and content not in common_stressors:
            common_stressors.append(content)
        elif tag == TAG_EMOTION and content not in recurring_emotions:
            recurring_emotions.append(content)
        elif tag == TAG_STRATEGY and content not in helpful_strategies:
            helpful_strategies.append(content)
        elif tag == TAG_SUPPORT_STYLE and content not in support_preferences:
            support_preferences.append(content)
        elif tag == TAG_PATTERN and content not in recent_patterns:
            recent_patterns.append(content)
        elif tag == TAG_SESSION_SUMMARY:
            summaries.append(content)

    logger.debug(
        "Loaded profile for %s: %d stressors, %d emotions, %d strategies, %d patterns",
        assistant_id, len(common_stressors), len(recurring_emotions),
        len(helpful_strategies), len(recent_patterns),
    )

    return UserProfileMemory(
        common_stressors=common_stressors,
        recurring_emotions=recurring_emotions,
        helpful_strategies=helpful_strategies,
        support_preferences=support_preferences,
        recent_patterns=recent_patterns,
        summary=summaries[-1] if summaries else "",
    )
