# Journal Entry Storage - Reference Guide

## Quick Lookup

**Q: Are journal entries stored in Firebase?**  
A: ✅ YES - In `diary_entries` collection

**Q: Is user_id attached to each entry?**  
A: ✅ YES - `entry_data["user_id"] = user_id`

**Q: Can users see each other's entries?**  
A: ✅ NO - Queries filter `.where("user_id", "==", user_id)`

**Q: What happens on subsequent logins?**  
A: ✅ User's full entry history is loaded from Firebase

**Q: Where is mood data stored?**  
A: ✅ `mood_history` collection with `user_id` field

**Q: Where is profile data stored?**  
A: ✅ `user_profiles` collection at document_id = user_id

**Q: How does Backboard connect to user?**  
A: ✅ `assistant_id = f"assistant_{user_id}"`

---

## Code References

### Entry Storage
```python
# Location: backend/db/queries.py, lines 16-37
def save_entry(user_id: str, text: str, embedding: List[float]) -> str:
    entry_data = {
        "user_id": user_id,        # ✅ User tied here
        "text": text,
        "embedding": embedding,
        "timestamp": datetime.utcnow(),
    }
    doc_ref = db.collection("diary_entries").add(entry_data)
    return doc_ref[1].id
```

**Called from:** `backend/api/diary.py`, line 70

### Entry Retrieval
```python
# Location: backend/db/queries.py, lines 69-89
def get_all_entries(user_id: str) -> List[Dict[str, Any]]:
    query = (
        db.collection("diary_entries")
        .where("user_id", "==", user_id)  # ✅ User filter
        .order_by("timestamp", direction="DESCENDING")
    )
    # Returns only this user's entries
```

**Called from:** `backend/api/diary.py`, line 64

### Mood Storage
```python
# Location: backend/db/queries.py, lines 109-135
def save_mood(user_id: str, mood: str, intensity: int) -> str:
    mood_data = {
        "user_id": user_id,  # ✅ User tied here
        "mood": mood,
        "intensity": intensity,
        "date": now.strftime("%Y-%m-%d"),
        "timestamp": now,
    }
    doc_ref = db.collection("mood_history").add(mood_data)
    return doc_ref[1].id
```

**Called from:** `backend/api/diary.py`, line 74

### Profile Storage
```python
# Location: backend/db/queries.py, lines 287-305
def store_user_long_term_memory(user_id: str, memory: Dict[str, Any]) -> str:
    memory_data = {
        **memory,
        "updated_at": datetime.utcnow(),
    }
    db.collection("user_profiles").document(user_id).set(
        memory_data, 
        merge=True
    )
    # ✅ Document ID = user_id (no separate field needed)
```

**Called from:** `backend/api/diary.py`, line 85

### Endpoint Authentication
```python
# Location: backend/api/diary.py, lines 58-59
@router.post("/journal-entry")
async def save_journal_entry(
    data: JournalEntryRequest, 
    user_id: str = Depends(get_current_user_id)  # ✅ From token
):
```

**Auth source:** `backend/api/auth.py` - `get_current_user_id()`

---

## Firebase Collections Schema

### Collection: `diary_entries`

```
Document Structure (auto-generated ID):
{
  "user_id": "user_123",
  "text": "Today I felt accomplished...",
  "embedding": [0.123, 0.456, ..., 0.789],
  "timestamp": Timestamp(2026-03-14, 10:30:00)
}

Indexes:
- user_id (for filtering per user)
- timestamp (for ordering)
```

**Query Example:**
```python
db.collection("diary_entries")
  .where("user_id", "==", "user_123")
  .order_by("timestamp", direction="DESCENDING")
  .stream()
```

### Collection: `mood_history`

```
Document Structure (auto-generated ID):
{
  "user_id": "user_123",
  "mood": "happy",
  "intensity": 8,
  "note": "",
  "date": "2026-03-14",
  "timestamp": Timestamp(2026-03-14, 10:30:00)
}

Indexes:
- user_id (for filtering per user)
- date (for date-range queries)
```

**Query Example:**
```python
db.collection("mood_history")
  .where("user_id", "==", "user_123")
  .where("date", ">=", "2026-02-13")  # Last 30 days
  .order_by("date", direction="DESCENDING")
  .stream()
```

### Collection: `user_profiles`

```
Document Structure (ID = user_id):
Document ID: "user_123"
{
  "common_stressors": ["deadline stress", "perfectionism"],
  "recurring_emotions": ["anxiety", "overwhelm"],
  "helpful_strategies": ["meditation", "exercise"],
  "support_preferences": ["validation", "encouragement"],
  "recent_patterns": ["stress on Mondays"],
  "summary": "User is driven but needs self-compassion",
  "updated_at": Timestamp(2026-03-14, 10:30:00)
}
```

**Access Example:**
```python
db.collection("user_profiles")
  .document("user_123")  # ← Direct access using user_id
  .get()
```

---

## Data Flow: Step by Step

| Step | Function | Location | Input | Output |
|------|----------|----------|-------|--------|
| 0 | `get_current_user_id()` | auth.py | JWT token | user_id |
| 1 | `generate_embedding()` | embedding_service.py | entry text | 1536-dim vector |
| 2 | `get_all_entries()` | queries.py | user_id | [entries] |
| 3 | `find_similar_entries()` | similarity_search.py | embedding, [entries] | [(score, entry)] |
| 4 | `run_agent_loop()` | agent.py | entry, assistant_id | AgentResult |
| 5 | `save_entry()` | queries.py | **user_id**, text, embedding | entry_id ✅ |
| 6 | `save_mood()` | queries.py | **user_id**, mood, intensity | mood_id ✅ |
| 7 | `store_user_long_term_memory()` | queries.py | **user_id**, profile | user_id ✅ |
| 8 | `update_user_activity()` | queries.py | **user_id** | - |
| 9 | `_schedule_notifications()` | notification_scheduler.py | **user_id**, ... | - |
| 10 | Return response | diary.py | response data | JSON ✅ |

**✅ = Uses user_id to maintain isolation**

---

## Multi-User Safety Verification

### Scenario: User A tries to see User B's entries

```python
# User A's request
user_id = "user_A"  # From User A's token

# Backend executes:
db.collection("diary_entries")
  .where("user_id", "==", "user_A")  # ← Filters for user_A only
  .stream()

# Result: Only User A's entries returned
# User B's entries are never retrieved
```

### Scenario: Database contains mixed user data

```
diary_entries collection:
├─ doc1: {user_id: "user_A", text: "A's entry"}
├─ doc2: {user_id: "user_B", text: "B's entry"}
├─ doc3: {user_id: "user_A", text: "A's other entry"}
└─ doc4: {user_id: "user_C", text: "C's entry"}

Query: .where("user_id", "==", "user_A")
Returns: doc1, doc3 only
Never: doc2, doc4
```

✅ **Automatic isolation maintained by queries**

---

## Backboard Integration

### User-Specific Assistant

```python
# backend/api/diary.py, line 63
assistant_id = f"assistant_{user_id}"

# Results in assistants named:
# - assistant_user_123
# - assistant_user_456
# - etc.

# Each user's Backboard memory is separate
load_user_profile(f"assistant_{user_id}")
store_profile_update(f"assistant_{user_id}", profile)
```

---

## Session Continuity Example

### Day 1 (March 14)

```python
user_id = "user_alice"

# Save entry
save_entry("user_alice", "I feel great!", embedding1)
save_mood("user_alice", "happy", 8)
store_user_long_term_memory("user_alice", {
    "common_stressors": [],
    "recurring_emotions": ["happiness"],
    ...
})
```

**Firebase State:**
```
diary_entries:
  - doc1: {user_id: "user_alice", text: "I feel great!", ...}

mood_history:
  - doc1: {user_id: "user_alice", mood: "happy", ...}

user_profiles:
  - user_alice: {recurring_emotions: ["happiness"], ...}
```

### Day 7 (March 21 - Same User Returns)

```python
user_id = "user_alice"  # Same user_id from token

# Load history
entries = get_all_entries("user_alice")  # ← Gets Day 1 entries!
moods = get_user_mood_history("user_alice")  # ← Gets Day 1 mood!
profile = get_user_long_term_memory("user_alice")  # ← Gets Day 1 profile!

# All data available for context
```

**AI Response:** References Day 1 conversation because profile was loaded

✅ **Full continuity**

---

## Troubleshooting

### "User can't see their entries"
1. Check user_id is extracted correctly from token
2. Verify Firebase query includes `.where("user_id", "==", user_id)`
3. Confirm entries were saved with correct user_id

### "User sees another user's data"
1. Check if query filter is missing `.where("user_id", "==", user_id)`
2. Verify user_id is unique per user (from JWT)
3. Check Firebase composite indexes

### "Profile not updating"
1. Verify `store_user_long_term_memory()` is called after agent loop
2. Check document ID = user_id (not a field name)
3. Verify user_profiles collection exists

---

## Summary Table

| Aspect | Status | Details |
|--------|--------|---------|
| **Entry Storage** | ✅ Implemented | Firebase diary_entries with user_id |
| **User Isolation** | ✅ Enforced | Queries filter by user_id |
| **Mood Tracking** | ✅ Implemented | Firebase mood_history with user_id |
| **Profile Storage** | ✅ Implemented | Firebase user_profiles at user_id |
| **Backboard Integration** | ✅ Implemented | Assistant per user |
| **Session Continuity** | ✅ Working | Full history loaded per user |
| **Multi-User Safety** | ✅ Verified | No cross-user data leakage |
| **Authentication** | ✅ Enforced | JWT token → user_id extraction |

---

## Documentation Files

- `JOURNAL_STORAGE_SUMMARY.md` - Quick overview
- `JOURNAL_STORAGE_VERIFICATION.md` - Detailed code walkthrough
- `JOURNAL_STORAGE_DIAGRAM.md` - Visual data flow
- This file - Reference lookup

---

**Last Updated:** March 14, 2026
