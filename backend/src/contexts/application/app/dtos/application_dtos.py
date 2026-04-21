"""
申請案件相關 DTO（建立草稿、更新、明細、列表項、時間軸）。

責任：與 API 契約對齊之輸入輸出結構；校驗由 Pydantic 執行，領域值物件建構在服務層完成。
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .attachment_dtos import AttachmentSummaryDTO
from .vehicle_dtos import VehicleDTO


class CreateDraftApplicationInputDTO(BaseModel):
    """UC-APP-01 輸入：建立草稿所需之申請主體欄位。"""

    model_config = ConfigDict(str_strip_whitespace=True)

    applicant_type: str = Field(..., description="申請人類型代碼")
    reason_type: str = Field(..., description="申請事由類型")
    reason_detail: str | None = Field(None, description="事由說明")
    requested_start_at: datetime = Field(..., description="申請許可期間起（建議 UTC aware）")
    requested_end_at: datetime = Field(..., description="申請許可期間迄")
    delivery_method: str = Field(..., description="送達方式代碼")
    source_channel: str = Field(..., description="來源通路代碼")


class CreateDraftApplicationOutputDTO(BaseModel):
    """UC-APP-01 輸出：新案件識別與編號。"""

    application_id: UUID
    application_no: str
    status: str


class PatchApplicationInputDTO(BaseModel):
    """UC-APP-02 輸入：部分更新主表與關聯欄位（皆為可選）。"""

    model_config = ConfigDict(str_strip_whitespace=True)

    reason_type: str | None = None
    reason_detail: str | None = None
    requested_start_at: datetime | None = None
    requested_end_at: datetime | None = None
    delivery_method: str | None = None


class ApplicantProfileDTO(BaseModel):
    """自然人申請人區塊。"""

    name: str
    id_no: str | None = None
    gender: str | None = None
    email: str | None = None
    mobile: str | None = None
    phone_area: str | None = None
    phone_no: str | None = None
    phone_ext: str | None = None
    address_county: str | None = None
    address_district: str | None = None
    address_detail: str | None = None


class CompanyProfileDTO(BaseModel):
    """公司申請人區塊。"""

    company_name: str | None = None
    tax_id: str | None = None
    principal_name: str | None = None
    contact_name: str | None = None
    contact_mobile: str | None = None
    contact_phone: str | None = None
    address: str | None = None


class PatchApplicationProfilesInputDTO(BaseModel):
    """UC-APP-02 可一併提交之申請人／公司資料。"""

    applicant: ApplicantProfileDTO | None = None
    company: CompanyProfileDTO | None = None


class PatchApplicationRequestDTO(BaseModel):
    """
    PATCH 申請案件之 HTTP 請求體。

    責任：合併主表欄位與申請人／公司區塊，對應 `ApplicationCommandService.update_draft_application`；
    兩區塊皆可選，至少其一非空始有實際更新（由服務與領域判定）。
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    patch: PatchApplicationInputDTO | None = None
    profiles: PatchApplicationProfilesInputDTO | None = None


class DeleteAckDTO(BaseModel):
    """刪除資源成功之最小回應。"""

    deleted: bool = True


class ApplicationSummaryListDTO(BaseModel):
    """申請案件列表（GET /applicant/applications）。"""

    applications: list[ApplicationSummaryDTO] = Field(default_factory=list)


class VehicleListDTO(BaseModel):
    """車輛列表包裝。"""

    vehicles: list[VehicleDTO] = Field(default_factory=list)


class AttachmentListDTO(BaseModel):
    """附件列表包裝。"""

    attachments: list[AttachmentSummaryDTO] = Field(default_factory=list)


class ChecklistItemDTO(BaseModel):
    """檢核清單列。"""

    checklist_id: UUID
    item_code: str
    item_name: str
    is_required: bool
    is_satisfied: bool
    source: str
    note: str | None = None


class StatusHistoryEntryDTO(BaseModel):
    """狀態歷程一筆。"""

    history_id: UUID
    from_status: str | None
    to_status: str
    changed_by: UUID | None
    reason: str | None
    created_at: datetime


class ApplicationSummaryDTO(BaseModel):
    """列表用精簡案件資訊。"""

    application_id: UUID
    application_no: str
    status: str
    applicant_type: str
    updated_at: datetime


class ApplicationDetailDTO(BaseModel):
    """GET 單筆案件完整明細（含子集合）。"""

    application_id: UUID
    application_no: str
    status: str
    applicant_type: str
    reason_type: str
    reason_detail: str | None
    requested_start_at: datetime
    requested_end_at: datetime
    delivery_method: str
    source_channel: str
    applicant_user_id: UUID | None
    consent_accepted_at: datetime | None
    submitted_at: datetime | None
    version: int
    created_at: datetime
    updated_at: datetime
    applicant: ApplicantProfileDTO | None
    company: CompanyProfileDTO | None
    vehicles: list[VehicleDTO]
    checklist: list[ChecklistItemDTO]
    attachments: list[AttachmentSummaryDTO]
    status_history: list[StatusHistoryEntryDTO]


class ApplicationEditModelDTO(BaseModel):
    """
    與 `ApplicationDetailDTO` 對齊之編輯用模型（供前端表單綁定）。

    責任：規格 GET .../edit-model 可與 detail 共用結構；日後若需差異可獨立擴充欄位。
    """

    detail: ApplicationDetailDTO


class SupplementRequestItemDTO(BaseModel):
    """補件要求項目（讀模型尚未接審查 context 時之佔位）。"""

    request_id: UUID
    title: str
    description: str | None = None
    created_at: datetime


class SupplementResponseInputDTO(BaseModel):
    """UC-APP-07 輸入：補件回覆（可併同 PATCH 主檔）。"""

    model_config = ConfigDict(str_strip_whitespace=True)

    supplement_request_id: UUID | None = Field(
        None,
        description="若審查 context 已提供補件單 ID，可一併傳入供幕等",
    )
    note: str | None = Field(None, description="申請人備註")
    patch: PatchApplicationInputDTO | None = None
    profiles: PatchApplicationProfilesInputDTO | None = None


class SupplementRequestListDTO(BaseModel):
    """補件要求列表包裝。"""

    items: list[SupplementRequestItemDTO] = Field(default_factory=list)


class TimelineListDTO(BaseModel):
    """時間軸／狀態歷程列表包裝。"""

    entries: list[StatusHistoryEntryDTO] = Field(default_factory=list)
