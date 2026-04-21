"""
讀取模型埠（Query side）。

責任：支援 GET /ops/* 列表與詳情，回傳 App DTO；由 Infra 以 SQLAlchemy 實作，
避免在 Application Service 內直接依賴 ORM，維持用例層清晰。
"""

from __future__ import annotations

from typing import Optional, Protocol
from uuid import UUID

from src.contexts.integration_operations.app.dtos import (
    AuditLogListItemDTO,
    ImportJobDetailDTO,
    ImportJobListItemDTO,
    NotificationJobListItemDTO,
    OcrJobDetailDTO,
    OcrJobListItemDTO,
)


class OpsReadPort(Protocol):
    """Integration_Operations 唯讀查詢埠。"""

    def list_ocr_jobs(self, *, limit: int, offset: int) -> list[OcrJobListItemDTO]:
        """分頁列出 OCR 作業。"""
        ...

    def get_ocr_job_detail(self, ocr_job_id: UUID) -> Optional[OcrJobDetailDTO]:
        """依 ocr_job_id 取得作業與其 ocr_results（依 attachment_id 關聯）。"""
        ...

    def list_notification_jobs(self, *, limit: int, offset: int) -> list[NotificationJobListItemDTO]:
        ...

    def list_import_jobs(self, *, limit: int, offset: int) -> list[ImportJobListItemDTO]:
        ...

    def get_import_job_detail(self, import_job_id: UUID) -> Optional[ImportJobDetailDTO]:
        ...

    def list_audit_logs(self, *, limit: int, offset: int) -> list[AuditLogListItemDTO]:
        ...
