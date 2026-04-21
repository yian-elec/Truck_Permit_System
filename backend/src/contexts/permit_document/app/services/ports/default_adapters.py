"""
`outbound` Protocol 之開發／測試用預設實作（Adapter）。

責任：與 **outbound.py** 中抽象並列於 `ports` 套件，方便辨識「介面定義」與「可替換實作」；
供本地組合 **PermitServiceContext**。**不可**作為正式環境之授權與簽章邏輯。
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from src.contexts.permit_document.app.services.ports.outbound import (
    PermitAuthorizationPort,
    PermitObjectStoragePort,
)
from src.contexts.permit_document.infra.permit_local_storage import build_temporary_download_url


class PermissivePermitAuthorizationPort:
    """
    一律允許通過（僅開發／單元測試）。

    責任：不執行任何檢查；正式 API 必須替換。
    """

    def assert_may_access_application(self, *, actor_user_id: UUID, application_id: UUID) -> None:
        _ = (actor_user_id, application_id)

    def assert_may_access_permit(self, *, actor_user_id: UUID, permit_id: UUID) -> None:
        _ = (actor_user_id, permit_id)


class PlaceholderObjectStoragePort:
    """
    回傳假 URL 與過期時間（無實際簽章）。

    責任：滿足 UC-PERMIT-03 之介面形狀；測試可手動注入。
    """

    def create_temporary_download_url(
        self,
        *,
        file_id: UUID,
        suggested_ttl_seconds: int = 600,
    ) -> tuple[str, datetime]:
        from datetime import timedelta, timezone

        expires = datetime.now(timezone.utc) + timedelta(seconds=suggested_ttl_seconds)
        return (f"https://storage.placeholder.local/download/{file_id}", expires)


class LocalSignedDownloadStoragePort:
    """
    本機磁碟檔案 + HMAC 簽名之短期 GET URL（與 **permit_local_storage**、路由搭配）。

    責任：開發環境可實際下載；正式環境應換成 S3／GCS presigned URL 等實作。
    """

    def create_temporary_download_url(
        self,
        *,
        file_id: UUID,
        suggested_ttl_seconds: int = 600,
    ) -> tuple[str, datetime]:
        return build_temporary_download_url(file_id=file_id, ttl_seconds=suggested_ttl_seconds)


def build_default_permit_service_context_dependencies() -> tuple[
    PermitAuthorizationPort,
    PermitObjectStoragePort,
]:
    """回傳預設 port 實例（tuple 利於解構注入）。"""
    return (PermissivePermitAuthorizationPort(), LocalSignedDownloadStoragePort())
