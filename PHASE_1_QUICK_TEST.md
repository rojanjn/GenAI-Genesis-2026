# Quick Testing Guide for Phase 1.1

## Prerequisites

### 1. Environment Setup
```bash
# Create .env file in project root
cp .env.example .env

# Fill in required values:
# - FIREBASE_CREDENTIALS_PATH (path to your service account JSON)
# - OPENAI_API_KEY (for future use)
# - JWT_SECRET_KEY (can be any secure random string)
```

### 2. Backend Setup
```bash
cd /Users/farisabuain/GenAI-Genesis-2026

# Install dependencies
pip install -r requirements.txt

# Start backend server
python -m uvicorn backend.api.main:app --reload --port 8000
```

You should see:
```
✓ Firebase initialised
Uvicorn running on http://127.0.0.1:8000
```

### 3. Frontend Setup
```bash
cd /Users/farisabuain/GenAI-Genesis-2026/frontend

# Install dependencies
npm install

# Create frontend .env
echo "REACT_APP_API_URL=http://localhost:8000" > .env

# Start frontend
npm start
```

You should see:
```
Compiled successfully!
On Your Network: http://192.168.x.x:3000
```

---

## Testing Flows

### Test 1: Signup Flow ✅

**Steps:**
1. Open http://localhost:3000 in browser
2. Should auto-redirect to `/login` (not authenticated)
3. Click "Sign up" link
4. Fill form:
   - Full Name: `John Doe`
   - Email: `john.doe@example.com`
   - Password: `SecurePass123`
5. Click "Sign Up"

**Expected Results:**
- ✅ Form validates password strength
- ✅ "Password is strong ✓" appears
- ✅ Sign Up button is enabled
- ✅ After submitting, redirects to `/` (home page)
- ✅ Sidebar shows "John Doe" (if Sidebar is integrated)
- ✅ Token is stored in browser sessionStorage

**Browser Console Check:**
- Open DevTools (F12)
- Go to Application → Session Storage
- Should see:
  - `auth_token`: JWT token
  - `auth_user`: JSON with user object

---

### Test 2: Login Flow ✅

**Steps:**
1. Click logout button (or navigate to `/login`)
2. Enter email: `john.doe@example.com`
3. Enter password: `SecurePass123`
4. Click "Sign In"

**Expected Results:**
- ✅ Form accepts credentials
- ✅ Shows "Signing in..." while loading
- ✅ Redirects to home page
- ✅ Sidebar shows user name
- ✅ Token is stored in sessionStorage

---

### Test 3: Protected Routes ✅

**Steps:**
1. Open new browser tab
2. Navigate to `http://localhost:3000/journal` (without logging in)
3. Should redirect to `/login`
4. Log in
5. Navigate to `/journal`, `/progress`, etc.

**Expected Results:**
- ✅ Without auth: all routes redirect to `/login`
- ✅ With auth: all routes load normally
- ✅ Can navigate between routes

---

### Test 4: Token in API Calls ✅

**Steps:**
1. Log in successfully
2. Open DevTools (F12)
3. Go to Network tab
4. Make any API request (e.g., save journal entry)
5. Click the request
6. Look at "Request Headers"

**Expected Results:**
- ✅ Request includes: `Authorization: Bearer eyJh...`
- ✅ Backend receives token and extracts user_id
- ✅ Response uses correct user_id for data isolation

---

### Test 5: Error Handling ✅

**Test 5a: Weak Password**
- Try to signup with password: `weak`
- Should show: "Password must be at least 8 characters"
- Sign Up button should be disabled

**Test 5b: Duplicate Email**
- Try to signup with email that already exists
- Should show: "Email already registered"

**Test 5c: Invalid Credentials**
- Login with wrong password
- Should show: "Invalid email or password"

---

## Backend Testing (curl)

### Signup
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "password": "Password123",
    "display_name": "Alice Smith"
  }'
```

Response:
```json
{
  "success": true,
  "user_id": "xABCDEFGH...",
  "email": "alice@example.com",
  "display_name": "Alice Smith",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 86400,
  "token_type": "Bearer"
}
```

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "password": "Password123"
  }'
```

### Verify Token
```bash
TOKEN="your_token_here"
curl -X POST http://localhost:8000/api/auth/verify \
  -H "Authorization: Bearer $TOKEN"
```

### Get Profile (Protected)
```bash
TOKEN="your_token_here"
curl -X GET http://localhost:8000/api/auth/profile \
  -H "Authorization: Bearer $TOKEN"
```

Response:
```json
{
  "user_id": "xABCDEFGH...",
  "email": "alice@example.com",
  "display_name": "Alice Smith",
  "created_at": "2024-03-14T10:30:00.123456",
  "last_active": "2024-03-14T10:35:00.654321"
}
```

---

## Interactive API Testing (Swagger UI)

1. Start backend: `python -m uvicorn backend.api.main:app --reload`
2. Open http://localhost:8000/docs
3. Expand "Authentication" section
4. Test endpoints interactively:
   - Click "Try it out" on endpoint
   - Fill in parameters
   - Click "Execute"
   - See response in real-time

**Pro Tip:** After signup, copy the token from response and use it for protected endpoints:
- Click "Authorize" (lock icon)
- Paste: `Bearer <your_token>`
- Now all requests include the token

---

## Common Issues & Fixes

### Issue: "Connection refused" (Backend not running)
```bash
python -m uvicorn backend.api.main:app --reload --port 8000
```

### Issue: "CORS error" (Frontend/Backend domain mismatch)
- Verify `http://localhost:3000` is in `cors_origins` in `backend/api/main.py`
- Or check `.env` has correct `FRONTEND_URL`

### Issue: "FIREBASE_CREDENTIALS_PATH not found"
- Add `.env` file with path to Firebase service account JSON
- Download from Firebase Console → Project Settings → Service Accounts

### Issue: "Email already exists"
- Use a different email for each test
- Or delete user from Firebase Console

### Issue: Token not in sessionStorage
- Check browser privacy mode
- Check console for errors
- Clear session storage and try again

---

## Database Verification

### Check Firestore Collections

**1. Firebase Console:**
- Go to [Firebase Console](https://console.firebase.google.com)
- Select your project
- Go to Firestore Database
- Check "users" collection

**Expected Document:**
```
users/user_id
├── user_id: "xABCDEFGH..."
├── email: "john.doe@example.com"
├── display_name: "John Doe"
├── created_at: "2024-03-14T10:30:00.123456"
├── last_active: "2024-03-14T10:35:00.654321"
└── preferences: {...}
```

---

## Debugging Checklist

- [ ] Backend server running on port 8000
- [ ] Frontend dev server running on port 3000
- [ ] `.env` file exists with required variables
- [ ] Firebase is initialized (check console output)
- [ ] JWT_SECRET_KEY is set in `.env`
- [ ] CORS origins include `http://localhost:3000`
- [ ] sessionStorage working (check DevTools)
- [ ] No 401 errors in Network tab
- [ ] No CORS errors in browser console
- [ ] Firebase rules allow read/write for authenticated users

---

## Success Criteria

✅ **Phase 1.1 is working if:**
- Signup creates user in Firebase Auth
- User profile created in Firestore "users" collection
- Login generates valid JWT token
- Token stored in sessionStorage
- Protected routes redirect to login when not authenticated
- All API requests include Authorization header
- Frontend shows user name after login
- Logout clears token and redirects to login

---

## Next: Phase 1.2 Testing

Once Phase 1.1 passes all tests:
1. Update sidebar/navbar to show authenticated user
2. Add logout button functionality
3. Integrate existing endpoints with authentication
4. Protect journal entry endpoint
5. Protect progress endpoint

See `PHASE_1_IMPLEMENTATION.md` for detailed next steps.
