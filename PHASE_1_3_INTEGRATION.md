# Frontend-Backend Integration Guide (Phase 1.3)

## Overview

This guide documents the alignment fixes between frontend and backend to ensure proper data flow and authentication across the application.

## Fixed Misalignments

### Problem 1: User ID Mismatch ✅ FIXED

**Issue:** Frontend used mock user "john-doe", backend expected real `user_id`

**Solution:**
- Added `useContext(AuthContext)` to JournalEditor component
- Added `useContext(AuthContext)` to MoodCheckIn component
- Replaced hardcoded mock user with authenticated `user.uid`
- Frontend now sends real user_id in request body (for verification)
- Backend extracts user_id from JWT token (dependency injection)

**Files Changed:**
- `frontend/src/features/journal/components/JournalEditor.jsx`
- `frontend/src/features/home/components/MoodCheckIn.jsx`
- `frontend/src/pages/HomePage.jsx`

### Problem 2: No Token Authentication ✅ FIXED

**Issue:** Frontend made API calls without Authorization header, backend expected Bearer token

**Solution:**
- Added `Authorization: Bearer ${token}` header to all fetch calls
- Backend uses `get_current_user_id()` dependency to extract user_id from token
- Frontend stores token in `AuthContext` from login response
- All protected endpoints now validate token before processing

**Files Changed:**
- `frontend/src/features/journal/components/JournalEditor.jsx` (fetch call)
- `frontend/src/features/home/components/MoodCheckIn.jsx` (fetch call)
- `frontend/src/pages/HomePage.jsx` (fetch call)
- `backend/api/diary.py` (added Depends(get_current_user_id))
- `backend/api/insights.py` (added Depends(get_current_user_id))
- `backend/api/moods.py` (new, with auth)

### Problem 3: Entry Format Consistency ✅ NO CHANGE NEEDED

**Issue:** Frontend stores HTML from TipTap editor, backend saves to database

**Current Solution:**
- Frontend sends `editor.getHTML()` to backend
- Backend stores full HTML string in `diary_entries.text`
- This is fine - rich text is preserved

**Optional Enhancement:** Can strip HTML on frontend if plain text is preferred.

### Problem 4: Mock Data in Frontend ✅ REPLACED

**Issue:** Frontend used hardcoded mock data, should use real Firestore data

**Solution:**
- JournalEditor: Now calls real `/api/journal-entry` endpoint
- MoodCheckIn: Now calls real `/api/mood-entry` endpoint
- HomePage: Now calls real `/api/stats/{user_id}` endpoint
- All components accept and display real API responses

**Files Changed:**
- `frontend/src/features/journal/components/JournalEditor.jsx`
- `frontend/src/features/home/components/MoodCheckIn.jsx`
- `frontend/src/pages/HomePage.jsx`

---

## API Endpoints (Updated)

### Authentication
```
POST   /api/auth/signup              Create account
POST   /api/auth/login               Login
POST   /api/auth/verify              Verify token
GET    /api/auth/profile             Get user profile (protected)
POST   /api/auth/logout              Logout
```

### Diary Entries
```
POST   /api/journal-entry            Save journal entry (protected)
```

**Request:**
```json
{
  "prompt": "What's on your mind?",
  "entry": "<p>HTML content here</p>",
  "entry_text": "Plain text for analysis"
}
```

**Response:**
```json
{
  "success": true,
  "entry_id": "entry_123",
  "mood_id": "mood_456",
  "mood": { "emotion": "...", "intensity": 0.6, ... },
  "response": { "reflection": "...", ... },
  "similar_entries_used": 3,
  "similarity_scores": [0.85, 0.72, 0.68]
}
```

### Mood Check-ins
```
POST   /api/mood-entry               Save mood check-in (protected)
GET    /api/moods/{user_id}          Get mood history (protected)
```

**POST Request:**
```json
{
  "mood": "Calm",
  "intensity": 7,
  "note": "Feeling good today"
}
```

**POST Response:**
```json
{
  "success": true,
  "mood_id": "mood_789",
  "message": "Mood check-in saved successfully"
}
```

### Statistics
```
GET    /api/stats/{user_id}          Get user stats (protected)
GET    /api/progress/{user_id}       Get detailed progress (protected)
```

**Response:**
```json
{
  "total_entries": 15,
  "total_moods": 42,
  "mood_average": 6.5,
  "streak": 5,
  "recent_moods": [...]
}
```

---

## Frontend Components Updated

### JournalEditor
```jsx
import { useContext } from 'react';
import AuthContext from '../../../contexts/AuthContext';

const JournalEditor = () => {
  const { user, token } = useContext(AuthContext);
  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
  
  const handleSave = async () => {
    const response = await fetch(`${API_BASE_URL}/api/journal-entry`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,  // ✅ Auth token
      },
      body: JSON.stringify({
        user_id: user.uid,  // ✅ Real user ID
        prompt: PROMPTS[promptIndex],
        entry: editor.getHTML(),
      }),
    });
    // ... handle response
  };
};
```

### MoodCheckIn
```jsx
import { useContext } from 'react';
import AuthContext from '../../../contexts/AuthContext';

const MoodCheckIn = () => {
  const { user, token } = useContext(AuthContext);
  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
  
  const handleSave = async () => {
    const response = await fetch(`${API_BASE_URL}/api/mood-entry`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,  // ✅ Auth token
      },
      body: JSON.stringify({
        user_id: user.uid,  // ✅ Real user ID
        mood: selected,
        intensity: 5,
        note: note,
      }),
    });
    // ... handle response
  };
};
```

### HomePage
```jsx
import { useContext, useEffect, useState } from 'react';
import AuthContext from '../contexts/AuthContext';

const HomePage = () => {
  const { user, token } = useContext(AuthContext);
  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
  const [stats, setStats] = useState(null);
  
  useEffect(() => {
    if (!user || !token) return;
    
    const fetchStats = async () => {
      const response = await fetch(`${API_BASE_URL}/api/stats/${user.uid}`, {
        headers: {
          'Authorization': `Bearer ${token}`,  // ✅ Auth token
        },
      });
      const data = await response.json();
      setStats(data);
    };
    
    fetchStats();
  }, [user, token]);
};
```

---

## Backend Components Updated

### Auth Integration
```python
from fastapi import Depends
from backend.api.auth import get_current_user_id

@router.post("/journal-entry")
async def save_journal_entry(
  data: JournalEntryRequest, 
  user_id: str = Depends(get_current_user_id)  # ✅ Auto-extract from token
):
    # user_id is guaranteed to be authenticated
    # Save to Firestore with correct user_id
    pass
```

### Moods Endpoint
```python
# backend/api/moods.py
@router.post("/mood-entry")
def save_mood_entry(
  data: MoodEntryRequest,
  user_id: str = Depends(get_current_user_id)
):
    mood_id = save_mood(
        user_id=user_id,
        mood=data.mood,
        intensity=data.intensity,
        note=data.note
    )
    return {"success": True, "mood_id": mood_id}
```

### Stats Endpoint
```python
# backend/api/insights.py
@router.get("/stats/{user_id}")
def get_user_statistics(
  user_id: str, 
  current_user: str = Depends(get_current_user_id)
):
    # Verify authorization
    if current_user != user_id:
        raise HTTPException(status_code=403)
    
    return get_user_stats(user_id)
```

---

## Testing the Integration

### Setup
```bash
# Backend
cd /Users/farisabuain/GenAI-Genesis-2026
python -m uvicorn backend.api.main:app --reload --port 8000

# Frontend
cd frontend
npm start
```

### Test 1: Journal Entry with Real Backend
1. Login to frontend
2. Go to `/journal`
3. Write entry
4. Click "Save entry"
5. Check Network tab: Request includes `Authorization: Bearer <token>`
6. Response includes real mood analysis from backend

### Test 2: Mood Check-in with Backend
1. Login to frontend
2. On home page, select a mood
3. Click "Save check-in"
4. Check Network tab: Request includes auth token
5. Success message appears, data saved to Firestore

### Test 3: Stats from Backend
1. Login to frontend
2. Home page loads
3. Stats cards show real data from `/api/stats/{user_id}`
4. Stats are personalized to logged-in user

### Test 4: Authorization Verification
```bash
# Try to access another user's data without token
curl http://localhost:8000/api/stats/other_user_id
# Should get 401 Unauthorized

# Try to access another user's data with token
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/stats/other_user_id
# Should get 403 Forbidden
```

---

## Security Considerations

✅ **Implemented:**
- Token-based authentication on all protected routes
- User ID extracted from token (can't be forged)
- Authorization checks on per-user endpoints
- Error handling for missing/invalid tokens
- All user data isolated by user_id in Firestore

⚠️ **To Implement:**
- Rate limiting on auth endpoints
- HTTPS enforcement in production
- Token refresh mechanism
- Session timeout handling
- Password reset flow

---

## Data Flow Diagram

```
SIGNUP/LOGIN
├─ Frontend: POST /auth/signup or /auth/login
├─ Backend: Creates user in Firebase Auth
├─ Backend: Stores profile in Firestore users/{uid}
├─ Backend: Returns JWT token (24hr expiration)
└─ Frontend: Stores token in sessionStorage

JOURNAL ENTRY
├─ User: Writes entry in editor
├─ Frontend: GET `user.uid` and `token` from AuthContext
├─ Frontend: POST /api/journal-entry with Authorization header
├─ Backend: Dependency extracts user_id from token
├─ Backend: Saves entry to diary_entries/{entry_id} with user_id
├─ Backend: Runs agent loop for mood analysis
├─ Backend: Saves mood to mood_history with user_id
├─ Frontend: Displays real mood analysis response
└─ Firestore: Entry isolated to user's collection

MOOD CHECK-IN
├─ User: Selects mood on home page
├─ Frontend: POST /api/mood-entry with Authorization header
├─ Backend: Extracts user_id from token
├─ Backend: Saves mood to mood_history with user_id
├─ Frontend: Shows success message
└─ Firestore: Mood isolated to user's collection

DASHBOARD STATS
├─ Frontend: useEffect runs on mount
├─ Frontend: GET /api/stats/{user.uid} with Authorization header
├─ Backend: Extracts user_id from token, verifies ownership
├─ Backend: Queries Firestore for user's entries and moods
├─ Backend: Calculates streak, average, count
├─ Frontend: Displays stats in cards
└─ Stats update when entries/moods are saved
```

---

## Troubleshooting

### 401 Unauthorized Error
**Cause:** Token missing or invalid
**Fix:**
- Check AuthContext has token
- Verify Authorization header format: `Bearer <token>`
- Login again to get fresh token

### 403 Forbidden Error
**Cause:** User trying to access another user's data
**Fix:**
- Only request your own user_id
- Use `user.uid` from AuthContext

### CORS Error
**Cause:** Frontend URL not in backend CORS allow_origins
**Fix:**
- Check `.env` has `FRONTEND_URL` set
- Verify backend CORS includes `http://localhost:3000`

### "Cannot read property 'uid' of null"
**Cause:** AuthContext.user is null (not logged in)
**Fix:**
- Check if authentication succeeded
- Protected routes should redirect to login

### Stats showing as 0
**Cause:** Backend stats endpoint not called or user has no data
**Fix:**
- Make a journal entry to generate data
- Check Network tab for /api/stats request
- Verify backend returns data

---

## Files Changed Summary

### Frontend
- `frontend/src/features/journal/components/JournalEditor.jsx` - Real backend API, real user_id
- `frontend/src/features/home/components/MoodCheckIn.jsx` - Real backend API, auth token
- `frontend/src/pages/HomePage.jsx` - Real backend stats, useEffect fetch

### Backend
- `backend/api/auth.py` - Authentication endpoints (already created)
- `backend/api/diary.py` - Added auth dependency, uses token for user_id
- `backend/api/insights.py` - Added auth dependency, authorization checks
- `backend/api/moods.py` - New endpoints for mood save/history
- `backend/api/main.py` - Registered moods router
- `backend/db/queries.py` - Added note parameter to save_mood

---

## Next Steps

1. **Test the integration** using the Testing section above
2. **Add Sidebar integration** - Show user name and logout button
3. **Add error handling** - Toast notifications for API errors
4. **Add loading states** - Show spinners during requests
5. **Add offline support** - Keep localStorage as fallback

---

**Status:** Phase 1.3 Complete ✅
**Ready for:** Phase 2 (Frontend/Backend Alignment continued)
