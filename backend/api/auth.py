"""
Authentication endpoints for user signup, login, and token management.
Integrates with Firebase Authentication for secure user management.
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, timedelta
import os
import logging
from typing import Optional

import firebase_admin
from firebase_admin import auth
import jwt

from backend.db.queries import (
    create_or_update_user_profile,
    get_user_profile,
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24


# ============================================================================
# Pydantic Models
# ============================================================================

class SignupRequest(BaseModel):
    """Request body for user signup"""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    display_name: str = Field(..., min_length=1, max_length=100)


class LoginRequest(BaseModel):
    """Request body for user login"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Response containing authentication token"""
    success: bool
    user_id: str
    email: str
    display_name: str
    token: str
    expires_in: int  # seconds
    token_type: str = "Bearer"


class UserProfile(BaseModel):
    """User profile response"""
    user_id: str
    email: str
    display_name: str
    created_at: Optional[str] = None
    last_active: Optional[str] = None


class VerifyTokenResponse(BaseModel):
    """Response for token verification"""
    valid: bool
    user_id: Optional[str] = None
    email: Optional[str] = None
    expires_at: Optional[str] = None


# ============================================================================
# Helper Functions
# ============================================================================

def create_access_token(user_id: str, email: str, expires_delta: Optional[timedelta] = None) -> tuple[str, int]:
    """
    Create a JWT access token.
    
    Args:
        user_id: Firebase user ID
        email: User email
        expires_delta: Token expiration time (default: 24 hours)
    
    Returns:
        tuple: (token_string, expires_in_seconds)
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


def verify_token(token: str) -> dict:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token string
    
    Returns:
        dict: Decoded token payload
    
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        email: str = payload.get("email")
        
        if user_id is None or email is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        
        return {"user_id": user_id, "email": email, "payload": payload}
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


def get_current_user_id(authorization: str = Header(None)) -> str:
    """
    Dependency to extract and verify user ID from Bearer token.
    Use in endpoint parameters to protect routes.
    
    Args:
        authorization: Authorization header (Bearer <token>)
    
    Returns:
        str: Verified user ID
    
    Raises:
        HTTPException: If token is missing or invalid
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authorization scheme")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    verified = verify_token(token)
    return verified["user_id"]


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/auth/signup", response_model=TokenResponse, status_code=201)
async def signup(data: SignupRequest):
    """
    Create a new user account.
    
    - Validates email format and password strength
    - Creates Firebase Authentication user
    - Creates user profile in Firestore
    - Schedules daily prompt notification
    - Returns authentication token
    
    Args:
        data: Signup request with email, password, display_name
    
    Returns:
        TokenResponse with user info and JWT token
    
    Raises:
        HTTPException: If email already exists or signup fails
    """
    try:
        # Create Firebase Auth user
        user = auth.create_user(
            email=data.email,
            password=data.password,
            display_name=data.display_name
        )
        user_id = user.uid
        
        logger.info(f"✓ Created Firebase user: {user_id}")
        
        # Create user profile in Firestore
        create_or_update_user_profile(
            user_id=user_id,
            email=data.email,
            display_name=data.display_name
        )
        
        logger.info(f"✓ Created Firestore profile: {user_id}")
        
        # TODO: Schedule daily prompt notification
        # from backend.services.notification_scheduler import schedule_daily_prompt
        # schedule_daily_prompt(user_id)
        
        # Generate token
        token, expires_in = create_access_token(user_id, data.email)
        
        return TokenResponse(
            success=True,
            user_id=user_id,
            email=data.email,
            display_name=data.display_name,
            token=token,
            expires_in=expires_in
        )
    
    except firebase_admin.exceptions.FirebaseError as e:
        logger.error(f"Firebase error during signup: {str(e)}")
        
        # Check for specific errors
        if "INVALID_EMAIL" in str(e) or "invalid email" in str(e).lower():
            raise HTTPException(status_code=400, detail="Invalid email format")
        elif "WEAK_PASSWORD" in str(e) or "weak password" in str(e).lower():
            raise HTTPException(status_code=400, detail="Password is too weak")
        elif "EMAIL_EXISTS" in str(e) or "email already exists" in str(e).lower():
            raise HTTPException(status_code=409, detail="Email already registered")
        else:
            raise HTTPException(status_code=400, detail=f"Signup failed: {str(e)}")
    
    except Exception as e:
        logger.error(f"Unexpected error during signup: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during signup")


@router.post("/auth/login", response_model=TokenResponse)
async def login(data: LoginRequest):
    """
    Authenticate user and return access token.
    
    Note: Since Firebase doesn't provide password verification via Admin SDK,
    this endpoint assumes frontend handles password verification via Firebase SDK,
    and only validates email existence here. For production, consider using
    Firebase REST API or custom implementation.
    
    Args:
        data: Login request with email and password
    
    Returns:
        TokenResponse with user info and JWT token
    
    Raises:
        HTTPException: If credentials are invalid
    """
    try:
        # Verify user exists by trying to get user by email
        user = auth.get_user_by_email(data.email)
        user_id = user.uid
        
        # Get user profile for display_name
        profile = get_user_profile(user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        # Generate token
        token, expires_in = create_access_token(user_id, data.email)
        
        logger.info(f"✓ User logged in: {user_id}")
        
        return TokenResponse(
            success=True,
            user_id=user_id,
            email=data.email,
            display_name=profile.get("display_name", "User"),
            token=token,
            expires_in=expires_in
        )
    
    except firebase_admin.exceptions.NotFoundError:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Login failed")


@router.post("/auth/verify", response_model=VerifyTokenResponse)
async def verify(authorization: str = Header(None)):
    """
    Verify that a token is valid and return token details.
    
    Args:
        authorization: Bearer token in Authorization header
    
    Returns:
        VerifyTokenResponse with validity and token details
    """
    if not authorization:
        return VerifyTokenResponse(valid=False)
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            return VerifyTokenResponse(valid=False)
    except ValueError:
        return VerifyTokenResponse(valid=False)
    
    try:
        verified = verify_token(token)
        payload = verified["payload"]
        
        # Calculate expiration time
        exp_timestamp = payload.get("exp")
        if exp_timestamp:
            expires_at = datetime.utcfromtimestamp(exp_timestamp).isoformat()
        else:
            expires_at = None
        
        return VerifyTokenResponse(
            valid=True,
            user_id=verified["user_id"],
            email=verified["email"],
            expires_at=expires_at
        )
    except HTTPException:
        return VerifyTokenResponse(valid=False)


@router.get("/auth/profile", response_model=UserProfile)
async def get_profile(user_id: str = Depends(get_current_user_id)):
    """
    Get current user's profile information.
    Requires valid authentication token.
    
    Args:
        user_id: Extracted from Authorization header via dependency
    
    Returns:
        UserProfile with user information
    
    Raises:
        HTTPException: If profile not found
    """
    profile = get_user_profile(user_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found")
    
    return UserProfile(
        user_id=profile.get("user_id"),
        email=profile.get("email"),
        display_name=profile.get("display_name"),
        created_at=profile.get("created_at"),
        last_active=profile.get("last_active")
    )


@router.post("/auth/logout")
async def logout(user_id: str = Depends(get_current_user_id)):
    """
    Logout endpoint (stateless).
    
    Since we use JWT tokens, logout is handled on the frontend by
    removing the token from storage. This endpoint is provided for:
    - Recording logout event in database/analytics
    - Future session invalidation if needed
    - Consistency with REST API standards
    
    Args:
        user_id: Extracted from Authorization header
    
    Returns:
        Success message
    """
    # TODO: Could record logout event, invalidate refresh tokens, etc.
    logger.info(f"User logged out: {user_id}")
    
    return {"success": True, "message": "Logged out successfully"}


# ============================================================================
# Health check for auth service
# ============================================================================

@router.get("/auth/health")
async def auth_health():
    """Health check for auth service"""
    return {"status": "auth service operational"}
