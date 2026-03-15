from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import os

from .diary import router as diary_router
from .chat import router as chat_router
from .insights import router as insights_router
from .auth import router as auth_router
from .moods import router as moods_router
from .history import router as history_router
from backend.db.firebase_client import init_firebase
from backend.services.scheduler import start_background_tasks, stop_background_tasks

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Agentic Reflection Companion API",
    description="Backend API for journaling and mood reflection system",
    version="1.0.0"
)

# CORS configuration - allow frontend + localhost for development
cors_origins = [
    "http://localhost:3000",  # React development
    "http://127.0.0.1:3000",
    "http://localhost:5173",  # Vite development
    "http://127.0.0.1:5173",
]

# Add production domain if available
if os.getenv("FRONTEND_URL"):
    cors_origins.append(os.getenv("FRONTEND_URL"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "Authorization"],
)

# Register routers
app.include_router(auth_router, prefix="/api", tags=["Authentication"])
app.include_router(diary_router, prefix="/api", tags=["Diary"])
app.include_router(moods_router, prefix="/api", tags=["Moods"])
app.include_router(chat_router, prefix="/api", tags=["Chat"])
app.include_router(insights_router, prefix="/api", tags=["Insights"])
app.include_router(history_router, prefix="/api", tags=["History"])

@app.on_event("startup")
def startup_event():
    init_firebase()
    logger.info("✓ Firebase initialised")

    try:
        start_background_tasks()
        logger.info("✓ Background tasks started")
    except Exception as e:
        logger.warning(f"Background tasks failed to start: {e}")

# Root endpoint
@app.get("/")
def root():
    logger.info("Health check called")
    return {"status": "backend running"}


@app.on_event("shutdown")
def shutdown_event():
    try:
        stop_background_tasks()
        logger.info("✓ Background tasks stopped")
    except Exception as e:
        logger.warning(f"Error stopping background tasks: {e}")


# run
# python -m uvicorn backend.api.main:app --reload
# http://127.0.0.1:8000/docs
