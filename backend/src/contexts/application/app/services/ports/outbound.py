"""
Application App 層對外埠（檔案儲存、事件發布、補件協作）。

責任：隸屬於 `services` 套件，避免在 `app` 根目錄另立與 dtos／errors 同級之目錄；
以 Protocol／具象類別描述 Infra 須實作之能力；預設提供空實作供開發與本地開發。
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Protocol
from uuid import UUID

from src.contexts.application.app.dtos import SupplementRequestItemDTO


class FileStoragePort(Protocol):
    """物件儲存：上傳／下載 presigned URL。"""

    def create_presigned_upload_url(
        self,
        *,
        application_id: UUID,
        file_id: UUID,
        object_key: str,
        mime_type: str,
    ) -> str:
        """回傳前端 PUT／POST 上傳用之 URL。"""
        ...

    def create_presigned_download_url(self, *, object_key: str) -> str:
        """回傳限期內有效之下載 URL。"""
        ...


class ApplicationEventPublisher(Protocol):
    """領域事件／整合事件發布（如 AttachmentUploaded、ApplicationSubmitted）。"""

    def publish(self, event_name: str, payload: dict[str, Any]) -> None:
        ...


class SupplementWorkflowPort(Protocol):
    """
    與審查／補件 context 之協作埠。

    責任：UC-APP-07 在標示 resubmitted 前，可由此驗證「最新補件要求是否已滿足」；
    並提供申請人端可讀之補件通知列表（對應 review.supplement_requests）。
    """

    def assert_may_finalize_supplement_response(self, application_id: UUID) -> None:
        """若不滿足補件條件，應拋出例外。"""
        ...

    def record_applicant_supplement_reply(
        self,
        application_id: UUID,
        supplement_request_id: UUID,
        *,
        applicant_note: str | None,
        now: datetime,
    ) -> None:
        """
        將指定之 OPEN 補件單標記為 fulfilled 並寫入申請人備註。

        無法更新（ID 錯誤或已非 open）時應拋 ApplicationValidationAppError。
        """

    def count_open_supplement_requests(self, application_id: UUID) -> int:
        """本案仍為 open 之補件筆數（用於判斷是否須轉 resubmitted）。"""

    def list_supplement_notifications(
        self,
        application_id: UUID,
    ) -> list[SupplementRequestItemDTO]:
        """依案件列出補件主檔（供 GET .../supplement-requests）。"""
        ...


class NoopFileStoragePort:
    """預設假實作：固定回傳占位 URL。"""

    def create_presigned_upload_url(
        self,
        *,
        application_id: UUID,
        file_id: UUID,
        object_key: str,
        mime_type: str,
    ) -> str:
        _ = (application_id, file_id, object_key, mime_type)
        return "https://storage.example.invalid/presigned-upload"

    def create_presigned_download_url(self, *, object_key: str) -> str:
        return f"https://storage.example.invalid/download?k={object_key}"


class NoopApplicationEventPublisher:
    """預設不發布任何事件。"""

    def publish(self, event_name: str, payload: dict[str, Any]) -> None:
        _ = (event_name, payload)


class NoopSupplementWorkflowPort:
    """未接審查服務：不寫入 review，回覆一律視為通過；未完成筆數視為 0 以維持既存單元測試行為。"""

    def assert_may_finalize_supplement_response(self, application_id: UUID) -> None:
        _ = application_id

    def record_applicant_supplement_reply(
        self,
        application_id: UUID,
        supplement_request_id: UUID,
        *,
        applicant_note: str | None,
        now: datetime,
    ) -> None:
        _ = (application_id, supplement_request_id, applicant_note, now)

    def count_open_supplement_requests(self, application_id: UUID) -> int:
        _ = application_id
        return 0

    def list_supplement_notifications(
        self,
        application_id: UUID,
    ) -> list[SupplementRequestItemDTO]:
        _ = application_id
        return []
