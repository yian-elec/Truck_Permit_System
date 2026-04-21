"""
ai_config.py - AI 相關設定
管理 OpenAI 和 LangChain 相關設定
"""

from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field

from .env_file_path import backend_env_file


class AIConfig(BaseSettings):
    """
    AI 設定類別
    管理 OpenAI 和 LangChain 相關設定
    """
    
    # OpenAI 設定
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    openai_api_base: Optional[str] = Field(default=None, env="OPENAI_API_BASE")
    openai_organization: Optional[str] = Field(default=None, env="OPENAI_ORGANIZATION")
    
    # 預設模型設定
    default_model: str = Field(default="gpt-3.5-turbo", env="AI_DEFAULT_MODEL")
    default_temperature: float = Field(default=0.7, env="AI_DEFAULT_TEMPERATURE")
    default_max_tokens: int = Field(default=1000, env="AI_DEFAULT_MAX_TOKENS")
    
    # 支援的模型列表
    supported_models: List[str] = [
        "gpt-4",
        "gpt-4-turbo-preview",
        "gpt-4-1106-preview",
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-16k",
    ]
    
    # 超時設定
    request_timeout: int = Field(default=60, env="AI_REQUEST_TIMEOUT")
    
    # 重試設定
    max_retries: int = Field(default=3, env="AI_MAX_RETRIES")
    
    # 串流設定
    enable_streaming: bool = Field(default=True, env="AI_ENABLE_STREAMING")
    
    # 對話歷史設定
    max_history_messages: int = Field(default=10, env="AI_MAX_HISTORY_MESSAGES")
    
    # 快取設定
    enable_cache: bool = Field(default=False, env="AI_ENABLE_CACHE")
    cache_ttl: int = Field(default=3600, env="AI_CACHE_TTL")
    
    class Config:
        env_file = backend_env_file()
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"
