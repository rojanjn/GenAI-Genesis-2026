# Backboard.io Chat Memory Integration Summary

## What You Asked
"How do I use Backboard.io in the chat functionality to maintain context and memory across conversations/sessions?"

## The Answer: It's Already Set Up! ✨

Your project already has **full Backboard.io integration** for chat memory persistence. Here's what's happening behind the scenes:

---

## How It Works (High-Level)

```
User sends message → System retrieves stored memories from Backboard 
                  → Uses memories to contextualize response 
                  → Returns personalized answer
```

Every time a user chats:
1. Their unique **Backboard assistant** is retrieved (created on first chat)
2. All **stored memories** (stressors, emotions, strategies) are loaded
3. Memories are **injected into the LLM prompt** for context
4. AI generates **personalized responses** using their history

When user returns weeks/months later:
- Same assistant ID is used
- All previous memories are still there
- Context continues seamlessly

---

## What's Already Implemented

### ✅ File: `backend/ai/memory.py`
- **Complete Backboard REST API client**
- `get_or_create_assistant()` - Creates unique assistant per user
- `load_user_profile()` - Fetches all stored memories
- `store_profile_update()` - Saves new insights
- Memory tagging system (stressors, emotions, strategies, etc.)

### ✅ File: `backend/ai/chat_agent.py`
- Loads Backboard profile on every chat turn
- Converts profile to text format
- Passes profile to LLM via prompt

### ✅ File: `backend/api/chat.py`
- REST endpoint `/api/chat/`
- Automatically handles Backboard orchestration
- No manual configuration needed

### ✅ Integration Points
- Memories automatically loaded before response generation
- Memories automatically updated after sessions
- Multi-turn chat maintains context
- Cross-session memory persistence

---

## To Use It: 3 Simple Steps

### Step 1: Get Backboard API Key
```bash
1. Go to app.backboard.io
2. Sign up → Create organization
3. Settings → API Keys → Generate
4. Copy key (format: espr_xxxxx...)
```

### Step 2: Add to `.env`
```bash
# .env (in project root)
BACKBOARD_API_KEY=espr_YOUR_KEY_HERE
```

### Step 3: Start Using!
```bash
# Start API server
uvicorn backend.api.main:app --reload

# Send chat request (memories loaded automatically!)
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "message": "I feel anxious about work",
    "chat_history": []
  }'
```

That's it! Backboard handles the rest.

---

## Under the Hood: What Happens on Each Chat

```python
POST /api/chat/
  ↓
assistant_id = await get_or_create_assistant(user_id)
  # First time: Creates new assistant named "arc-user_id"
  # Subsequent: Reuses same assistant
  ↓
profile = await load_user_profile(assistant_id)
  # Fetches ALL memories for this user from Backboard
  # Result: UserProfileMemory with:
  #   - common_stressors: ["work deadlines", "perfectionism"]
  #   - recurring_emotions: ["anxiety", "overwhelm"]
  #   - helpful_strategies: ["meditation", "talking to friends"]
  #   - support_preferences: ["validation", "encouragement"]
  #   - recent_patterns: ["stress increases on Mondays"]
  #   - summary: "User is driven but struggles with perfectionism..."
  ↓
profile_memory_text = _profile_to_text(profile)
  # Converts to readable format for LLM
  ↓
response = generate_chat_response(
    user_message=user_message,
    user_profile_memory=profile_memory_text,  # ← Memories injected here!
    chat_history=chat_history,
    similar_entries=similar_entries,
)
  # LLM receives context about user's personality, stressors, preferences
  # Generates highly personalized response
  ↓
return response
  # User gets answer that's aware of their history
```

---

## Memory Structure (Tagged System)

Backboard stores memories with tags for organization:

| Tag | Purpose | Example |
|-----|---------|---------|
| `stressor` | Things that stress user | "tight work deadlines" |
| `emotion` | Recurring emotions | "anxiety about perfectionism" |
| `strategy` | What helps user | "meditation for 10 min" |
| `support_style` | How to support them | "validation over advice" |
| `pattern` | Behavioral patterns | "stress spikes on Mondays" |
| `session_summary` | Overall insights | "User is driven but needs balance" |

Each memory is a separate entry in Backboard, making them queryable and editable individually.

---

## Real Example: Multi-Session Continuity

**Day 1 (March 14):**
```
User: "I feel overwhelmed at work"
→ AI detects emotion: anxiety
→ AI stores memory: "work stress" (stressor), "anxiety" (emotion)
```

**Day 8 (March 21):**
```
User returns: "I'm nervous about an important meeting"
→ Backboard loads memories from Day 1
→ AI now knows: This user experiences work anxiety
→ AI generates response referencing previous conversations!
→ Memory context: "I know you've felt overwhelmed at work before..."
```

The user doesn't have to re-explain their situation. Context is maintained.

---

## API Reference

### Load Memories
```python
from backend.ai.memory import load_user_profile, get_or_create_assistant

assistant_id = await get_or_create_assistant("user_123")
profile = await load_user_profile(assistant_id)

# Access different memory types
print(profile.common_stressors)       # ["deadline stress", "perfectionism"]
print(profile.recurring_emotions)     # ["anxiety", "overwhelm"]
print(profile.helpful_strategies)     # ["meditation", "exercise"]
print(profile.support_preferences)    # ["validation", "encouragement"]
print(profile.recent_patterns)        # ["stressed on Mondays"]
print(profile.summary)                # "User is driven but needs self-compassion"
```

### Store Memories
```python
from backend.ai.memory import store_profile_update
from backend.ai.schemas import UserProfileMemory

updated_profile = UserProfileMemory(
    common_stressors=["deadlines", "perfectionism"],
    recurring_emotions=["anxiety"],
    helpful_strategies=["meditation", "walking"],
    support_preferences=["validation"],
    recent_patterns=["stress on Mondays"],
    summary="User needs self-compassion"
)

await store_profile_update(assistant_id, updated_profile)
```

---

## Features Enabled by Backboard

| Capability | Without Backboard | With Backboard |
|------------|-------------------|----------------|
| **Multi-Session Memory** | ❌ Lost after session | ✅ Persists forever |
| **Context Awareness** | ❌ Each chat isolated | ✅ Full history available |
| **Pattern Recognition** | ❌ No pattern tracking | ✅ Recurring patterns tracked |
| **Personalization** | ❌ Generic responses | ✅ Personalized responses |
| **Long-term Profile** | ❌ None | ✅ Complete user profile |
| **Device Sync** | ❌ Lost on device switch | ✅ Seamless across devices |

---

## Debug & Verify

### Check Backboard Dashboard
1. Go to [app.backboard.io](https://app.backboard.io)
2. Click on an assistant (named `arc-{user_id}`)
3. View all stored memories and tags

### Test Locally
```bash
python test_chatbot.py
```

This runs a multi-turn conversation. Memories persist across turns!

### Verify Setup
```python
import asyncio
from backend.ai.memory import get_or_create_assistant, load_user_profile

async def verify():
    asst_id = await get_or_create_assistant("test_user")
    profile = await load_user_profile(asst_id)
    print(f"Loaded {len(profile.common_stressors)} stressors")
    print(f"Loaded {len(profile.recurring_emotions)} emotions")

asyncio.run(verify())
```

---

## Troubleshooting

### Error: "BACKBOARD_API_KEY environment variable is not set"
**Solution**: Add to `.env` file:
```bash
BACKBOARD_API_KEY=espr_YOUR_KEY_HERE
```

### Error: "Failed to create assistant"
**Solution**: 
1. Verify API key in Backboard dashboard is valid
2. Check API key hasn't been revoked
3. Verify network connectivity

### Memories Not Loading
**Debug**:
```python
# Check if memories were stored
import asyncio
from backend.ai.memory import load_user_profile, get_or_create_assistant

async def debug():
    asst_id = await get_or_create_assistant("debug_user")
    profile = await load_user_profile(asst_id)
    print(profile)  # Should show stored memories

asyncio.run(debug())
```

---

## Files You Need to Know

| File | Purpose |
|------|---------|
| `backend/ai/memory.py` | Backboard API client - all memory operations |
| `backend/ai/chat_agent.py` | Loads memories, orchestrates chat |
| `backend/api/chat.py` | REST endpoint for chat |
| `backend/ai/schemas.py` | `UserProfileMemory` data structure |
| `.env` | Contains `BACKBOARD_API_KEY` |

---

## Next Steps

1. ✅ Get Backboard API key from [app.backboard.io](https://app.backboard.io)
2. ✅ Add `BACKBOARD_API_KEY=espr_...` to `.env`
3. ✅ Run `uvicorn backend.api.main:app --reload`
4. ✅ Send chat requests to `/api/chat/` endpoint
5. ✅ Check Backboard dashboard to see stored memories

---

## Deep Dive Documentation

- **Full Guide**: `BACKBOARD_INTEGRATION_GUIDE.md` - Comprehensive explanation
- **Quick Reference**: `BACKBOARD_QUICK_START.md` - TL;DR version
- **Code Examples**: `BACKBOARD_CODE_EXAMPLES.md` - Practical code samples

---

## Key Insight

The beauty of this integration is **simplicity**: You don't need to manage memory yourself. Just send messages to `/api/chat/`, and the system:
- Automatically creates/retrieves user assistants
- Automatically loads memories
- Automatically uses memories in responses
- Automatically persists new insights

**It just works.** 🚀

---

**Generated**: March 14, 2026
