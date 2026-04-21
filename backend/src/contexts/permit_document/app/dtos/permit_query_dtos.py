"""
Permit_Document — 查詢面用例之輸入／輸出 DTO。

責任：UC-PERMIT-03 之讀模型與下載 URL 回傳形狀；不含授權邏輯本體。
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List
from uuid import UUID


@dataclass(frozen=True)
class PermitCertificateSummaryDTO:
    """最新一筆使用證（§8 certificate 區塊；status 為對外語意）。"""

    document_id: UUID
    version_no: int
    status: str
    generated_at: datetime | None
    downloadable: bool


@dataclass(frozen=True)
class PermitSummaryDTO:
    """單筆許可證摘要（列表或詳情共用欄位子集）。"""

    permit_id: UUID
    permit_no: str
    application_id: UUID
    status: str
    approved_start_at: datetime
    approved_end_at: datetime
    route_summary_text: str
    issued_at: datetime | None
    certificate: PermitCertificateSummaryDTO | None = None


@dataclass(frozen=True)
class PermitDocumentRowDTO:
    """permit.documents 列之查詢視圖。"""

    document_id: UUID
    permit_id: UUID | None
    application_id: UUID
    document_type: str
    file_id: UUID
    template_code: str
    version_no: int
    status: str


@dataclass(frozen=True)
class GetPermitByApplicationQueryDTO:
    """依申請案查許可（申請人端）。"""

    application_id: UUID
    actor_user_id: UUID


@dataclass(frozen=True)
class GetPermitByIdQueryDTO:
    """依許可識別查詳情。"""

    permit_id: UUID
    actor_user_id: UUID


@dataclass(frozen=True)
class ListPermitDocumentsQueryDTO:
    """列出許可底下文件版本。"""

    permit_id: UUID
    actor_user_id: UUID


@dataclass(frozen=True)
class ApplicantPermitDocumentDownloadBodyDTO:
    """
    申請人端 POST body：可指定欲下載之文件列識別。

    責任：對應 8.4 `.../applicant/applications/{applicationId}/permit/download-url`；
    路徑帶 **application_id**，JWT 提供 **actor_user_id**，與本 body 組成完整用例輸入。
    **document_id** 省略時，由後端選定預設可下載文件（優先通行證主檔 permit_pdf）。
    """

    document_id: UUID | None = None


@dataclass(frozen=True)
class RequestPermitDocumentDownloadByApplicationDTO:
    """
    依申請案產生指定文件之下載 URL（UC-PERMIT-03）。

    責任：先解析該申請之許可識別，再委派 **CreateDocumentDownloadUrlInputDTO** 流程。
    **document_id** 為 None 時，選定該許可下之預設可下載文件。
    """

    application_id: UUID
    actor_user_id: UUID
    document_id: UUID | None = None


@dataclass(frozen=True)
class CreateDocumentDownloadUrlInputDTO:
    """請求單一文件之短期下載 URL。"""

    permit_id: UUID
    document_id: UUID
    actor_user_id: UUID


@dataclass(frozen=True)
class CreateDocumentDownloadUrlOutputDTO:
    """下載 URL 與建議過期時間（實際簽章由 ObjectStoragePort 決定）。"""

    download_url: str
    expires_at: datetime
    file_name: str


@dataclass(frozen=True)
class ListPermitDocumentsOutputDTO:
    """文件列表包裝。"""

    permit_id: UUID
    documents: List[PermitDocumentRowDTO]
