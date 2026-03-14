from fastapi import APIRouter
from backend.db.queries import (
    get_user_mood_history,
    get_user_mood_average,
    get_entry_count,
    get_check_in_streak,
)

router = APIRouter()


@router.get("/progress/{user_id}")
def get_progress(user_id: str):
    """
    Returns comprehensive stats for the dashboard.
    Queries Firestore for real user data.
    
    Args:
        user_id: Unique user identifier
        
    Returns:
        Dictionary with user statistics and trends
    """
    
    # Get mood history for past 30 days
    mood_history = get_user_mood_history(user_id, days=30)
    
    # Calculate statistics
    check_in_streak = get_check_in_streak(user_id)
    sessions_done = get_entry_count(user_id)
    journal_entries = len(get_user_mood_history(user_id, days=365))  # All-time entries with mood
    mood_average = get_user_mood_average(user_id, days=30)
    
    # Calculate mood change (compare last week to previous week)
    mood_history_week1 = get_user_mood_average(user_id, days=7)
    mood_history_week2 = get_user_mood_average(user_id, days=14)
    
    if mood_history_week2 > 0:
        mood_change = "up this week" if mood_history_week1 > mood_history_week2 else "down this week"
    else:
        mood_change = "stable"
    
    return {
        "user_id": user_id,
        "check_in_streak": check_in_streak,
        "sessions_done": sessions_done,
        "journal_entries": journal_entries,
        "mood_average": round(mood_average, 1),
        "mood_average_change": mood_change,
        "recent_mood_history": [
            {
                "date": mood.get("date"),
                "mood": mood.get("mood"),
                "intensity": mood.get("intensity"),
            }
            for mood in mood_history[:7]  # Last 7 entries
        ],
    }