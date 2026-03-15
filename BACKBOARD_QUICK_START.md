# Backboard.io Quick Reference

## TL;DR - Use Backboard in 5 Minutes

### 1. Get API Key
- Sign up at [app.backboard.io](https://app.backboard.io)
- Settings → API Keys → Generate New Key
- Copy key (format: `espr_xxxxx`)

### 2. Add to `.env`
```bash
BACKBOARD_API_KEY=espr_YOUR_KEY_HERE
```

### 3. That's It! ✨
The code handles the rest:
- Automatic assistant creation per user
- Memory loading on chat start
- Memory persistence across sessions

---

## How to Use

### Send Chat Message (with Backboard memory)
```python
from backend.api.chat import router
# POST /api/chat/ with:
# {
#   "user_id": "user_123",
#   "message": "I feel anxious",
#   "chat_history": []
# }
# ↓ Backend automatically:
#   - Creates/retrieves assistant for user_123
#   - Loads stored memories from Backboard
#   - Uses memories in LLM context
#   - Returns personalized response
```

### Manual Operations
```python
from backend.ai.memory import (
    get_or_create_assistant,
    load_user_profile,
    store_profile_update,
)

# Create/get assistant
assistant_id = await get_or_create_assistant("user_123")

# Load memories
profile = await load_user_profile(assistant_id)
print(profile.common_stressors)      # ["work stress", "perfectionism"]
print(profile.recurring_emotions)    # ["anxiety", "overwhelm"]
print(profile.helpful_strategies)    # ["meditation", "journaling"]

# Update memories
updated_profile = UserProfileMemory(
    common_stressors=["work stress"],
    recurring_emotions=["anxiety"],
    helpful_strategies=["meditation"],
    support_preferences=["validation"],
    recent_patterns=["stress spikes on Mondays"],
    summary="User is driven but struggles with perfectionism"
)
await store_profile_update(assistant_id, updated_profile)
```

---

## Memory Tags
```python
TAG_STRESSOR        = "stressor"        # What stresses user
TAG_EMOTION         = "emotion"         # Feelings user experiences
TAG_STRATEGY        = "strategy"        # What helps user
TAG_SUPPORT_STYLE   = "support_style"   # How to support user
TAG_PATTERN         = "pattern"         # User's patterns
TAG_SESSION_SUMMARY = "session_summary" # Session summaries
```

---

## Architecture
```
Chat Request
    ↓
get_or_create_assistant()  ← Gets unique assistant for user
    ↓
load_user_profile()        ← Fetches stored memories from Backboard
    ↓
[LLM processes with memory context]
    ↓
Generate Response           ← Personalized because of memories
    ↓
(Optional) store_profile_update()  ← Save new insights for next session
```

---

## Debug

### Check Memory Loaded
```python
import asyncio
from backend.ai.memory import get_or_create_assistant, load_user_profile

async def check():
    asst_id = await get_or_create_assistant("test_user")
    profile = await load_user_profile(asst_id)
    print("Stressors:", profile.common_stressors)
    print("Emotions:", profile.recurring_emotions)

asyncio.run(check())
```

### View in Backboard Dashboard
1. Log into [app.backboard.io](https://app.backboard.io)
2. Click on an assistant (named `arc-{user_id}`)
3. See all stored memories and tags

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "BACKBOARD_API_KEY not set" | Add to `.env`, restart server |
| No memories loading | Check `.env` has correct key, check Backboard dashboard |
| New assistant created every time | Normal - maps to same `user_id` automatically |
| Backboard API errors | Verify API key valid in Backboard settings |

---

## Files Modified/Created

- ✅ `backend/ai/memory.py` - Backboard client
- ✅ `backend/ai/chat_agent.py` - Uses memory in chat
- ✅ `backend/api/chat.py` - Chat endpoint
- ✅ `.env` - Add `BACKBOARD_API_KEY`

## Test It
```bash
python test_chatbot.py
```
Runs multi-turn chat; memories persist across turns.

---

See `BACKBOARD_INTEGRATION_GUIDE.md` for full documentation.
