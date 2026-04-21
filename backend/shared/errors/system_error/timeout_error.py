"""
TimeoutError - 外部 API 逾時錯誤
用於外部 API 逾時的情況
狀態碼：504 Gateway Timeout
"""

from typing import Any, Dict, Optional
from .system_error import SystemError


class TimeoutError(SystemError):
    """
    外部 API 逾時錯誤
    
    用途：外部 API 逾時
    狀態碼：504 Gateway Timeout
    
    範例：
    {
        "data": null,
        "error": {
            "code": "ExternalAPITimeoutException",
            "message": "External API request timed out",
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
        初始化外部 API 逾時錯誤
        
        Args:
            message: 人類可讀的錯誤訊息
            details: 可選的詳細資訊，用於 debug
        """
        super().__init__(message, details)
    
    @property
    def status_code(self) -> int:
        """HTTP 狀態碼：504 Gateway Timeout"""
        return 504


class ExternalAPITimeoutException(TimeoutError):
    """外部 API 請求逾時錯誤"""
    pass


class DatabaseTimeoutException(TimeoutError):
    """資料庫操作逾時錯誤"""
    pass
