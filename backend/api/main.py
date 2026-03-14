from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from .diary import router as diary_router
from .chat import router as chat_router
from .insights import router as insights_router

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Agentic Reflection Companion API",
    description="Backend API for journaling and mood reflection system",
    version="1.0.0"
)

# CORS (allow React frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(diary_router, prefix="/api", tags=["Diary"])
app.include_router(chat_router, prefix="/api", tags=["Chat"])
app.include_router(insights_router, prefix="/api", tags=["Insights"])

# Root endpoint
@app.get("/")
def root():
    logger.info("Health check called")
    return {"status": "backend running"}

# run
# python -m uvicorn backend.api.main:app --reload
# http://127.0.0.1:8000/docs