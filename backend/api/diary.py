from fastapi import APIRouter
from pydantic import BaseModel

from backend.ai.mood_analysis import analyse_mood
from backend.ai.response_generator import generate_reflective_response
from backend.db.queries import save_entry, get_all_entries, save_mood
from backend.embeddings.embedding_service import generate_embedding
from backend.embeddings.similarity_search import find_similar_entries

router = APIRouter()


class JournalEntryRequest(BaseModel):
    user_id: str
    prompt: str
    entry: str


@router.post("/journal-entry")
def save_journal_entry(data: JournalEntryRequest):
    print("Step 1: generating embedding")
    new_embedding = generate_embedding(data.entry)

    print("Step 2: loading all past entries")
    all_entries = get_all_entries(data.user_id)

    print("Step 3: finding similar past entries")
    similar_results = find_similar_entries(new_embedding, all_entries, top_k=3)
    similar_entries = [entry for _, entry in similar_results]

    print("Step 4: analysing mood")
    mood_result = analyse_mood(data.entry)

    print("Step 5: deciding support level")
    support_level = decide_support_level(mood_result)

    user_profile_memory = None

    print("Step 6: generating reflective response")
    ai_response = generate_reflective_response(
        today_entry=data.entry,
        recent_entries=similar_entries,
        user_profile_memory=user_profile_memory,
    )

    print("Step 7: saving journal entry to Firebase")
    entry_id = save_entry(
        user_id=data.user_id,
        text=data.entry,
        embedding=new_embedding,
    )

    print("Step 8: saving mood to Firebase")
    mood_id = save_mood(
        user_id=data.user_id,
        mood=mood_result.emotion,
        intensity=max(1, min(10, round(mood_result.intensity * 10))),
    )

    print("Step 9: building final payload")
    return {
        "success": True,
        "entry_id": entry_id,
        "mood_id": mood_id,
        "message": "Journal entry saved",
        "prompt": data.prompt,
        "support_level": support_level,
        "mood": mood_result.model_dump(),
        "response": ai_response.model_dump(),
        "agent_actions": build_agent_actions(mood_result, support_level),
        "similar_entries_used": len(similar_entries),
        "similarity_scores": [round(score, 3) for score, _ in similar_results],
    }


def decide_support_level(mood_result) -> str:
    if mood_result.risk_level == "high":
        return "high"
    if mood_result.intensity >= 0.75 or mood_result.needs_followup:
        return "medium"
    return "low"


def build_agent_actions(mood_result, support_level: str) -> list[str]:
    actions = [
        "generate_embedding",
        "find_similar_entries",
        "analyse_mood",
        "generate_reflective_response",
        "save_entry",
        "save_mood",
    ]

    if mood_result.needs_followup:
        actions.append("flag_followup")

    if support_level in ["medium", "high"]:
        actions.append("increase_support")

    return actions