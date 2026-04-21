"""
ValidationError - 驗證錯誤
用於 Domain 規則不符的情況
狀態碼：422 Unprocessable Entity
"""

from typing import Any, Dict, Optional
from .domain_error import DomainError


class ValidationError(DomainError):
    """
    驗證錯誤
    
    用途：Domain 規則不符
    狀態碼：422 Unprocessable Entity
    
    範例：
    {
        "data": null,
        "error": {
            "code": "InvalidAnswerError",
            "message": "Answer format is invalid",
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
        初始化驗證錯誤
        
        Args:
            message: 人類可讀的錯誤訊息
            details: 可選的詳細資訊，用於 debug
        """
        super().__init__(message, details)
    
    @property
    def status_code(self) -> int:
        """HTTP 狀態碼：422 Unprocessable Entity"""
        return 422
