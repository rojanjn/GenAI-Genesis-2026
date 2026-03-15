# Backboard.io Integration Guide for Chat Memory & Context

## Overview

This project uses **Backboard.io** to maintain persistent user memory and context across chat conversations and sessions. Backboard provides a REST API that stores structured memory (stressors, emotions, strategies, etc.) associated with each user's assistant.

**Current Implementation Status**: ✅ **Fully Integrated**
- Memory persistence across chat sessions
- Automatic assistant creation per user
- Profile loading and updating with tagged memories

---

## Architecture: How Backboard Enables Persistent Chat Context

```
User's Chat Session
        ↓
[Message] → run_chatbot_turn()
        ↓
1. get_or_create_assistant()      ← Creates unique Backboard assistant per user
2. load_user_profile()             ← Fetches previous session memories from Backboard
3. Generate embeddings & retrieve similar past entries
4. generate_chat_response()        ← Uses profile memory to contextualize response
        ↓
Response sent to user
        ↓
[Next Session - User returns days/weeks later]
        ↓
load_user_profile()                ← ✨ MEMORIES STILL THERE! Context maintained
```

### Key Benefit
Without Backboard: Each chat session is isolated; assistant has no memory of previous conversations.

With Backboard: Assistant remembers user's stressors, emotions, strategies, and patterns from all previous sessions.

---

## Setup: Getting Started with Backboard.io

### Step 1: Create a Backboard Account

1. Go to [app.backboard.io](https://app.backboard.io)
2. Sign up for a free account
3. Create an organization (e.g., "GenAI-Genesis-2026")

### Step 2: Generate API Key

1. In Backboard dashboard, go to **Settings → API Keys**
2. Click **Generate New Key**
3. Name it (e.g., "GenAI Chat Memory")
4. Copy the key (format: `espr_xxxxx...`)

### Step 3: Add to `.env` File

Add this to your `.env` file in the project root:

```bash
# .env

BACKBOARD_API_KEY=espr_YOUR_API_KEY_HERE
```

**Important**: Never commit this to git. Ensure `.env` is in `.gitignore`.

### Step 4: Verify Setup

Run the test to confirm Backboard is working:

```bash
python test_chatbot.py
```

Expected behavior:
- First run: Creates a new assistant for the test user
- Subsequent runs: Reuses the same assistant, loads stored memories
- Check [app.backboard.io](https://app.backboard.io) dashboard to see stored memories

---

## How Backboard Works in This Project

### 1. **Assistant Management** (`backend/ai/memory.py`)

Every user gets a unique Backboard assistant:

```python
from backend.ai.memory import get_or_create_assistant

# Called automatically in chat endpoint
assistant_id = await get_or_create_assistant(user_id="user_123")
# Returns: existing assistant ID or creates new one named "arc-user_123"
```

**What happens**:
- Checks if assistant with name `arc-{user_id}` already exists
- If yes: Returns existing `assistant_id`
- If no: Creates new assistant with system prompt, returns new `assistant_id`

### 2. **Memory Storage** (Tagged Memories)

Backboard stores memories with tags for organization:

```
TAG_STRESSOR        = "stressor"        # Things that stress the user
TAG_EMOTION         = "emotion"         # Recurring emotions
TAG_STRATEGY        = "strategy"        # Helpful coping strategies
TAG_SUPPORT_STYLE   = "support_style"   # How user prefers to be supported
TAG_PATTERN         = "pattern"         # Behavioral/emotional patterns
TAG_SESSION_SUMMARY = "session_summary" # Overall summaries from sessions
```

**Example memory in Backboard**:
```json
{
  "id": "mem_xyz",
  "content": "User feels anxious when facing tight deadlines",
  "metadata": {
    "tag": "stressor"
  },
  "created_at": "2026-03-14T10:30:00Z"
}
```

### 3. **Profile Loading** (Read Memory)

When a user starts a chat, retrieve all stored memories:

```python
from backend.ai.memory import load_user_profile

profile = await load_user_profile(assistant_id)
# Returns UserProfileMemory object with all tagged memories

# Structure:
# profile.common_stressors        → List of stressors
# profile.recurring_emotions      → List of emotions
# profile.helpful_strategies      → List of strategies
# profile.support_preferences     → List of support styles
# profile.recent_patterns         → List of patterns
# profile.summary                 → Latest session summary
```

### 4. **Using Profile in Chat**

The loaded profile is converted to text and passed to the LLM:

```python
# In chat_agent.py
profile = await load_user_profile(assistant_id)
profile_memory_text = _profile_to_text(profile)

# Profile becomes part of the context:
# "User memory: Known stressors: work deadlines, comparison anxiety. 
#  Helpful strategies: meditation, journaling. Prefers: validation over advice."

response = generate_chat_response(
    user_message=user_message,
    user_profile_memory=profile_memory_text,  # ← Used here!
    chat_history=chat_history,
    similar_entries=similar_entries,
)
```

---

## Chat Flow with Backboard Context

### Complete Flow: User Sends Message

```
POST /chat/
{
  "user_id": "user_123",
  "message": "I'm feeling overwhelmed with deadlines again",
  "chat_history": [
    {"role": "user", "content": "I feel stressed"},
    {"role": "assistant", "content": "That sounds tough..."}
  ]
}
```

**What Happens**:

```python
async def chat_with_ai(request: ChatRequest):
    # 1. Get or create Backboard assistant for this user
    assistant_id = await get_or_create_assistant(request.user_id)
    
    # 2. Run chatbot turn (internal orchestration)
    result = await run_chatbot_turn(
        user_message=request.message,
        assistant_id=assistant_id,
        user_id=request.user_id,
        chat_history=request.chat_history,
    )
    return result
```

**Inside `run_chatbot_turn()`**:

```python
async def run_chatbot_turn(...):
    # 1. LOAD BACKBOARD MEMORY
    profile = await load_user_profile(assistant_id)
    profile_memory_text = _profile_to_text(profile)
    # Result: "Stressors: work deadlines, comparing myself to others..."
    
    # 2. Analyze current mood
    mood_result = analyse_mood(user_message)  # → "anxiety"
    
    # 3. Find similar past journal entries
    message_embedding = generate_embedding(user_message)
    past_entries = get_all_entries(user_id)
    similar_entries = find_similar_entries(message_embedding, past_entries, top_k=3)
    # Result: List of past entries about deadlines/stress
    
    # 4. GENERATE RESPONSE with memory context
    response = generate_chat_response(
        user_message=user_message,
        chat_history=chat_history,
        similar_entries=similar_entries,
        user_profile_memory=profile_memory_text,  # ✨ Backboard context used here!
    )
    
    return {
        "response": response,
        "similar_entries": similar_entries,
        "current_mood": mood_result.emotion,
    }
```

### LLM Context with Backboard Memory

The prompt sent to OpenAI includes Backboard profile:

```
USER MEMORY:
- Stressors: work deadlines, comparing myself to others, perfectionism
- Recurring emotions: anxiety, overwhelm
- Helpful strategies: meditation, taking breaks, talking to friends
- Support preferences: validation and encouragement
- Recent patterns: stress spikes around deadlines
- Summary: User is driven but struggles with perfectionism and social comparison

SIMILAR PAST JOURNAL ENTRIES:
- 2026-03-10: "Feeling overwhelmed with project deadlines..."
- 2026-03-05: "Compared myself to my coworkers today and felt inadequate..."

RECENT CHAT HISTORY:
user: I'm feeling stressed
assistant: That sounds challenging. What's been on your mind?

LATEST USER MESSAGE:
"I'm feeling overwhelmed with deadlines again"

---

Your role: Help them explore their feelings using motivational interviewing.
Avoid advice. Ask open-ended questions. Be warm and validating.
```

---

## Persisting Memory Updates

After processing a journal entry (main diary endpoint), the agent loop updates Backboard:

```python
# In agent.py - Step 5
await store_profile_update(assistant_id, updated_profile)

# This writes individual memories for each item:
# - Each stressor, emotion, strategy, pattern gets its own memory entry
# - All tagged appropriately
# - Available on next chat session
```

---

## Practical Example: Multi-Session Continuity

### Session 1: Day 1

```python
# User chats about anxiety
message = "I've been having panic attacks at work"

# Backboard loads (empty for new user)
profile = await load_user_profile(assistant_id)
# Result: empty profile

# Assistant generates response, stores memories
# Backboard now stores:
# - "panic attacks at work" (stressor)
# - "anxiety" (emotion)
```

### Session 2: Day 8 (User Returns)

```python
# User chats again (same user_id)
message = "I had another panic attack today"

# ✨ Backboard automatically loads previous memory!
profile = await load_user_profile(assistant_id)
# Result:
# {
#   common_stressors: ["panic attacks at work"],
#   recurring_emotions: ["anxiety"],
#   ...
# }

# Assistant now knows about previous panic attacks
# Context is maintained across sessions!
```

---

## API Endpoints for Manual Operations

You can also interact with Backboard directly if needed:

### Get All Assistants

```python
import httpx
import os

api_key = os.getenv("BACKBOARD_API_KEY")
headers = {"X-API-Key": api_key, "Content-Type": "application/json"}

async with httpx.AsyncClient() as client:
    r = await client.get(
        "https://app.backboard.io/api/assistants",
        headers=headers
    )
    assistants = r.json()
    for asst in assistants:
        print(f"ID: {asst['assistant_id']}, Name: {asst['name']}")
```

### Get Memories for an Assistant

```python
async with httpx.AsyncClient() as client:
    r = await client.get(
        f"https://app.backboard.io/api/assistants/{assistant_id}/memories",
        headers=headers
    )
    memories = r.json()
    for mem in memories.get("memories", []):
        tag = mem.get("metadata", {}).get("tag")
        content = mem.get("content")
        print(f"[{tag}] {content}")
```

### Manually Store a Memory

```python
async with httpx.AsyncClient() as client:
    r = await client.post(
        f"https://app.backboard.io/api/assistants/{assistant_id}/memories",
        headers=headers,
        json={
            "content": "User practices yoga daily",
            "metadata": {"tag": "strategy"}
        }
    )
    result = r.json()
    print(f"Memory stored: {result['memory_id']}")
```

---

## Troubleshooting

### Issue: "BACKBOARD_API_KEY environment variable is not set"

**Solution**:
1. Check `.env` file exists in project root
2. Verify it contains: `BACKBOARD_API_KEY=espr_xxxxx`
3. Restart your FastAPI server: `uvicorn backend.api.main:app --reload`

### Issue: New Backboard Assistant Created Every Chat

**Cause**: Firebase database not persisting the `assistant_id` mapping

**Solution**:
- The project stores `assistant_id` as part of user profile in Backboard
- On first chat: Creates assistant automatically
- On subsequent chats: Reuses same assistant
- This is automatic; no manual action needed

### Issue: Memories Not Loading

**Debug**:

```python
import asyncio
from backend.ai.memory import load_user_profile, get_or_create_assistant

async def debug():
    assistant_id = await get_or_create_assistant("debug_user")
    print(f"Assistant ID: {assistant_id}")
    
    profile = await load_user_profile(assistant_id)
    print(f"Loaded profile: {profile}")

asyncio.run(debug())
```

### Issue: Backboard API Errors

**Check**:
1. API key is valid: Log into [app.backboard.io](https://app.backboard.io)
2. API key hasn't been revoked: Check **Settings → API Keys**
3. Network connectivity: `curl -H "X-API-Key: YOUR_KEY" https://app.backboard.io/api/assistants`

---

## Best Practices

### 1. **Always Call `init_firebase()` First**

```python
from backend.db.firebase_client import init_firebase

# Do this before any chat operations
init_firebase()
```

### 2. **Reuse Assistant IDs**

```python
# ✅ Good: Same user → same assistant across sessions
assistant_id = await get_or_create_assistant(user_id)

# ❌ Avoid: Creating new assistants for same user
# This would fragment their memory across multiple assistants
```

### 3. **Handle API Errors Gracefully**

```python
try:
    profile = await load_user_profile(assistant_id)
except httpx.HTTPError as e:
    logger.error(f"Failed to load profile: {e}")
    # Fall back to empty profile
    profile = UserProfileMemory()
```

### 4. **Update Profile After Each Session**

```python
# After chat response is generated, update profile with new insights
updated_profile = generate_updated_profile(
    old_profile=profile,
    new_insights=chat_insights
)
await store_profile_update(assistant_id, updated_profile)
```

### 5. **Regular Memory Cleanup**

For long-running apps, periodically archive old memories:

```python
# Example: Archive memories older than 90 days
async def archive_old_memories(assistant_id: str, days=90):
    memories = await load_user_profile(assistant_id)
    # Implement archive logic based on created_at timestamp
```

---

## Integration with Frontend

### API Call from Frontend

```javascript
// Frontend: Send chat message with history
const response = await fetch('/api/chat/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    user_id: 'user_123',
    message: 'I feel overwhelmed again',
    chat_history: [
      { role: 'user', content: 'I have anxiety' },
      { role: 'assistant', content: 'I hear you...' }
    ]
  })
});

const data = await response.json();
console.log(data.response.reply);  // AI's response
console.log(data.current_mood);     // Detected mood
```

### Backend Handles Backboard Automatically

```python
# Backend receives request, automatically:
# 1. Loads user's Backboard assistant
# 2. Retrieves stored memories
# 3. Uses them to contextualize response
# 4. Returns enriched response

# Frontend just sends message and chat_history
# No need to manually manage Backboard
```

---

## Summary: What Backboard Gives You

| Feature | Without Backboard | With Backboard |
|---------|-------------------|----------------|
| **Session Memory** | Lost after session ends | Persists indefinitely |
| **User Context** | Each conversation is isolated | Full history available |
| **Pattern Recognition** | None | Tracks recurring stressors/emotions |
| **Personalization** | Generic responses | Contextual, personalized responses |
| **Multi-Device** | Conversation lost on device switch | Seamless across devices |
| **Long-term Profile** | None | Complete user profile built over time |

---

## Next Steps

1. ✅ Set `BACKBOARD_API_KEY` in `.env`
2. ✅ Run `python test_chatbot.py` to verify setup
3. ✅ Check [app.backboard.io](https://app.backboard.io) dashboard to see stored memories
4. ✅ Start the FastAPI server: `uvicorn backend.api.main:app --reload`
5. ✅ Send chat requests to `/api/chat/` endpoint

---

## Reference: File Locations

| File | Purpose |
|------|---------|
| `backend/ai/memory.py` | Backboard API client, memory load/store |
| `backend/ai/chat_agent.py` | Orchestrates chat with memory |
| `backend/api/chat.py` | Chat endpoint, calls chat_agent |
| `backend/ai/schemas.py` | `UserProfileMemory` data structure |

---

**Last Updated**: March 14, 2026
