"""
NotFoundError - 資源不存在錯誤
用於資源不存在的情況
狀態碼：404 Not Found
"""

from typing import Any, Dict, Optional
from .domain_error import DomainError


class NotFoundError(DomainError):
    """
    資源不存在錯誤
    
    用途：資源不存在
    狀態碼：404 Not Found
    
    範例：
    {
        "data": null,
        "error": {
            "code": "SessionNotFoundError",
            "message": "Study session does not exist",
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
        初始化資源不存在錯誤
        
        Args:
            message: 人類可讀的錯誤訊息
            details: 可選的詳細資訊，用於 debug
        """
        super().__init__(message, details)
    
    @property
    def status_code(self) -> int:
        """HTTP 狀態碼：404 Not Found"""
        return 404
