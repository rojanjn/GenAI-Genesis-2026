# Authentication Integration Status Report

## Executive Summary

**Current Status**: Frontend authentication context is **partially implemented**. Authentication works for journal entries but **NOT for chat**, causing the "test_user hardcoding" issue.

**Root Cause**: 
- ✅ Backend: Fully implemented JWT authentication (signup, login, protected endpoints)
- ✅ Frontend: AuthContext created and integrated with JournalEditor
- ❌ Frontend: ChatPage.jsx NOT using AuthContext, still hardcoded to `test_user`
- ❌ Backend: `/api/chat/` endpoint NOT protected, accepts `user_id` from request body

---

## Detailed Status by Component

### ✅ WORKING: Authentication System (Backend)

**File**: `backend/api/auth.py`

#### Signup Endpoint (Lines 170-233)
```python
@router.post("/signup")
async def signup(credentials: SignupRequest):
    # 1. Creates Firebase Auth user
    # 2. Creates Firestore profile document
    # 3. Generates JWT token
    # Returns: TokenResponse {token, user_id, email, display_name}
```

- **Token Generation**: `create_access_token(user_id, email)` 
- **Algorithm**: HS256 with SECRET_KEY from .env
- **Expiration**: 24 hours
- **Payload**: `{user_id, email, exp, iat}`

#### Login Endpoint (Lines 235-288)
```python
@router.post("/login")
async def login(credentials: LoginRequest):
    # 1. Validates email exists in Firebase Auth
    # 2. Generates JWT token
    # 3. Returns TokenResponse
```

#### Token Verification (Lines 138-163)
```python
def get_current_user_id(authorization: str = Header(None)):
    # Extracts "Bearer {token}" from Authorization header
    # Validates signature with SECRET_KEY
    # Returns verified user_id
```

#### Protected Endpoints Using JWT
- ✅ `POST /api/journal-entry` - Uses `Depends(get_current_user_id)`
- ✅ `GET /api/progress/{user_id}` - Uses `Depends(get_current_user_id)`  
- ✅ `GET /api/moods` - Uses `Depends(get_current_user_id)`

---

### ✅ WORKING: Journal Entry with Authentication (Frontend)

**File**: `frontend/src/features/journal/components/JournalEditor.jsx`

#### AuthContext Integration (Lines 80-81, 148)
```jsx
const { user, token } = useContext(AuthContext);
// ...
if (isEmpty || !user || !token) return; // Prevents save if not authenticated
```

#### Authenticated API Call (Lines 155-165)
```jsx
const response = await fetch(`${API_BASE_URL}/api/journal-entry`, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,  // ✅ SENDING TOKEN
    },
    body: JSON.stringify({
        user_id: user.uid,  // ✅ USING REAL USER ID FROM CONTEXT
        prompt: PROMPTS[promptIndex],
        entry: editor.getHTML(),
        entry_text: content,
    }),
});
```

**Result**: Journal entries ARE saved to Firebase with correct user_id ✅

---

### ❌ BROKEN: Chat Without Authentication (Frontend)

**File**: `frontend/src/pages/ChatPage.jsx`

#### Missing AuthContext (No import)
- Does NOT import AuthContext
- Does NOT import useContext hook
- Does NOT check for authentication

#### Hardcoded test_user (Lines 60-73)
```jsx
const response = await fetch(`${API_BASE_URL}/api/chat/`, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        // ❌ NO Authorization header
    },
    body: JSON.stringify({
        user_id: 'test_user',  // ❌ HARDCODED
        message: content,
        chat_history: buildChatHistory(messages),
    }),
});
```

**Problems**:
1. Always sends same `user_id: 'test_user'`
2. Never sends Authorization header
3. Can't authenticate real users
4. All chat sessions merged under single test_user

---

### ❌ BROKEN: Chat Endpoint Without Protection (Backend)

**File**: `backend/api/chat.py` (Lines 19-30)

```python
@router.post("/")
async def chat_with_ai(request: ChatRequest):  # ❌ NO AUTHENTICATION
    assistant_id = await get_or_create_assistant(request.user_id)
    # Accept any user_id from request body
```

**Problems**:
1. No `Depends(get_current_user_id)` protection
2. Accepts `user_id` directly from POST body
3. Anyone can impersonate any user
4. Accepts requests without Authorization header

---

### ✅ WORKING: AuthContext Provider (Frontend)

**File**: `frontend/src/contexts/AuthContext.jsx`

#### State Management
```jsx
const [user, setUser] = useState(null);
const [token, setToken] = useState(null);
const [loading, setLoading] = useState(true);
const [error, setError] = useState(null);
```

#### Token Persistence (Lines 26-40)
```jsx
useEffect(() => {
    const storedToken = sessionStorage.getItem('auth_token');
    const storedUser = sessionStorage.getItem('auth_user');
    
    if (storedToken && storedUser) {
        // Restore from sessionStorage on page reload
        setToken(storedToken);
        setUser(JSON.parse(storedUser));
    }
    setLoading(false);
});
```

#### Signup Method (Lines 47-90)
```jsx
const signup = async (email, password, displayName) => {
    // POST /api/auth/signup
    // Receives: {token, user_id, email, display_name}
    // Stores token in sessionStorage
    // Returns user object
```

#### Login Method (Lines 102-140)
```jsx
const login = async (email, password) => {
    // POST /api/auth/login
    // Receives: {token, user_id, email, display_name}
    // Stores token in sessionStorage
    // Returns user object
```

#### Logout Method
```jsx
const logout = () => {
    // Clear sessionStorage and state
    sessionStorage.removeItem('auth_token');
    sessionStorage.removeItem('auth_user');
    setToken(null);
    setUser(null);
```

#### Context Value
```jsx
const value = {
    user,           // {uid, email, displayName}
    token,          // JWT token string
    loading,        // Auth loading status
    error,          // Auth error message
    login,          // async login(email, password)
    signup,         // async signup(email, password, displayName)
    logout,         // logout()
    isAuthenticated: !!token,  // Boolean
};
```

**Status**: Ready to use, just needs to be imported in ChatPage ✅

---

## Data Flow Comparison

### Journal Entry Flow (WORKING ✅)

```
1. User types journal entry
   ↓
2. User clicks "Save"
   ↓
3. JournalEditor checks: if (!user || !token) return;
   ↓
4. Sends: POST /api/journal-entry
   Headers: Authorization: Bearer {JWT_TOKEN}
   Body: {user_id: user.uid, entry: "..."}
   ↓
5. Backend get_current_user_id():
   - Extracts token from Authorization header
   - Validates signature with SECRET_KEY
   - Returns user_id from token
   ✅ Authentication succeeds
   ↓
6. save_entry(user_id, text, embedding)
   - Stores in Firebase with user_id field
   ✅ Only saves for authenticated user
```

### Chat Flow (BROKEN ❌)

```
1. User types message
   ↓
2. User clicks "Send"
   ↓
3. ChatPage sends: POST /api/chat/
   Headers: Content-Type: application/json
   ❌ NO Authorization header
   Body: {user_id: 'test_user', message: "..."}
   ↓
4. Backend /api/chat/:
   ❌ No authentication check
   ✅ Just accepts user_id from request body
   ↓
5. Uses: user_id = 'test_user' (from request body)
   ❌ Always same user
   ❌ No real user isolation
   ❌ Anyone can send any user_id
```

---

## Root Cause Analysis

### Why Are Only test_user Entries Saved?

**For Journal Entries**:
- Real users CAN save journal entries IF they're authenticated
- But they DON'T authenticate because they don't have a login page yet
- So they're never redirected to a login flow
- Therefore journal entries are never submitted with valid tokens

**For Chat**:
- Chat always uses hardcoded `test_user`
- Backend accepts it without checking
- All chat data belongs to `test_user`

**Test Setup**:
- `seed_test_entries.py` creates entries for `test_user`
- `test_chatbot.py` uses `test_user`
- `test_ai_flow.py` uses `test_user`
- Only `test_user` has any data in Firebase

### Why Frontend Auth Context Exists But Isn't Used

1. **Auth context is implemented** (AuthContext.jsx) for future use
2. **JournalEditor uses it** (proper implementation)
3. **ChatPage doesn't use it** (still has hardcoded test_user comment)
4. **No login page exists** (frontend can't initiate signup/login flow)
5. **Users can't authenticate** (no UI to call signup/login endpoints)

---

## Required Fixes

### 1. Fix Chat Frontend (Priority: HIGH)

**File**: `frontend/src/pages/ChatPage.jsx`

```jsx
// ADD THIS AT TOP
import { useContext } from "react";
import AuthContext from "../contexts/AuthContext";

// MODIFY COMPONENT
const ChatPage = () => {
    // ADD THIS LINE
    const { user, token } = useContext(AuthContext);
    
    const handleSend = async (text) => {
        // ADD THESE CHECKS
        if (!user || !token) {
            alert("Please log in to use chat");
            return;
        }
        
        // MODIFY FETCH
        const response = await fetch(`${API_BASE}/api/chat/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,  // ADD THIS
            },
            body: JSON.stringify({
                user_id: user.uid,  // CHANGE FROM: 'test_user'
                message: content,
                chat_history: buildChatHistory(messages),
            }),
        });
```

### 2. Fix Chat Backend (Priority: HIGH)

**File**: `backend/api/chat.py`

```python
from fastapi import APIRouter, Depends  # ADD: Depends
from backend.api.auth import get_current_user_id  # ADD THIS IMPORT

@router.post("/")
async def chat_with_ai(
    request: ChatRequest,
    user_id: str = Depends(get_current_user_id)  # ADD THIS
):
    # REMOVE user_id from request body, use from auth instead
    assistant_id = await get_or_create_assistant(user_id)
    
    result = await run_chatbot_turn(
        user_message=request.message,
        assistant_id=assistant_id,
        user_id=user_id,  # From auth, not request
        chat_history=request.chat_history,
    )
    return result


class ChatRequest(BaseModel):
    # REMOVE this line:
    # user_id: str
    message: str
    chat_history: List[Dict] = []
```

### 3. Create Login Page (Priority: HIGH)

Frontend needs a login/signup page to redirect users for authentication.

### 4. Add Auth Guards (Priority: MEDIUM)

Protect ChatPage from unauthenticated access:

```jsx
// In ChatPage component
if (!user || !token) {
    return (
        <div className={styles.page}>
            <div className={styles.messageBox}>
                <p>Please log in to use chat</p>
                <button onClick={() => navigate('/login')}>Go to Login</button>
            </div>
        </div>
    );
}
```

### 5. Update Test Files (Priority: LOW)

After fixes are in place, update test scripts to use real authentication:

- `test_chatbot.py`: Obtain JWT token via login endpoint
- `test_agent.py`: Same
- `seed_test_entries.py`: Same

---

## Summary Table

| Component | File | Status | Issue | Fix |
|-----------|------|--------|-------|-----|
| Auth Backend | auth.py | ✅ Working | None | None |
| Journal Frontend | JournalEditor.jsx | ✅ Working | None | None |
| Chat Frontend | ChatPage.jsx | ❌ Broken | No AuthContext, hardcoded test_user | Import AuthContext, send token |
| Chat Backend | chat.py | ❌ Broken | No authentication | Add Depends(get_current_user_id) |
| AuthContext | AuthContext.jsx | ✅ Ready | Not used by Chat | Already implemented |
| Login Page | N/A | ❌ Missing | No UI to login | Create login/signup pages |

---

## Next Steps

1. **Immediate** (Unblocks real user journaling):
   - Fix ChatPage to use AuthContext ✅
   - Fix chat backend to require auth ✅
   - Create login/signup pages ✅

2. **Short term** (Improves UX):
   - Add auth guards to protected pages
   - Improve error messages for auth failures
   - Add loading states during auth

3. **Testing**:
   - Test signup → login → journal entry → data in Firebase
   - Test signup → login → chat → data in Backboard memory
   - Verify data isolation (User A can't see User B's data)

---

**Last Updated**: Current session
**Next Review**: After fixing ChatPage and creating login pages
