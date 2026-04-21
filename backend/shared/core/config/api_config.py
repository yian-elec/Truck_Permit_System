"""
api_config.py - API 相關設定
管理 API 相關設定 (host, port, 路由等)
"""

from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field

from .env_file_path import backend_env_file


class APIConfig(BaseSettings):
    """
    API 設定類別
    管理 API 相關設定
    """
    
    # 伺服器設定
    host: str = Field(default="0.0.0.0", env="API_HOST")
    port: int = Field(default=8000, env="API_PORT")
    
    # API 版本設定
    version: str = Field(default="v1", env="API_VERSION")
    prefix: str = Field(default="/api", env="API_PREFIX")
    
    # 應用程式設定
    title: str = Field(default="Truck_Permit_System API", env="API_TITLE")
    description: str = Field(default="Truck_Permit_System Backend API", env="API_DESCRIPTION")
    version_info: str = Field(default="1.0.0", env="API_VERSION_INFO")
    
    # 文檔設定
    docs_url: str = Field(default="/docs", env="API_DOCS_URL")
    redoc_url: str = Field(default="/redoc", env="API_REDOC_URL")
    openapi_url: str = Field(default="/openapi.json", env="API_OPENAPI_URL")
    
    # 健康檢查設定
    health_check_url: str = Field(default="/health", env="API_HEALTH_CHECK_URL")
    
    # 請求設定
    max_request_size: int = Field(default=10485760, env="API_MAX_REQUEST_SIZE")  # 10MB
    request_timeout: int = Field(default=30, env="API_REQUEST_TIMEOUT")  # 30 秒
    
    # 回應設定
    response_timeout: int = Field(default=30, env="API_RESPONSE_TIMEOUT")  # 30 秒
    
    # 分頁設定
    default_page_size: int = Field(default=20, env="API_DEFAULT_PAGE_SIZE")
    max_page_size: int = Field(default=100, env="API_MAX_PAGE_SIZE")
    
    # 快取設定
    cache_ttl: int = Field(default=300, env="API_CACHE_TTL")  # 5 分鐘
    
    # 其他設定
    enable_metrics: bool = Field(default=True, env="API_ENABLE_METRICS")
    enable_tracing: bool = Field(default=False, env="API_ENABLE_TRACING")
    
    @property
    def base_url(self) -> str:
        """
        取得 API 基礎 URL
        
        Returns:
            API 基礎 URL
        """
        return f"http://{self.host}:{self.port}{self.prefix}/{self.version}"
    
    @property
    def full_docs_url(self) -> str:
        """
        取得完整的文檔 URL
        
        Returns:
            完整的文檔 URL
        """
        return f"http://{self.host}:{self.port}{self.docs_url}"
    
    class Config:
        env_file = backend_env_file()
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"
