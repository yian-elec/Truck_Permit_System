"""
InternalError - 系統內部錯誤
用於系統內部錯誤的情況
狀態碼：500 Internal Server Error
"""

from typing import Any, Dict, Optional
from .system_error import SystemError


class InternalError(SystemError):
    """
    系統內部錯誤
    
    用途：系統內部錯誤
    狀態碼：500 Internal Server Error
    
    範例：
    {
        "data": null,
        "error": {
            "code": "DBConnectionException",
            "message": "Database connection failed",
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
        初始化系統內部錯誤
        
        Args:
            message: 人類可讀的錯誤訊息
            details: 可選的詳細資訊，用於 debug
        """
        super().__init__(message, details)
    
    @property
    def status_code(self) -> int:
        """HTTP 狀態碼：500 Internal Server Error"""
        return 500


class DBConnectionException(InternalError):
    """資料庫連線失敗錯誤"""
    pass


class ConfigurationException(InternalError):
    """設定檔錯誤"""
    pass


class ServiceUnavailableException(InternalError):
    """服務不可用錯誤"""
    pass
