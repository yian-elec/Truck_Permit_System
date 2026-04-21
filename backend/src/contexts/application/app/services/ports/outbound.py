"""
Application App 層對外埠（檔案儲存、事件發布、補件協作）。

責任：隸屬於 `services` 套件，避免在 `app` 根目錄另立與 dtos／errors 同級之目錄；
以 Protocol／具象類別描述 Infra 須實作之能力；預設提供空實作供開發與單元測試。
"""

from __future__ import annotations

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
    """未接審查服務時一律允許完成補件回覆（僅限開發）。"""

    def assert_may_finalize_supplement_response(self, application_id: UUID) -> None:
        _ = application_id

    def list_supplement_notifications(
        self,
        application_id: UUID,
    ) -> list[SupplementRequestItemDTO]:
        _ = application_id
        return []
