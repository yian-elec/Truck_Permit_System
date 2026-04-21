"""
Permit_Document — 命令面用例之輸入／輸出 DTO。

責任：承載 UC-PERMIT-01（產生許可）、UC 補充之「請求重產文件」等命令參數與回傳摘要；
不含業務規則，僅資料形狀。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class CreatePermitInputDTO:
    """
    UC-PERMIT-01 輸入：於 **ApplicationApproved** 後建立許可。

    責任：僅傳申請識別與選填備註；核准事實、路線與期間由 **IssuanceContextReader** 載入。
    """

    application_id: UUID
    note: str | None = None


@dataclass(frozen=True)
class CreatePermitOutputDTO:
    """UC-PERMIT-01 輸出：新建許可與首筆產檔工作識別。"""

    permit_id: UUID
    permit_no: str
    application_id: UUID
    status: str
    document_job_id: UUID


@dataclass(frozen=True)
class RequestDocumentRegenerationInputDTO:
    """
    觸發文件重產（對應 API regenerate）。

    責任：以申請識別定位許可；下載權限由服務內 **AuthorizationPort** 檢查。
    """

    application_id: UUID
    actor_user_id: UUID


@dataclass(frozen=True)
class RequestDocumentRegenerationOutputDTO:
    """重產請求已受理後之摘要（例如新工作單 id）。"""

    permit_id: UUID
    new_document_job_id: UUID
    permit_status: str


@dataclass(frozen=True)
class RecordDocumentJobCompletedInputDTO:
    """
    UC-PERMIT-02 後段：工作單完成時寫回（供 worker／內部排程呼叫）。

    責任：僅資料載體；實際寫入 ORM 與領域協調在 Command Service。
    """

    job_id: UUID
    completed_at: datetime


@dataclass(frozen=True)
class RegisterGeneratedDocumentInputDTO:
    """產檔成功後登記 permit.documents 列與檔案 id。"""

    document_id: UUID
    permit_id: UUID
    application_id: UUID
    document_type: str
    file_id: UUID
    template_code: str
    version_no: int
