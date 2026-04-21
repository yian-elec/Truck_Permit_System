"""
JWTHandler - JWT 處理器
提供 JWT encode/decode/verify 功能
使用 HS256 演算法
"""

import jwt
import os
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from shared.errors.system_error.auth_error import (
    MissingTokenError,
    InvalidTokenError,
    ExpiredTokenError
)


class JWTHandler:
    """
    JWT 處理器
    
    使用 JWT (JSON Web Token)，演算法 HS256
    Payload 固定欄位：
    {
        "sub": "user_id",   // 使用者唯一識別
        "exp": 1234567890,  // 過期時間 (timestamp)
        "iat": 1234567000,  // 簽發時間
        "roles": ["user"]   // 使用者角色
    }
    """
    
    def __init__(self, secret_key: Optional[str] = None):
        """
        初始化 JWT 處理器
        
        Args:
            secret_key: JWT 密鑰，如果未提供則從配置取得
        """
        from shared.core.config import settings
        
        self.secret_key = secret_key or settings.security.jwt_secret
        self.algorithm = settings.security.jwt_algorithm
        self.default_expiry_hours = settings.security.jwt_expire_seconds // 3600  # 轉換為小時
    
    def encode(
        self,
        user_id: str,
        roles: List[str] = None,
        expiry_hours: Optional[int] = None
    ) -> str:
        """
        編碼 JWT Token
        
        Args:
            user_id: 使用者唯一識別
            roles: 使用者角色列表，預設為 ["user"]
            expiry_hours: 過期時間（小時），預設為 24 小時
            
        Returns:
            編碼後的 JWT Token
        """
        if roles is None:
            roles = ["user"]
        
        if expiry_hours is None:
            expiry_hours = self.default_expiry_hours
        
        now_timestamp = int(time.time())
        exp_timestamp = now_timestamp + (expiry_hours * 3600)
        payload = {
            "sub": user_id,
            "iat": now_timestamp,
            "exp": exp_timestamp,
            "roles": roles
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def decode(self, token: str) -> Dict[str, Any]:
        """
        解碼 JWT Token
        
        Args:
            token: JWT Token
            
        Returns:
            解碼後的 payload
            
        Raises:
            InvalidTokenError: Token 無效
            ExpiredTokenError: Token 過期
        """
        try:
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise ExpiredTokenError("JWT token has expired")
        except jwt.InvalidTokenError:
            raise InvalidTokenError("Invalid JWT token")
    
    def verify(self, token: str) -> Dict[str, Any]:
        """
        驗證 JWT Token
        
        Args:
            token: JWT Token
            
        Returns:
            驗證成功後的 payload
            
        Raises:
            MissingTokenError: 缺少 Token
            InvalidTokenError: Token 無效
            ExpiredTokenError: Token 過期
        """
        if not token:
            raise MissingTokenError("Missing Authorization header")
        
        return self.decode(token)
    
    def extract_user_id(self, token: str) -> str:
        """
        從 JWT Token 中提取 user_id
        
        Args:
            token: JWT Token
            
        Returns:
            使用者 ID
            
        Raises:
            MissingTokenError: 缺少 Token
            InvalidTokenError: Token 無效
            ExpiredTokenError: Token 過期
        """
        payload = self.verify(token)
        return payload.get("sub")
    
    def extract_roles(self, token: str) -> List[str]:
        """
        從 JWT Token 中提取使用者角色
        
        Args:
            token: JWT Token
            
        Returns:
            使用者角色列表
            
        Raises:
            MissingTokenError: 缺少 Token
            InvalidTokenError: Token 無效
            ExpiredTokenError: Token 過期
        """
        payload = self.verify(token)
        return payload.get("roles", [])
    
    def is_token_valid(self, token: str) -> bool:
        """
        檢查 JWT Token 是否有效（不拋出異常）
        
        Args:
            token: JWT Token
            
        Returns:
            True 如果 Token 有效，False 如果無效
        """
        try:
            self.verify(token)
            return True
        except (MissingTokenError, InvalidTokenError, ExpiredTokenError):
            return False
    
    def get_token_from_header(self, authorization_header: str) -> str:
        """
        從 Authorization header 中提取 JWT Token
        
        Args:
            authorization_header: Authorization header 值
            
        Returns:
            JWT Token
            
        Raises:
            MissingTokenError: 缺少或格式錯誤的 Authorization header
        """
        if not authorization_header:
            raise MissingTokenError("Missing Authorization header")
        
        if not authorization_header.startswith("Bearer "):
            raise MissingTokenError("Invalid Authorization header format")
        
        token = authorization_header[7:]  # 移除 "Bearer " 前綴
        
        if not token:
            raise MissingTokenError("Missing JWT token")
        
        return token


# 注意：不再提供全域實例，請在需要時創建新的實例：JWTHandler()
# 這確保每次都使用最新的配置
