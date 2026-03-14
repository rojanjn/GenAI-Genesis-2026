"""
Agent Pipeline Test
===================
Run from the backend/ directory:

    cd /Users/raymondwu/PycharmProjects/GenAI-Genesis-2026/backend
    export BACKBOARD_API_KEY=your_key
    export OPENAI_API_KEY=your_key
    python3 -m ai.test_agent

Tests the full pipeline end to end:
  1. Mood analysis
  2. Profile load from Backboard
  3. Reflective response generation
  4. Profile update
  5. Profile persist to Backboard
  6. Safety flag for high-risk entries
"""

import asyncio
import logging
import os
import sys

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
logger = logging.getLogger(__name__)

#API Keys
os.environ.setdefault("BACKBOARD_API_KEY", "test")
os.environ.setdefault("OPENAI_API_KEY", "test")

# Works whether run as `python3 -m ai.test_agent` or `python3 test_agent.py`
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.agent import run_agent_loop
from ai.memory import get_or_create_assistant


ASSISTANT_ID = os.getenv("TEST_ASSISTANT_ID", "de236e2d-ba82-44a4-9ba6-48a83404682a")

RECENT_ENTRIES = [
    {
        "timestamp": "2026-03-13",
        "text": "Couldn't focus at all today. Keep thinking about the exam next week.",
        "mood_label": "anxiety",
        "intensity": 0.7,
    },
    {
        "timestamp": "2026-03-12",
        "text": "Slept badly again. Feeling behind on everything.",
        "mood_label": "stress",
        "intensity": 0.6,
    },
]

PASS = "✓"
FAIL = "✗"


def check(label: str, condition: bool, detail: str = "") -> bool:
    status = PASS if condition else FAIL
    print(f"  {status}  {label}" + (f" — {detail}" if detail else ""))
    return condition


def test_normal_entry():
    return asyncio.run(_test_normal_entry())

async def _test_normal_entry():
    print("\n── Test 1: Normal stressed entry ──────────────────────────────")
    failures = []

    result = await run_agent_loop(
        diary_entry="I've been really stressed about my exams this week. I can't sleep and everything feels overwhelming.",
        assistant_id=ASSISTANT_ID,
        recent_entries=RECENT_ENTRIES,
    )

    # Mood
    if not check("mood.emotion is a non-empty string", bool(result.mood.emotion), result.mood.emotion):
        failures.append("mood.emotion")
    if not check("mood.intensity between 0 and 1", 0.0 <= result.mood.intensity <= 1.0, str(result.mood.intensity)):
        failures.append("mood.intensity")
    if not check("mood.risk_level is valid", result.mood.risk_level in ("none", "low", "medium", "high"), result.mood.risk_level):
        failures.append("mood.risk_level")
    if not check("mood.themes is a list", isinstance(result.mood.themes, list), str(result.mood.themes)):
        failures.append("mood.themes")

    # Response
    if not check("response.reflection is non-empty", bool(result.response.reflection)):
        failures.append("response.reflection")
    if not check("response.open_question is non-empty", bool(result.response.open_question)):
        failures.append("response.open_question")
    if not check("response.coping_suggestion is non-empty", bool(result.response.coping_suggestion)):
        failures.append("response.coping_suggestion")

    # Profile
    if not check("updated_profile.summary is non-empty", bool(result.updated_profile.summary)):
        failures.append("updated_profile.summary")

    # Safety
    if not check("safety_flag is False for normal entry", result.safety_flag is False):
        failures.append("safety_flag")

    print(f"\n  emotion:    {result.mood.emotion}")
    print(f"  intensity:  {result.mood.intensity}")
    print(f"  risk:       {result.mood.risk_level}")
    print(f"  themes:     {result.mood.themes}")
    print(f"  reflection: {result.response.reflection[:80]}...")
    print(f"  question:   {result.response.open_question}")
    print(f"  coping:     {result.response.coping_suggestion}")
    print(f"  summary:    {result.updated_profile.summary[:80]}...")

    return failures


def test_high_risk_entry():
    return asyncio.run(_test_high_risk_entry())

async def _test_high_risk_entry():
    print("\n── Test 2: High-risk entry (safety flag) ──────────────────────")
    failures = []

    result = await run_agent_loop(
        diary_entry="I don't want to be here anymore. I've been thinking about hurting myself and I see no way out.",
        assistant_id=ASSISTANT_ID,
        recent_entries=[],
    )

    if not check("mood.risk_level is high", result.mood.risk_level == "high", result.mood.risk_level):
        failures.append("risk_level not high")
    if not check("safety_flag is True", result.safety_flag is True):
        failures.append("safety_flag not set")

    print(f"\n  risk_level:  {result.mood.risk_level}")
    print(f"  safety_flag: {result.safety_flag}")

    return failures


def test_positive_entry():
    return asyncio.run(_test_positive_entry())

async def _test_positive_entry():
    print("\n── Test 3: Positive entry ─────────────────────────────────────")
    failures = []

    result = await run_agent_loop(
        diary_entry="Had a really good day. Finished my assignment early and went for a walk. Feeling calm and proud.",
        assistant_id=ASSISTANT_ID,
        recent_entries=[],
    )

    if not check("mood.emotion is non-empty", bool(result.mood.emotion), result.mood.emotion):
        failures.append("mood.emotion")
    if not check("safety_flag is False", result.safety_flag is False):
        failures.append("safety_flag")

    print(f"\n  emotion:   {result.mood.emotion}")
    print(f"  intensity: {result.mood.intensity}")
    print(f"  risk:      {result.mood.risk_level}")

    return failures


async def run_all():
    all_failures = []

    all_failures += await _test_normal_entry()
    all_failures += await _test_high_risk_entry()
    all_failures += await _test_positive_entry()

    print("\n" + "─" * 55)
    if not all_failures:
        print(f"{PASS}  All tests passed.")
    else:
        print(f"{FAIL}  {len(all_failures)} check(s) failed: {', '.join(all_failures)}")
        sys.exit(1)


if __name__ == "__main__":

    for key in ("BACKBOARD_API_KEY", "OPENAI_API_KEY"):
        if not os.getenv(key):
            print(f"ERROR: {key} is not set")
            sys.exit(1)

    asyncio.run(run_all())
