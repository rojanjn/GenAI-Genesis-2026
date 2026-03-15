# Journal Entry Save Issue: Root Cause Analysis

## The Problem

**UI journal entries are NOT being saved to Firebase.**  
**Only `test_user` entries (from test scripts) appear in Firebase.**

## Root Cause: Authentication Mismatch

### Frontend (JournalEditor.jsx) - Lines 155-165

```jsx
const response = await fetch(`${API_BASE_URL}/api/journal-entry`, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,  // ← Sends JWT token
    },
    body: JSON.stringify({
        user_id: user.uid,
        prompt: PROMPTS[promptIndex],
        entry: editor.getHTML(),
        entry_text: content,
    }),
});
```

**Frontend is sending:**
- ✅ `Authorization: Bearer {token}` - JWT token header
- ✅ `user.uid` - user ID from authentication context

### Backend (diary.py) - Lines 33-34

```python
@router.post("/journal-entry")
async def save_journal_entry(
    data: JournalEntryRequest, 
    user_id: str = Depends(get_current_user_id)  # ← Requires auth
):
    print(f"Step 0: Processing entry for user {user_id}")
    save_entry(user_id, data.entry, embedding)
```

**Backend expects:**
- ✅ `Authorization` header with valid JWT token
- ✅ Extracts `user_id` from the token (ignores `request.user_id`)

---

## Why It's Failing: Authentication Chain Breakdown

### What Happens When User Submits Entry from UI

```
1. User types in journal editor
2. Clicks "Save"
   ↓
3. Frontend checks: if (!user || !token) return
   └─ If user is NOT logged in: Entry is NOT sent to backend
   └─ If user IS logged in: Entry is sent with token
   ↓
4. Frontend sends POST /api/journal-entry
   Headers: Authorization: Bearer {token}
   Body: {entry: "...", user_id: "...", ...}
   ↓
5. Backend receives request
   ↓
6. get_current_user_id() dependency runs:
   ├─ Reads Authorization header
   ├─ Extracts token
   ├─ Decodes and verifies JWT signature
   ├─ If valid: Extracts user_id from token payload
   ├─ If invalid/missing: Returns 401 Unauthorized
   ↓
7. If 401: Request fails, entry NOT saved
   If valid: Entry saved with correct user_id
```

---

## What's Actually Happening

### Scenario 1: User NOT Logged In ❌

```
Frontend:
  if (!user || !token) return;  // ← Exits before sending request
  
Result: Entry is NOT sent to backend at all
```

**Check in browser console:**
1. Open DevTools (F12)
2. Go to Network tab
3. Try to save a journal entry
4. Do you see a POST request to `/api/journal-entry`?

### Scenario 2: User Logged In BUT Token Invalid ❌

```
Frontend sends:
  Authorization: Bearer {token}
  
Backend:
  get_current_user_id(token)
    → jwt.decode(token, SECRET_KEY)
    → If signature doesn't match: HTTPException 401
    
Result: Request rejected with 401 Unauthorized
```

**Check in browser console:**
1. Open DevTools (F12)
2. Go to Network tab
3. Click the POST request to `/api/journal-entry`
4. Go to Response tab
5. Do you see `{"detail": "Invalid token..."}` or similar?

### Scenario 3: User Logged In, Token Valid ✅

```
Frontend sends valid token
  ↓
Backend verifies token
  ↓
Extracts user_id from token
  ↓
save_entry(user_id, entry, embedding)
  ↓
Entry saved to Firebase diary_entries with user_id

Result: Entry appears in Firebase!
```

---

## Why Only test_user Entries Are Visible

### test_user Entries (From Test Scripts)

```
test_chatbot.py:
  user_id = "test_user"  # Hardcoded
  run_chatbot_turn(user_id="test_user", ...)
  
seed_test_entries.py:
  user_id = "test_user"  # Hardcoded
  save_entry(user_id="test_user", text, embedding)

Result: 
  ✅ Saved directly to Firebase with user_id="test_user"
  ✅ No authentication required (test scripts call functions directly)
  ✅ Visible in Firebase
```

### UI Journal Entries (From Frontend)

```
JournalEditor.jsx:
  if (!user || !token) return;  // ← Likely exits here!
  
  fetch('/api/journal-entry', {
    headers: {'Authorization': `Bearer ${token}`}
  })
  
Result:
  ❌ Either:
     1. User not logged in → entry not sent
     2. Token invalid → 401 error → entry not saved
     3. Token doesn't exist → entry not sent
```

---

## Diagnosis: Check These Things

### 1. Is User Logged In?

**In browser console (DevTools → Console):**
```javascript
// Check localStorage
localStorage.getItem('auth_token');  // Should return a token string
localStorage.getItem('user');        // Should return user object

// Or check auth context (depends on your implementation)
const { user, token } = useAuth();  // Check if both exist
```

**Expected output:**
```
auth_token: "eyJ0eXAiOiJKV1QiLCJhbGc..."  (JWT token)
user: {uid: "user_abc123", email: "user@example.com", ...}
```

**If missing:** User is NOT logged in → entries won't be sent

### 2. Is Token Being Sent?

**In DevTools → Network tab:**
1. Type a journal entry
2. Click Save
3. Look for POST request to `/api/journal-entry`
4. Click on the request
5. Go to "Headers" tab
6. Look for `Authorization: Bearer ...`

**If not present:** Token not being sent → 401 error

### 3. Is Backend Getting the Request?

**Check server logs:**
```bash
# Terminal where you ran: uvicorn backend.api.main:app --reload

# You should see:
POST /api/journal-entry
Authorization: Bearer {token}

# And then:
Step 0: Processing entry for user {user_id}
Step 1: generating embedding
Step 2: loading all past entries
...
```

**If you don't see "Step 0":** Request isn't reaching backend

### 4. Is there a 401 Error?

**In DevTools → Network tab:**
1. Look at the response status of the POST request
2. Should be 200 (success) or 401 (auth failed)
3. If 401, click on the response tab to see error message

---

## The Fix: Authentication Setup

### Issue: User Likely Not Logged In

The frontend has authentication code, but user might not have:
1. ✅ Signed up via `/auth/signup` endpoint
2. ✅ Logged in via `/auth/login` endpoint
3. ✅ Token stored in localStorage

### Solution Flow

```
1. Frontend loads
2. Check if user exists in localStorage
3. If not: Redirect to login/signup page
4. User signs up/logs in
5. Backend returns JWT token
6. Frontend stores token in localStorage
7. Now journal entry endpoint works!
```

---

## Quick Test: Force Save as test_user

If you want journal entries to save immediately for testing:

### Option 1: Temporarily Disable Auth in Backend

```python
# backend/api/diary.py - Line 33
@router.post("/journal-entry")
async def save_journal_entry(
    data: JournalEntryRequest,
    # Comment out this line temporarily for testing:
    # user_id: str = Depends(get_current_user_id)
    # Add this instead:
):
    # TEMPORARY - remove after testing!
    user_id = data.user_id if data.user_id else "test_user"
    
    print(f"Step 0: Processing entry for user {user_id}")
    # ... rest of function
```

**⚠️ WARNING: Only for testing! Re-enable auth before production**

### Option 2: Make Frontend Send test_user

```jsx
// frontend/src/features/journal/components/JournalEditor.jsx - Line 165
const response = await fetch(`${API_BASE_URL}/api/journal-entry`, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        // Comment out token for testing:
        // 'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({
        user_id: 'test_user',  // Hardcode for testing
        prompt: PROMPTS[promptIndex],
        entry: editor.getHTML(),
        entry_text: content,
    }),
});
```

**⚠️ WARNING: Only for testing! Use real auth before production**

---

## Proper Fix: Ensure Auth Works

### 1. Sign Up a User

```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "securepass123",
    "display_name": "Test User"
  }'
```

**Response:**
```json
{
  "success": true,
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "uid": "user_xyz123",
    "email": "test@example.com",
    "display_name": "Test User"
  }
}
```

### 2. Save Token in Frontend

Store the token from signup/login response:
```javascript
localStorage.setItem('auth_token', response.token);
localStorage.setItem('user', JSON.stringify(response.user));
```

### 3. Use Token in API Calls

Frontend already does this:
```javascript
headers: {
  'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
}
```

### 4. Now Submit Journal Entry

Journal entry will be saved with the authenticated user's ID.

---

## Summary: Why Entries Aren't Saved

| Reason | Evidence | Fix |
|--------|----------|-----|
| **User not logged in** | No `auth_token` in localStorage | Sign up/login first |
| **Token not valid** | 401 error in Network tab | Re-authenticate |
| **Token not sent** | No `Authorization` header | Check frontend code |
| **Auth disabled in code** | `get_current_user_id` commented out | Re-enable auth dependency |
| **Entry sent as test_user** | Frontend hardcodes `user_id` | Use real user ID from context |

---

## Files Involved

| File | Role | Status |
|------|------|--------|
| `frontend/src/features/journal/components/JournalEditor.jsx` | Sends request with token | ✅ Correct |
| `backend/api/diary.py` | Requires authentication | ✅ Correct |
| `backend/api/auth.py` | Handles login/signup, tokens | ✅ Correct |
| `backend/api/main.py` | Registers auth middleware | ✅ Correct |
| Frontend auth context | Stores user/token | Need to verify |

---

## Next Step: Verify

1. **Open browser DevTools (F12)**
2. **Go to Network tab**
3. **Try to save a journal entry**
4. **Do you see POST `/api/journal-entry` request?**
   - **YES:** Check response (should be 200 or error code)
   - **NO:** Entry not being sent (user not logged in)

Report what you find and I can help narrow down the exact issue!
