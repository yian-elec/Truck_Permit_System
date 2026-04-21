"""
Review_Decision App 層錯誤匯出。

責任：集中於 `review_app_errors.py`（與 Application 之 `application_app_errors.py` 命名對齊）；
服務層僅透過本套件匯出之型別與 `raise_*` 輔助函式拋錯。
"""

from .review_app_errors import (
    ReviewAppError,
    ReviewConflictAppError,
    ReviewNotFoundAppError,
    ReviewValidationAppError,
    map_review_domain_exception_to_app,
    raise_application_domain_as_app,
    raise_review_domain_as_app,
)

__all__ = [
    "ReviewAppError",
    "ReviewNotFoundAppError",
    "ReviewValidationAppError",
    "ReviewConflictAppError",
    "map_review_domain_exception_to_app",
    "raise_review_domain_as_app",
    "raise_application_domain_as_app",
]
