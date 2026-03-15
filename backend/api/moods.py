"""
Mood tracking endpoints for mood check-ins and history.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from backend.api.auth import get_current_user_id
from backend.db.queries import (
    save_mood,
    get_user_mood_history,
    update_user_activity,
)

router = APIRouter()


class MoodEntryRequest(BaseModel):
    """Request body for mood check-in"""
    mood: str
    intensity: int = 5  # 1-10 scale
    note: Optional[str] = None


class MoodEntryResponse(BaseModel):
    """Response after saving mood"""
    success: bool
    mood_id: str
    message: str


@router.post("/mood-entry", response_model=MoodEntryResponse)
def save_mood_entry(
    data: MoodEntryRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Save a mood check-in for the current user.
    
    - Requires authentication (token in Authorization header)
    - Records mood, intensity, and optional note
    - Updates user's last_active timestamp
    
    Args:
        data: Mood check-in request with mood, intensity, optional note
        user_id: Authenticated user ID from token
        
    Returns:
        MoodEntryResponse with success status and mood_id
    """
    try:
        # Validate intensity is in range
        intensity = max(1, min(10, data.intensity))
        
        # Save to Firestore
        mood_id = save_mood(
            user_id=user_id,
            mood=data.mood,
            intensity=intensity,
            note=data.note or ""
        )
        
        # Update user activity
        update_user_activity(user_id)
        
        return MoodEntryResponse(
            success=True,
            mood_id=mood_id,
            message="Mood check-in saved successfully"
        )
    
    except Exception as e:
        return MoodEntryResponse(
            success=False,
            mood_id="",
            message=f"Error saving mood: {str(e)}"
        )


@router.get("/moods/{user_id}")
def get_mood_history(
    user_id: str,
    days: int = 30,
    current_user: str = Depends(get_current_user_id)
):
    """
    Get mood history for a user.
    Requires authentication - users can only access their own moods.
    
    Args:
        user_id: User ID (from URL)
        days: Number of days to retrieve (default: 30)
        current_user: Authenticated user ID (from token)
        
    Returns:
        List of mood entries with dates and intensity
    """
    from fastapi import HTTPException
    
    # Verify user is requesting their own data
    if current_user != user_id:
        raise HTTPException(status_code=403, detail="Cannot access other users' moods")
    
    moods = get_user_mood_history(user_id, days=days)
    
    return {
        "user_id": user_id,
        "moods": moods,
        "count": len(moods),
        "period_days": days
    }
