"""
檢核項目實體（Checklist item）。

責任：對應 application.checklists 一列在領域中的可變狀態（是否已滿足、備註）；
「必備附件未齊不得送件」由聚合參考 `is_required` 與 `is_satisfied` 判定。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class ChecklistItem:
    """
    單一檢核項（文件或條件）。

    責任：由 Application 聚合透過 AttachmentBundle 維護；item_code 常與 AttachmentType.code 對齊以便上傳後勾選。
    """

    checklist_id: UUID
    item_code: str
    item_name: str
    is_required: bool
    is_satisfied: bool
    source: str
    note: str | None = None

    @classmethod
    def seed(
        cls,
        *,
        item_code: str,
        item_name: str,
        is_required: bool,
        source: str,
        checklist_id: UUID | None = None,
        note: str | None = None,
    ) -> ChecklistItem:
        """建立新檢核項（初始化 checklist 時使用）；預設尚未滿足。"""
        return cls(
            checklist_id=checklist_id or uuid4(),
            item_code=item_code,
            item_name=item_name,
            is_required=is_required,
            is_satisfied=False,
            source=source,
            note=note,
        )

    def mark_satisfied(self, *, note: str | None = None) -> None:
        """標記為已滿足；可附註解說明來源（例如人工審核）。"""
        self.is_satisfied = True
        if note is not None:
            self.note = note

    def mark_unsatisfied(self) -> None:
        """撤銷滿足狀態（例如補件流程中重設特定項目）。"""
        self.is_satisfied = False
