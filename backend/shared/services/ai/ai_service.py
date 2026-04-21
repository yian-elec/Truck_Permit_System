"""
ai_service.py - AI 服務核心實現
使用 LangChain 和 OpenAI 提供 AI 對話功能
"""

import uuid
from typing import Optional, List, Dict, Any, AsyncIterator
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

from shared.core.config import settings
from shared.core.logger.logger import logger
from .models import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    ConversationHistory,
    StreamResponse
)
from .prompts import PromptTemplates


class AIService:
    """
    AI 服務類
    提供 OpenAI 整合功能
    """
    
    def __init__(self):
        """初始化 AI 服務"""
        self.config = settings.ai
        self.conversations: Dict[str, ConversationHistory] = {}
        
        # 驗證 API Key
        if not self.config.openai_api_key:
            logger.warn("OpenAI API Key not configured")
    
    def _get_llm(
        self,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        streaming: bool = False
    ) -> ChatOpenAI:
        """
        取得 LangChain ChatOpenAI 實例
        
        Args:
            model: 模型名稱
            temperature: 溫度參數
            max_tokens: 最大 token 數
            streaming: 是否使用串流
            
        Returns:
            ChatOpenAI 實例
        """
        return ChatOpenAI(
            model=model or self.config.default_model,
            temperature=temperature if temperature is not None else self.config.default_temperature,
            max_tokens=max_tokens or self.config.default_max_tokens,
            openai_api_key=self.config.openai_api_key,
            openai_api_base=self.config.openai_api_base,
            streaming=streaming,
            request_timeout=self.config.request_timeout,
            max_retries=self.config.max_retries
        )
    
    async def chat(
        self,
        message: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        conversation_id: Optional[str] = None
    ) -> ChatResponse:
        """
        發送聊天訊息並取得回應
        
        Args:
            message: 用戶訊息
            model: AI 模型名稱
            system_prompt: 系統提示詞
            temperature: 溫度參數
            max_tokens: 最大 token 數
            conversation_id: 對話 ID（用於維護歷史）
            
        Returns:
            ChatResponse: AI 回應
        """
        try:
            logger.info(f"Processing chat request", 
                       model=model or self.config.default_model,
                       has_history=conversation_id is not None)
            
            # 取得 LLM 實例
            llm = self._get_llm(model, temperature, max_tokens, streaming=False)
            
            # 準備訊息
            messages = []
            
            # 添加系統提示詞
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))
            
            # 如果有對話 ID，載入歷史記錄
            if conversation_id and conversation_id in self.conversations:
                history = self.conversations[conversation_id]
                for msg in history.get_messages(limit=self.config.max_history_messages):
                    if msg.role == "system":
                        messages.append(SystemMessage(content=msg.content))
                    elif msg.role == "user":
                        messages.append(HumanMessage(content=msg.content))
                    elif msg.role == "assistant":
                        messages.append(AIMessage(content=msg.content))
            
            # 添加當前訊息
            messages.append(HumanMessage(content=message))
            
            # 調用 LLM
            response = await llm.ainvoke(messages)
            
            # 取得回應內容
            response_content = response.content
            
            # 儲存到對話歷史
            if conversation_id:
                if conversation_id not in self.conversations:
                    self.conversations[conversation_id] = ConversationHistory(
                        conversation_id=conversation_id
                    )
                
                # 添加用戶訊息和 AI 回應
                self.conversations[conversation_id].add_message(
                    ChatMessage(role="user", content=message)
                )
                self.conversations[conversation_id].add_message(
                    ChatMessage(role="assistant", content=response_content)
                )
            
            logger.info("Chat request processed successfully")
            
            # 建立回應
            return ChatResponse(
                message=response_content,
                model=model or self.config.default_model,
                conversation_id=conversation_id,
                finish_reason="stop",
                metadata={
                    "system_prompt": system_prompt,
                    "temperature": temperature or self.config.default_temperature
                }
            )
            
        except Exception as e:
            logger.error(f"Chat request failed: {str(e)}")
            raise
    
    async def chat_with_template(
        self,
        message: str,
        template_name: str,
        model: Optional[str] = None,
        **kwargs
    ) -> ChatResponse:
        """
        使用預設模板發送聊天訊息
        
        Args:
            message: 用戶訊息
            template_name: 模板名稱
            model: AI 模型名稱
            **kwargs: 其他參數
            
        Returns:
            ChatResponse: AI 回應
        """
        system_prompt = PromptTemplates.get_template(template_name)
        return await self.chat(
            message=message,
            model=model,
            system_prompt=system_prompt,
            **kwargs
        )
    
    async def stream_chat(
        self,
        message: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> AsyncIterator[StreamResponse]:
        """
        串流模式聊天
        
        Args:
            message: 用戶訊息
            model: AI 模型名稱
            system_prompt: 系統提示詞
            temperature: 溫度參數
            max_tokens: 最大 token 數
            
        Yields:
            StreamResponse: 串流回應片段
        """
        try:
            logger.info("Processing streaming chat request")
            
            # 取得 LLM 實例（啟用串流）
            llm = self._get_llm(model, temperature, max_tokens, streaming=True)
            
            # 準備訊息
            messages = []
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))
            messages.append(HumanMessage(content=message))
            
            # 串流調用
            full_response = ""
            async for chunk in llm.astream(messages):
                if chunk.content:
                    full_response += chunk.content
                    yield StreamResponse(
                        content=chunk.content,
                        is_final=False
                    )
            
            # 發送最後一個片段
            yield StreamResponse(
                content="",
                is_final=True
            )
            
            logger.info("Streaming chat completed")
            
        except Exception as e:
            logger.error(f"Streaming chat failed: {str(e)}")
            raise
    
    def create_conversation(self, conversation_id: Optional[str] = None) -> str:
        """
        創建新對話
        
        Args:
            conversation_id: 對話 ID（可選，不提供則自動生成）
            
        Returns:
            對話 ID
        """
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        
        self.conversations[conversation_id] = ConversationHistory(
            conversation_id=conversation_id
        )
        
        logger.info(f"Created new conversation: {conversation_id}")
        return conversation_id
    
    def get_conversation(self, conversation_id: str) -> Optional[ConversationHistory]:
        """
        取得對話歷史
        
        Args:
            conversation_id: 對話 ID
            
        Returns:
            對話歷史或 None
        """
        return self.conversations.get(conversation_id)
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """
        刪除對話
        
        Args:
            conversation_id: 對話 ID
            
        Returns:
            是否成功刪除
        """
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            logger.info(f"Deleted conversation: {conversation_id}")
            return True
        return False
    
    def clear_conversation(self, conversation_id: str) -> bool:
        """
        清除對話歷史（保留對話 ID）
        
        Args:
            conversation_id: 對話 ID
            
        Returns:
            是否成功清除
        """
        if conversation_id in self.conversations:
            self.conversations[conversation_id].clear()
            logger.info(f"Cleared conversation: {conversation_id}")
            return True
        return False
    
    async def summarize_text(
        self,
        text: str,
        max_length: int = 200,
        model: Optional[str] = None
    ) -> str:
        """
        文字摘要功能
        
        Args:
            text: 要摘要的文字
            max_length: 最大摘要長度
            model: AI 模型名稱
            
        Returns:
            摘要文字
        """
        prompt = f"""請用不超過 {max_length} 字總結以下內容：

{text}

摘要："""
        
        response = await self.chat(
            message=prompt,
            model=model,
            system_prompt=PromptTemplates.SUMMARIZER,
            temperature=0.3
        )
        
        return response.message
    
    async def translate_text(
        self,
        text: str,
        target_language: str,
        source_language: Optional[str] = None,
        model: Optional[str] = None
    ) -> str:
        """
        文字翻譯功能
        
        Args:
            text: 要翻譯的文字
            target_language: 目標語言
            source_language: 來源語言（可選）
            model: AI 模型名稱
            
        Returns:
            翻譯後的文字
        """
        if source_language:
            prompt = f"請將以下 {source_language} 文字翻譯成 {target_language}：\n\n{text}"
        else:
            prompt = f"請將以下文字翻譯成 {target_language}：\n\n{text}"
        
        response = await self.chat(
            message=prompt,
            model=model,
            system_prompt=PromptTemplates.TRANSLATION_ASSISTANT,
            temperature=0.3
        )
        
        return response.message
    
    async def generate_code(
        self,
        description: str,
        language: str,
        model: Optional[str] = None
    ) -> str:
        """
        程式碼生成功能
        
        Args:
            description: 程式碼描述
            language: 程式語言
            model: AI 模型名稱
            
        Returns:
            生成的程式碼
        """
        prompt = f"請用 {language} 寫一段程式碼：{description}"
        
        response = await self.chat(
            message=prompt,
            model=model,
            system_prompt=PromptTemplates.PROGRAMMING_ASSISTANT,
            temperature=0.2
        )
        
        return response.message
    
    async def extract_json(
        self,
        text: str,
        schema_description: Optional[str] = None,
        model: Optional[str] = None
    ) -> str:
        """
        從文字中提取 JSON
        
        Args:
            text: 輸入文字
            schema_description: JSON schema 描述
            model: AI 模型名稱
            
        Returns:
            JSON 字串
        """
        if schema_description:
            prompt = f"""從以下文字中提取資訊，並按照此格式返回 JSON：
{schema_description}

文字：
{text}"""
        else:
            prompt = f"從以下文字中提取關鍵資訊，以 JSON 格式返回：\n\n{text}"
        
        response = await self.chat(
            message=prompt,
            model=model,
            system_prompt=PromptTemplates.JSON_GENERATOR,
            temperature=0.1
        )
        
        return response.message
    
    def get_available_models(self) -> List[str]:
        """
        取得可用的 AI 模型列表
        
        Returns:
            模型列表
        """
        return self.config.supported_models
    
    def get_available_templates(self) -> Dict[str, str]:
        """
        取得可用的提示詞模板
        
        Returns:
            模板字典
        """
        return PromptTemplates.get_all_templates()


# 全域 AI Service 實例
ai_service = AIService()

