"""
DocumentRef — 指向一筆已產製文件（含 storage）之參照值物件。

責任：封裝下載與稽核所需之穩定識別（document_id、file_id、類型、版本號），
不可變；**版本號** 用於落實「文件重產需保留版本」之追溯，與 PermitDocument 實體一一對應語意。
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from src.contexts.permit_document.domain.errors import InvalidPermitValueError


@dataclass(frozen=True)
class DocumentRef:
    """
    單一文件版本之參照（值物件）。

    責任：
    - **document_id**：資料列主鍵（permit.documents.document_id）。
    - **file_id**：物件儲存或檔案服務之檔案識別。
    - **document_type**：與 `DocumentTypeCode` 字串一致之類型（此處以 str 避免循環匯入，由工廠保證）。
    - **version_no**：從 1 遞增；重產時新版本號必須大於舊版。
    """

    document_id: UUID
    file_id: UUID
    document_type: str
    version_no: int

    def __post_init__(self) -> None:
        if self.version_no < 1:
            raise InvalidPermitValueError("DocumentRef.version_no must be >= 1")
        if not self.document_type.strip():
            raise InvalidPermitValueError("DocumentRef.document_type must not be empty")
