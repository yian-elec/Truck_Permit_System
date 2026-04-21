"""
Logger - 統一日誌系統
遵循 Logger 等級規範，提供統一的日誌格式和行為
"""

import logging
import sys
from typing import Any, Dict, Optional


class Logger:
    """
    統一日誌系統
    
    Log Level 對應表：
    - DEBUG: 開發/除錯用，顯示詳細內部狀態。不在生產環境開啟。
    - INFO: 一般正常流程事件，對系統行為的摘要紀錄。
    - WARN: 發生異常但系統仍可繼續運行。需追蹤改善。
    - ERROR: 發生錯誤，導致請求或流程失敗。必須回應錯誤給用戶或進行 rollback。
    - CRITICAL: 系統無法運行，需立即介入處理。
    """
    
    def __init__(self, name: str = "BaseProject", level: str = "INFO"):
        """
        初始化 Logger
        
        Args:
            name: Logger 名稱
            level: 日誌等級 (DEBUG, INFO, WARN, ERROR, CRITICAL)
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # 避免重複添加 handler
        if not self.logger.handlers:
            self._setup_handler()
    
    def _setup_handler(self):
        """設定日誌處理器"""
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def debug(self, message: str, context: Optional[str] = None, **kwargs):
        """
        DEBUG 等級日誌
        
        使用情境：開發/除錯用，顯示詳細內部狀態。不在生產環境開啟。
        範例：Query SQL 原始語句、DTO 轉換細節
        """
        log_message = self._format_message(message, context, **kwargs)
        self.logger.debug(log_message)
    
    def info(self, message: str, context: Optional[str] = None, **kwargs):
        """
        INFO 等級日誌
        
        使用情境：一般正常流程事件，對系統行為的摘要紀錄。
        範例：API 被呼叫、DB 成功連線、Repository CRUD 成功
        """
        log_message = self._format_message(message, context, **kwargs)
        self.logger.info(log_message)
    
    def warn(self, message: str, context: Optional[str] = None, **kwargs):
        """
        WARN 等級日誌
        
        使用情境：發生異常但系統仍可繼續運行。需追蹤改善。
        範例：外部 API 回傳非 200，但 fallback 成功；快取失效，改走 DB
        """
        log_message = self._format_message(message, context, **kwargs)
        self.logger.warning(log_message)
    
    def error(self, message: str, context: Optional[str] = None, **kwargs):
        """
        ERROR 等級日誌
        
        使用情境：發生錯誤，導致請求或流程失敗。必須回應錯誤給用戶或進行 rollback。
        範例：JWT 驗證失敗、DB transaction rollback、外部 API timeout
        """
        log_message = self._format_message(message, context, **kwargs)
        self.logger.error(log_message)
    
    def critical(self, message: str, context: Optional[str] = None, **kwargs):
        """
        CRITICAL 等級日誌
        
        使用情境：系統無法運行，需立即介入處理。
        範例：DB 完全無法連線、設定檔遺失、系統崩潰
        """
        log_message = self._format_message(message, context, **kwargs)
        self.logger.critical(log_message)
    
    def _format_message(self, message: str, context: Optional[str] = None, **kwargs) -> str:
        """
        格式化日誌訊息
        
        Args:
            message: 主要訊息
            context: 上下文 (如 API, Infra, DB)
            **kwargs: 額外的參數
            
        Returns:
            格式化後的日誌訊息
        """
        if context:
            message = f"[{context}] {message}"
        
        if kwargs:
            # 將額外參數格式化為 key=value 的形式
            extra_info = " ".join([f"{k}={v}" for k, v in kwargs.items()])
            message = f"{message} {extra_info}"
        
        return message
    
    # API 層專用方法
    def api_info(self, method: str, path: str, user_id: Optional[str] = None, **kwargs):
        """
        API 層 INFO 日誌
        
        範例：INFO [API] POST /users user_id=123
        """
        message = f"{method} {path}"
        if user_id:
            kwargs["user_id"] = user_id
        self.info(message, context="API", **kwargs)
    
    def api_error(self, error_code: str, error_message: str, **kwargs):
        """
        API 層 ERROR 日誌
        
        範例：ERROR [API] InvalidTokenError - Invalid JWT token
        """
        message = f"{error_code} - {error_message}"
        self.error(message, context="API", **kwargs)
    
    # Infra 層專用方法
    def infra_info(self, message: str, **kwargs):
        """
        Infra 層 INFO 日誌
        
        範例：INFO [Infra] Call External API /payments status=200
        """
        self.info(message, context="Infra", **kwargs)
    
    def infra_warn(self, message: str, **kwargs):
        """
        Infra 層 WARN 日誌
        
        範例：WARN [Infra] Cache miss for key=user:123, fallback to DB
        """
        self.warn(message, context="Infra", **kwargs)
    
    def infra_error(self, message: str, **kwargs):
        """
        Infra 層 ERROR 日誌
        
        範例：ERROR [Infra] Call External API /payments timeout
        """
        self.error(message, context="Infra", **kwargs)
    
    # DB 層專用方法
    def db_info(self, message: str, **kwargs):
        """
        DB 層 INFO 日誌
        
        範例：INFO [DB] Connection established host=localhost db=base_project
        """
        self.info(message, context="DB", **kwargs)
    
    def db_error(self, message: str, **kwargs):
        """
        DB 層 ERROR 日誌
        
        範例：ERROR [DB] Transaction rollback table=users id=123 error=DuplicateKey
        """
        self.error(message, context="DB", **kwargs)

    def db_warning(self, message: str, **kwargs):
        """
        DB 層 WARN 日誌（例如 PostGIS 未安裝時仍繼續建立其他 schema）。

        範例：WARN [DB] PostGIS extension could not be enabled
        """
        self.warn(message, context="DB", **kwargs)


# 全域 Logger 實例
logger = Logger()
