# Backboard Integration: Architecture Diagrams & Flows

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend/Client                           │
│                  (Web or Mobile App)                             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                    POST /api/chat/
                    {user_id, message, chat_history}
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                             │
│                    (backend/api/main.py)                        │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Chat Endpoint (/api/chat/)                            │   │
│  │                                                         │   │
│  │  1. get_or_create_assistant(user_id)                   │   │
│  │     ↓                                                   │   │
│  │     [Call Backboard API]                               │   │
│  │                                                         │   │
│  │  2. load_user_profile(assistant_id)                    │   │
│  │     ↓                                                   │   │
│  │     [Fetch memories: stressors, emotions, strategies]  │   │
│  │                                                         │   │
│  │  3. run_chatbot_turn()                                 │   │
│  │     - Analyze mood                                     │   │
│  │     - Find similar past entries                        │   │
│  │     - Generate contextual response                     │   │
│  │                                                         │   │
│  │  4. Return response with mood & context                │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└────────────────────┬─────────────────────────────────────────┬──┘
                     │                                         │
         ┌───────────▼──────────────┐         ┌───────────────▼──┐
         │  Firestore Database      │         │  Backboard API   │
         │  (Diary Entries)         │         │  (User Memory)   │
         │                          │         │                  │
         │  Collections:            │         │  Assistants:     │
         │  - diary_entries         │         │  - arc-user_1    │
         │  - mood_history          │         │  - arc-user_2    │
         │  - notifications         │         │                  │
         │  - user_profiles         │         │  Memories:       │
         │                          │         │  - stressors     │
         └──────────────────────────┘         │  - emotions      │
                                              │  - strategies    │
                                              │  - patterns      │
                                              │  - summaries     │
                                              └──────────────────┘
```

---

## Chat Flow Sequence Diagram

```
User                Frontend              Backend              Backboard         Firebase
 │                    │                    │                    │                 │
 │  "I feel anxious"  │                    │                    │                 │
 ├───────────────────►│                    │                    │                 │
 │                    │  POST /api/chat/   │                    │                 │
 │                    ├───────────────────►│                    │                 │
 │                    │                    │                    │                 │
 │                    │    get_or_create   │                    │                 │
 │                    │    _assistant()    │                    │                 │
 │                    │                    ├───────────────────►│                 │
 │                    │                    │  Check/Create      │                 │
 │                    │                    │  assistant         │                 │
 │                    │                    │◄───────────────────┤                 │
 │                    │                    │  assistant_id      │                 │
 │                    │                    │                    │                 │
 │                    │    load_user_      │                    │                 │
 │                    │    profile()       │                    │                 │
 │                    │                    ├───────────────────►│                 │
 │                    │                    │  Fetch memories    │                 │
 │                    │                    │◄───────────────────┤                 │
 │                    │                    │  { stressors,      │                 │
 │                    │                    │    emotions,       │                 │
 │                    │                    │    strategies... } │                 │
 │                    │                    │                    │                 │
 │                    │    Analyze mood,   │                    │                 │
 │                    │    find similar    │                    │                 │
 │                    │    entries         │                    │                 │
 │                    │                    ├────────────────────────────────────►│
 │                    │                    │  get_all_entries() │                 │
 │                    │                    │◄────────────────────────────────────┤
 │                    │                    │  past entries      │                 │
 │                    │                    │                    │                 │
 │                    │    Generate        │                    │                 │
 │                    │    response        │                    │                 │
 │                    │    (with memory!)  │                    │                 │
 │                    │                    │                    │                 │
 │                    │  Response JSON     │                    │                 │
 │                    │◄───────────────────┤                    │                 │
 │  AI Reply          │                    │                    │                 │
 │◄───────────────────┤                    │                    │                 │
 │                    │                    │                    │                 │
```

---

## Data Flow: How Memory Affects Responses

```
TURN 1: User shares experience
┌──────────────────────────────────────────┐
│ User: "I feel overwhelmed at work"       │
└──────────────────────────┬───────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
   ┌─────────┐     ┌──────────┐      ┌─────────────┐
   │ Backboard│     │ Firestore│      │ Analyze     │
   │ (empty)  │     │ Store    │      │ Emotion     │
   │          │     │ entry    │      │ "anxiety"   │
   └─────────┘     └──────────┘      └─────────────┘
                           │
                    ┌──────┘
                    ▼
        ┌─────────────────────┐
        │ AI Response:        │
        │ "That sounds        │
        │ tough. Tell me      │
        │ more?"              │
        │                     │
        │ (Generic - no       │
        │  memory context)    │
        └─────────────────────┘
                    │
                    ▼
        ┌─────────────────────────┐
        │ ✓ Store to Backboard:   │
        │   - "work stress"       │
        │   - "anxiety"           │
        │   - "overwhelming"      │
        └─────────────────────────┘

═════════════════════════════════════════════════════════════

TURN 2: User returns (days/weeks later)
┌─────────────────────────────────────────┐
│ User: "I'm stressed again"              │
└──────────────────────┬──────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
   ┌──────────┐  ┌──────────┐  ┌────────────┐
   │ Backboard│  │ Firebase │  │ Analyze    │
   │ ✨ LOADS │  │ Retrieve │  │ Emotion    │
   │ Previous │  │ past     │  │ "anxiety"  │
   │ memories:│  │ entries  │  └────────────┘
   │ - stress │  │ about    │
   │ - anxiety│  │ work     │
   │ - work   │  └──────────┘
   └──────────┘        │
        │              │
        └──────┬───────┘
               ▼
    ┌────────────────────────────┐
    │ AI Response (PERSONALIZED):│
    │ "I remember you mentioned  │
    │ work stress before. What   │
    │ happened this time?"       │
    │                            │
    │ (✨ Memory context used!)  │
    └────────────────────────────┘
```

---

## Memory Storage Structure

```
Backboard Assistant: arc-user_123
│
├─ Memory ID: mem_001
│  ├─ Content: "work deadlines"
│  ├─ Tag: "stressor"
│  └─ Created: 2026-03-10T14:30:00Z
│
├─ Memory ID: mem_002
│  ├─ Content: "anxiety"
│  ├─ Tag: "emotion"
│  └─ Created: 2026-03-10T14:30:00Z
│
├─ Memory ID: mem_003
│  ├─ Content: "perfectionism"
│  ├─ Tag: "stressor"
│  └─ Created: 2026-03-12T10:15:00Z
│
├─ Memory ID: mem_004
│  ├─ Content: "meditation helps"
│  ├─ Tag: "strategy"
│  └─ Created: 2026-03-12T10:15:00Z
│
├─ Memory ID: mem_005
│  ├─ Content: "prefers validation over advice"
│  ├─ Tag: "support_style"
│  └─ Created: 2026-03-14T09:00:00Z
│
├─ Memory ID: mem_006
│  ├─ Content: "stress increases on Mondays"
│  ├─ Tag: "pattern"
│  └─ Created: 2026-03-14T09:00:00Z
│
└─ Memory ID: mem_007
   ├─ Content: "User is driven but needs work-life balance"
   ├─ Tag: "session_summary"
   └─ Created: 2026-03-14T09:00:00Z

Total: 7 memories organized by tag
```

---

## LLM Prompt Construction

```
WITHOUT BACKBOARD MEMORY:
┌─────────────────────────────────────┐
│ System Prompt                       │
│ (generic mental wellness guidelines)│
│                                     │
│ User Message:                       │
│ "I feel overwhelmed"                │
│                                     │
│ Chat History: (empty)               │
│                                     │
│ Similar Entries: (empty)            │
└─────────────────────────────────────┘
         │
         ▼
    ┌─────────────────┐
    │ OpenAI LLM      │
    │                 │
    │ [Generic logic] │
    └─────────────────┘
         │
         ▼
    Response: "That sounds hard. Can you tell me more?"


═════════════════════════════════════════════════════════════

WITH BACKBOARD MEMORY:
┌─────────────────────────────────────────────────────┐
│ System Prompt                                       │
│ (generic mental wellness guidelines)                │
│                                                     │
│ USER MEMORY:  ✨ ← FROM BACKBOARD                  │
│ - Stressors: work deadlines, perfectionism         │
│ - Emotions: anxiety, overwhelm                     │
│ - Strategies: meditation, talking to friends      │
│ - Preferences: validation, not advice             │
│ - Patterns: stress on Mondays                      │
│ - Summary: Driven but needs balance               │
│                                                     │
│ SIMILAR PAST ENTRIES:  ← FROM FIREBASE            │
│ - (past entries with similar emotions)             │
│                                                     │
│ CHAT HISTORY: (previous messages)                  │
│                                                     │
│ User Message:                                       │
│ "I feel overwhelmed"                               │
└─────────────────────────────────────────────────────┘
         │
         ▼
    ┌─────────────────┐
    │ OpenAI LLM      │
    │                 │
    │ [Rich context!] │
    └─────────────────┘
         │
         ▼
    Response: "I remember you struggle with perfectionism at work.
               This Monday overwhelm again? What's happening?"


Note: Same user, same message, completely different response!
      Reason: Backboard memory provides context
```

---

## State Transitions: Memory Lifecycle

```
┌─────────────┐
│  NEW USER   │
└──────┬──────┘
       │
       ├─ POST /api/chat/ (first message)
       │
       ▼
┌────────────────────────────┐
│ Check if assistant exists  │
│ (Backboard)                │
│ Result: NO                 │
└────────┬───────────────────┘
         │
         ├─ CREATE new assistant
         │  Name: "arc-user_123"
         │
         ▼
┌────────────────────────────┐
│ Load profile               │
│ (Backboard)                │
│ Result: EMPTY              │
└────────┬───────────────────┘
         │
         ├─ Generate response (generic)
         │  Store insights to Firebase
         │
         ▼
┌────────────────────────────┐
│  EXISTING USER (Day 1)     │
│  Assistant created         │
│  No memories yet           │
└────────┬───────────────────┘
         │
         ├─ POST /api/chat/ (subsequent messages)
         │
         ▼
┌────────────────────────────┐
│ Check if assistant exists  │
│ (Backboard)                │
│ Result: YES                │
└────────┬───────────────────┘
         │
         ├─ REUSE assistant
         │
         ▼
┌────────────────────────────┐
│ Load profile               │
│ (Backboard)                │
│ Result: EMPTY              │
└────────┬───────────────────┘
         │
         ├─ Generate response
         │  Store insights + emotions
         │
         ▼
┌────────────────────────────┐
│  ESTABLISHED USER (Day 8+) │
│  Assistant exists          │
│  Memories accumulating     │
└────────┬───────────────────┘
         │
         ├─ POST /api/chat/ (user returns)
         │
         ▼
┌────────────────────────────┐
│ Check if assistant exists  │
│ (Backboard)                │
│ Result: YES                │
└────────┬───────────────────┘
         │
         ├─ REUSE assistant
         │
         ▼
┌────────────────────────────┐
│ Load profile               │
│ (Backboard)                │
│ Result: ✨ RICH PROFILE    │
│  - Multiple stressors      │
│  - Recurring emotions      │
│  - Known strategies        │
│  - Support preferences     │
│  - Patterns identified     │
└────────┬───────────────────┘
         │
         ├─ Generate PERSONALIZED response
         │  (uses memory context!)
         │  Update/enrich profile
         │
         ▼
┌────────────────────────────┐
│  MATURE USER (6+ months)   │
│  Rich memory history       │
│  Deep personalization      │
│  Strong context awareness  │
└────────────────────────────┘
```

---

## Error Handling Flow

```
┌──────────────────────┐
│ Chat Request         │
└──────────┬───────────┘
           │
           ▼
    ┌──────────────┐
    │ Get/Create   │
    │ Assistant    │
    └──┬───────┬───┘
       │       │
   SUCCESS  FAILURE
       │       │
       ▼       ▼
    [Continue] ┌──────────────────┐
               │ Log Error        │
               │ Raise RuntimeErr │
               │ → Request fails  │
               └──────────────────┘
           │
           ▼
    ┌──────────────┐
    │ Load Profile │
    │ from Backend │
    └──┬───────┬───┘
       │       │
   SUCCESS  FAILURE
       │       │
       ▼       ▼
    [Continue] ┌──────────────────┐
               │ Log Warning      │
               │ Use empty profile│
               │ Continue chat    │
               │ (degraded mode)  │
               └──────────────────┘
           │
           ▼
    ┌──────────────┐
    │ Generate     │
    │ Response     │
    └──┬───────┬───┐
       │       │   │
   SUCCESS  RETRY  FAILURE
       │       │   │
       ▼       ▼   ▼
    [Return] [x2] ┌──────────────────┐
                  │ Return error     │
                  │ response to user │
                  └──────────────────┘
```

---

## Integration Points

```
┌─────────────────────────────────────────────────────────┐
│                    Your Application                     │
└─────────────────────────────────────────────────────────┘
         │                         │
         │ Uses                    │ Uses
         ▼                         ▼
┌──────────────────┐      ┌──────────────────┐
│  Firebase        │      │  Backboard       │
│  (Journal Data)  │      │  (Memory Data)   │
│                  │      │                  │
│  - Entries       │      │  - Assistants    │
│  - Mood history  │      │  - Memories      │
│  - Timestamps    │      │  - Tags          │
│                  │      │  - Metadata      │
└──────────────────┘      └──────────────────┘
         ▲                         ▲
         │ Reads/Writes           │ Reads/Writes
         │                         │
┌────────┴──────────────────────────┴───────────┐
│     backend/ai/chat_agent.py                   │
│                                                │
│  - Loads memories (Backboard)                 │
│  - Retrieves similar entries (Firebase)       │
│  - Generates personalized responses           │
│  - Stores insights                            │
└────────┬──────────────────────────┬───────────┘
         │                          │
         └──────────────┬───────────┘
                        │
              Frontend receives response
```

---

## Summary Visual

```
┌────────────────────────────────────────────────────────┐
│                                                        │
│  Backboard.io provides:                                │
│                                                        │
│  ✓ Persistent user assistants                        │
│  ✓ Structured memory storage (tagged)                │
│  ✓ Multi-session context continuity                  │
│  ✓ Personalized response generation                  │
│                                                        │
│  Without Backboard:                                   │
│  User: "I feel anxious"                              │
│  AI: "That sounds hard. Tell me more?"               │
│  [Session ends → context lost]                       │
│                                                        │
│  With Backboard:                                      │
│  User: "I feel anxious"                              │
│  AI: "I see you have anxiety around deadlines.       │
│       Has a project deadline come up?"               │
│  [User returns next week → same context!]            │
│  AI: "How are those deadlines treating you now?"     │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

See documentation files for code and setup details:
- `BACKBOARD_QUICK_START.md` - Get started quickly
- `BACKBOARD_INTEGRATION_GUIDE.md` - Complete reference
- `BACKBOARD_CODE_EXAMPLES.md` - Code samples
