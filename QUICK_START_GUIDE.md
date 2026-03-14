# Quick Start Guide - GenAI-Genesis-2026 Local Development

## Prerequisites
- Python 3.9+
- Node.js 14+
- Firebase service account JSON file
- OpenAI API key

## Step 1: Setup Backend

### 1a. Create `.env` file in project root
```bash
cd /Users/farisabuain/GenAI-Genesis-2026
cat > .env << 'EOF'
# Firebase
FIREBASE_CREDENTIALS_PATH=./firebase-adminsdk-abc123.json

# OpenAI
OPENAI_API_KEY=sk-proj-your-key-here

# JWT
JWT_SECRET_KEY=your-super-secret-key-min-32-chars-12345678

# Email (optional, for notifications)
EMAIL_PROVIDER=sendgrid
SENDGRID_API_KEY=SG.your-key
EMAIL_FROM=noreply@genai-genesis.com

# Frontend URL (for CORS)
FRONTEND_URL=http://localhost:3000
EOF
```

### 1b. Install Python dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 1c. Start the backend server
```bash
# From project root
source venv/bin/activate
python -m uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

✅ Backend is now running at `http://localhost:8000`

## Step 2: Setup Frontend

### 2a. Create `.env.local` in `frontend/` directory
```bash
cd /Users/farisabuain/GenAI-Genesis-2026/frontend
cat > .env.local << 'EOF'
REACT_APP_API_URL=http://localhost:8000
REACT_APP_FIREBASE_API_KEY=your-firebase-api-key
REACT_APP_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
REACT_APP_FIREBASE_PROJECT_ID=your-project-id
REACT_APP_FIREBASE_STORAGE_BUCKET=your-bucket.appspot.com
REACT_APP_FIREBASE_MESSAGING_SENDER_ID=123456789
REACT_APP_FIREBASE_APP_ID=1:123456789:web:abc123def456
EOF
```

### 2b. Install Node dependencies
```bash
cd frontend
npm install
```

### 2c. Start the frontend development server
```bash
npm start
```

Expected output:
```
Compiled successfully!

You can now view genai-genesis-2026 in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.x.x:3000
```

✅ Frontend is now running at `http://localhost:3000`

## Step 3: Test the Application

### 3a. Open browser
Navigate to `http://localhost:3000`

### 3b. Signup
1. Click "Sign Up"
2. Enter email: `test@example.com`
3. Enter password: `TestPass123`
4. Enter name: `Test User`
5. Click "Sign Up"

### 3c. Check browser console
Open DevTools (F12 or Cmd+Option+I) and check:
- Network tab: POST to `http://localhost:8000/api/auth/signup` should return 200
- Console: No errors

## Troubleshooting

### "fail to fetch" error
**Problem:** Backend not running
**Solution:** 
```bash
# Terminal 1: Backend
source venv/bin/activate
python -m uvicorn backend.api.main:app --reload

# Terminal 2: Frontend
cd frontend
npm start
```

### "Module not found" error on frontend
**Problem:** Missing dependencies
**Solution:**
```bash
cd frontend
npm install
```

### "CORS error" in browser console
**Problem:** API URL mismatch
**Solution:** Check `REACT_APP_API_URL` in `frontend/.env.local` matches backend URL

### Firebase initialization error
**Problem:** Firebase credentials not found
**Solution:**
1. Get `firebase-adminsdk-abc123.json` from Firebase Console
2. Place in project root
3. Update `FIREBASE_CREDENTIALS_PATH` in `.env`

### Port 8000 already in use
**Problem:** Another service using port 8000
**Solution:**
```bash
# Use different port
python -m uvicorn backend.api.main:app --reload --port 8001
# Update REACT_APP_API_URL to http://localhost:8001
```

### Port 3000 already in use
**Problem:** Another service using port 3000
**Solution:**
```bash
cd frontend
PORT=3001 npm start
```

## Development Workflow

### Terminal Setup (3 terminals recommended)

**Terminal 1: Backend**
```bash
cd /Users/farisabuain/GenAI-Genesis-2026
source venv/bin/activate
python -m uvicorn backend.api.main:app --reload
```

**Terminal 2: Frontend**
```bash
cd /Users/farisabuain/GenAI-Genesis-2026/frontend
npm start
```

**Terminal 3: Git/Admin**
```bash
cd /Users/farisabuain/GenAI-Genesis-2026
# Use for git commands, testing, etc.
```

## Testing API Endpoints

### Test signup via curl
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123",
    "display_name": "Test User"
  }'
```

Expected response:
```json
{
  "success": true,
  "message": "User created successfully",
  "user_id": "abc123...",
  "email": "test@example.com",
  "display_name": "Test User",
  "token": "eyJhbGc..."
}
```

### Test login via curl
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123"
  }'
```

## API Documentation

Once backend is running, visit:
- `http://localhost:8000/docs` - Interactive API docs (Swagger UI)
- `http://localhost:8000/redoc` - Alternative API docs (ReDoc)

## Environment Variables Checklist

### Backend (`.env` in project root)
- [ ] FIREBASE_CREDENTIALS_PATH
- [ ] OPENAI_API_KEY
- [ ] JWT_SECRET_KEY (min 32 chars)
- [ ] EMAIL_PROVIDER (optional)
- [ ] SENDGRID_API_KEY (optional)
- [ ] EMAIL_FROM (optional)

### Frontend (`frontend/.env.local`)
- [ ] REACT_APP_API_URL=http://localhost:8000
- [ ] REACT_APP_FIREBASE_API_KEY
- [ ] REACT_APP_FIREBASE_AUTH_DOMAIN
- [ ] REACT_APP_FIREBASE_PROJECT_ID
- [ ] REACT_APP_FIREBASE_STORAGE_BUCKET
- [ ] REACT_APP_FIREBASE_MESSAGING_SENDER_ID
- [ ] REACT_APP_FIREBASE_APP_ID

## Next Steps

Once running:
1. Test signup/login flow
2. Create a journal entry
3. Check mood tracking
4. View dashboard stats
5. Review Firestore data

See `DEPLOYMENT_CHECKLIST.md` for production deployment steps.

---
**Last Updated:** March 14, 2026
