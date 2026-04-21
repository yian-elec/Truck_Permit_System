"""
AuthError - 認證錯誤
用於 JWT 驗證失敗的情況
狀態碼：401 Unauthorized
"""

from typing import Any, Dict, Optional
from .system_error import SystemError


class AuthError(SystemError):
    """
    認證錯誤
    
    用途：JWT 驗證失敗 (缺少 / 無效 / 過期)
    狀態碼：401 Unauthorized
    
    範例：
    {
        "data": null,
        "error": {
            "code": "MissingTokenError",
            "message": "Missing Authorization header",
            "details": null
        }
    }
    
    {
        "data": null,
        "error": {
            "code": "InvalidTokenError",
            "message": "Invalid JWT token",
            "details": null
        }
    }
    """
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        初始化認證錯誤
        
        Args:
            message: 人類可讀的錯誤訊息
            details: 可選的詳細資訊，用於 debug
        """
        super().__init__(message, details)
    
    @property
    def status_code(self) -> int:
        """HTTP 狀態碼：401 Unauthorized"""
        return 401


class MissingTokenError(AuthError):
    """缺少 Authorization header 錯誤"""
    pass


class InvalidTokenError(AuthError):
    """無效 JWT token 錯誤"""
    pass


class ExpiredTokenError(AuthError):
    """過期 JWT token 錯誤"""
    pass
