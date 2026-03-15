"""
Token utility functions for JWT handling and verification.
Provides centralized token management for authentication.
"""

from datetime import datetime, timedelta
from typing import Dict, Tuple
import os
import jwt
from fastapi import HTTPException

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24


def create_access_token(user_id: str, email: str, expires_delta: timedelta = None) -> Tuple[str, int]:
    """
    Create a JWT access token for a user.
    
    Args:
        user_id: Firebase user ID
        email: User email address
        expires_delta: Token expiration time (default: 24 hours)
    
    Returns:
        Tuple of (token_string, expires_in_seconds)
    """
    if expires_delta is None:
        expires_delta = timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    
    expire = datetime.utcnow() + expires_delta
    to_encode = {
        "user_id": user_id,
        "email": email,
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    expires_in = int(expires_delta.total_seconds())
    
    return encoded_jwt, expires_in


def verify_token(token: str) -> Dict:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token string to verify
    
    Returns:
        Dictionary containing decoded payload with user_id and email
    
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        email: str = payload.get("email")
        
        if user_id is None or email is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        
        return {
            "user_id": user_id,
            "email": email,
            "payload": payload
        }
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


def extract_token_from_header(authorization: str) -> str:
    """
    Extract bearer token from Authorization header.
    
    Args:
        authorization: Authorization header value (e.g., "Bearer <token>")
    
    Returns:
        Token string
    
    Raises:
        HTTPException: If header format is invalid
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authorization scheme")
        return token
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
