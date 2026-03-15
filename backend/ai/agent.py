"""
Agent Loop
==========
Brings together all modules into a single end-to-end pipeline for
processing a diary entry.

Pipeline per entry:
  1. analyse_mood()                 — emotion, intensity, themes, risk level
  2. load_user_profile()            — fetch long-term memory from Backboard
  3. generate_reflective_response() — MI-style reflection + coping suggestion
  4. update_user_profile_memory()   — summarise patterns into updated profile
  5. store_profile_update()         — persist updated memory to Backboard
  6. Return AgentResult

Safety: risk_level == "high" sets safety_flag on the result so the API
layer can surface crisis resources without this module needing to know them.
"""

import logging
from dataclasses import dataclass
from typing import Any

from .mood_analysis import analyse_mood
from .response_generator import generate_reflective_response
from .profile_updater import update_user_profile_memory
from .schemas import MoodAnalysisResult, GeneratedResponse, UserProfileMemory
from .memory import load_user_profile, store_profile_update

logger = logging.getLogger(__name__)


# ── Result type ───────────────────────────────────────────────────────────────

@dataclass
class AgentResult:
    mood: MoodAnalysisResult
    response: GeneratedResponse
    updated_profile: UserProfileMemory
    safety_flag: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "mood": self.mood.model_dump(),
            "response": self.response.model_dump(),
            "updated_profile": self.updated_profile.model_dump(),
            "safety_flag": self.safety_flag,
        }


# ── Main entry point ──────────────────────────────────────────────────────────

async def run_agent_loop(
    diary_entry: str,
    assistant_id: str,
    recent_entries: list[dict],
) -> AgentResult:
    """
    Run the full pipeline for a single diary entry submission.

    Args:
        diary_entry:    Raw text the user wrote today.
        assistant_id:   Backboard assistant ID for this user.
        recent_entries: Last N diary entries from your DB, each a dict with keys:
                        timestamp, text, mood_label, intensity.

    Returns:
        AgentResult with mood, response, updated profile, and safety flag.
    """

    # Step 1 — Mood analysis
    logger.info("Step 1: analysing mood")
    mood = analyse_mood(diary_entry)
    logger.debug("Mood: %s intensity=%.2f risk=%s", mood.emotion, mood.intensity, mood.risk_level)

    # Step 2 — Load existing profile from Backboard
    logger.info("Step 2: loading user profile")
    profile = await load_user_profile(assistant_id)
    profile_memory_text = _profile_to_text(profile)

    # Step 3 — Generate reflective response
    logger.info("Step 3: generating reflective response")
    response = generate_reflective_response(
        today_entry=diary_entry,
        recent_entries=recent_entries,
        user_profile_memory=profile_memory_text,
    )

    # Step 4 — Update long-term profile memory
    logger.info("Step 4: updating user profile memory")
    updated_profile = update_user_profile_memory(
        recent_entries=[
            {
                "timestamp": "today",
                "text": diary_entry,
                "mood_label": mood.emotion,
                "intensity": mood.intensity,
            },
            *recent_entries,
        ],
        current_memory=profile_memory_text,
    )

    # Step 5 — Persist to Backboard
    logger.info("Step 5: persisting profile to Backboard")
    await store_profile_update(
        assistant_id=assistant_id,
        profile=updated_profile,
    )

    safety_flag = mood.risk_level == "high"
    if safety_flag:
        logger.warning("Safety flag raised for assistant %s", assistant_id)

    return AgentResult(
        mood=mood,
        response=response,
        updated_profile=updated_profile,
        safety_flag=safety_flag,
    )


# ── Helpers ───────────────────────────────────────────────────────────────────

def _profile_to_text(profile: UserProfileMemory) -> str:
    """Convert a UserProfileMemory to plain text for the LLM prompts."""
    lines = []
    if profile.common_stressors:
        lines.append(f"Common stressors: {', '.join(profile.common_stressors)}")
    if profile.recurring_emotions:
        lines.append(f"Recurring emotions: {', '.join(profile.recurring_emotions)}")
    if profile.helpful_strategies:
        lines.append(f"Helpful strategies: {', '.join(profile.helpful_strategies)}")
    if profile.support_preferences:
        lines.append(f"Support preferences: {', '.join(profile.support_preferences)}")
    if profile.recent_patterns:
        lines.append(f"Recent patterns: {', '.join(profile.recent_patterns)}")
    if profile.summary:
        lines.append(f"Summary: {profile.summary}")
    return "\n".join(lines) if lines else "No existing profile memory."
