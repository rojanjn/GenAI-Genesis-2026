from fastapi import APIRouter

router = APIRouter()


@router.get("/chat/health")
def chat_health():
    return {"chat": "ok"}