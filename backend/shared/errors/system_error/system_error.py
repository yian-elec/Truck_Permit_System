"""
SystemError - System 層錯誤基底類別
用於系統與技術性錯誤 (安全、基礎設施、外部 API)
狀態碼：401 Unauthorized, 500 Internal Server Error, 504 Gateway Timeout
"""

from typing import Any, Dict, Optional
from shared.errors.base_error.base_error import BaseError


class SystemError(BaseError):
    """
    System 層錯誤基底類別
    
    用途：系統與技術性錯誤 (安全、基礎設施、外部 API)
    狀態碼：401 Unauthorized, 500 Internal Server Error, 504 Gateway Timeout
    命名規則：PascalCase + Exception (安全例外可用 ...Error)
    """
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        初始化 System 錯誤
        
        Args:
            message: 人類可讀的錯誤訊息
            details: 可選的詳細資訊，用於 debug
        """
        super().__init__(message, details)
    
    @property
    def status_code(self) -> int:
        """
        HTTP 狀態碼
        預設為 500 Internal Server Error
        子類別可以覆寫為 401 Unauthorized 或 504 Gateway Timeout
        """
        return 500
