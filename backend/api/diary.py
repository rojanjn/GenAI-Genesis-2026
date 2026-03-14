from fastapi import APIRouter
from pydantic import BaseModel

from backend.ai.mood_analysis import analyse_mood
from backend.ai.response_generator import generate_reflective_response

router = APIRouter()


class JournalEntryRequest(BaseModel):
    user_id: str
    prompt: str
    entry: str


@router.post("/journal-entry")
def save_journal_entry(data: JournalEntryRequest):
    print("Step 1: analysing mood")
    mood_result = analyse_mood(data.entry)

    print("Step 2: deciding support level")
    support_level = decide_support_level(mood_result)

    recent_entries = []
    user_profile_memory = None

    print("Step 3: generating reflective response")
    ai_response = generate_reflective_response(
        today_entry=data.entry,
        recent_entries=recent_entries,
        user_profile_memory=user_profile_memory,
    )

    print("Step 4: building final payload")
    return {
        "success": True,
        "entry_id": "entry_001",
        "message": "Journal entry saved",
        "prompt": data.prompt,
        "support_level": support_level,
        "mood": mood_result.model_dump(),
        "response": ai_response.model_dump(),
        "agent_actions": build_agent_actions(mood_result, support_level),
    }

def decide_support_level(mood_result) -> str:
    if mood_result.risk_level == "high":
        return "high"
    if mood_result.intensity >= 0.75 or mood_result.needs_followup:
        return "medium"
    return "low"

def build_agent_actions(mood_result, support_level: str) -> list[str]:
    actions = ["analyse_mood", "generate_reflective_response"]

    if mood_result.needs_followup:
        actions.append("flag_followup")

    if support_level in ["medium", "high"]:
        actions.append("increase_support")

    return actions