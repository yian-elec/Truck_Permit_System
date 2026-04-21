"""
BaseError - 所有錯誤的基底類別
統一錯誤格式和行為
"""

from typing import Any, Dict, Optional


class BaseError(Exception):
    """
    所有錯誤的基底類別
    
    統一錯誤格式：
    {
        "data": null,
        "error": {
            "code": "ErrorName",
            "message": "Human readable message",
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
        初始化錯誤
        
        Args:
            message: 人類可讀的錯誤訊息
            details: 可選的詳細資訊，用於 debug
        """
        self.message = message
        self.details = details
        super().__init__(self.message)
    
    @property
    def code(self) -> str:
        """錯誤代碼（對應錯誤類別名稱）"""
        return self.__class__.__name__
    
    @property
    def status_code(self) -> int:
        """HTTP 狀態碼，由子類別實作"""
        raise NotImplementedError("Subclasses must implement status_code")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        轉換為統一的錯誤格式
        
        Returns:
            符合 API 規範的錯誤字典
        """
        return {
            "data": None,
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details
            }
        }
    
    def __str__(self) -> str:
        """字串表示"""
        return f"{self.code}: {self.message}"
