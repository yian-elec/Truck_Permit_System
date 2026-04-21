"""
DomainError - Domain 層錯誤基底類別
用於業務邏輯錯誤
狀態碼：422 Unprocessable Entity, 404 Not Found
"""

from typing import Any, Dict, Optional
from shared.errors.base_error.base_error import BaseError


class DomainError(BaseError):
    """
    Domain 層錯誤基底類別
    
    用途：業務邏輯錯誤
    狀態碼：422 Unprocessable Entity, 404 Not Found
    命名規則：PascalCase + Error
    """
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        初始化 Domain 錯誤
        
        Args:
            message: 人類可讀的錯誤訊息
            details: 可選的詳細資訊，用於 debug
        """
        super().__init__(message, details)
    
    @property
    def status_code(self) -> int:
        """
        HTTP 狀態碼
        預設為 422 Unprocessable Entity
        子類別可以覆寫為 404 Not Found
        """
        return 422
