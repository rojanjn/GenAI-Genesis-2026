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
    
    Args:
        user_id: Unique user identifier
        mood: Mood label (e.g., "happy", "sad", "anxious")
        intensity: Mood intensity on scale 1-10
        
    Returns:
        mood_record_id: Auto-generated document ID
    """
    db = get_db()
    
    mood_data = {
        "user_id": user_id,
        "mood": mood,
        "intensity": intensity,
        "date": datetime.utcnow().date(),
        "timestamp": datetime.utcnow(),
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


if __name__ == "__main__":
    # Test database operations
    print("Database queries module loaded successfully")
    print("Available functions:")
    print("  - save_entry(user_id, text, embedding)")
    print("  - get_recent_entries(user_id, limit=3)")
    print("  - get_all_entries(user_id)")
    print("  - save_mood(user_id, mood, intensity)")
    print("  - save_notification(user_id, notification_type, message, scheduled_time)")
