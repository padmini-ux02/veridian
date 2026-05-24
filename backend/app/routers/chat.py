"""Chat API routes for AI assistant interactions."""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.ai.chat_assistant import ChatAssistant
from app.database import get_db
from app.models.user import User
from app.services.scan_service import ScanService
from app.utils.security import get_current_user

logger = logging.getLogger("veridian.routers.chat")

router = APIRouter(prefix="/chat", tags=["AI Chat Assistant"])

# Singleton assistant instance
_chat_assistant: Optional[ChatAssistant] = None


def get_assistant() -> ChatAssistant:
    global _chat_assistant
    if _chat_assistant is None:
        _chat_assistant = ChatAssistant()
    return _chat_assistant


class ChatRequest(BaseModel):
    """Schema for chat message request."""
    message: str = Field(..., min_length=1, max_length=2000)
    scan_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Schema for chat response."""
    response: str
    intent: str
    has_context: bool


@router.post("/", response_model=ChatResponse)
def chat_with_assistant(
    chat_data: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Send a message to the AI fraud detection assistant.

    Optionally provide a scan_id to give the assistant context
    about a specific scan result for more targeted guidance.
    """
    scan_context = None

    if chat_data.scan_id:
        scan_result = ScanService.get_scan_by_id(
            db=db, scan_id=chat_data.scan_id, user_id=current_user.id
        )
        if scan_result:
            scan_context = scan_result

    assistant = get_assistant()
    result = assistant.chat(
        message=chat_data.message,
        scan_context=scan_context,
    )

    return ChatResponse(
        response=result["response"],
        intent=result["intent"],
        has_context=result["has_context"],
    )
