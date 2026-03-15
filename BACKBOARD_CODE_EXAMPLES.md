# Backboard Integration: Code Examples & Tutorials

This file contains practical code examples for using Backboard.io in the GenAI-Genesis chat application.

---

## Example 1: Basic Chat with Backboard Memory

### Scenario
User sends a message. System loads their memories from Backboard and uses them to personalize the response.

### Code

```python
# backend/api/chat.py (simplified)
from fastapi import APIRouter
from pydantic import BaseModel
from backend.ai.chat_agent import run_chatbot_turn
from backend.ai.memory import get_or_create_assistant

class ChatRequest(BaseModel):
    user_id: str
    message: str
    chat_history: list = []

@router.post("/chat/")
async def chat_with_ai(request: ChatRequest):
    """
    1. Creates/retrieves Backboard assistant for this user
    2. Loads user's stored memories
    3. Generates personalized response
    """
    
    # Step 1: Get or create assistant
    assistant_id = await get_or_create_assistant(request.user_id)
    print(f"Using assistant: {assistant_id}")
    
    # Step 2: Run chat (internally loads Backboard memory)
    result = await run_chatbot_turn(
        user_message=request.message,
        assistant_id=assistant_id,
        user_id=request.user_id,
        chat_history=request.chat_history,
    )
    
    return {
        "response": result["response"],
        "mood": result["current_mood"],
    }
```

### Frontend Usage

```javascript
// frontend/src/pages/Chat.js
async function sendMessage(userMessage) {
  const response = await fetch('/api/chat/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: 'user_123',
      message: userMessage,
      chat_history: chatHistory  // Previous messages in this session
    })
  });
  
  const data = await response.json();
  return data.response.reply;  // AI's personalized response (using Backboard memory!)
}
```

---

## Example 2: Loading & Using Stored Memories

### Scenario
You want to programmatically access what Backboard knows about a user.

### Code

```python
import asyncio
from backend.ai.memory import load_user_profile, get_or_create_assistant

async def example_load_memories():
    """Load user's stored memories from Backboard"""
    
    user_id = "alice_789"
    
    # Get user's assistant
    assistant_id = await get_or_create_assistant(user_id)
    
    # Load their profile from Backboard
    profile = await load_user_profile(assistant_id)
    
    # Access the different memory categories
    print("=== Alice's Profile ===")
    print(f"Stressors: {profile.common_stressors}")
    # Output: ["work deadlines", "perfectionism", "social comparison"]
    
    print(f"Emotions: {profile.recurring_emotions}")
    # Output: ["anxiety", "overwhelm", "self-doubt"]
    
    print(f"Strategies that help: {profile.helpful_strategies}")
    # Output: ["meditation", "talking to friends", "taking breaks"]
    
    print(f"Prefers: {profile.support_preferences}")
    # Output: ["validation", "encouragement", "non-judgmental listening"]
    
    print(f"Recent patterns: {profile.recent_patterns}")
    # Output: ["stress increases on Mondays", "feels better after exercise"]
    
    print(f"Summary: {profile.summary}")
    # Output: "Alice is a driven professional who struggles with perfectionism..."

# Run it
asyncio.run(example_load_memories())
```

---

## Example 3: Storing New Memories

### Scenario
After a therapy/journal session, you extract insights and store them in Backboard for future use.

### Code

```python
import asyncio
from backend.ai.memory import (
    store_profile_update,
    get_or_create_assistant,
)
from backend.ai.schemas import UserProfileMemory

async def example_store_memories():
    """Store new insights in Backboard"""
    
    user_id = "bob_456"
    assistant_id = await get_or_create_assistant(user_id)
    
    # Create a profile with new insights discovered in this session
    updated_profile = UserProfileMemory(
        common_stressors=[
            "team conflicts",
            "unclear project requirements",
            "imposter syndrome"
        ],
        recurring_emotions=[
            "frustration",
            "anxiety",
            "inadequacy"
        ],
        helpful_strategies=[
            "speaking with mentor",
            "breaking tasks into smaller chunks",
            "celebrating small wins"
        ],
        support_preferences=[
            "practical advice",
            "acknowledgment of effort",
            "gentle pushback"
        ],
        recent_patterns=[
            "gets overwhelmed when scope expands mid-project",
            "feels better after mentoring others"
        ],
        summary="Bob is a junior engineer dealing with imposter syndrome. "
               "He responds well to mentorship and structured support. "
               "Confidence increases when he helps others."
    )
    
    # Store to Backboard
    await store_profile_update(assistant_id, updated_profile)
    print(f"✓ Stored memories for {user_id}")
    
    # Verify it was stored by loading it back
    from backend.ai.memory import load_user_profile
    loaded = await load_user_profile(assistant_id)
    print(f"✓ Verified: {loaded.common_stressors}")

asyncio.run(example_store_memories())
```

---

## Example 4: Multi-Session Continuity

### Scenario
Demonstrate how Backboard maintains context across multiple sessions/days.

### Code

```python
import asyncio
from datetime import datetime
from backend.ai.chat_agent import run_chatbot_turn
from backend.ai.memory import get_or_create_assistant

async def example_multi_session():
    """
    Simulate user chatting across two separate sessions.
    Backboard remembers everything!
    """
    
    user_id = "charlie_123"
    chat_history = []
    
    # ============ SESSION 1: Day 1 ============
    print("\n=== SESSION 1: Day 1 (March 14) ===")
    
    assistant_id = await get_or_create_assistant(user_id)
    
    message_1 = "I had a stressful day at work today. My manager criticized my code review."
    result_1 = await run_chatbot_turn(
        user_message=message_1,
        assistant_id=assistant_id,
        user_id=user_id,
        chat_history=chat_history,
    )
    
    print(f"User: {message_1}")
    print(f"AI: {result_1['response']['reply']}")
    print(f"Mood detected: {result_1['current_mood']}")
    
    # Update chat history
    chat_history.append({"role": "user", "content": message_1})
    chat_history.append({"role": "assistant", "content": result_1['response']['reply']})
    
    # → Backboard now stores: "code review criticism" as stressor, "anxiety" as emotion
    
    # ============ SESSION 2: Day 8 (one week later) ============
    print("\n=== SESSION 2: Day 8 (one week later) ===")
    print("(User returns after a week)")
    
    # New session, fresh chat_history (but NOT fresh assistant!)
    chat_history = []
    
    # Same assistant_id - this is key!
    assistant_id = await get_or_create_assistant(user_id)  # Returns SAME assistant
    
    message_2 = "I'm worried about another code review coming up."
    result_2 = await run_chatbot_turn(
        user_message=message_2,
        assistant_id=assistant_id,
        user_id=user_id,
        chat_history=chat_history,
    )
    
    print(f"User: {message_2}")
    print(f"AI: {result_2['response']['reply']}")
    print(f"Mood detected: {result_2['current_mood']}")
    
    # ✨ The AI's response now references Session 1 insights!
    # ✨ It knows about the previous code review criticism
    # ✨ It can offer context-aware comfort
    # All because Backboard persisted the memories!
    
    # Verify what's in Backboard
    from backend.ai.memory import load_user_profile
    profile = await load_user_profile(assistant_id)
    print(f"\nBackboard memory after both sessions:")
    print(f"  Stressors: {profile.common_stressors}")
    print(f"  Emotions: {profile.recurring_emotions}")

asyncio.run(example_multi_session())
```

---

## Example 5: Personalizing Responses with Memory

### Scenario
Show how memory affects the actual LLM prompt and response generation.

### Code

```python
from backend.ai.chat_response_generator import generate_chat_response

async def example_personalized_responses():
    """
    Without Backboard memory vs. With Backboard memory
    """
    
    user_message = "I made a mistake at work today."
    
    # ❌ WITHOUT BACKBOARD
    print("=== WITHOUT BACKBOARD MEMORY ===")
    response_generic = generate_chat_response(
        user_message=user_message,
        chat_history=[],
        similar_entries=[],
        user_profile_memory=None  # No memory!
    )
    print(f"Generic AI: {response_generic['reply']}")
    # Output: "That sounds challenging. What happened?"
    
    # ✅ WITH BACKBOARD
    print("\n=== WITH BACKBOARD MEMORY ===")
    backboard_memory = """
    - Stressors: perfectionism, making mistakes, self-criticism
    - Emotions: shame, self-doubt, anxiety
    - Strategies that help: self-compassion, talking to mentors, reflecting
    - Prefers: gentle validation, not harsh criticism
    - Pattern: "gets very hard on himself after mistakes"
    """
    
    response_personalized = generate_chat_response(
        user_message=user_message,
        chat_history=[],
        similar_entries=[],
        user_profile_memory=backboard_memory  # ← Magic happens here!
    )
    print(f"Personalized AI: {response_personalized['reply']}")
    # Output: "Mistakes are how we learn. Can you think of what you learned from this one?"
    # Notice: Validates, acknowledges perfectionism pattern, asks reflective question
    
    print("\n^ Same user, same message.")
    print("^ Response completely different because of Backboard memory!")

asyncio.run(example_personalized_responses())
```

---

## Example 6: Manual API Calls (Advanced)

### Scenario
Directly call Backboard REST API if needed (not usually necessary, but useful for debugging).

### Code

```python
import httpx
import os

async def example_direct_backboard_api():
    """Call Backboard REST API directly"""
    
    api_key = os.getenv("BACKBOARD_API_KEY")
    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }
    
    base_url = "https://app.backboard.io/api"
    
    async with httpx.AsyncClient() as client:
        # 1. List all assistants
        print("=== Listing assistants ===")
        r = await client.get(f"{base_url}/assistants", headers=headers)
        assistants = r.json()
        for asst in assistants:
            print(f"  {asst['assistant_id']}: {asst.get('name')}")
        
        # 2. Get memories for specific assistant
        if assistants:
            asst_id = assistants[0]['assistant_id']
            print(f"\n=== Memories for {asst_id} ===")
            r = await client.get(
                f"{base_url}/assistants/{asst_id}/memories",
                headers=headers
            )
            memories = r.json()
            for mem in memories.get("memories", []):
                tag = mem.get("metadata", {}).get("tag", "untagged")
                content = mem.get("content", "")
                print(f"  [{tag}] {content[:50]}...")
        
        # 3. Manually add a memory
        print(f"\n=== Adding memory ===")
        r = await client.post(
            f"{base_url}/assistants/{asst_id}/memories",
            headers=headers,
            json={
                "content": "User loves hiking on weekends",
                "metadata": {"tag": "interest"}
            }
        )
        result = r.json()
        print(f"  Created: {result.get('memory_id')}")

asyncio.run(example_direct_backboard_api())
```

---

## Example 7: Error Handling

### Scenario
How to gracefully handle Backboard errors.

### Code

```python
import asyncio
import httpx
import logging
from backend.ai.memory import (
    load_user_profile,
    get_or_create_assistant,
)
from backend.ai.schemas import UserProfileMemory

logger = logging.getLogger(__name__)

async def example_error_handling():
    """Robust error handling for Backboard operations"""
    
    user_id = "diana_999"
    
    try:
        # Get or create assistant
        assistant_id = await get_or_create_assistant(user_id)
    except RuntimeError as e:
        logger.error(f"Failed to get assistant: {e}")
        return {"error": "Could not initialize assistant"}
    except httpx.HTTPError as e:
        logger.error(f"Network error with Backboard: {e}")
        return {"error": "Service temporarily unavailable"}
    
    try:
        # Load profile with fallback
        profile = await load_user_profile(assistant_id)
    except httpx.HTTPError as e:
        logger.warning(f"Failed to load profile, using empty: {e}")
        profile = UserProfileMemory()  # Fallback to empty profile
    
    # Continue with empty profile if loading failed
    return {
        "assistant_id": assistant_id,
        "profile": profile,
        "status": "ok"
    }

asyncio.run(example_error_handling())
```

---

## Example 8: Testing Backboard Integration

### Scenario
Write tests to verify Backboard memory is working correctly.

### Code

```python
import asyncio
from backend.ai.memory import (
    get_or_create_assistant,
    load_user_profile,
    store_profile_update,
)
from backend.ai.schemas import UserProfileMemory

async def test_backboard_integration():
    """Integration test for Backboard"""
    
    test_user_id = "test_integration_user"
    
    # Test 1: Create assistant
    print("Test 1: Creating/retrieving assistant...")
    asst_1 = await get_or_create_assistant(test_user_id)
    asst_2 = await get_or_create_assistant(test_user_id)
    assert asst_1 == asst_2, "Same user should get same assistant"
    print("  ✓ Assistant reuse working")
    
    # Test 2: Store and load profile
    print("\nTest 2: Storing and loading profile...")
    profile = UserProfileMemory(
        common_stressors=["test stress"],
        recurring_emotions=["test emotion"],
        helpful_strategies=["test strategy"],
        support_preferences=["test preference"],
        recent_patterns=["test pattern"],
        summary="Test summary"
    )
    await store_profile_update(asst_1, profile)
    
    loaded = await load_user_profile(asst_1)
    assert "test stress" in loaded.common_stressors, "Stressor not found"
    assert "test emotion" in loaded.recurring_emotions, "Emotion not found"
    print("  ✓ Profile storage/retrieval working")
    
    # Test 3: Verify persistence
    print("\nTest 3: Verifying memory persists...")
    reloaded = await load_user_profile(asst_1)
    assert reloaded.common_stressors == loaded.common_stressors
    print("  ✓ Persistence verified")
    
    print("\n✓ All tests passed!")

asyncio.run(test_backboard_integration())
```

---

## Running Examples

```bash
# Run individual examples
python -c "from examples import example_1; asyncio.run(example_1())"

# Or add to a test file and run
python examples.py

# Or use the existing test file
python test_chatbot.py
```

---

## Key Takeaways

1. **Automatic**: Most operations are automatic; you just call the endpoints
2. **Persistent**: Memories survive across sessions and devices
3. **Personalized**: LLM gets user history, generates better responses
4. **Backward Compatible**: Works with existing chat flow
5. **Optional**: If Backboard fails, system gracefully degrades

---

See `BACKBOARD_INTEGRATION_GUIDE.md` for complete documentation.
