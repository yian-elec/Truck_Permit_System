"""
ForbiddenError - 權限不足錯誤
用於權限不足的情況
狀態碼：403 Forbidden
"""

from typing import Any, Dict, Optional
from .app_error import AppError


class ForbiddenError(AppError):
    """
    權限不足錯誤
    
    用途：權限不足
    狀態碼：403 Forbidden
    
    範例：
    {
        "data": null,
        "error": {
            "code": "ForbiddenAccessError",
            "message": "You do not have permission",
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
        初始化權限不足錯誤
        
        Args:
            message: 人類可讀的錯誤訊息
            details: 可選的詳細資訊，用於 debug
        """
        super().__init__(message, details)
    
    @property
    def status_code(self) -> int:
        """HTTP 狀態碼：403 Forbidden"""
        return 403
