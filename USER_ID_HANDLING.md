# User ID Handling: Where Does user_id Come From?

## TL;DR

**In Production/Real App:**
- User logs in → receives JWT token
- Token contains `user_id`
- Backend extracts `user_id` from token via `Depends(get_current_user_id)`
- API ensures only authenticated users can access their own data

**In Testing/Development:**
- `user_id` is hardcoded as `"test_user"` in test files
- Used for local testing without authentication
- Not suitable for production

---

## Two Flows: Authentication vs Testing

### Flow 1: Real User (Production) ✅

```
User (Frontend)
    ↓
User enters email + password
    ↓
POST /auth/login
    ↓
Backend verifies with Firebase Auth
    ↓
Backend generates JWT token with user_id
    ↓
Response: {token: "eyJ0eXAiOiJKV1QiLCJhbGc..."}
    ↓
User stores token (localStorage)
    ↓
User requests journal entry: POST /journal-entry
  Headers: Authorization: Bearer {token}
    ↓
Backend: get_current_user_id(authorization) 
  └─ Extracts and verifies user_id from token
    ↓
save_entry(user_id="user_123", ...)
    ↓
Only this user's data is accessed
```

### Flow 2: Test User (Development) ❌ Not for Production

```
Test script or frontend
    ↓
Hardcode: user_id = "test_user"
    ↓
POST /chat/  (NO authorization header)
{
  "user_id": "test_user",
  "message": "...",
  "chat_history": []
}
    ↓
Backend ignores missing auth (chat endpoint not protected)
    ↓
run_chatbot_turn(user_id="test_user", ...)
    ↓
Data stored with user_id = "test_user"
```

---

## Where test_user Is Hardcoded

| File | Line | Purpose | Status |
|------|------|---------|--------|
| `test_chatbot.py` | 11 | Multi-turn chat testing | ⚠️ Hardcoded |
| `seed_test_entries.py` | 8 | Populate test data | ⚠️ Hardcoded |
| `frontend/src/pages/ChatPage.jsx` | 70 | Frontend chat | ⚠️ Hardcoded |

### 1. Test Chatbot Script

```python
# test_chatbot.py - Lines 1-11
import asyncio
from backend.ai.chat_agent import run_chatbot_turn
from backend.ai.memory import get_or_create_assistant
from backend.db.firebase_client import init_firebase

async def main():
    init_firebase()

    user_id = "test_user"  # ← HARDCODED
    assistant_id = await get_or_create_assistant(user_id)
    
    # Runs multi-turn conversation with test_user
```

**Purpose:** Test chat functionality without authentication

**Usage:**
```bash
python test_chatbot.py
```

### 2. Seed Test Entries Script

```python
# seed_test_entries.py - Lines 1-8
from backend.db.firebase_client import init_firebase
from backend.db.queries import save_entry
from backend.embeddings.embedding_service import generate_embedding

def main():
    init_firebase()

    user_id = "test_user"  # ← HARDCODED
    
    entries = [
        "I have been really stressed about my midterms and deadlines lately.",
        # ... more entries
    ]
    
    for text in entries:
        embedding = generate_embedding(text)
        entry_id = save_entry(user_id, text, embedding)
```

**Purpose:** Populate Firebase with sample data for "test_user"

**Usage:**
```bash
python seed_test_entries.py
```

**Result:** Firebase now has entries under `diary_entries` with `user_id="test_user"`

### 3. Frontend Chat Page

```jsx
// frontend/src/pages/ChatPage.jsx - Lines 60-80
const response = await fetch(`${API_BASE}/api/chat/`, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        user_id: 'test_user', // ← HARDCODED - comment says "replace later"
        message: content,
        chat_history: buildChatHistory(messages),
    }),
});
```

**Purpose:** Frontend testing without login

**Comment:** `// replace later with real logged-in user id`

**Should be:**
```jsx
// Get from context/state after user logs in
const { user } = useAuth();  // or get from localStorage, etc.
body: JSON.stringify({
    user_id: user.uid,  // Real user ID from authentication
    message: content,
    chat_history: buildChatHistory(messages),
})
```

---

## Real Authentication Flow

### Backend: `get_current_user_id()` 

```python
# backend/api/auth.py - Lines 138-163

def get_current_user_id(authorization: str = Header(None)) -> str:
    """
    Dependency to extract and verify user ID from Bearer token.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authorization scheme")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    verified = verify_token(token)  # Validates JWT signature
    return verified["user_id"]  # Extracts user_id from token payload
```

**How it works:**
1. Reads `Authorization` header from request
2. Parses: `"Bearer {token}"`
3. Decodes JWT token
4. Verifies signature (ensures token wasn't tampered with)
5. Extracts `user_id` from token payload
6. Returns user_id to endpoint

### Protected Endpoints (Using Auth)

```python
# backend/api/diary.py - Lines 7, 33

from backend.api.auth import get_current_user_id

@router.post("/journal-entry")
async def save_journal_entry(
    data: JournalEntryRequest, 
    user_id: str = Depends(get_current_user_id)  # ✅ PROTECTED
):
    # user_id is automatically extracted from token
    # User cannot access other users' data
```

### Unprotected Endpoints (No Auth)

```python
# backend/api/chat.py - Lines 19-30

@router.post("/")
async def chat_with_ai(request: ChatRequest):
    # ❌ NO AUTHENTICATION
    # user_id comes from request body (client can send anything!)
    assistant_id = await get_or_create_assistant(request.user_id)
```

**Problem:** Frontend can send any `user_id`

```javascript
// Frontend could do this:
{
    user_id: "hacker_user",  // Impersonate another user!
    message: "..."
}
```

---

## Current Status: Auth Implementation

### ✅ Implemented

- JWT token generation on signup/login
- `get_current_user_id()` dependency function
- Protected endpoints: `/journal-entry`, `/progress`, `/moods`
- Token verification with signature checking
- User profile creation and retrieval

### ❌ NOT Protected

- `/chat/` endpoint - Missing `Depends(get_current_user_id)`
- Frontend hardcodes `user_id: 'test_user'`

### 🔧 Needs Fixing

1. **Add auth to chat endpoint**
```python
# backend/api/chat.py
from backend.api.auth import get_current_user_id

@router.post("/")
async def chat_with_ai(
    request: ChatRequest, 
    user_id: str = Depends(get_current_user_id)  # ← ADD THIS
):
    # Use parameter user_id, ignore request.user_id
    assistant_id = await get_or_create_assistant(user_id)
    result = await run_chatbot_turn(
        user_message=request.message,
        assistant_id=assistant_id,
        user_id=user_id,  # ← Use from token, not request
        chat_history=request.chat_history,
    )
    return result
```

2. **Update frontend to use real user ID**
```jsx
// frontend/src/pages/ChatPage.jsx
import { useAuth } from '../contexts/AuthContext';  // or similar

export default function ChatPage() {
    const { user } = useAuth();  // Get logged-in user
    
    // In sendMessage function:
    const response = await fetch(`${API_BASE}/api/chat/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${user.token}`,  // Include token
        },
        body: JSON.stringify({
            message: content,
            chat_history: buildChatHistory(messages),
            // ❌ Don't send user_id in body (get from token instead)
        }),
    });
}
```

3. **Update ChatRequest model**
```python
# backend/api/chat.py
class ChatRequest(BaseModel):
    message: str
    chat_history: List[Dict] = []
    # Remove user_id - it comes from token now
```

---

## Token Payload Structure

When a user logs in, the backend creates a JWT token like:

```python
# backend/api/auth.py (create_access_token function)
payload = {
    "user_id": "user_123",
    "email": "user@example.com",
    "exp": datetime.utcnow() + timedelta(hours=24),
    "iat": datetime.utcnow()
}

token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
# Result: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

When the token is verified:

```python
# backend/api/auth.py (verify_token function)
decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
# Result: {"user_id": "user_123", "email": "...", "exp": ..., "iat": ...}
```

---

## Multi-User Example: How Auth Prevents Cross-User Access

```
Scenario: Two users logged in simultaneously

User A:
  Token contains: {user_id: "user_A", ...}
  
  POST /journal-entry
  Headers: Authorization: Bearer token_A
    ↓
  Backend extracts: user_id = "user_A"
    ↓
  save_entry("user_A", text, embedding)
    ↓
  Data stored with user_id = "user_A" only

User B:
  Token contains: {user_id: "user_B", ...}
  
  POST /journal-entry
  Headers: Authorization: Bearer token_B
    ↓
  Backend extracts: user_id = "user_B"
    ↓
  save_entry("user_B", text, embedding)
    ↓
  Data stored with user_id = "user_B" only

If User B tries to use User A's token:
  Token contains: {user_id: "user_A", ...}
  
  But User B can't get User A's token
  (Tokens stored securely on client, rotated on logout)

If User B manually creates token:
  Backend verifies signature
  Signature won't match (only backend knows SECRET_KEY)
  Request rejected with 401 Unauthorized
```

---

## Summary Table

| Aspect | Testing | Production |
|--------|---------|------------|
| **user_id Source** | Hardcoded in code | JWT token |
| **Authentication** | None | Required |
| **User Isolation** | Manual (hardcoded) | Automatic (verified token) |
| **Security** | None (unsafe) | High (JWT signature verification) |
| **Files Affected** | test scripts, frontend | All endpoints |
| **Current Status** | Working for MVP | Partially implemented |

---

## What Happens With test_user

### Current Setup

```
1. Seed data:
   python seed_test_entries.py
   → Saves 4 entries to Firebase with user_id="test_user"

2. Test chat:
   python test_chatbot.py
   → Runs chatbot with user_id="test_user"
   → References same entries from step 1

3. Test frontend:
   Frontend hardcodes user_id="test_user"
   → Chat uses same test_user
   → No authentication required
```

### Firebase State After Testing

```
diary_entries collection:
  - doc1: {user_id: "test_user", text: "stressed about midterms", ...}
  - doc2: {user_id: "test_user", text: "feeling overwhelmed", ...}
  - doc3: {user_id: "test_user", text: "anxious about exams", ...}
  - doc4: {user_id: "test_user", text: "workload feels heavy", ...}

mood_history collection:
  - doc1: {user_id: "test_user", mood: "anxiety", ...}
  - doc2: {user_id: "test_user", mood: "overwhelm", ...}
  - ...

user_profiles collection:
  - test_user: {
      common_stressors: ["deadlines", "exams"],
      recurring_emotions: ["anxiety", "overwhelm"],
      ...
    }

Backboard API:
  - Assistant named: "arc-test_user"
  - Memories: [stressors, emotions, strategies, ...]
```

---

## Next Steps: Secure the Chat Endpoint

1. **Add auth to chat endpoint** ← High priority
2. **Update frontend to use real user ID** ← High priority
3. **Remove hardcoded test_user from production code** ← Medium priority
4. **Add tests for multi-user isolation** ← Medium priority
5. **Set up user session management** ← Long term

---

## Files Involved

| File | Purpose | Current Status |
|------|---------|-----------------|
| `backend/api/auth.py` | Auth endpoints, JWT, `get_current_user_id()` | ✅ Complete |
| `backend/api/diary.py` | Journal endpoint | ✅ Protected |
| `backend/api/chat.py` | Chat endpoint | ❌ NOT protected |
| `backend/api/insights.py` | Analytics endpoint | ✅ Protected |
| `backend/api/moods.py` | Mood endpoint | ✅ Protected |
| `test_chatbot.py` | Chat test script | ⚠️ Uses test_user |
| `seed_test_entries.py` | Seed test data | ⚠️ Uses test_user |
| `frontend/src/pages/ChatPage.jsx` | Frontend chat | ❌ Hardcoded test_user |

---

**Summary:** `test_user` is a hardcoded placeholder for testing. In production, real `user_id` comes from JWT tokens via `get_current_user_id()` dependency. The chat endpoint needs to be updated to use authentication like other protected endpoints.

See `JOURNAL_STORAGE_REFERENCE.md` for authentication code examples.
