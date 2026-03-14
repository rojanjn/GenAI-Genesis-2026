# Quick Reference: What Changed

## Files Modified (4)

### 1. `backend/db/queries.py` — NEW FUNCTIONS
```python
# Analytics Functions (NEW)
get_user_mood_history(user_id, days=30)      # List[Dict]
get_user_mood_average(user_id, days=30)      # float
get_entry_count(user_id)                     # int
get_check_in_streak(user_id)                 # int

# Profile Storage (NEW)
store_user_long_term_memory(user_id, memory) # str (user_id)
get_user_long_term_memory(user_id)           # Dict | None
```

### 2. `backend/api/diary.py` — AGENT LOOP INTEGRATION
```python
# CHANGED: Now async
async def save_journal_entry(data: JournalEntryRequest):
    
    # CHANGED: Uses run_agent_loop instead of manual orchestration
    agent_result = await run_agent_loop(
        diary_entry=data.entry,
        assistant_id=f"assistant_{data.user_id}",
        recent_entries=similar_entries,
    )
    
    # NEW: Store profile after agent loop
    store_user_long_term_memory(data.user_id, agent_result.updated_profile)
    
    # CHANGED: Response now includes updated_profile and safety_flag
    return {
        "updated_profile": agent_result.updated_profile.model_dump(),
        "safety_flag": agent_result.safety_flag,
        ...
    }
```

### 3. `backend/api/insights.py` — REAL DATA QUERIES
```python
# CHANGED: No more mock data
def get_progress(user_id: str):
    mood_average = get_user_mood_average(user_id, days=30)
    check_in_streak = get_check_in_streak(user_id)
    journal_entries = len(get_user_mood_history(user_id, days=365))
    
    return {
        "check_in_streak": check_in_streak,      # Real data
        "sessions_done": sessions_done,          # Real data
        "journal_entries": journal_entries,      # Real data
        "mood_average": mood_average,            # Real data
        "mood_average_change": mood_change,      # Real calculation
        "recent_mood_history": [...]             # Real data
    }
```

### 4. `.github/copilot-instructions.md` — UPDATED DOCS
- Architecture overview updated
- Agent loop integration documented
- New database functions listed
- Workflow examples updated

---

## API Endpoint Changes

### POST `/api/journal-entry`
**NEW Response Fields**:
```json
{
  "updated_profile": {
    "common_stressors": [...],
    "recurring_emotions": [...],
    ...
  },
  "safety_flag": true|false
}
```

### GET `/api/progress/{user_id}`
**CHANGED**: Now returns real data from Firestore
```json
{
  "user_id": "user123",
  "check_in_streak": 5,          // Real
  "sessions_done": 42,           // Real
  "journal_entries": 42,         // Real
  "mood_average": 7.2,           // Real
  "mood_average_change": "up",   // Real
  "recent_mood_history": [...]   // Real
}
```

---

## Import Changes for Developers

### If you're working on `backend/api/`:
```python
# OLD (if you were doing analytics)
# Had to calculate manually or return mock

# NEW (now available)
from backend.db.queries import (
    get_user_mood_history,
    get_user_mood_average,
    get_entry_count,
    get_check_in_streak,
    store_user_long_term_memory,
    get_user_long_term_memory,
)
```

### If you're working on `backend/ai/`:
```python
# Your agent.py is now being used!
# Make sure it's tested with:
# - Backboard API key set (if using external memory)
# - Recent entries passed correctly
# - Safety flags working as expected
```

---

## Database Collection Updates

### NEW: `user_profiles` Collection
Now actively used after every journal entry:
```
user_profiles/{user_id}
├── common_stressors: [...]
├── recurring_emotions: [...]
├── helpful_strategies: [...]
├── support_preferences: [...]
├── recent_patterns: [...]
├── summary: "..."
└── updated_at: datetime
```

### ENHANCED: `mood_history` Collection
New queries support analytics:
- Date range filtering
- Aggregation/averaging
- Streak calculation

### UNCHANGED: `diary_entries` Collection
Same structure, but now queried for similarity + analytics

---

## Testing Changes

### OLD Test Command
```bash
python3 backend/db/queries.py
```

### NEW Test Command
```bash
python -m backend.db.queries
```
(Better for relative imports)

### New Endpoints to Test
```bash
# Test dashboard
curl http://localhost:8000/api/progress/user123

# Test journal entry (now async)
curl -X POST http://localhost:8000/api/journal-entry \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user123","prompt":"...","entry":"..."}'
```

---

## Key Architectural Change

### Before: Orphaned Agent Loop
```
diary.py ──manual─→ analyse_mood()
                    generate_response()
                    ❌ run_agent_loop() unused
                    
insights.py ──mock→ hardcoded data
```

### After: Integrated Pipeline
```
diary.py ──→ run_agent_loop() ──→ Save entry + mood + profile
                (orchestrates)    (complete workflow)
                
insights.py ──real queries→ Firestore ──→ Real analytics
```

---

## Migration Checklist for Code Review

- [ ] **diary.py**: Changed from sync to async function
- [ ] **diary.py**: Now uses `run_agent_loop()` instead of manual steps
- [ ] **diary.py**: Calls `store_user_long_term_memory()` after agent loop
- [ ] **insights.py**: Removed mock data, added real queries
- [ ] **insights.py**: Now queries 4 analytics functions
- [ ] **queries.py**: Added 6 new functions for analytics + profile storage
- [ ] **queries.py**: Uses Firestore `user_profiles` collection
- [ ] **queries.py**: Handles date range queries for analytics
- [ ] **.github/copilot-instructions.md**: Updated with new architecture

---

## Next Steps for Team

### Frontend Team
- Endpoint `/api/journal-entry` is now async (no change to how you call it)
- Response now includes `updated_profile` and `safety_flag`
- Dashboard endpoint `/api/progress/{user_id}` now returns real data

### Backend Team (Adding Auth)
- User profiles are persisted in `user_profiles` collection
- Use `get_user_long_term_memory(user_id)` to load user context
- Map Firebase `uid` to Backboard `assistant_id` in users collection

### DevOps Team
- Firestore indexes needed for `mood_history` date range queries
- Consider caching user profiles (TTL strategy)
- Monitor agent loop performance (async may need tuning)

---

## Important Notes

⚠️ **diary.py is now ASYNC**
- If you import `save_journal_entry()` directly, use `await`
- FastAPI handles this automatically in routes

⚠️ **Backboard Optional**
- If `BACKBOARD_API_KEY` is not set, agent loop will fail
- Set it in your `.env` or pass as environment variable
- Or use Firestore-only mode (future optimization)

✅ **Backwards Compatible**
- Existing database queries still work
- Old entry structure unchanged
- Only additions, no breaking changes

---

## Questions?

Check:
1. `IMPLEMENTATION_SUMMARY.md` — Detailed changelog
2. `IMPLEMENTATION_STATUS.md` — Visual diagrams
3. `.github/copilot-instructions.md` — Architecture docs
4. `SETUP.md` — Environment setup (includes Backboard)
