from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Dict

from backend.ai.chat_agent import run_chatbot_turn
from backend.ai.memory import get_or_create_assistant
from backend.api.auth import get_current_user_id

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    message: str
    chat_history: List[Dict] = []


@router.get("/health")
def chat_health():
    return {"status": "chat ok"}


@router.post("/")
async def chat_with_ai(
    request: ChatRequest,
    user_id: str = Depends(get_current_user_id),
):
    """
    Chat endpoint - requires JWT authentication.
    User ID is extracted from the Authorization header token.
    """
    assistant_id = await get_or_create_assistant(user_id)

    result = await run_chatbot_turn(
        user_message=request.message,
        assistant_id=assistant_id,
        user_id=user_id,
        chat_history=request.chat_history,
    )
    return result