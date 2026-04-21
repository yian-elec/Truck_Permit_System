"""
附件列表唯讀視圖（Domain 讀模型）。

責任：供 ApplicationReadModelQuery 回傳，不含行為；App 層可映射為 DTO。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class AttachmentSummaryView:
    """對應 application.attachments 一列之查詢結果摘要。"""

    attachment_id: UUID
    attachment_type: str
    file_id: UUID
    original_filename: str
    mime_type: str
    size_bytes: int
    status: str
    ocr_status: str
    uploaded_by: UUID | None
    uploaded_at: datetime
