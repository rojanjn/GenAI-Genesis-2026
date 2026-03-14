from fastapi import APIRouter

router = APIRouter()

@router.get("/progress/{user_id}")
def get_progress(user_id: str):
    """
    Returns basic stats for the dashboard.
    Later this will pull from Firebase.
    """

    return {
        "check_in_streak": 2,
        "sessions_done": 5,
        "journal_entries": 5,
        "mood_average": 7.2,
        "mood_average_change": "up this week"
    }