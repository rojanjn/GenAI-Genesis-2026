# AI Coding Agent Instructions for GenAI-Genesis-2026

## Project Overview
**GenAI-Genesis-2026** is an AI journaling companion MVP that retrieves similar past journal entries using semantic embeddings. This is a hackathon project with a Python backend (FastAPI) and JavaScript frontend.

## Architecture

### Core Components
1. **Database Layer** (`backend/db/`)
   - `firebase_client.py`: Singleton Firestore client initialization
   - `queries.py`: Database operations (CRUD for entries, moods, notifications)

2. **Embeddings Layer** (`backend/embeddings/`)
   - `embedding_service.py`: OpenAI text-embedding-3-small integration
   - `similarity_search.py`: Cosine similarity calculations and retrieval

### Data Flow
```
User Entry → generate_embedding() → save_entry() → Firestore
             ↓
        get_all_entries() → find_similar_entries() → Top 3 similar entries
```

### Firestore Collections
- **diary_entries**: `{user_id, text, embedding, timestamp, mood_label?, intensity?}` (mood fields optional, populated by AI analysis)
- **mood_history**: `{user_id, mood, intensity, date}`
- **notifications**: `{user_id, type, message, scheduled_time, sent}`
- **users**: User profiles and preferences

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

### Adding an Entry
```python
from backend.db.queries import save_entry, get_all_entries
from backend.embeddings.embedding_service import generate_embedding
from backend.embeddings.similarity_search import find_similar_entries

# 1. Generate embedding
embedding = generate_embedding(entry_text)

# 2. Save to database
entry_id = save_entry(user_id, entry_text, embedding)

# 3. Find similar past entries
all_entries = get_all_entries(user_id)
similar = find_similar_entries(embedding, all_entries, top_k=3)
```

### Retrieving Recent Entries
```python
from backend.db.queries import get_recent_entries

entries = get_recent_entries(user_id, limit=3)  # Returns last 3 entries
```

### Recording Mood
```python
from backend.db.queries import save_mood

mood_id = save_mood(user_id, mood="happy", intensity=8)
```

## Implementation Notes

### Firebase Client
- Initializes once using service account credentials
- Raises `RuntimeError` if `init_firebase()` not called before `get_db()`
- Check `firebase_admin._apps` to avoid re-initialization

### Queries Module
- All entry lookups filtered by `user_id` for multi-user isolation
- Timestamps stored as UTC via `datetime.utcnow()`
- Returns entries as dicts with `entry_id` populated from `doc.id`

### Embedding Service
- Wraps OpenAI client—no batching for MVP (keep simple)
- Returns raw embedding vector; dimension checking done in similarity search
- API key validation happens at runtime, not import time

### Similarity Search
- `cosine_similarity()` handles dimension mismatch validation
- `find_similar_entries()` automatically skips entries without embeddings
- Results returned as `(similarity_score, entry)` tuples sorted descending

## Files Not Yet Implemented
- **FastAPI routes**: Handled by another developer; use `/` prefix in imports
- **Frontend code**: Separate JS module; backend exports JSON responses
- **AI prompt logic**: Separate orchestration layer (not in this codebase yet)
- **Agent coordination**: Multi-step workflows handled at API level

## Testing
Each module includes `if __name__ == "__main__":` test blocks for manual validation:
- Run `python backend/embeddings/similarity_search.py` to test vector math
- Run `python backend/embeddings/embedding_service.py` to test OpenAI connection
- Database tests require Firebase credentials configured

## Dependencies
- `firebase-admin`: Firestore client
- `openai`: Embedding generation
- `math`: Built-in for cosine similarity (no additional dependency)

**Last Updated**: March 14, 2026
