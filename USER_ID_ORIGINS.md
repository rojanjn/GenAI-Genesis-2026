# User ID Origins: Quick Reference

## Where Does user_id Come From?

### Option 1: Real User (Production) ✅

```
Login: user@example.com + password
         ↓
POST /auth/login
         ↓
Backend: Verify with Firebase Auth
         ↓
Create JWT token:
{
  "user_id": "user_123",
  "email": "user@example.com",
  "exp": 2026-03-14T18:30:00,
  "iat": 2026-03-14T18:00:00
}
         ↓
Response: {token: "eyJ0eXAi..."}
         ↓
Frontend: Store token (localStorage)
         ↓
Next request: 
  Headers: Authorization: Bearer eyJ0eXAi...
         ↓
Backend: get_current_user_id()
  ├─ Parse: "Bearer {token}"
  ├─ Decode: JWT token
  ├─ Verify: Signature (SECRET_KEY)
  ├─ Extract: user_id from payload
  └─ Return: "user_123"
         ↓
save_entry(user_id="user_123", ...)
```

### Option 2: Test User (Development) ❌

```
Test script
         ↓
Hardcode: user_id = "test_user"
         ↓
No authentication
         ↓
run_chatbot_turn(user_id="test_user", ...)
         ↓
save_entry(user_id="test_user", ...)
```

---

## Hardcoded Locations

### 1. Test Script: `test_chatbot.py`

```python
async def main():
    init_firebase()
    
    user_id = "test_user"  # ← HERE (Line 11)
    assistant_id = await get_or_create_assistant(user_id)
    # ... runs multi-turn chat ...
```

**Usage:** `python test_chatbot.py`

### 2. Seed Script: `seed_test_entries.py`

```python
def main():
    init_firebase()
    
    user_id = "test_user"  # ← HERE (Line 8)
    
    entries = [...]
    for text in entries:
        embedding = generate_embedding(text)
        entry_id = save_entry(user_id, text, embedding)
```

**Usage:** `python seed_test_entries.py`

### 3. Frontend: `frontend/src/pages/ChatPage.jsx`

```jsx
const response = await fetch(`${API_BASE}/api/chat/`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        user_id: 'test_user',  // ← HERE (Line 70)
        message: content,
        chat_history: buildChatHistory(messages),
    }),
});
```

**Issue:** Comment says `// replace later with real logged-in user id`

---

## Protected vs Unprotected Endpoints

### Protected Endpoints ✅

```python
# These use get_current_user_id() dependency
# User ID comes from JWT token

@router.post("/journal-entry")
async def save_journal_entry(
    data: JournalEntryRequest,
    user_id: str = Depends(get_current_user_id)  # ✅ From token
):
    save_entry(user_id, data.entry, embedding)

@router.get("/progress/{user_id}")
async def get_progress(
    user_id: str,
    current_user: str = Depends(get_current_user_id)  # ✅ From token
):
    # Verify current_user == user_id (prevent cross-user access)

@router.post("/mood")
async def record_mood(
    data: MoodRequest,
    user_id: str = Depends(get_current_user_id)  # ✅ From token
):
    save_mood(user_id, data.mood, data.intensity)
```

### Unprotected Endpoints ❌

```python
# No authentication - anyone can call
# user_id comes from request body (client decides)

@router.post("/chat/")
async def chat_with_ai(request: ChatRequest):
    # request.user_id = whatever client sends!
    # Could be "test_user", "hacker", "anyone"
    
    assistant_id = await get_or_create_assistant(request.user_id)
    # Uses untrusted user_id
```

---

## How JWT Token Works

### Creation (At Login)

```python
# backend/api/auth.py
import jwt
from datetime import datetime, timedelta

SECRET_KEY = "super-secret-key-stored-safely"  # ← Only backend knows this

def create_access_token(user_id: str) -> str:
    payload = {
        "user_id": user_id,
        "email": user_email,
        "exp": datetime.utcnow() + timedelta(hours=24),
        "iat": datetime.utcnow()
    }
    
    # Encode with SECRET_KEY
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    
    # Result: "eyJ0eXAiOiJKV1QiLCJhbGc..."
    return token
```

### Verification (At Each Request)

```python
# backend/api/auth.py
def verify_token(token: str) -> dict:
    try:
        # Decode with SECRET_KEY
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        
        # Check expiration
        if decoded["exp"] < datetime.utcnow():
            raise HTTPException(status_code=401, detail="Token expired")
        
        return decoded  # {"user_id": "user_123", "email": "...", ...}
    
    except jwt.InvalidSignatureError:
        raise HTTPException(status_code=401, detail="Invalid token signature")
```

### Extraction (In Endpoint)

```python
# backend/api/auth.py
def get_current_user_id(authorization: str = Header(None)) -> str:
    # Extract token from header
    scheme, token = authorization.split()  # "Bearer {token}"
    
    # Verify and decode
    verified = verify_token(token)
    
    # Return user_id
    return verified["user_id"]  # "user_123"
```

---

## Why Hardcoding test_user Is Bad

### Problem 1: No User Isolation

```
User A (in browser):
  fetch('/api/chat/', {
    user_id: 'test_user',
    message: 'my secrets'
  })

User B (in other browser):
  fetch('/api/chat/', {
    user_id: 'test_user',
    message: 'my secrets'
  })

Result: Both users share same data!
```

### Problem 2: Can't Have Multiple Users

```
test_user 1 and test_user 2 don't exist
All data goes to single "test_user"
Can't test multi-user scenarios
```

### Problem 3: Impersonation Risk

```
Attacker:
  fetch('/api/chat/', {
    user_id: 'victim_user',
    message: 'accessing their data'
  })

Backend doesn't verify the user_id is real
Attacker can access anyone's data
```

---

## What test_user Represents

```
Firebase Data After Running Tests:
diary_entries/
  ├─ doc1: {user_id: "test_user", text: "stressed about midterms"}
  ├─ doc2: {user_id: "test_user", text: "feeling overwhelmed"}
  ├─ doc3: {user_id: "test_user", text: "anxious about exams"}
  └─ doc4: {user_id: "test_user", text: "workload feels heavy"}

mood_history/
  ├─ doc1: {user_id: "test_user", mood: "anxiety"}
  ├─ doc2: {user_id: "test_user", mood: "overwhelm"}
  └─ ...

user_profiles/
  └─ test_user: {
       common_stressors: ["deadlines", "exams"],
       recurring_emotions: ["anxiety", "overwhelm"],
       helpful_strategies: ["meditation"],
       ...
     }

Backboard API:
  └─ Assistant: "arc-test_user" with memories
```

All data belongs to a **single fictional user** for testing purposes.

---

## Comparison Table

| Aspect | test_user (Current) | Real User (Needed) |
|--------|-------------------|-------------------|
| **Source** | Hardcoded in code | JWT token |
| **Unique per user** | ❌ Single user | ✅ One per login |
| **Secure** | ❌ No | ✅ Yes (signature verified) |
| **Can test multi-user** | ❌ No | ✅ Yes |
| **Prevents impersonation** | ❌ No | ✅ Yes |
| **Production ready** | ❌ No | ✅ Yes |

---

## To Fix: Enable Real Users

### Backend Change

```python
# backend/api/chat.py - BEFORE
@router.post("/")
async def chat_with_ai(request: ChatRequest):
    # ❌ Uses user_id from request
    user_id = request.user_id

# backend/api/chat.py - AFTER
from backend.api.auth import get_current_user_id

@router.post("/")
async def chat_with_ai(
    request: ChatRequest,
    user_id: str = Depends(get_current_user_id)  # ✅ From token
):
    # ✅ Uses user_id from authentication
```

### Frontend Change

```jsx
// BEFORE
body: JSON.stringify({
    user_id: 'test_user',  // ❌ Hardcoded
    message: content,
})

// AFTER
import { useAuth } from '../contexts/AuthContext';

export default function ChatPage() {
    const { user, token } = useAuth();
    
    fetch('/api/chat/', {
        headers: {
            'Authorization': `Bearer ${token}`,  // ✅ Include token
        },
        body: JSON.stringify({
            message: content,  // ✅ No user_id in body
            chat_history: buildChatHistory(messages),
        }),
    })
}
```

---

## Files Needing Updates

| File | Issue | Fix |
|------|-------|-----|
| `backend/api/chat.py` | Missing auth | Add `Depends(get_current_user_id)` |
| `frontend/src/pages/ChatPage.jsx` | Hardcoded user | Use logged-in user from context |
| `test_chatbot.py` | Uses test_user | Keep for local testing, document as dev-only |
| `seed_test_entries.py` | Uses test_user | Keep for seeding test data, document as dev-only |

---

See `USER_ID_HANDLING.md` for complete details.
