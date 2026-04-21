"""
AppError - Application 層錯誤
用於 Use Case 流程錯誤 (授權、資源衝突)
狀態碼：403 Forbidden, 409 Conflict
"""

from .app_error import AppError
from .forbidden_error import ForbiddenError
from .conflict_error import ConflictError

__all__ = ["AppError", "ForbiddenError", "ConflictError"]
