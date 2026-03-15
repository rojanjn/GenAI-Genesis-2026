# Backboard.io Chat Memory Documentation Index

Welcome! This documentation covers how Backboard.io enables persistent memory and context in the GenAI-Genesis chat application.

## 📚 Documentation Files

### 🚀 **Start Here**
- **[BACKBOARD_QUICK_START.md](BACKBOARD_QUICK_START.md)** - 5-minute setup guide
  - Get API key
  - Add to `.env`
  - That's it!

### 📖 **Main Guides**

1. **[BACKBOARD_SUMMARY.md](BACKBOARD_SUMMARY.md)** - Executive Summary
   - What Backboard does
   - How it's already set up
   - 3-step quick start
   - Architecture overview
   - Key features enabled

2. **[BACKBOARD_INTEGRATION_GUIDE.md](BACKBOARD_INTEGRATION_GUIDE.md)** - Complete Reference
   - Detailed architecture explanation
   - Full setup instructions
   - How Backboard works in this project
   - Memory tagging system
   - Chat flow walkthrough
   - Practical examples
   - Best practices
   - Troubleshooting guide

3. **[BACKBOARD_CODE_EXAMPLES.md](BACKBOARD_CODE_EXAMPLES.md)** - Code Samples
   - Example 1: Basic chat with memory
   - Example 2: Loading stored memories
   - Example 3: Storing new memories
   - Example 4: Multi-session continuity
   - Example 5: Personalizing responses
   - Example 6: Manual API calls
   - Example 7: Error handling
   - Example 8: Testing

4. **[BACKBOARD_DIAGRAMS.md](BACKBOARD_DIAGRAMS.md)** - Visual Architecture
   - System architecture diagram
   - Chat flow sequence diagram
   - Data flow visualization
   - Memory storage structure
   - LLM prompt construction
   - State transitions
   - Error handling flow
   - Integration points

---

## 🎯 Quick Navigation

### "I just want to get started"
1. Read: [BACKBOARD_QUICK_START.md](BACKBOARD_QUICK_START.md)
2. Get API key from [app.backboard.io](https://app.backboard.io)
3. Add to `.env`
4. Done!

### "Tell me how it works"
1. Read: [BACKBOARD_SUMMARY.md](BACKBOARD_SUMMARY.md)
2. Look at: [BACKBOARD_DIAGRAMS.md](BACKBOARD_DIAGRAMS.md)

### "I need complete details"
1. Read: [BACKBOARD_INTEGRATION_GUIDE.md](BACKBOARD_INTEGRATION_GUIDE.md)

### "Show me code"
1. Read: [BACKBOARD_CODE_EXAMPLES.md](BACKBOARD_CODE_EXAMPLES.md)
2. Reference: [backend/ai/memory.py](backend/ai/memory.py)
3. Reference: [backend/ai/chat_agent.py](backend/ai/chat_agent.py)

### "I'm debugging an issue"
1. Check: [BACKBOARD_INTEGRATION_GUIDE.md](BACKBOARD_INTEGRATION_GUIDE.md#troubleshooting)
2. See: [BACKBOARD_CODE_EXAMPLES.md](BACKBOARD_CODE_EXAMPLES.md#example-7-error-handling)

---

## 🏗️ Architecture at a Glance

```
User sends message
        ↓
[Backend retrieves user's Backboard assistant]
        ↓
[Loads all stored memories: stressors, emotions, strategies, patterns]
        ↓
[Memories injected into LLM prompt]
        ↓
[AI generates personalized response]
        ↓
User gets response that knows their history
```

---

## ✨ Key Features Enabled by Backboard

| Feature | Benefit |
|---------|---------|
| **Multi-Session Memory** | User's memories persist across conversations |
| **Context Awareness** | AI knows user's stressors, emotions, strategies |
| **Personalization** | Responses are tailored to user's history |
| **Pattern Recognition** | System identifies recurring themes |
| **Device Sync** | Memories accessible from any device |
| **Long-term Profile** | Complete user understanding builds over time |

---

## 📁 Relevant Project Files

### Core Backboard Integration
- `backend/ai/memory.py` - Backboard API client
- `backend/ai/chat_agent.py` - Chat orchestration using memory
- `backend/api/chat.py` - Chat REST endpoint
- `backend/ai/schemas.py` - `UserProfileMemory` data structure

### Testing & Examples
- `test_chatbot.py` - Multi-turn chat test
- Examples in `BACKBOARD_CODE_EXAMPLES.md`

### Configuration
- `.env` - Must contain `BACKBOARD_API_KEY`

### Database Integration
- `backend/db/firebase_client.py` - Firebase/Firestore client
- `backend/db/queries.py` - Database operations
- `backend/embeddings/similarity_search.py` - Vector similarity

---

## 🔍 How Memory Flows Through the System

### 1. **Assistant Creation** (First Chat)
```
get_or_create_assistant(user_id)
→ Checks Backboard for existing assistant
→ If not found: Creates new one named "arc-{user_id}"
→ Returns: assistant_id (unique per user)
```

### 2. **Memory Loading** (Every Chat)
```
load_user_profile(assistant_id)
→ Fetches all memories from Backboard
→ Organizes by tag: stressors, emotions, strategies, etc.
→ Returns: UserProfileMemory object
```

### 3. **Memory Usage** (Response Generation)
```
generate_chat_response(
    message,
    user_profile_memory,  ← From Backboard!
    similar_entries,
    chat_history
)
→ LLM receives context about user's personality
→ Generates personalized response
→ Returns: AI reply + open-ended question
```

### 4. **Memory Storage** (After Session)
```
store_profile_update(assistant_id, updated_profile)
→ Breaks profile into tagged memories
→ Stores each memory separately in Backboard
→ Future chats will load these memories
```

---

## 🎓 Learning Path

**Level 1: User**
- Read: [BACKBOARD_QUICK_START.md](BACKBOARD_QUICK_START.md)
- Get: API key
- Set: `.env`
- Result: Chat works with memory

**Level 2: Developer**
- Read: [BACKBOARD_SUMMARY.md](BACKBOARD_SUMMARY.md)
- Read: [BACKBOARD_INTEGRATION_GUIDE.md](BACKBOARD_INTEGRATION_GUIDE.md)
- View: [BACKBOARD_DIAGRAMS.md](BACKBOARD_DIAGRAMS.md)
- Result: Understand full architecture

**Level 3: Advanced**
- Read: [BACKBOARD_CODE_EXAMPLES.md](BACKBOARD_CODE_EXAMPLES.md)
- Study: [backend/ai/memory.py](backend/ai/memory.py)
- Study: [backend/ai/chat_agent.py](backend/ai/chat_agent.py)
- Result: Can implement custom memory features

---

## 🚀 5-Minute Start

```bash
# Step 1: Get Backboard API key
# → Visit app.backboard.io
# → Sign up → Settings → API Keys → Generate
# → Copy: espr_xxxxxxxxxxxxx

# Step 2: Add to .env
echo "BACKBOARD_API_KEY=espr_xxxxxxxxxxxxx" >> .env

# Step 3: Start server
uvicorn backend.api.main:app --reload

# Step 4: Test chat
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "message": "I feel anxious",
    "chat_history": []
  }'

# Step 5: Check Backboard dashboard
# → Visit app.backboard.io
# → See assistant "arc-test_user" with stored memories!
```

---

## ❓ FAQ

**Q: Is Backboard already integrated?**  
A: Yes! It's fully integrated. Just add the API key.

**Q: What if I don't set the API key?**  
A: Chat will fail. See [troubleshooting](BACKBOARD_INTEGRATION_GUIDE.md#troubleshooting).

**Q: How are memories stored?**  
A: Tagged individually in Backboard (stressor, emotion, strategy, etc.)

**Q: Do memories persist across devices?**  
A: Yes! Same user_id → same assistant → same memories everywhere.

**Q: Can I manually edit memories in Backboard?**  
A: Yes! Log into [app.backboard.io](https://app.backboard.io) and edit directly.

**Q: How do I debug memory issues?**  
A: See [Example 7: Error Handling](BACKBOARD_CODE_EXAMPLES.md#example-7-error-handling)

**Q: Can I use this without Backboard?**  
A: Not recommended. Chat would lose context between sessions.

---

## 🔗 External Resources

- **Backboard Dashboard**: [app.backboard.io](https://app.backboard.io)
- **Backboard API Docs**: [docs.backboard.io](https://docs.backboard.io)
- **OpenAI API**: [platform.openai.com](https://platform.openai.com)
- **Firebase**: [firebase.google.com](https://firebase.google.com)

---

## 📝 Documentation Status

- ✅ Quick Start Guide
- ✅ Integration Guide (Complete)
- ✅ Code Examples (8 examples)
- ✅ Architecture Diagrams (Visual flows)
- ✅ Setup Instructions
- ✅ Troubleshooting
- ✅ Best Practices
- ✅ This Index

---

## 💡 Key Insights

1. **Already Implemented**: Backboard integration is complete. Just provide API key.

2. **Automatic**: You don't manage memory yourself. System handles it automatically.

3. **Powerful**: Enables personalized, context-aware responses across sessions.

4. **Simple**: From frontend perspective, it's just a normal chat endpoint.

5. **Optional but Recommended**: Chat works without it, but loses context.

---

## 🎯 Next Steps

1. **Setup**: Follow [BACKBOARD_QUICK_START.md](BACKBOARD_QUICK_START.md)
2. **Learn**: Read [BACKBOARD_SUMMARY.md](BACKBOARD_SUMMARY.md)
3. **Code**: Check [BACKBOARD_CODE_EXAMPLES.md](BACKBOARD_CODE_EXAMPLES.md)
4. **Deploy**: Use [BACKBOARD_INTEGRATION_GUIDE.md](BACKBOARD_INTEGRATION_GUIDE.md)

---

**Last Updated**: March 14, 2026

For questions or issues, refer to the troubleshooting section in [BACKBOARD_INTEGRATION_GUIDE.md](BACKBOARD_INTEGRATION_GUIDE.md#troubleshooting).
