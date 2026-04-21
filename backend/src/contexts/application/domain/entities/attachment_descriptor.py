"""
已上傳附件之領域描述（非完整 persistence 列）。

責任：在 Domain 表達「某類型附件已存在一筆紀錄」供 **AttachmentBundle** 與送件檢查使用。
`application.attachments` 與 `ops.stored_files` 之 file_id、checksum、mime、size 等欄位由 Infra 映射並在 App 組裝
本物件時選擇性帶入；聚合不讀取 Object Storage，**FileStoragePort／VirusScanPort** 僅在 App／Infra 實作。
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from ..value_objects import AttachmentType


@dataclass
class AttachmentDescriptor:
    """
    聚合內對單一附件的輕量檢視。

    責任：UC-APP-04 寫入 storage 後，App 層建構並交由聚合更新 checklist；OCR 由 Ops context 接手，此處可選帶 ocr_status 字串供規則延伸。
    """

    attachment_id: UUID
    attachment_type: AttachmentType
    status: str
    ocr_status: str = "pending"

    def is_upload_complete(self) -> bool:
        """
        是否視為「已成功上傳且可供送件檢查」之附件。

        責任：預設 status == uploaded 即算完成；virus 失敗等狀態由 App 層寫入 status 字串，領域可擴充白名單。
        """
        return (self.status or "").lower() == "uploaded"
