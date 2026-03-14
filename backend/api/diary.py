import asyncio
from fastapi import APIRouter
from pydantic import BaseModel

from backend.ai.agent import run_agent_loop
from backend.db.queries import (
    save_entry,
    get_all_entries,
    save_mood,
    store_user_long_term_memory,
    get_user_long_term_memory,
)
from backend.embeddings.embedding_service import generate_embedding
from backend.embeddings.similarity_search import find_similar_entries

router = APIRouter()


class JournalEntryRequest(BaseModel):
    user_id: str
    prompt: str
    entry: str


@router.post("/journal-entry")
async def save_journal_entry(data: JournalEntryRequest):
    print("Step 1: generating embedding")
    new_embedding = generate_embedding(data.entry)

    print("Step 2: loading all past entries")
    all_entries = get_all_entries(data.user_id)

    print("Step 3: finding similar past entries")
    similar_results = find_similar_entries(new_embedding, all_entries, top_k=3)
    similar_entries = [entry for _, entry in similar_results]

    print("Step 4: running agent loop")
    # Use a mock assistant_id based on user_id for now
    # In full implementation with auth, this would come from user profile
    assistant_id = f"assistant_{data.user_id}"
    
    agent_result = await run_agent_loop(
        diary_entry=data.entry,
        assistant_id=assistant_id,
        recent_entries=similar_entries,
    )

    print("Step 5: saving journal entry to Firebase")
    entry_id = save_entry(
        user_id=data.user_id,
        text=data.entry,
        embedding=new_embedding,
    )

    print("Step 6: saving mood to Firebase")
    mood_id = save_mood(
        user_id=data.user_id,
        mood=agent_result.mood.emotion,
        intensity=max(1, min(10, round(agent_result.mood.intensity * 10))),
    )

    print("Step 7: storing updated user profile to Firebase")
    store_user_long_term_memory(
        user_id=data.user_id,
        memory=agent_result.updated_profile.model_dump(),
    )

    print("Step 8: building final payload")
    return {
        "success": True,
        "entry_id": entry_id,
        "mood_id": mood_id,
        "message": "Journal entry saved",
        "prompt": data.prompt,
        "support_level": decide_support_level(agent_result.mood),
        "mood": agent_result.mood.model_dump(),
        "response": agent_result.response.model_dump(),
        "updated_profile": agent_result.updated_profile.model_dump(),
        "safety_flag": agent_result.safety_flag,
        "agent_actions": build_agent_actions(agent_result.mood, decide_support_level(agent_result.mood)),
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
        "run_agent_loop",
        "save_entry",
        "save_mood",
        "store_user_long_term_memory",
    ]

    if mood_result.needs_followup:
        actions.append("flag_followup")

    if support_level in ["medium", "high"]:
        actions.append("increase_support")

    return actions