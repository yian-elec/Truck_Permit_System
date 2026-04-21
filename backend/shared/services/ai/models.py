"""
models.py - AI Service 資料模型
定義 AI 服務的請求和回應格式
"""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class ChatMessage(BaseModel):
    """聊天訊息模型"""
    role: Literal["system", "user", "assistant", "function"] = Field(
        description="訊息角色"
    )
    content: str = Field(description="訊息內容")
    name: Optional[str] = Field(default=None, description="函數名稱（當 role 為 function 時）")
    function_call: Optional[Dict[str, Any]] = Field(default=None, description="函數調用資訊")
    
    class Config:
        json_schema_extra = {
            "example": {
                "role": "user",
                "content": "你好，請幫我翻譯這段文字"
            }
        }


class ChatRequest(BaseModel):
    """聊天請求模型"""
    message: str = Field(description="用戶訊息")
    model: Optional[str] = Field(
        default=None,
        description="AI 模型名稱，如 gpt-4, gpt-3.5-turbo"
    )
    system_prompt: Optional[str] = Field(
        default=None,
        description="系統提示詞（預設角色設定）"
    )
    temperature: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=2.0,
        description="溫度參數，控制回應的隨機性 (0-2)"
    )
    max_tokens: Optional[int] = Field(
        default=None,
        ge=1,
        description="最大 token 數量"
    )
    stream: bool = Field(
        default=False,
        description="是否使用串流模式"
    )
    conversation_id: Optional[str] = Field(
        default=None,
        description="對話 ID（用於維護對話歷史）"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "請幫我寫一段 Python 程式碼",
                "model": "gpt-4",
                "system_prompt": "你是一個專業的 Python 程式設計師",
                "temperature": 0.7,
                "stream": False
            }
        }


class ChatResponse(BaseModel):
    """聊天回應模型"""
    message: str = Field(description="AI 回應內容")
    model: str = Field(description="使用的 AI 模型")
    conversation_id: Optional[str] = Field(
        default=None,
        description="對話 ID"
    )
    tokens_used: Optional[int] = Field(
        default=None,
        description="使用的 token 數量"
    )
    finish_reason: Optional[str] = Field(
        default=None,
        description="完成原因（stop, length, function_call 等）"
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="建立時間"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="額外的元數據"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "這是 AI 的回應",
                "model": "gpt-4",
                "tokens_used": 150,
                "finish_reason": "stop"
            }
        }


class ConversationHistory(BaseModel):
    """對話歷史模型"""
    conversation_id: str = Field(description="對話 ID")
    messages: List[ChatMessage] = Field(
        default_factory=list,
        description="訊息列表"
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="建立時間"
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        description="更新時間"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="對話元數據"
    )
    
    def add_message(self, message: ChatMessage):
        """添加訊息到歷史記錄"""
        self.messages.append(message)
        self.updated_at = datetime.now()
    
    def get_messages(self, limit: Optional[int] = None) -> List[ChatMessage]:
        """取得訊息列表"""
        if limit:
            return self.messages[-limit:]
        return self.messages
    
    def clear(self):
        """清除歷史記錄"""
        self.messages = []
        self.updated_at = datetime.now()


class FunctionCall(BaseModel):
    """函數調用模型"""
    name: str = Field(description="函數名稱")
    arguments: Dict[str, Any] = Field(description="函數參數")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "get_weather",
                "arguments": {
                    "location": "Taipei",
                    "unit": "celsius"
                }
            }
        }


class StreamResponse(BaseModel):
    """串流回應模型"""
    content: str = Field(description="內容片段")
    is_final: bool = Field(
        default=False,
        description="是否為最後一個片段"
    )
    tokens_used: Optional[int] = Field(
        default=None,
        description="使用的 token 數量"
    )

