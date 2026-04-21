"""
Permit_Document 應用層出站埠（Protocol）。

責任：隔離「授權」「物件儲存簽章 URL」等與本 context 無直接關係之基建；
由 API／組合根注入實作，服務僅依賴抽象。
"""

from __future__ import annotations

from datetime import datetime
from typing import Protocol
from uuid import UUID


class PermitAuthorizationPort(Protocol):
    """
    下載與查詢前之身分／權限檢查。

    責任：UC-PERMIT-03 要求「驗證使用者是否有權」；具體規則（申請人／承辦／角色）由實作決定。
    """

    def assert_may_access_application(self, *, actor_user_id: UUID, application_id: UUID) -> None:
        """無權時應拋出 PermitForbiddenAppError。"""
        ...

    def assert_may_access_permit(self, *, actor_user_id: UUID, permit_id: UUID) -> None:
        """無權時應拋出 PermitForbiddenAppError。"""
        ...


class PermitObjectStoragePort(Protocol):
    """
    物件儲存：依 file_id 產生短期下載 URL。

    責任：UC-PERMIT-02 寫檔、UC-PERMIT-03 簽章 URL；本埠僅暴露讀取下載鏈結能力。
    """

    def create_temporary_download_url(
        self,
        *,
        file_id: UUID,
        suggested_ttl_seconds: int = 600,
    ) -> tuple[str, datetime]:
        """
        Returns:
            (url, expires_at)
        """
        ...
