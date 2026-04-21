"""
DocumentTypeCode — 文件類型代碼值物件。

責任：對齊產製／下載 UC 所需之 `document_type varchar(50)` 封閉集合，
並對應規格中的 DocumentBundle（permit_pdf、route_map_pdf、decision_pdf）三類。
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from src.contexts.permit_document.domain.errors import InvalidPermitValueError


class DocumentTypeCodePhase(StrEnum):
    """
    標準文件類型（持久化字串值）。

    責任：與模板／產檔工作類型對齊，供 DocumentBundle 與查詢「每類最新 ACTIVE 版本」使用。
    """

    PERMIT_PDF = "permit_pdf"
    PERMIT_CERTIFICATE_PDF = "permit_certificate_pdf"
    ROUTE_MAP_PDF = "route_map_pdf"
    DECISION_PDF = "decision_pdf"


@dataclass(frozen=True)
class DocumentTypeCode:
    """封裝並驗證 document_type 字串。"""

    value: str

    def __post_init__(self) -> None:
        allowed = {p.value for p in DocumentTypeCodePhase}
        if self.value not in allowed:
            raise InvalidPermitValueError(
                f"Invalid document type: {self.value!r}; expected one of {sorted(allowed)}"
            )

    @classmethod
    def permit_pdf(cls) -> DocumentTypeCode:
        return cls(DocumentTypeCodePhase.PERMIT_PDF.value)

    @classmethod
    def route_map_pdf(cls) -> DocumentTypeCode:
        return cls(DocumentTypeCodePhase.ROUTE_MAP_PDF.value)

    @classmethod
    def decision_pdf(cls) -> DocumentTypeCode:
        return cls(DocumentTypeCodePhase.DECISION_PDF.value)
