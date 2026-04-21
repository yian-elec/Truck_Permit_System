"""
Application context — App 層（用例服務、DTO、錯誤）。

目錄結構（`app` 根下三個主目錄）：
- **dtos/**：輸入輸出資料傳輸物件
- **errors/**：應用層錯誤型別與領域例外映射
- **services/**：用例服務、共用上下文、對外埠（`services/ports/`）

責任：協調領域與 Infra，實作 UC-APP-01～07；不包含 HTTP 路由（見 api 層）。
"""

from .errors import (
    ApplicationAppError,
    ApplicationConflictAppError,
    ApplicationNotFoundAppError,
    ApplicationSubmissionBlockedAppError,
    ApplicationValidationAppError,
    to_app_error,
)
from .services import ApplicationCommandService

__all__ = [
    "ApplicationCommandService",
    "ApplicationAppError",
    "ApplicationNotFoundAppError",
    "ApplicationValidationAppError",
    "ApplicationConflictAppError",
    "ApplicationSubmissionBlockedAppError",
    "to_app_error",
]
