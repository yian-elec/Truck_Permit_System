"""
重型貨車通行證公開資訊用例（對應 5.4 Public API）。

責任：組裝唯讀 DTO；必備文件與 App 層 checklist 範本對齊，避免在 API 路由重複定義結構。
"""

from __future__ import annotations

from ..dtos.public_service_dtos import (
    ConsentLatestDTO,
    HandlingUnitDTO,
    HandlingUnitsListDTO,
    HeavyTruckPermitServiceOverviewDTO,
    RequiredDocumentItemDTO,
    RequiredDocumentsListDTO,
)

from ._checklist_template import default_checklist_items_for_heavy_truck_permit


class PublicHeavyTruckPermitService:
    """公開服務資訊之讀取服務（無需登入）。"""

    @staticmethod
    def get_service_overview() -> HeavyTruckPermitServiceOverviewDTO:
        """服務總覽（名稱、代碼、說明）。"""
        return HeavyTruckPermitServiceOverviewDTO()

    @staticmethod
    def get_consent_latest() -> ConsentLatestDTO:
        """目前生效之同意條款版本摘要（完整 HTML／PDF 由前端另址載入）。"""
        return ConsentLatestDTO(
            version="2026-04-01",
            effective_at="2026-04-01",
            summary="使用本服務即表示您已閱讀並理解個人資料蒐集、利用與送件責任等事項；送件前須於表單勾選同意。",
            must_accept_before_submit=True,
        )

    @staticmethod
    def list_required_documents() -> RequiredDocumentsListDTO:
        """必備文件清單（與草稿初始化 checklist 之代碼一致）。"""
        items = default_checklist_items_for_heavy_truck_permit()
        return RequiredDocumentsListDTO(
            documents=[
                RequiredDocumentItemDTO(
                    item_code=i.item_code,
                    item_name=i.item_name,
                    is_required=i.is_required,
                )
                for i in items
            ]
        )

    @staticmethod
    def list_handling_units() -> HandlingUnitsListDTO:
        """受理／承辦單位公開聯絡資訊（示範資料，可改接設定檔或主檔）。"""
        return HandlingUnitsListDTO(
            units=[
                HandlingUnitDTO(
                    unit_code="HTP-HQ-01",
                    unit_name="監理機關示範受理櫃台",
                    phone="02-0000-0000",
                    address="示範縣市示範路一段1號",
                )
            ]
        )
