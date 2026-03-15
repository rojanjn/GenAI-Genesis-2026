"""
Firebase Client Module

Initializes Firebase Admin SDK and exposes a Firestore database client.
This is the single entry point for all database operations across the backend.

Role in system:
- Handles Firebase authentication via service account credentials
- Manages singleton Firestore client instance
- Provides error handling for initialization failures
"""

import os
import json
import base64
import firebase_admin
from firebase_admin import credentials, firestore
from typing import Optional, Any
from dotenv import load_dotenv
load_dotenv()

_db: Optional[Any] = None # Wildcard datatype for flexibility, but ideally should be firestore.client.Client. Why is this not working? Is it a circular import issue?

def init_firebase() -> None:
    """
    Initialize Firebase Admin SDK.

    Loads credentials from either:
    1. FIREBASE_CREDENTIALS_PATH environment variable (path to JSON file)
    2. FIREBASE_CREDENTIALS_B64 environment variable (base64-encoded JSON)

    Should be called once at application startup.

    Raises:
        FileNotFoundError: If credentials file doesn't exist
        ValueError: If neither credential method is configured
        RuntimeError: If Firebase initialization fails
    """
    global _db

    if firebase_admin._apps:
        print("Firebase already initialized")
        return

    # Try to get credentials from base64 env var first (for Render/production)
    credentials_b64 = os.getenv("FIREBASE_CREDENTIALS_B64")
    credentials_path = os.getenv("FIREBASE_CREDENTIALS_PATH")

    if not credentials_b64 and not credentials_path:
        raise ValueError("Either FIREBASE_CREDENTIALS_B64 or FIREBASE_CREDENTIALS_PATH environment variable must be set")

    try:
        if credentials_b64:
            # Decode base64 and parse JSON
            credentials_json = base64.b64decode(credentials_b64).decode('utf-8')
            credentials_dict = json.loads(credentials_json)
            creds = credentials.Certificate(credentials_dict)
            print("Firebase credentials loaded from FIREBASE_CREDENTIALS_B64")
        else:
            # Load from file path
            if not os.path.exists(credentials_path):
                raise FileNotFoundError(f"Firebase credentials file not found: {credentials_path}")
            creds = credentials.Certificate(credentials_path)
            print("Firebase credentials loaded from FIREBASE_CREDENTIALS_PATH")

        firebase_admin.initialize_app(creds)
        _db = firestore.client()
        print("Firebase initialized successfully")
    except Exception as e:
        raise RuntimeError(f"Failed to initialize Firebase: {str(e)}")


def get_db() -> Any:  # can't access .Client on a function. Using Any for flexibility, but ideally should be more specific. Potentally fix later.
    """
    Get the Firestore database client.

    Returns:
        Firestore client instance for database operations

    Raises:
        RuntimeError: If Firebase not initialized
    """
    global _db

    if _db is None:
        raise RuntimeError("Firebase not initialized. Call init_firebase() first.")

    return _db


if __name__ == "__main__":
    # Test Firebase initialization
    try:
        init_firebase()
        db = get_db()
        print("✓ Firebase client initialized successfully")
        print(f"✓ Firestore client type: {type(db)}")
    except Exception as e:
        print(f"✗ Firebase initialization failed: {e}")
