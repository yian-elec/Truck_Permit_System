"""
AI Service - OpenAI 和 LangChain 整合服務
提供簡單易用的 AI 對話功能
"""

from .ai_service import AIService
from .models import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    ConversationHistory,
    FunctionCall,
    StreamResponse
)
from .prompts import PromptTemplates

__all__ = [
    "AIService",
    "ChatMessage",
    "ChatRequest",
    "ChatResponse",
    "ConversationHistory",
    "FunctionCall",
    "StreamResponse",
    "PromptTemplates"
]

