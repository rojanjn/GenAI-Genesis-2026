# Journal Entry Storage - Quick Summary

## TL;DR

✅ **YES - Journal entries ARE stored to Firebase with user IDs**

Every piece of data is properly saved and tied to the user who submitted it.

---

## What Gets Saved

| Data | Collection | Field | Stored With |
|------|-----------|-------|------------|
| Entry text | `diary_entries` | `text` | `user_id` ✅ |
| Embedding vector | `diary_entries` | `embedding` | `user_id` ✅ |
| Entry timestamp | `diary_entries` | `timestamp` | `user_id` ✅ |
| Mood emotion | `mood_history` | `mood` | `user_id` ✅ |
| Mood intensity | `mood_history` | `intensity` | `user_id` ✅ |
| Stressors | `user_profiles` | `common_stressors` | Document ID = `user_id` ✅ |
| Emotions | `user_profiles` | `recurring_emotions` | Document ID = `user_id` ✅ |
| Strategies | `user_profiles` | `helpful_strategies` | Document ID = `user_id` ✅ |
| Preferences | `user_profiles` | `support_preferences` | Document ID = `user_id` ✅ |
| Patterns | `user_profiles` | `recent_patterns` | Document ID = `user_id` ✅ |
| Summary | `user_profiles` | `summary` | Document ID = `user_id` ✅ |

---

## Complete Flow

```
User (token) → /api/journal-entry endpoint
  ↓
Extract user_id from token
  ↓
1. Generate embedding
2. Load user's past entries (filtered by user_id)
3. Find similar entries (vector search)
4. Run agent loop (mood analysis, profile update)
  ↓
5. save_entry(user_id, text, embedding)
   └─ Stored to Firebase diary_entries with user_id field
  ↓
6. save_mood(user_id, mood, intensity)
   └─ Stored to Firebase mood_history with user_id field
  ↓
7. store_user_long_term_memory(user_id, profile)
   └─ Stored to Firebase user_profiles at document id = user_id
  ↓
8. Update user activity tracking
  ↓
9. Schedule notifications
  ↓
Return response with entry_id, mood_id, feedback
```

---

## User Isolation Verification

**Query for entries:**
```python
db.collection("diary_entries")
  .where("user_id", "==", user_id)  # ← FILTERS by user_id
```

Only that user's entries are returned. No cross-user data leakage.

---

## Example: Two Users Same Day

**Firebase Result:**

| Document | user_id | text | timestamp |
|----------|---------|------|-----------|
| doc_abc | user_123 | "Great day!" | 2026-03-14T10:30Z |
| doc_xyz | user_456 | "Rough day" | 2026-03-14T10:45Z |

**When user_123 queries:**
- Gets: `doc_abc` only
- Cannot see: `doc_xyz`

**When user_456 queries:**
- Gets: `doc_xyz` only
- Cannot see: `doc_abc`

✅ **Complete isolation**

---

## Session Continuity

**Day 1:** User submits entry → saved with user_id
**Day 7:** User returns → queries using same user_id → gets ALL old entries

```
get_all_entries("user_123")
  → Returns entries from Day 1, Day 2, Day 3, ..., Day 7
  → Full history available
  → No data loss
```

---

## Security

- ✅ Each user only accesses their own data
- ✅ User ID comes from JWT token (not user input)
- ✅ Queries filter by user_id
- ✅ No way for user to see another user's data
- ✅ All timestamps recorded (audit trail)

---

## Files Involved

```
backend/api/diary.py
  ↓
save_entry(user_id, text, embedding)
save_mood(user_id, mood, intensity)
store_user_long_term_memory(user_id, profile)
  ↓
backend/db/queries.py
  ↓
Firebase (Firestore)
  ├─ diary_entries (with user_id field)
  ├─ mood_history (with user_id field)
  └─ user_profiles (with user_id as document ID)
```

---

## Verification

- Code: `backend/db/queries.py` lines 16-305
- Flow: `backend/api/diary.py` lines 58-90
- Each save includes user_id
- Each query filters by user_id
- No leakage between users

✅ **CONFIRMED: Properly implemented**

---

See detailed verification in:
- `JOURNAL_STORAGE_VERIFICATION.md` - Full code walkthrough
- `JOURNAL_STORAGE_DIAGRAM.md` - Visual data flow
