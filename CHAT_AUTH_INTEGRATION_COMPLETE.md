# Chat Authentication Integration - Completed Changes

## Summary of Changes

This document records the changes made to integrate JWT authentication into the chat system, fixing the `test_user` hardcoding issue.

### Changes Made

#### 1. Frontend: ChatPage.jsx

**File**: `frontend/src/pages/ChatPage.jsx`

**Changes**:
1. Added AuthContext import
2. Added useContext and useNavigate hooks
3. Extract `user` and `token` from AuthContext
4. Added authentication check in `handleSend()`
5. Changed request body to remove `user_id` (now from token)
6. Added Authorization header with JWT token

**Before**:
```jsx
import { useState, useRef, useEffect } from "react";
import styles from './ChatPage.module.css';

const ChatPage = () => {
    const [messages, setMessages] = useState([INITIAL_MESSAGE]);
    // ...
    
    const handleSend = async (text) => {
        // ...
        const response = await fetch(`${API_BASE}/api/chat/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: 'test_user',  // ❌ HARDCODED
                message: content,
                chat_history: buildChatHistory(messages),
            }),
        });
```

**After**:
```jsx
import { useState, useRef, useEffect, useContext } from "react";
import { useNavigate } from "react-router-dom";
import AuthContext from "../contexts/AuthContext";
import styles from './ChatPage.module.css';

const ChatPage = () => {
    const { user, token } = useContext(AuthContext);  // ✅ USE AUTH CONTEXT
    const navigate = useNavigate();
    const [messages, setMessages] = useState([INITIAL_MESSAGE]);
    // ...
    
    const handleSend = async (text) => {
        const content = (text || input).trim();
        if (!content) return;

        // ✅ CHECK AUTHENTICATION
        if (!user || !token) {
            const errorMsg = {
                id: Date.now() + 1,
                role: 'assistant',
                text: "Please log in to use chat. Redirecting you to login...",
                time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            };
            setMessages((prev) => [...prev, errorMsg]);
            setTimeout(() => navigate('/login'), 2000);
            return;
        }
        
        // ... add message to state ...
        
        const response = await fetch(`${API_BASE}/api/chat/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,  // ✅ SEND JWT TOKEN
            },
            body: JSON.stringify({
                // ✅ REMOVED user_id (now comes from token)
                message: content,
                chat_history: buildChatHistory(messages),
            }),
        });
```

#### 2. Backend: chat.py

**File**: `backend/api/chat.py`

**Changes**:
1. Added `Depends` import from FastAPI
2. Added `get_current_user_id` import from auth module
3. Modified `ChatRequest` model to remove `user_id` field
4. Added `user_id: str = Depends(get_current_user_id)` parameter to endpoint
5. Updated docstring to document authentication requirement
6. Now extracts `user_id` from JWT token instead of request body

**Before**:
```python
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict

from backend.ai.chat_agent import run_chatbot_turn
from backend.ai.memory import get_or_create_assistant

router = APIRouter(prefix="/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    user_id: str  # ❌ ACCEPTED FROM REQUEST BODY (SECURITY ISSUE)
    message: str
    chat_history: List[Dict] = []

@router.post("/")
async def chat_with_ai(request: ChatRequest):  # ❌ NO AUTHENTICATION
    assistant_id = await get_or_create_assistant(request.user_id)
    result = await run_chatbot_turn(
        user_message=request.message,
        assistant_id=assistant_id,
        user_id=request.user_id,
        chat_history=request.chat_history,
    )
    return result
```

**After**:
```python
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Dict

from backend.ai.chat_agent import run_chatbot_turn
from backend.ai.memory import get_or_create_assistant
from backend.api.auth import get_current_user_id  # ✅ IMPORT AUTH

router = APIRouter(prefix="/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    # ✅ REMOVED user_id (now comes from JWT token)
    message: str
    chat_history: List[Dict] = []

@router.get("/health")
def chat_health():
    return {"status": "chat ok"}

@router.post("/")
async def chat_with_ai(
    request: ChatRequest,
    user_id: str = Depends(get_current_user_id),  # ✅ EXTRACT FROM TOKEN
):
    """
    Chat endpoint - requires JWT authentication.
    User ID is extracted from the Authorization header token.
    """
    assistant_id = await get_or_create_assistant(user_id)

    result = await run_chatbot_turn(
        user_message=request.message,
        assistant_id=assistant_id,
        user_id=user_id,  # ✅ FROM AUTHENTICATED TOKEN
        chat_history=request.chat_history,
    )
    return result
```

---

## Data Flow After Fix

### Chat Authentication Flow (NEW ✅)

```
1. User types message
   ↓
2. User clicks "Send"
   ↓
3. ChatPage checks: if (!user || !token) redirect to login
   ✅ Authentication required before sending
   ↓
4. Sends: POST /api/chat/
   Headers: Authorization: Bearer {JWT_TOKEN}
   Body: {message: "...", chat_history: [...]}
   ✓ No user_id in body
   ↓
5. Backend get_current_user_id():
   - Extracts token from Authorization header
   - Validates signature with SECRET_KEY
   - Returns verified user_id from token
   ✅ Authentication succeeds or 401 Unauthorized
   ↓
6. run_chatbot_turn(user_id=verified_id, ...)
   - Uses Backboard API with authenticated user_id
   - Creates assistant: "arc-{verified_id}"
   - Stores memories under user's account
   ✅ All chat data isolated per user
```

### Complete User Flow (All Systems)

```
New User:
1. Navigate to /signup
   ↓
2. Fill signup form (email, password, name)
   ↓
3. POST /api/auth/signup
   - Creates Firebase Auth user
   - Creates Firestore profile
   - Returns JWT token
   ↓
4. Frontend stores token in sessionStorage
   ↓
5. User authenticated, can now:
   - Submit journal entries ✅
   - Chat with AI ✅
   - View progress/insights ✅
   ↓
All data is tied to user_id from JWT token

Returning User:
1. Navigate to /login
   ↓
2. Fill login form (email, password)
   ↓
3. POST /api/auth/login
   - Validates email with Firebase Auth
   - Returns JWT token
   ↓
4. Frontend stores token in sessionStorage
   ↓
5. User authenticated, accesses previous:
   - Journal entries (from Firebase)
   - Chat history (from Backboard)
   - Mood data (from Firebase)
```

---

## Security Improvements

### Before (Vulnerable)
- ❌ User ID sent in request body (user_id can be spoofed)
- ❌ No authentication check
- ❌ Anyone could pretend to be any user
- ❌ No token required
- ❌ All users' chat merged under test_user

### After (Secure)
- ✅ User ID comes from JWT token (cryptographically signed)
- ✅ Token validated using SECRET_KEY
- ✅ Cannot forge valid token without SECRET_KEY
- ✅ Authentication required (401 Unauthorized if missing/invalid)
- ✅ Each user has isolated chat history
- ✅ Can verify user identity server-side

---

## Testing the Changes

### Prerequisites
1. Backend running: `uvicorn backend.api.main:app --reload`
2. Frontend running: `npm start` (in frontend directory)
3. Have valid JWT token from login or signup

### Test 1: Unauthenticated Chat Request

```bash
curl -X POST http://127.0.0.1:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello",
    "chat_history": []
  }'
```

**Expected Result**: 
```json
{
  "detail": "Not authenticated"
}
```
**Status**: 403 Unauthorized ✅

### Test 2: Chat with Valid Token

First, get a token from login:
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

Then use token in chat request:
```bash
curl -X POST http://127.0.0.1:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token_from_login}" \
  -d '{
    "message": "How are you?",
    "chat_history": []
  }'
```

**Expected Result**: 
```json
{
  "response": {
    "reply": "...",
    "open_question": "..."
  }
}
```
**Status**: 200 OK ✅

### Test 3: Chat from Frontend

1. Navigate to login page
2. Sign up or log in with credentials
3. Navigate to chat page
4. Send a message
5. Should see response (not "Chat error")

**Expected**: Message is sent and response received ✅

---

## What Still Needs to Be Done

### High Priority

1. **Create Login/Signup Pages** (Frontend)
   - Currently users have no way to authenticate
   - Need `/login` and `/signup` routes
   - Need forms for email/password input
   - Need to call signup/login endpoints

2. **Test End-to-End Authentication**
   - Signup with real user
   - Submit journal entry (should save to Firebase)
   - Submit chat message (should save to Backboard)
   - Verify data isolation

### Medium Priority

1. **Update Test Scripts**
   - `test_chatbot.py`: Should obtain JWT token first
   - `test_agent.py`: Same
   - `seed_test_entries.py`: Same

2. **Add Auth Guards to Other Pages**
   - HomePage: Check auth before loading progress
   - JournalPage: Check auth before loading entries
   - ProgressPage: Check auth before loading analytics

3. **Improve Error Handling**
   - Show better error messages for auth failures
   - Handle token expiration (24 hours)
   - Implement token refresh mechanism

### Low Priority

1. **Delete Hardcoded Test User Data** (After testing new flow)
   - Remove test_user entries from Firebase
   - Create real test users instead
   - Update all test files

2. **Add Loading States**
   - Show loading spinner during auth
   - Show loading during token verification

---

## Files Modified

| File | Changes | Status |
|------|---------|--------|
| `frontend/src/pages/ChatPage.jsx` | Added AuthContext, removed hardcoded test_user, added auth check | ✅ Complete |
| `backend/api/chat.py` | Added authentication requirement, extract user_id from token | ✅ Complete |

## Files Not Modified (But Relevant)

| File | Reason | Status |
|------|--------|--------|
| `backend/api/auth.py` | Already implemented signup, login, token generation | ✅ No changes needed |
| `frontend/src/contexts/AuthContext.jsx` | Already implemented, working with JournalEditor | ✅ No changes needed |
| `frontend/src/features/journal/components/JournalEditor.jsx` | Already using AuthContext correctly | ✅ No changes needed |

---

## Next Steps

**Immediate** (Complete authentication integration):
1. Create login/signup pages
2. Test signup → login → journal entry → Firebase
3. Test signup → login → chat → Backboard
4. Verify data isolation between users

**Follow-up** (Improve robustness):
1. Add auth guards to protected pages
2. Handle token expiration
3. Implement token refresh
4. Update test scripts
5. Delete test_user data

---

**Last Updated**: Current session
**Status**: Chat authentication integration COMPLETE ✅
**Next Review**: After creating login/signup pages and testing end-to-end flow
