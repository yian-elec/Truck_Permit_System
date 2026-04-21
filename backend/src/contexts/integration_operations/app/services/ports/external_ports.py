"""
外部系統埠（Application 邊界）。

責任：定義用例與「附件儲存、OCR、通知發送、匯入落地」等外部能力的介面；
實作由 Infra 或其他 context 注入，Application 僅依賴 Protocol 不直接呼叫 SDK／HTTP。
"""

from __future__ import annotations

from typing import Any, Protocol
from uuid import UUID

from src.contexts.integration_operations.app.dtos import OcrExtractedFieldDTO


class AttachmentBlobPort(Protocol):
    """從儲存體讀取附件位元組（他界 Attachment／Storage）。"""

    def fetch_attachment_bytes(self, attachment_id: UUID) -> bytes:
        """若讀取失敗應丟出例外，由用例轉為 OpsExternalDependencyError。"""
        ...


class OcrExtractorPort(Protocol):
    """呼叫 OCR 供應商並回傳欄位級結果。"""

    def extract_fields(self, *, image_bytes: bytes, provider_code: str) -> list[OcrExtractedFieldDTO]:
        ...


class AttachmentOcrStatusPort(Protocol):
    """回寫附件 OCR 狀態（他界；可選）。"""

    def update_ocr_status(
        self,
        *,
        attachment_id: UUID,
        status: str,
        error_message: str | None = None,
    ) -> None:
        ...


class NotificationDispatchPort(Protocol):
    """套用模板並透過實際通道送出通知。"""

    def dispatch(
        self,
        *,
        channel: str,
        recipient: str,
        template_code: str,
        payload: dict[str, Any],
    ) -> None:
        """成功不回傳值；失敗丟例外。"""
        ...


class ImportIngestionPort(Protocol):
    """
    匯入落地：抓資料、標準化、寫 routing／holiday 等。

    回傳人類可讀摘要供 import_jobs.result_summary 使用。
    """

    def ingest(
        self,
        *,
        import_job_id: UUID,
        job_type: str,
        source_name: str,
        source_ref: str | None,
    ) -> str:
        ...
