"""
PermitDocument — 單一文件版本實體（對應 permit.documents）。

責任：持有 document 列之識別、類型、檔案參照、模板代碼、**版本號** 與列層狀態；
維護「重產保留版本」：新版本建立時，舊 ACTIVE 列須標為 SUPERSEDED（由聚合根協調）；
狀態轉移之不變條件由本實體方法執行。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from src.contexts.permit_document.domain.errors import PermitDocumentStateError
from src.contexts.permit_document.domain.value_objects import (
    PermitDocumentRecordStatus,
    PermitDocumentRecordStatusPhase,
)

# 尚未寫入 object storage 前，滿足 persistence「file_id NOT NULL」之領域佔位（Infra 可對應同一常數）。
PENDING_FILE_ID_PLACEHOLDER: UUID = UUID(int=0)


@dataclass
class PermitDocument:
    """
    一筆許可相關文件紀錄（聚合內實體）。

    責任欄位對應 schema：
    document_id, permit_id, application_id, document_type, file_id, template_code,
    version_no, status, created_at, updated_at。
    """

    document_id: UUID
    permit_id: UUID | None
    application_id: UUID
    document_type: str
    file_id: UUID
    template_code: str
    version_no: int
    status: PermitDocumentRecordStatus
    created_at: datetime
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def mark_active_after_storage_write(
        self,
        *,
        file_id: UUID,
        template_code: str,
        now: datetime,
    ) -> None:
        """
        UC-PERMIT-02：寫入 object storage 後，將列標為 ACTIVE 並填入 file／template。

        責任：僅允許自 **PENDING** 轉為 **ACTIVE**；其他狀態拋錯。
        """
        if self.status.value != PermitDocumentRecordStatusPhase.PENDING.value:
            raise PermitDocumentStateError(
                "only PENDING document record may become ACTIVE",
                details={"current_status": self.status.value},
            )
        if file_id == PENDING_FILE_ID_PLACEHOLDER:
            raise PermitDocumentStateError("active file_id must not be the pending placeholder")
        self.file_id = file_id
        self.template_code = template_code.strip()
        if not self.template_code:
            raise PermitDocumentStateError("template_code must not be empty when activating")
        self.status = PermitDocumentRecordStatus.active()
        self._touch(now)

    def mark_failed(self, now: datetime) -> None:
        """
        產製失敗：列標為 FAILED（不回滾核准，由 Permit 聚合另標待補產語意）。

        責任：**PENDING** 可標失敗；**ACTIVE** 若因重產流程失敗是否允許由產品決定—此處允許 **PENDING** 與 **ACTIVE** 轉 **FAILED**
        （ACTIVE 失敗表示現行檔失效，下載應阻擋，直至新版本 ACTIVE）。
        """
        cur = self.status.value
        if cur not in (
            PermitDocumentRecordStatusPhase.PENDING.value,
            PermitDocumentRecordStatusPhase.ACTIVE.value,
        ):
            raise PermitDocumentStateError(
                "cannot mark FAILED from current status",
                details={"current_status": cur},
            )
        self.status = PermitDocumentRecordStatus.failed()
        self._touch(now)

    def mark_superseded(self, now: datetime) -> None:
        """
        新版本產出並 ACTIVE 後，舊版改為 SUPERSEDED。

        責任：僅 **ACTIVE** 可被取代；落實「文件重產需保留版本」之歷史列。
        """
        if self.status.value != PermitDocumentRecordStatusPhase.ACTIVE.value:
            raise PermitDocumentStateError(
                "only ACTIVE document record may be superseded",
                details={"current_status": self.status.value},
            )
        self.status = PermitDocumentRecordStatus.superseded()
        self._touch(now)

    def _touch(self, now: datetime) -> None:
        """更新 updated_at。"""
        self.updated_at = now
