# AI Coding Agent Instructions for GenAI-Genesis-2026

## Project Overview
**GenAI-Genesis-2026** is an AI journaling companion MVP that retrieves similar past journal entries using semantic embeddings. This is a hackathon project with a Python backend (FastAPI) and JavaScript frontend.

## Architecture

### Core Components
1. **Database Layer** (`backend/db/`)
   - `firebase_client.py`: Singleton Firestore client initialization
   - `queries.py`: Database operations (CRUD for entries, moods, profiles, analytics)

2. **Embeddings Layer** (`backend/embeddings/`)
   - `embedding_service.py`: OpenAI text-embedding-3-small integration
   - `similarity_search.py`: Cosine similarity calculations and retrieval

3. **AI Agent Layer** (`backend/ai/`)
   - `agent.py`: Main agent loop orchestrating mood analysis → profile updates
   - `mood_analysis.py`: OpenAI-based mood/emotion classification
   - `response_generator.py`: MI-style reflective response generation
   - `profile_updater.py`: Long-term user profile memory summarization
   - `memory.py`: Backboard API integration for persistent user memory

4. **API Layer** (`backend/api/`)
   - `diary.py`: `/journal-entry` endpoint (main entry point)
   - `insights.py`: `/progress/{user_id}` endpoint for dashboard stats

### Data Flow
```
POST /journal-entry
    ↓
1. Generate embedding
2. Find similar past entries (semantic search)
3. Run agent loop:
   - Analyze mood
   - Load user profile (long-term memory)
   - Generate reflective response
   - Update profile with new patterns
   - Store updated profile
4. Persist entry + mood to Firestore
5. Return comprehensive response
```

### Firestore Collections
- **diary_entries**: `{user_id, text, embedding, timestamp}`
- **mood_history**: `{user_id, mood, intensity, date, timestamp}`
- **user_profiles**: `{user_id, common_stressors, recurring_emotions, helpful_strategies, support_preferences, recent_patterns, summary, updated_at}`
- **notifications**: `{user_id, type, message, scheduled_time, sent, created_at}`
- **users**: User metadata (created for auth in future)

## Key Patterns & Conventions

### Environment Configuration
- **FIREBASE_CREDENTIALS_PATH**: Path to Firebase service account JSON
- **OPENAI_API_KEY**: OpenAI API key for embeddings

### Database Operations
- Always use `from firebase_client import get_db()` to access Firestore
- All functions return Python dictionaries, not Firestore objects
- Entry IDs are auto-generated; use `doc.id` after `.add()` operations
- Queries use `.where()`, `.order_by()`, `.limit()` method chains

### Embeddings
- Model: `text-embedding-3-small`
- Format: Lists of floats stored directly in Firestore
- All embeddings must have matching dimensions for similarity comparison (checked at runtime)
- Use `cosine_similarity()` for all vector comparisons (ranges -1 to 1)

### Error Handling
- Firebase operations: Check initialization via `try/except RuntimeError`
- OpenAI calls: Handle `openai.APIError` for API failures
- Similarity search: Skip invalid/missing embeddings gracefully

## Common Workflows

### Complete Journal Entry Processing (What Actually Happens)
```python
# User submits entry via POST /api/journal-entry
async def save_journal_entry(data: JournalEntryRequest):
    # 1. Embeddings
    embedding = generate_embedding(data.entry)
    
    # 2. Semantic search for context
    all_entries = get_all_entries(data.user_id)
    similar = find_similar_entries(embedding, all_entries, top_k=3)
    
    # 3. Full agent loop (orchestrates all AI steps)
    agent_result = await run_agent_loop(
        diary_entry=data.entry,
        assistant_id=f"assistant_{data.user_id}",
        recent_entries=similar,
    )
    # Returns: mood, response, updated_profile, safety_flag
    
    # 4. Persist to database
    entry_id = save_entry(data.user_id, data.entry, embedding)
    mood_id = save_mood(data.user_id, agent_result.mood.emotion, intensity)
    store_user_long_term_memory(data.user_id, agent_result.updated_profile)
    
    return {...}
```

### Querying User Analytics (Insights Dashboard)
```python
from backend.db.queries import (
    get_user_mood_average,
    get_entry_count,
    get_check_in_streak,
    get_user_mood_history,
)

# Dashboard endpoint uses these for stats
mood_avg = get_user_mood_average(user_id, days=30)
streak = get_check_in_streak(user_id)
total_entries = get_entry_count(user_id)
history = get_user_mood_history(user_id, days=30)
```

### Retrieving User Profile Memory
```python
from backend.db.queries import get_user_long_term_memory

# Used by agent loop to contextualize response
profile = get_user_long_term_memory(user_id)
# Returns: common_stressors, recurring_emotions, strategies, preferences, patterns, summary
```

## Implementation Notes

### Firebase Client
- Initializes once using service account credentials
- Raises `RuntimeError` if `init_firebase()` not called before `get_db()`
- Check `firebase_admin._apps` to avoid re-initialization

### Queries Module
All database operations:
- Filtered by `user_id` for multi-user isolation
- Return Python dictionaries (not Firestore objects)
- Timestamps stored as UTC via `datetime.utcnow()`
- Support CRUD operations and analytics queries

**New analytics functions**:
- `get_user_mood_history(user_id, days=30)` - Mood records over N days
- `get_user_mood_average(user_id, days=30)` - Average intensity
- `get_entry_count(user_id)` - Total entries
- `get_check_in_streak(user_id)` - Consecutive days with entries
- `store_user_long_term_memory(user_id, memory)` - Save profile
- `get_user_long_term_memory(user_id)` - Load profile

### Agent Loop Integration
- `run_agent_loop()` orchestrates full pipeline (5 steps)
- Takes `diary_entry`, `assistant_id`, `recent_entries`
- Returns `AgentResult` with mood, response, updated_profile, safety_flag
- Must be awaited (async function)
- Requires Backboard API key for persistent memory (optional)

### Embedding Service
- Wraps OpenAI client—no batching for MVP
- Returns raw embedding vector; dimension checking in similarity search
- API key validation at runtime

### Similarity Search
- `cosine_similarity()` handles dimension validation
- `find_similar_entries()` skips entries without embeddings
- Results: `(similarity_score, entry)` tuples sorted descending

## Files Implemented
- ✅ **Database layer**: Complete CRUD + analytics
- ✅ **Embeddings layer**: Generation + similarity search
- ✅ **AI agent loop**: Full orchestration pipeline
- ✅ **API endpoints**: `/journal-entry`, `/progress/{user_id}`
- ✅ **FastAPI setup**: CORS, logging, Firebase init

## Files Not Yet Implemented
- **Frontend code**: Separate JS module; backend exports JSON
- **User authentication**: Firebase Auth integration pending
- **Backboard API setup**: Optional for memory persistence

## Testing
Each module includes `if __name__ == "__main__":` test blocks:
- Run `python -m backend.embeddings.similarity_search` to test vector math
- Run `python -m backend.embeddings.embedding_service` to test OpenAI
- Run `python -m backend.db.queries` to list database functions
- Run `uvicorn backend.api.main:app --reload` to start API server

## Dependencies
- `firebase-admin`: Firestore client
- `openai`: Embedding + chat generation
- `python-dotenv`: Environment variable management
- `numpy`: (optional, for advanced vector operations)

**Last Updated**: March 14, 2026
