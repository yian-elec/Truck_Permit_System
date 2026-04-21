"""
Integration_Operations — Application 層錯誤。

責任：將用例層可預期的失敗（找不到資源、外部依賴失敗等）與 Domain 錯誤區隔，
供 API 層對應 HTTP 狀態碼與統一錯誤包裝。
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from shared.errors.app_error.app_error import AppError
from shared.errors.app_error.conflict_error import ConflictError
from shared.errors.system_error.internal_error import InternalError


class OpsResourceNotFoundError(AppError):
    """
    作業資源不存在（例如依 ocr_job_id 查無聚合）。

    建議對應 HTTP 404。
    """

    def __init__(self, message: str = "Resource not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)

    @property
    def status_code(self) -> int:
        return 404


class OpsConflictError(ConflictError):
    """
    作業狀態衝突（例如重複排程同一附件的 OCR，由用例規則決定）。

    建議對應 HTTP 409。
    """

    def __init__(self, message: str = "Operation conflict", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)


class OpsExternalDependencyError(InternalError):
    """
    外部依賴失敗（儲存體、OCR provider、通知通道、匯入來源等）。

    建議對應 HTTP 502／500，依 API 政策選擇；此處預設繼承 Internal 語意。
    """

    def __init__(self, message: str = "External dependency failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
