"""
讀取用例服務（對應 9.4 GET /ops/*）。

責任：委派 OpsReadPort 取得資料並轉為對外 DTO；對不存在資源丟 OpsResourceNotFoundError。
"""

from __future__ import annotations

from uuid import UUID

from src.contexts.integration_operations.app.dtos import (
    AuditLogListItemDTO,
    ImportJobDetailDTO,
    ImportJobListItemDTO,
    NotificationJobListItemDTO,
    OcrJobDetailDTO,
    OcrJobListItemDTO,
)
from src.contexts.integration_operations.app.errors import OpsResourceNotFoundError

from .ports import OpsReadPort


class OpsQueryApplicationService:
    """Ops 唯讀 API 之應用服務。"""

    def __init__(self, read_port: OpsReadPort) -> None:
        self._read = read_port

    def list_ocr_jobs(self, *, limit: int = 50, offset: int = 0) -> list[OcrJobListItemDTO]:
        """GET /ops/ocr-jobs"""
        lim = max(1, min(limit, 200))
        off = max(0, offset)
        return self._read.list_ocr_jobs(limit=lim, offset=off)

    def get_ocr_job(self, ocr_job_id: UUID) -> OcrJobDetailDTO:
        """GET /ops/ocr-jobs/{ocrJobId}"""
        detail = self._read.get_ocr_job_detail(ocr_job_id)
        if detail is None:
            raise OpsResourceNotFoundError(f"OCR job not found: {ocr_job_id}")
        return detail

    def list_notification_jobs(self, *, limit: int = 50, offset: int = 0) -> list[NotificationJobListItemDTO]:
        """GET /ops/notification-jobs"""
        lim = max(1, min(limit, 200))
        off = max(0, offset)
        return self._read.list_notification_jobs(limit=lim, offset=off)

    def list_import_jobs(self, *, limit: int = 50, offset: int = 0) -> list[ImportJobListItemDTO]:
        """GET /ops/import-jobs"""
        lim = max(1, min(limit, 200))
        off = max(0, offset)
        return self._read.list_import_jobs(limit=lim, offset=off)

    def get_import_job(self, import_job_id: UUID) -> ImportJobDetailDTO:
        """GET /ops/import-jobs/{importJobId}"""
        detail = self._read.get_import_job_detail(import_job_id)
        if detail is None:
            raise OpsResourceNotFoundError(f"import job not found: {import_job_id}")
        return detail

    def list_audit_logs(self, *, limit: int = 50, offset: int = 0) -> list[AuditLogListItemDTO]:
        """GET /ops/audit-logs"""
        lim = max(1, min(limit, 200))
        off = max(0, offset)
        return self._read.list_audit_logs(limit=lim, offset=off)
