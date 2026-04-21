"""
security_config.py - 安全 / JWT 相關設定
管理 JWT 和安全相關設定
"""

from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field

from .env_file_path import backend_env_file


class SecurityConfig(BaseSettings):
    """
    安全設定類別
    管理 JWT 和安全相關設定
    """
    
    # JWT 設定
    jwt_secret: str = Field(default="your-secret-key-here", env="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expire_seconds: int = Field(default=3600, env="JWT_EXPIRE_SECONDS")  # 1 小時
    jwt_refresh_expire_seconds: int = Field(default=86400, env="JWT_REFRESH_EXPIRE_SECONDS")  # 24 小時
    
    # 密碼設定
    password_min_length: int = Field(default=8, env="PASSWORD_MIN_LENGTH")
    password_require_uppercase: bool = Field(default=True, env="PASSWORD_REQUIRE_UPPERCASE")
    password_require_lowercase: bool = Field(default=True, env="PASSWORD_REQUIRE_LOWERCASE")
    password_require_numbers: bool = Field(default=True, env="PASSWORD_REQUIRE_NUMBERS")
    password_require_special_chars: bool = Field(default=True, env="PASSWORD_REQUIRE_SPECIAL_CHARS")
    
    # 加密設定
    bcrypt_rounds: int = Field(default=12, env="BCRYPT_ROUNDS")
    
    # CORS 設定（預檢會帶 Access-Control-Request-Method: GET/POST/...，須全部列出）
    cors_origins: List[str] = Field(
        default=["*"],
        env="CORS_ORIGINS",
        description="含 credentials 時建議改為明確來源，例如 http://localhost:5173",
    )
    cors_methods: List[str] = Field(
        default=["GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        env="CORS_METHODS",
    )
    cors_headers: List[str] = Field(default=["*"], env="CORS_HEADERS")
    
    # 速率限制設定
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=60, env="RATE_LIMIT_WINDOW")  # 秒
    
    # 其他安全設定
    session_timeout: int = Field(default=1800, env="SESSION_TIMEOUT")  # 30 分鐘
    max_login_attempts: int = Field(default=5, env="MAX_LOGIN_ATTEMPTS")
    lockout_duration: int = Field(default=900, env="LOCKOUT_DURATION")  # 15 分鐘
    
    class Config:
        env_file = backend_env_file()
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"
