"""
附件與檢核清單組合（Aggregate 內部概念）。

責任：對應規格中的 AttachmentBundle——匯集「必備項目／已上傳項目／檢核狀態」；
封裝必備項目是否齊全之判定，以及上傳後與 checklist 之對齊邏輯。非獨立聚合根，僅能由 Application 操作。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from .attachment_descriptor import AttachmentDescriptor
from .checklist_item import ChecklistItem


@dataclass
class AttachmentBundle:
    """
    附件與檢核清單的集合狀態。

    責任：
    - 追蹤已登記之附件描述（uploaded items）
    - 維護 checklist 各列滿足與否（required items + checklist state）
    - 提供送件前「必備附件是否齊全」之查詢
    """

    checklist_items: list[ChecklistItem] = field(default_factory=list)
    uploaded: list[AttachmentDescriptor] = field(default_factory=list)

    @classmethod
    def empty(cls) -> AttachmentBundle:
        """建立無檢核項、無附件之空組合（新建草稿後由 App 初始化 checklist）。"""
        return cls()

    def replace_checklist(self, items: list[ChecklistItem]) -> None:
        """
        以新清單取代檢核項（例如服務公版變更）；由 Application 在允許的編輯狀態下呼叫。

        責任：不保留舊清單之 UUID 對應，若需保留歷史應另寫入 status_histories 或稽核表（App/Infra）。
        """
        self.checklist_items = list(items)

    def register_uploaded_attachment(self, descriptor: AttachmentDescriptor) -> None:
        """
        登記一筆附件紀錄，並在「上傳流程已完成」時勾選同代碼之檢核項。

        責任：item_code 與 AttachmentType.code 一致者視為同一文件要件；若 status 非完成上傳
        （例如病毒掃描失敗），仍保留於 uploaded 清單但不視為已滿足必備文件。
        """
        self.uploaded.append(descriptor)
        if not descriptor.is_upload_complete():
            return
        code = descriptor.attachment_type.code
        for item in self.checklist_items:
            if item.item_code == code:
                item.mark_satisfied()

    def remove_attachment_reference(self, attachment_id: UUID) -> None:
        """
        從聚合視圖移除附件（例如使用者刪除附件後）。

        責任：移除後若無其他同類型之上傳完成附件，應將對應檢核項改回未滿足。
        """
        self.uploaded = [a for a in self.uploaded if a.attachment_id != attachment_id]
        self._recompute_satisfaction_from_uploads()

    def migrate_legacy_id_card_checklist_to_vehicle_license_copy(self) -> None:
        """
        舊版草稿檢核範本以 id_card 為必填代碼，與現行申請端上傳之 vehicle_license_copy 不一致，
        導致已上傳行照仍無法對應檢核列。載入聚合時將該列代碼對齊現行規格（不影響已為新代碼之案件）。
        """
        for item in self.checklist_items:
            if item.item_code == "id_card":
                item.item_code = "vehicle_license_copy"
                item.item_name = "行車執照影本（拖車使用證）"

    def reconcile_checklist_with_current_uploads(self) -> None:
        """
        依目前已登記之 uploaded 描述子重算檢核項滿足狀態。

        責任：於 Infra 寫入或刪除 `application.attachments` 後重新載入聚合時，DB 內 checklist 列
        之 is_satisfied 可能與實際附件不一致，應呼叫本方法同步（不重複 append 描述子）。
        """
        self._recompute_satisfaction_from_uploads()

    def align_checklist_after_load_from_db(self) -> None:
        """自 DB hydrate 後呼叫：對齊舊版代碼並依實際附件重算滿足狀態。"""
        self.migrate_legacy_id_card_checklist_to_vehicle_license_copy()
        self.reconcile_checklist_with_current_uploads()

    def _recompute_satisfaction_from_uploads(self) -> None:
        """依目前 uploaded 清單重算各 checklist 列之滿足狀態。"""
        satisfied_codes: set[str] = set()
        for att in self.uploaded:
            if att.is_upload_complete():
                satisfied_codes.add(att.attachment_type.code)
        for item in self.checklist_items:
            if item.item_code in satisfied_codes:
                if not item.is_satisfied:
                    item.mark_satisfied()
            else:
                item.mark_unsatisfied()

    def missing_required_item_codes(self) -> list[str]:
        """
        回傳尚未滿足之必備檢核項代碼列表。

        責任：供 UC-APP-05／UC-APP-06 組裝缺漏說明。
        """
        return [
            item.item_code
            for item in self.checklist_items
            if item.is_required and not item.is_satisfied
        ]

    def all_required_satisfied(self) -> bool:
        """必備檢核項是否均已滿足。"""
        return not self.missing_required_item_codes()
