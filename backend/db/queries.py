"""
Database Queries Module

Provides high-level database operations for the journaling application.
Abstracts Firestore interactions for saving entries, retrieving data, and managing moods.

Role in system:
- CRUD operations for diary entries
- User mood history tracking
- Notification management
- Direct abstraction over Firestore collections
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from .firebase_client import get_db   


def save_entry(user_id: str, text: str, embedding: List[float]) -> str:
    """
    Save a new diary entry to Firestore.
    
    Args:
        user_id: Unique user identifier
        text: Journal entry text content
        embedding: Vector embedding from OpenAI
        
    Returns:
        entry_id: Auto-generated document ID
    """
    db = get_db()
    
    entry_data = {
        "user_id": user_id,
        "text": text,
        "embedding": embedding,
        "timestamp": datetime.utcnow(),
    }
    
    doc_ref = db.collection("diary_entries").add(entry_data)
    entry_id = doc_ref[1].id
    
    return entry_id


def get_recent_entries(user_id: str, limit: int = 3) -> List[Dict[str, Any]]:
    """
    Retrieve most recent diary entries for a user.
    
    Args:
        user_id: Unique user identifier
        limit: Maximum number of entries to return
        
    Returns:
        List of entry dictionaries with full data
    """
    db = get_db()
    
    query = (
        db.collection("diary_entries")
        .where("user_id", "==", user_id)
        .order_by("timestamp", direction="DESCENDING")
        .limit(limit)
    )
    
    docs = query.stream()
    entries = []
    
    for doc in docs:
        entry = doc.to_dict()
        entry["entry_id"] = doc.id
        entries.append(entry)
    
    return entries


def get_all_entries(user_id: str) -> List[Dict[str, Any]]:
    """
    Retrieve all diary entries for a user.
    
    Used for embedding-based similarity search across user's entire history.
    
    Args:
        user_id: Unique user identifier
        
    Returns:
        List of all entry dictionaries for the user
    """
    db = get_db()
    
    query = (
        db.collection("diary_entries")
        .where("user_id", "==", user_id)
        .order_by("timestamp", direction="DESCENDING")
    )
    
    docs = query.stream()
    entries = []
    
    for doc in docs:
        entry = doc.to_dict()
        entry["entry_id"] = doc.id
        entries.append(entry)
    
    return entries


def save_mood(user_id: str, mood: str, intensity: int) -> str:
    """
    Save a mood record for a user.
    """
    db = get_db()

    now = datetime.utcnow()

    mood_data = {
        "user_id": user_id,
        "mood": mood,
        "intensity": intensity,
        "date": now.strftime("%Y-%m-%d"),
        "timestamp": now,
    }

    doc_ref = db.collection("mood_history").add(mood_data)
    mood_id = doc_ref[1].id

    return mood_id

def save_notification(
    user_id: str, notification_type: str, message: str, scheduled_time: datetime
) -> str:
    """
    Create a notification for a user.
    
    Args:
        user_id: Unique user identifier
        notification_type: Type of notification (e.g., "reminder", "suggestion")
        message: Notification message content
        scheduled_time: When the notification should be sent
        
    Returns:
        notification_id: Auto-generated document ID
    """
    db = get_db()
    
    notification_data = {
        "user_id": user_id,
        "type": notification_type,
        "message": message,
        "scheduled_time": scheduled_time,
        "sent": False,
        "created_at": datetime.utcnow(),
    }
    
    doc_ref = db.collection("notifications").add(notification_data)
    notification_id = doc_ref[1].id
    
    return notification_id


def get_user_mood_history(user_id: str, days: int = 30) -> List[Dict[str, Any]]:
    """
    Retrieve mood history for a user over the last N days.
    
    Args:
        user_id: Unique user identifier
        days: Number of days to retrieve (default: 30)
        
    Returns:
        List of mood history records sorted by date descending
    """
    db = get_db()
    
    cutoff_date = (datetime.utcnow() - __import__('datetime').timedelta(days=days)).strftime("%Y-%m-%d")
    
    query = (
        db.collection("mood_history")
        .where("user_id", "==", user_id)
        .where("date", ">=", cutoff_date)
        .order_by("date", direction="DESCENDING")
    )
    
    docs = query.stream()
    moods = []
    
    for doc in docs:
        mood = doc.to_dict()
        mood["mood_id"] = doc.id
        moods.append(mood)
    
    return moods


def get_user_mood_average(user_id: str, days: int = 30) -> float:
    """
    Calculate average mood intensity for a user over the last N days.
    
    Args:
        user_id: Unique user identifier
        days: Number of days to average (default: 30)
        
    Returns:
        Average intensity as float, or 0.0 if no moods recorded
    """
    moods = get_user_mood_history(user_id, days=days)
    
    if not moods:
        return 0.0
    
    total_intensity = sum(mood.get("intensity", 0) for mood in moods)
    return total_intensity / len(moods)


def get_entry_count(user_id: str) -> int:
    """
    Get total number of diary entries for a user.
    
    Args:
        user_id: Unique user identifier
        
    Returns:
        Count of entries
    """
    db = get_db()
    
    query = db.collection("diary_entries").where("user_id", "==", user_id)
    return len(list(query.stream()))


def get_check_in_streak(user_id: str) -> int:
    """
    Calculate consecutive days of journal entries (check-in streak).
    
    Args:
        user_id: Unique user identifier
        
    Returns:
        Number of consecutive recent days with entries
    """
    moods = get_user_mood_history(user_id, days=30)
    
    if not moods:
        return 0
    
    # Extract unique dates and sort in reverse
    dates_set = set()
    for mood in moods:
        date_str = mood.get("date")
        if date_str:
            dates_set.add(date_str)
    
    sorted_dates = sorted(list(dates_set), reverse=True)
    
    if not sorted_dates:
        return 0
    
    streak = 1
    today_date = datetime.utcnow().strftime("%Y-%m-%d")
    
    # Check if streak started today or yesterday
    if sorted_dates[0] != today_date and sorted_dates[0] != (datetime.utcnow() - __import__('datetime').timedelta(days=1)).strftime("%Y-%m-%d"):
        return 0
    
    # Count consecutive days
    for i in range(len(sorted_dates) - 1):
        current = datetime.strptime(sorted_dates[i], "%Y-%m-%d")
        next_day = datetime.strptime(sorted_dates[i + 1], "%Y-%m-%d")
        
        if (current - next_day).days == 1:
            streak += 1
        else:
            break
    
    return streak


def store_user_long_term_memory(user_id: str, memory: Dict[str, Any]) -> str:
    """
    Store or update user's long-term profile memory.
    
    Args:
        user_id: Unique user identifier
        memory: UserProfileMemory as dict (from model_dump())
        
    Returns:
        user_id if successful
    """
    db = get_db()
    
    memory_data = {
        **memory,
        "updated_at": datetime.utcnow(),
    }
    
    db.collection("user_profiles").document(user_id).set(memory_data, merge=True)
    
    return user_id


def get_user_long_term_memory(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve user's stored long-term profile memory.
    
    Args:
        user_id: Unique user identifier
        
    Returns:
        User profile memory dict, or None if not yet created
    """
    db = get_db()
    
    doc = db.collection("user_profiles").document(user_id).get()
    
    if doc.exists():
        return doc.to_dict()
    
    return None


if __name__ == "__main__":
    # Test database operations
    print("Database queries module loaded successfully")
    print("Available functions:")
    print("  - save_entry(user_id, text, embedding)")
    print("  - get_recent_entries(user_id, limit=3)")
    print("  - get_all_entries(user_id)")
    print("  - save_mood(user_id, mood, intensity)")
    print("  - save_notification(user_id, notification_type, message, scheduled_time)")
    print("  - get_user_mood_history(user_id, days=30)")
    print("  - get_user_mood_average(user_id, days=30)")
    print("  - get_entry_count(user_id)")
    print("  - get_check_in_streak(user_id)")
    print("  - store_user_long_term_memory(user_id, memory)")
    print("  - get_user_long_term_memory(user_id)")
