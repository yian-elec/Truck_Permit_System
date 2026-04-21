"""
ConflictError - 資源衝突錯誤
用於資源衝突的情況
狀態碼：409 Conflict
"""

from typing import Any, Dict, Optional
from .app_error import AppError


class ConflictError(AppError):
    """
    資源衝突錯誤
    
    用途：資源衝突
    狀態碼：409 Conflict
    
    範例：
    {
        "data": null,
        "error": {
            "code": "ResourceConflictError",
            "message": "Resource already exists",
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
        初始化資源衝突錯誤
        
        Args:
            message: 人類可讀的錯誤訊息
            details: 可選的詳細資訊，用於 debug
        """
        super().__init__(message, details)
    
    @property
    def status_code(self) -> int:
        """HTTP 狀態碼：409 Conflict"""
        return 409
