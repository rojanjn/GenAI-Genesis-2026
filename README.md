# GenAI-Genesis-2026 🧠✨

An AI-powered journaling companion MVP that uses semantic embeddings to retrieve similar past journal entries and provide reflective, personalized responses based on mood analysis and long-term user memory.

## 🎯 Features

- **Smart Journal Entry Processing**: Submit journal entries and receive AI-generated reflective responses using Motivational Interviewing (MI) techniques
- **Semantic Similarity Search**: Retrieve relevant past entries using OpenAI embeddings and cosine similarity
- **Mood Tracking**: Automatic emotion classification and intensity tracking from journal entries
- **User Profile Memory**: Long-term memory summarization to understand recurring patterns, stressors, and coping strategies
- **Chat Interface**: Interactive chatbot for additional support and reflection
- **Insights Dashboard**: View mood trends, entry counts, and check-in streaks over time
- **Email Notifications**: Scheduled reminder notifications via SendGrid
- **Background Scheduling**: APScheduler for automated notification delivery

## 🏗️ Architecture

### Backend (Python FastAPI)
- **API Layer** (`backend/api/`): REST endpoints for journal entries, insights, chat, authentication
- **AI Agent Loop** (`backend/ai/`): Orchestrates mood analysis, response generation, and profile updates
- **Embeddings** (`backend/embeddings/`): OpenAI integration for semantic search and similarity calculations
- **Database** (`backend/db/`): Firestore operations for entries, moods, profiles, and notifications
- **Services** (`backend/services/`): Email and notification scheduling

### Frontend (React + React Router)
- **Pages**: Home, Journal, History, Settings, Insights
- **Components**: Mood check-in, journal editor, chat interface
- **Context**: Authentication and user state management
- **Styling**: CSS modules for component-level styling

### Data Flow
```
POST /api/journal-entry
    ↓
1. Generate embedding for entry text
2. Find similar past entries (semantic search)
3. Run agent loop:
   - Analyze mood/emotion
   - Load user profile (long-term memory)
   - Generate reflective response (MI-style)
   - Update profile with new patterns
4. Store entry, mood, and profile to Firestore
5. Return response to frontend
```

## 🚀 Deployment

### Prerequisites
- Python 3.8+
- Node.js 16+
- Firebase project with service account credentials
- OpenAI API key
- SendGrid API key (for emails)

### Deploy to Railway (Recommended)

**Backend + Frontend on Same Platform**

1. **Sign up at [railway.app](https://railway.app)**
2. **Create new project** → Deploy from GitHub
3. **Add Backend Service**:
   - Root: (leave blank)
   - Environment variables:
     - `OPENAI_API_KEY`
     - `FIREBASE_CREDENTIALS_B64` (base64-encoded Firebase JSON)
     - `BACKBOARD_API_KEY`
     - `SENDGRID_API_KEY`
     - `EMAIL_FROM`
     - `EMAIL_PROVIDER=sendgrid`
     - `FRONTEND_URL` (your frontend URL, added after frontend deploys)
4. **Add Frontend Service**:
   - Root: `frontend/`
   - Environment variables:
     - `REACT_APP_API_URL` (your backend Railway URL)
5. Deploy both services
6. Update `FRONTEND_URL` in backend after frontend is live

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt
cd frontend && npm install

# Set up environment variables
cp .env.example .env
# Fill in your API keys and Firebase credentials

# Run backend and frontend together
python start.py

# Or run separately:
# Terminal 1:
python -m uvicorn backend.api.main:app --reload

# Terminal 2:
cd frontend && npm start
```

**Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API docs: http://localhost:8000/docs

## 📋 Environment Variables

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Firebase (choose one)
FIREBASE_CREDENTIALS_PATH=/path/to/credentials.json  # Local dev
FIREBASE_CREDENTIALS_B64=...  # Production (base64-encoded)

# Memory persistence
BACKBOARD_API_KEY=...

# Email notifications
SENDGRID_API_KEY=SG...
EMAIL_FROM=noreply@example.com
EMAIL_PROVIDER=sendgrid

# Frontend
FRONTEND_URL=http://localhost:3000  # Or your production URL
REACT_APP_API_URL=http://localhost:8000  # Or your backend URL
```

## 🗄️ Firestore Schema

### Collections
- **diary_entries**: `{user_id, text, embedding, timestamp, mood_id}`
- **mood_history**: `{user_id, mood, intensity, date, timestamp}`
- **user_profiles**: `{user_id, common_stressors, recurring_emotions, helpful_strategies, support_preferences, recent_patterns, summary, updated_at}`
- **notifications**: `{user_id, type, message, scheduled_time, sent, created_at}`

## 🧪 Testing

```bash
# Test individual modules
python -m backend.embeddings.embedding_service
python -m backend.embeddings.similarity_search
python -m backend.db.queries

# Run test files
python test_ai_flow.py
python test_chatbot.py
python test_client.py

# Seed test data
python seed_test_entries.py
```

## 📦 Key Dependencies

**Backend:**
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `firebase-admin` - Firestore client
- `openai` - Embeddings and chat
- `pydantic` - Data validation
- `APScheduler` - Background tasks
- `sendgrid` - Email service

**Frontend:**
- `react` - UI framework
- `react-router-dom` - Client-side routing
- `@tiptap/react` - Rich text editor

## 🔑 Key Modules

### Backend AI Agent Loop
**File**: `backend/ai/agent.py`

Orchestrates the complete AI pipeline:
1. Mood analysis (OpenAI classification)
2. Profile loading (long-term memory from Firestore)
3. Response generation (MI-style reflections)
4. Profile updating (pattern summarization)

### Embedding & Similarity Search
**Files**: `backend/embeddings/embedding_service.py`, `backend/embeddings/similarity_search.py`

- Generates text embeddings using OpenAI's `text-embedding-3-small`
- Performs cosine similarity calculations
- Retrieves top-k similar entries for context

### Database Operations
**File**: `backend/db/queries.py`

Complete CRUD + analytics:
- Store/retrieve entries and moods
- User profile memory management
- Mood analytics (average, streak, history)

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make changes and test locally
3. Commit: `git commit -m "Add feature description"`
4. Push: `git push origin feature/your-feature`
5. Open a Pull Request

## 📝 License

MIT License - see LICENSE file for details

## 👥 Team

Built for GenAI Genesis 2026 Hackathon

## 🐛 Troubleshooting

**Backend won't start:**
- Ensure `FIREBASE_CREDENTIALS_B64` or `FIREBASE_CREDENTIALS_PATH` is set
- Check all API keys are valid
- Run `python -m backend.db.firebase_client` to test Firebase init

**Frontend shows "failed to fetch":**
- Verify `REACT_APP_API_URL` in Vercel/Railway matches backend URL
- Check `FRONTEND_URL` in backend matches frontend URL
- Open browser DevTools (F12) → Network tab to see actual error
- Ensure backend is running and accessible

**Embeddings dimension mismatch:**
- All embeddings must use the same model (`text-embedding-3-small`)
- Clear and re-generate embeddings if switching models

## 📚 Documentation

- [AI Instructions](/.github/copilot-instructions.md) - Detailed architecture and patterns
- [FastAPI Docs](http://localhost:8000/docs) - Interactive API documentation