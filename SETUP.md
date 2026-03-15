# Environment Setup Guide for GenAI-Genesis-2026

## Prerequisites
- Python 3.8+
- pip or conda package manager
- Git

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `firebase-admin` - Firestore client
- `openai` - Embedding generation
- `python-dotenv` - Environment variable management
- `numpy` - Numerical operations

## Step 2: Set Up Firebase

### 2.1 Create a Firebase Project
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Add project"
3. Enter project name (e.g., "GenAI-Genesis-2026")
4. Follow the setup wizard (accept defaults for hackathon)
5. Wait for project creation to complete

### 2.2 Enable Firestore Database
1. In Firebase Console, go to **Build → Firestore Database**
2. Click **Create Database**
3. Select region (e.g., `us-central1`)
4. Start in **production mode** (you'll set security rules later if needed)
5. Click **Enable**

### 2.3 Generate Service Account Credentials
1. In Firebase Console, go to **Project Settings** (gear icon) → **Service Accounts**
2. Select **Python** in the SDK dropdown (already selected)
3. Click **Generate New Private Key**
4. A JSON file will download (e.g., `genai-genesis-2026-xxxxx.json`)
5. **Keep this file secure** — it contains sensitive credentials

### 2.4 Set Firebase Credentials Path
Move the service account JSON to a secure location and note the path:

```bash
# Example location (adjust as needed)
mkdir -p ~/.secrets
mv ~/Downloads/genai-genesis-2026-xxxxx.json ~/.secrets/
```

## Step 3: Set Up OpenAI API Key

### 3.1 Get Your API Key
1. Go to [OpenAI API Keys](https://platform.openai.com/account/api-keys)
2. Log in or create an account
3. Click **Create new secret key**
4. Copy the key (you won't be able to see it again)

### 3.2 Note the Key
Store it somewhere safe — you'll add it to environment variables next.

## Step 4: Create `.env` File

In the project root directory, create a `.env` file with your credentials:

```bash
# .env (in project root: /Users/farisabuain/GenAI-Genesis-2026/)

# Firebase service account JSON path (adjust to your actual path)
FIREBASE_CREDENTIALS_PATH=/Users/farisabuain/.secrets/genai-genesis-2026-xxxxx.json

# OpenAI API key
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**⚠️ IMPORTANT**: Add `.env` to `.gitignore` to prevent committing secrets:

```bash
echo ".env" >> .gitignore
```

## Step 5: Initialize Database at Startup

When your FastAPI application starts, call `init_firebase()` once:

```python
# Example: in your FastAPI main app file
from backend.db.firebase_client import init_firebase

# Initialize Firebase on app startup
init_firebase()

# Now you can use other db functions
from backend.db.queries import save_entry, get_recent_entries
```

The `init_firebase()` function will:
1. Read `FIREBASE_CREDENTIALS_PATH` environment variable
2. Load the service account credentials
3. Connect to Firestore
4. Create collections automatically on first write

## Step 6: Verify Setup

### Test Firebase Connection
```bash
python backend/db/firebase_client.py
```

Expected output:
```
Firebase initialized successfully
✓ Firebase client initialized successfully
✓ Firestore client type: <class 'google.cloud.firestore.Client'>
```

### Test OpenAI Connection
```bash
python backend/embeddings/embedding_service.py
```

Expected output:
```
✓ Embedding generated successfully
  Text: Today was a great day. I felt accomplished and happy.
  Embedding dimension: 1536
  First 5 values: [0.xxx, 0.xxx, ...]
```

### Test Similarity Search
```bash
python backend/embeddings/similarity_search.py
```

Expected output:
```
✓ Cosine similarity calculated successfully
  Identical vectors similarity: 1.0000 (expected: 1.0)
  Orthogonal vectors similarity: 0.0000 (expected: 0.0)

✓ Similarity search completed successfully
  Found 2 similar entries
  - Another happy day: 0.9823
  - Happy day: 1.0000
```

## Step 7: Firestore Collections

After initialization, your Firestore database will have these collections (created on first write):

- **`diary_entries`** - User journal entries with embeddings
  - Fields: `user_id`, `text`, `embedding`, `timestamp`

- **`mood_history`** - Mood tracking records
  - Fields: `user_id`, `mood`, `intensity`, `date`, `timestamp`

- **`notifications`** - Scheduled notifications
  - Fields: `user_id`, `type`, `message`, `scheduled_time`, `sent`, `created_at`

- **`users`** - User profiles (when needed)
  - Fields: `user_id`, `created_at`, `preferences`

## Troubleshooting

### `FIREBASE_CREDENTIALS_PATH not set`
- Ensure `.env` file exists in project root with correct path
- Check path is absolute (starts with `/`)
- Verify JSON file exists at that path

### `ModuleNotFoundError: No module named 'firebase_admin'`
- Run `pip install -r requirements.txt`
- Verify you're in the correct virtual environment

### `openai.APIError`
- Verify `OPENAI_API_KEY` is correct and starts with `sk-proj-`
- Check you have API credits (go to https://platform.openai.com/account/billing/overview)
- Verify API key hasn't been revoked

### Firestore Connection Fails
- Check service account JSON path is correct
- Verify JSON file has proper permissions (readable)
- Check Firebase project ID in JSON matches your project
- Ensure Firestore database is enabled in Firebase Console

### `RuntimeError: Firebase not initialized`
- Ensure `init_firebase()` is called before using `get_db()`
- This should be called once at application startup

## Security Notes

🔐 **Never commit secrets to git:**
- `.env` files should be in `.gitignore`
- Service account JSON should be stored securely
- API keys should be rotated periodically
- Use environment variables in production

## Next Steps

1. ✅ Install dependencies: `pip install -r requirements.txt`
2. ✅ Create Firebase project and Firestore database
3. ✅ Download service account credentials
4. ✅ Create `.env` file with credentials
5. ✅ Run verification tests (see Step 6)
6. ✅ Call `init_firebase()` in FastAPI startup
7. ✅ Use `backend.db.queries` functions in your routes

## Reference: Usage Example

```python
from backend.db.firebase_client import init_firebase
from backend.db.queries import save_entry, get_all_entries
from backend.embeddings.embedding_service import generate_embedding
from backend.embeddings.similarity_search import find_similar_entries

# Initialize at startup
init_firebase()

# Example workflow
user_id = "user123"
entry_text = "Today was a great day!"

# Generate embedding
embedding = generate_embedding(entry_text)

# Save entry
entry_id = save_entry(user_id, entry_text, embedding)
print(f"Entry saved: {entry_id}")

# Retrieve similar past entries
all_entries = get_all_entries(user_id)
similar = find_similar_entries(embedding, all_entries, top_k=3)
print(f"Found {len(similar)} similar entries")
for score, entry in similar:
    print(f"  - {entry['text']} (similarity: {score:.2f})")
```

---

**Questions?** Check the `.github/copilot-instructions.md` for architectural overview and patterns.
