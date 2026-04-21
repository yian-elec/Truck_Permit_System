"""
Application App 層錯誤匯出。

實作集中於 `application_app_errors.py`（應用層錯誤型別與領域例外映射函式）。
"""

from .application_app_errors import (
    ApplicationAppError,
    ApplicationConflictAppError,
    ApplicationNotFoundAppError,
    ApplicationSubmissionBlockedAppError,
    ApplicationValidationAppError,
    map_domain_exception_to_app,
    rethrow_if_app_error,
    to_app_error,
    wrap_lookup_error,
)

__all__ = [
    "ApplicationAppError",
    "ApplicationNotFoundAppError",
    "ApplicationValidationAppError",
    "ApplicationConflictAppError",
    "ApplicationSubmissionBlockedAppError",
    "map_domain_exception_to_app",
    "wrap_lookup_error",
    "rethrow_if_app_error",
    "to_app_error",
]
