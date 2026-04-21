"""
DocumentBundle — 三類標準文件之組合值物件。

責任：對應規格 Aggregate 敘述中的 DocumentBundle（permit_pdf、route_map_pdf、decision_pdf），
以三個可選的 **DocumentRef** 表達「目前有效下載標的」；由 Permit 聚合從子實體集合中 **計算** 得出，
本身不持有儲存層狀態。
"""

from __future__ import annotations

from dataclasses import dataclass

from src.contexts.permit_document.domain.value_objects.document_ref import DocumentRef


@dataclass(frozen=True)
class DocumentBundle:
    """
    許可相關三份 PDF 之參照組（值物件、不可變）。

    責任：欄位可為 None 表示該類文件尚未成功產製或尚未註冊 ACTIVE 版本；下載 UC 應檢查 None。
    """

    permit_pdf: DocumentRef | None
    route_map_pdf: DocumentRef | None
    decision_pdf: DocumentRef | None
