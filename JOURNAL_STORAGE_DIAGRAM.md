# Journal Entry Storage Flow Diagram

## Complete Data Journey: User Submits Entry

```
┌─────────────────────────────────────────────────────────────────┐
│                    User Submits Journal Entry                   │
│                   (via /api/journal-entry)                      │
│                                                                  │
│  Body: {                                                         │
│    "prompt": "How was your day?",                               │
│    "entry": "Today was amazing. I felt accomplished."           │
│  }                                                               │
│  Header: Authorization: Bearer {token}                          │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                    Step 0: Extract user_id from token
                                 │
                                 ▼
┌────────────────────────────────────────────────────────────────┐
│  get_current_user_id()  ← from backend/api/auth.py             │
│  Extracts user_id from JWT token                               │
│  Result: user_id = "user_123"                                  │
└────────────────────────┬───────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────────┐
│  Step 1: Generate Embedding                                     │
│  generate_embedding(entry_text)                                │
│  Model: text-embedding-3-small                                │
│  Result: embedding = [0.123, 0.456, ..., 0.789]  (1536 dims)  │
└────────────────────────────┬───────────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────────┐
│  Step 2: Load All Past Entries (for this user)                 │
│  get_all_entries(user_id="user_123")                           │
│                                                                 │
│  Firebase Query:                                               │
│  db.collection("diary_entries")                               │
│    .where("user_id", "==", "user_123")  ← USER_ID FILTER     │
│    .order_by("timestamp", DESCENDING)                         │
│                                                                 │
│  Result: [{entry1}, {entry2}, {entry3}, ...]                 │
└────────────────────────────┬───────────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────────┐
│  Step 3: Find Similar Entries                                   │
│  find_similar_entries(new_embedding, past_entries, top_k=3)   │
│  (Cosine similarity across all user's entries)                 │
│  Result: [(similarity_score, entry), ...]                      │
└────────────────────────────┬───────────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────────┐
│  Step 4: Run Agent Loop                                         │
│  run_agent_loop(                                                │
│    diary_entry=entry_text,                                     │
│    assistant_id=f"assistant_{user_id}",  ← USER-SPECIFIC     │
│    recent_entries=similar_entries                              │
│  )                                                              │
│                                                                 │
│  Inside Agent:                                                  │
│    - Analyze mood                                               │
│    - Load user profile from Backboard                           │
│    - Generate reflective response                               │
│    - Update user profile memory                                 │
│                                                                 │
│  Result: AgentResult {                                         │
│    mood: {emotion, intensity, risk},                           │
│    response: {text},                                           │
│    updated_profile: {stressors, emotions, ...},                │
│    safety_flag: bool                                           │
│  }                                                              │
└────────────────────────────┬───────────────────────────────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
          ▼                  ▼                  ▼
    ┌─────────────┐  ┌─────────────┐  ┌──────────────────┐
    │ Step 5:     │  │ Step 6:     │  │ Step 7:          │
    │ Save Entry  │  │ Save Mood   │  │ Store Profile    │
    └────┬────────┘  └────┬────────┘  └────┬─────────────┘
         │                │                 │
         ▼                ▼                 ▼
    Firebase             Firebase         Firebase
    diary_entries        mood_history    user_profiles
    ───────────────────────────────────────────────────
    {                    {               {user_id: {
      user_id: "user_123",user_id:       common_stressors: [..],
      text: "...",       "user_123",     recurring_emotions: [..],
      embedding: [...],  mood: "happy",  helpful_strategies: [..],
      timestamp: 2026... intensity: 8,   support_preferences: [..],
    }                    date: "2026...", recent_patterns: [..],
                         timestamp: ...  summary: "...",
                       }                 updated_at: 2026...
                                       }

         ✅                ✅                 ✅
    Entry Stored      Mood Stored      Profile Stored
    (With user_id)    (With user_id)   (At user_id)
         │                │                 │
         └──────────────────┼──────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────────────┐
│  Step 8: Update User Activity                                   │
│  update_user_activity(user_id="user_123")                      │
│  (For tracking active users and streaks)                        │
└────────────────────────────┬───────────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────────┐
│  Step 9: Schedule Notifications                                │
│  _schedule_notifications(user_id, mood, entry_text)            │
│  (For follow-up messages, crisis support, etc.)               │
└────────────────────────────┬───────────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────────┐
│  Step 10: Return Response to User                              │
│                                                                 │
│  Response: {                                                   │
│    "success": true,                                            │
│    "entry_id": "doc_xyz",                                      │
│    "mood_id": "mood_abc",                                      │
│    "mood": {emotion, intensity, risk},                         │
│    "response": {reply, suggestion, question},                  │
│    "similar_entries": [{...}, {...}, {...}],                   │
│    "messages": {                                               │
│      "entry": "✓ Entry saved to Firestore",                    │
│      "mood": "✓ Mood detected and saved",                      │
│      "profile": "✓ Profile updated to Backboard",              │
│      ...                                                       │
│    }                                                           │
│  }                                                              │
└────────────────────────────────────────────────────────────────┘
```

---

## User ID Isolation Throughout

```
Multiple Users:

User A (user_123)          User B (user_456)
       │                          │
       │ Submits entry            │ Submits entry
       │                          │
       ▼                          ▼
    save_entry(              save_entry(
      user_id="user_123",      user_id="user_456",
      text="...",              text="...",
      embedding=[...]          embedding=[...]
    )                        )
       │                          │
       ▼                          ▼
    ┌──────────────────────────────────────┐
    │  Firebase diary_entries Collection   │
    │                                      │
    │  Doc1: {                             │
    │    user_id: "user_123",  ← Filter   │
    │    text: "User A's entry",           │
    │    embedding: [A_embedding]          │
    │  }                                   │
    │                                      │
    │  Doc2: {                             │
    │    user_id: "user_456",  ← Filter   │
    │    text: "User B's entry",           │
    │    embedding: [B_embedding]          │
    │  }                                   │
    └──────────────────────────────────────┘
         │                    │
    Query:                Query:
    .where("user_id",  .where("user_id",
      "==",              "==",
      "user_123")        "user_456")
         │                    │
         ▼                    ▼
    Returns: Doc1 only   Returns: Doc2 only
    ✅ No leakage        ✅ No leakage
```

---

## Data Security: Field vs Document ID

### Entry Data: Field-Based Filtering
```
Collection: diary_entries

Query:
db.collection("diary_entries")
  .where("user_id", "==", user_id)  ← Filter by field value
  
Returns: Only documents with matching user_id field
```

### Profile Data: Document ID Based
```
Collection: user_profiles

Access:
db.collection("user_profiles")
  .document(user_id)  ← user_id IS the document ID
  .set(data, merge=true)
  
Only this user can access their document
```

---

## Storage Verification Checklist

```
For Each Journal Entry Submission:

✅ User ID Extracted
   └─ from JWT token via get_current_user_id()

✅ Entry Text Stored
   └─ Firebase diary_entries collection
   └─ with user_id field

✅ Embedding Generated & Stored
   └─ 1536-dimensional vector
   └─ with user_id field

✅ Timestamp Recorded
   └─ UTC datetime
   └─ with user_id field

✅ Mood Analyzed & Stored
   └─ Firebase mood_history collection
   └─ with user_id field

✅ Profile Updated & Stored
   └─ Firebase user_profiles document
   └─ document ID = user_id

✅ Backboard Memory Updated
   └─ assistant_id = f"assistant_{user_id}"
   └─ User-specific assistant

✅ Activity Recorded
   └─ For streak tracking

✅ Notifications Scheduled
   └─ For user-specific follow-ups

✅ Response Returned to User
   └─ With entry_id, mood_id, and feedback
```

---

## Cross-Session Continuity

```
Day 1:
User logs in (user_123)
  → get_all_entries("user_123")  ← Gets Day 1 entries
  → get_user_mood_history("user_123")  ← Gets Day 1 moods
  → get_user_long_term_memory("user_123")  ← Gets profile
  → Submits new entry
  → save_entry("user_123", text, embedding)
  → save_mood("user_123", mood, intensity)
  → store_user_long_term_memory("user_123", profile)

Day 7 (User Returns):
User logs in (user_123)  ← Same user_id
  → get_all_entries("user_123")  ← Gets ALL entries (including Day 1!)
  → get_user_mood_history("user_123")  ← Gets mood history
  → get_user_long_term_memory("user_123")  ← Gets accumulated profile
  → AI uses past data for context
  → Submit new entry
  → save_entry("user_123", new_text, new_embedding)

✅ Full continuity across sessions
✅ No data loss
✅ User isolation maintained
```

---

## Summary

```
Every journal entry:
  ✅ Includes user_id in storage
  ✅ Is queried by user_id
  ✅ Cannot be accessed by other users
  ✅ Persists across sessions
  ✅ Integrates with Backboard for long-term memory
  ✅ Links to mood history
  ✅ Updates user profile
  ✅ Maintains complete audit trail
```

---

See `JOURNAL_STORAGE_VERIFICATION.md` for detailed code references.
