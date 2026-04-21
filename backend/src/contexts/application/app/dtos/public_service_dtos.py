"""
重型貨車通行證「公開服務資訊」DTO（對應 5.4 Public API）。

責任：僅描述對外唯讀回應結構；內容可由 App 服務組裝自範本／設定，不與路由層重複定義。
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class HeavyTruckPermitServiceOverviewDTO(BaseModel):
    """GET .../heavy-truck-permit 之服務總覽。"""

    service_code: str = Field(default="heavy-truck-permit", description="服務代碼")
    display_name: str = Field(default="重型貨車通行證", description="顯示名稱")
    description: str = Field(
        default="線上申請重型貨車通行許可之相關說明與連結匯總。",
        description="簡要說明",
    )
    api_version: str = Field(default="v1", description="對外 API 版本")


class ConsentLatestDTO(BaseModel):
    """GET .../consent/latest 之條款版本摘要（完整條文可由前端另載）。"""

    version: str = Field(..., description="條款版本識別")
    effective_at: str = Field(..., description="生效日（ISO 日期字串）")
    summary: str = Field(..., description="摘要說明")
    must_accept_before_submit: bool = Field(default=True, description="送件前是否必須勾選同意")


class RequiredDocumentItemDTO(BaseModel):
    """必備文件清單單列。"""

    item_code: str = Field(..., description="與 checklist／附件類型對齊之代碼")
    item_name: str = Field(..., description="顯示名稱")
    is_required: bool = Field(default=True, description="是否為送件必填")


class HandlingUnitDTO(BaseModel):
    """受理單位／承辦窗口（公開聯絡資訊）。"""

    unit_code: str = Field(..., description="單位代碼")
    unit_name: str = Field(..., description="單位名稱")
    phone: str | None = Field(None, description="聯絡電話")
    address: str | None = Field(None, description="地址")


class RequiredDocumentsListDTO(BaseModel):
    """必備文件列表包裝（便於 OpenAPI 與客戶端型別一致）。"""

    documents: list[RequiredDocumentItemDTO] = Field(default_factory=list)


class HandlingUnitsListDTO(BaseModel):
    """受理單位列表包裝。"""

    units: list[HandlingUnitDTO] = Field(default_factory=list)
