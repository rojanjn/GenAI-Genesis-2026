import asyncio
import logging
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend.ai.agent import run_agent_loop
from backend.api.auth import get_current_user_id
from backend.db.queries import (
    save_entry,
    get_all_entries,
    save_mood,
    store_user_long_term_memory,
    get_user_long_term_memory,
    update_user_activity,
    get_user_profile,
)
from backend.embeddings.embedding_service import generate_embedding
from backend.embeddings.similarity_search import find_similar_entries
from backend.services.notification_scheduler import get_notification_scheduler

from backend.ai.memory import get_or_create_assistant

logger = logging.getLogger(__name__)

router = APIRouter()


class JournalEntryRequest(BaseModel):
    prompt: str
    entry: str
    entry_text: str = None  # Plain text version for analysis


@router.post("/journal-entry")
async def save_journal_entry(data: JournalEntryRequest, user_id: str = Depends(get_current_user_id)):
    """
    Save a journal entry with AI analysis.
    
    - Requires authentication (token in Authorization header)
    - Generates embedding for semantic search
    - Finds similar past entries
    - Runs agent loop for mood analysis and response
    - Stores entry, mood, and updated profile to Firestore
    """
    print(f"Step 0: Processing entry for user {user_id}")
    print("Step 1: generating embedding")
    new_embedding = generate_embedding(data.entry)

    print("Step 2: loading all past entries")
    all_entries = get_all_entries(user_id)

    print("Step 3: finding similar past entries")

    similar_results = find_similar_entries(
        new_embedding=new_embedding,
        entries=all_entries,
        top_k=3,
    )

    similar_entries = [entry for score, entry in similar_results]

    print("Step 4: running agent loop")
    # Use assistant_id based on user_id
    assistant_id = await get_or_create_assistant(user_id)

    agent_result = await run_agent_loop(
        diary_entry=data.entry,
        assistant_id=assistant_id,
        recent_entries=similar_entries,
    )

    print("Step 5: saving journal entry to Firebase")
    entry_id = save_entry(
        user_id=user_id,
        text=data.entry,
        embedding=new_embedding,
    )

    print("Step 6: saving mood to Firebase")
    mood_id = save_mood(
        user_id=user_id,
        mood=agent_result.mood.emotion,
        intensity=max(1, min(10, round(agent_result.mood.intensity * 10))),
    )

    print("Step 7: storing updated user profile to Firebase")
    store_user_long_term_memory(
        user_id=user_id,
        memory=agent_result.updated_profile.model_dump(),
    )

    print("Step 8: updating user activity")
    update_user_activity(user_id)

    print("Step 9: scheduling follow-up notifications")
    await _schedule_notifications(user_id, agent_result.mood, data.entry)

    print("Step 10: building final payload")
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


async def _schedule_notifications(user_id: str, mood_result, entry_text: str):
    """
    Schedule follow-up notifications based on mood analysis.
    This is agentic - automatically triggered by mood patterns.
    """
    try:
        scheduler = get_notification_scheduler()
        user = get_user_profile(user_id)
        
        if not user:
            logger.warning(f"Cannot schedule notifications - user {user_id} not found")
            return
        
        # Schedule mood follow-up if needed
        if mood_result.needs_followup or mood_result.risk_level in ["medium", "high"]:
            message = _generate_followup_message(mood_result, entry_text)
            scheduler.schedule_mood_followup(
                user_id=user_id,
                mood=mood_result.emotion,
                intensity=mood_result.intensity,
                message=message
            )
            logger.info(f"✓ Scheduled mood follow-up for {user_id}")
        
        # Schedule streak reminder for next day
        # (This would typically be done daily, not after each entry)
        # scheduler.schedule_streak_reminder(user_id, streak_days=1)
        
    except Exception as e:
        logger.error(f"Error scheduling notifications: {str(e)}")


def _generate_followup_message(mood_result, entry_text: str) -> str:
    """
    Generate AI-informed follow-up message based on mood analysis.
    Could be enhanced to use OpenAI for personalized messages.
    """
    emotion = mood_result.emotion
    intensity = mood_result.intensity
    themes = getattr(mood_result, 'themes', [])
    
    if mood_result.risk_level == "high":
        return f"""We noticed you're experiencing some strong feelings around {emotion}. 
        Remember that seeking support from a trusted friend, family member, or mental health professional 
        can make a real difference. You're not alone in this."""
    
    elif intensity >= 0.75:
        base_msg = f"You shared some vulnerable thoughts about {emotion}. That takes courage."
        if themes:
            base_msg += f" We noticed themes around {', '.join(themes)}."
        base_msg += " Taking time to process these feelings is an important part of growth."
        return base_msg
    
    else:
        return f"Thank you for continuing to check in with yourself and reflect on your {emotion} state. " \
               "This practice of self-awareness is valuable and helps you understand yourself better."


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