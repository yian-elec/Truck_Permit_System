"""
AppError - Application 層錯誤基底類別
用於 Use Case 流程錯誤 (授權、資源衝突)
狀態碼：403 Forbidden, 409 Conflict
"""

from typing import Any, Dict, Optional
from shared.errors.base_error.base_error import BaseError


class AppError(BaseError):
    """
    Application 層錯誤基底類別
    
    用途：Use Case 流程錯誤 (授權、資源衝突)
    狀態碼：403 Forbidden, 409 Conflict
    命名規則：PascalCase + Error
    """
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        初始化 Application 錯誤
        
        Args:
            message: 人類可讀的錯誤訊息
            details: 可選的詳細資訊，用於 debug
        """
        super().__init__(message, details)
    
    @property
    def status_code(self) -> int:
        """
        HTTP 狀態碼
        預設為 403 Forbidden
        子類別可以覆寫為 409 Conflict
        """
        return 403
