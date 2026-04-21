"""
新開草稿時之檢核清單範本（App 層）。

責任：對應公開服務「必備文件」之最小集合；日後可改為讀設定檔或查詢政策服務。
"""

from __future__ import annotations

from src.contexts.application.domain.entities import ChecklistItem


def default_checklist_items_for_heavy_truck_permit() -> list[ChecklistItem]:
    """
    重型貨車通行證草稿初始化用之檢核項。

    責任：item_code 須與申請端上傳之 attachment_type 一致，送件檢查方能對應勾選。
    必傳僅「行車執照影本」；其餘與申請端附件欄位對齊、標為選填。
    """
    return [
        ChecklistItem.seed(
            item_code="vehicle_license_copy",
            item_name="行車執照影本（拖車使用證）",
            is_required=True,
            source="template",
        ),
        ChecklistItem.seed(
            item_code="engineering_contract_or_order",
            item_name="工程合約書或訂購單",
            is_required=False,
            source="template",
        ),
        ChecklistItem.seed(
            item_code="waste_site_consent",
            item_name="棄土場同意書暨棄土流向證明",
            is_required=False,
            source="template",
        ),
        ChecklistItem.seed(
            item_code="other_power_of_attorney",
            item_name="其他(委託書)",
            is_required=False,
            source="template",
        ),
    ]
