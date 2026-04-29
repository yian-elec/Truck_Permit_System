"""
審查唯讀／聚合讀模型 DTO（UC-REV-02、決策／評論／補件歷史、稽核軌跡）。

責任：對應 GET 類用例與審核頁組裝；不含寫入命令之輸入形狀。
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.contexts.application.app.dtos import ApplicationDetailDTO


class DecisionSummaryDTO(BaseModel):
    """單筆決策紀錄（讀模型）。"""

    model_config = ConfigDict(from_attributes=True)

    decision_id: UUID
    application_id: UUID
    decision_type: str
    selected_candidate_id: UUID | None
    override_id: UUID | None
    approved_start_at: datetime | None
    approved_end_at: datetime | None
    reason: str
    decided_by: UUID
    decided_at: datetime
    created_at: datetime


class CommentSummaryDTO(BaseModel):
    """單筆評論讀模型。"""

    model_config = ConfigDict(from_attributes=True)

    comment_id: UUID
    application_id: UUID
    comment_type: str
    content: str
    created_by: UUID
    created_at: datetime


class SupplementItemSummaryDTO(BaseModel):
    """補件項目讀模型。"""

    supplement_item_id: UUID
    item_code: str
    item_name: str
    required_action: str
    note: str | None
    created_at: datetime


class SupplementRequestSummaryDTO(BaseModel):
    """補件請求與其項目。"""

    supplement_request_id: UUID
    application_id: UUID
    requested_by: UUID
    deadline_at: datetime | None
    status: str
    title: str
    message: str
    applicant_response_note: str | None = None
    responded_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    items: list[SupplementItemSummaryDTO] = Field(default_factory=list)


class ReviewPageOutputDTO(BaseModel):
    """
    UC-REV-02：審核頁聚合模型。

    責任：含 Application 明細、路線規劃快照、決策／評論／補件歷史；OCR 摘要可由 API 另接或後續擴充。
    """

    application: ApplicationDetailDTO
    route_plan: dict[str, Any] | None = None
    ocr_summary: dict[str, Any] | None = Field(
        default=None,
        description="占位：實際 OCR 彙總由附件／辨識服務提供後填入",
    )
    decisions: list[DecisionSummaryDTO] = Field(default_factory=list)
    comments: list[CommentSummaryDTO] = Field(default_factory=list)
    supplement_requests: list[SupplementRequestSummaryDTO] = Field(default_factory=list)


class AuditTrailEntryDTO(BaseModel):
    """稽核軌跡單列（時間序事件）。"""

    entry_type: str
    occurred_at: datetime
    payload: dict[str, Any]


class ReviewOcrSummaryDTO(BaseModel):
    """
    案件 OCR 彙總讀模型（GET …/ocr-summary）。

    責任：結構對齊審核頁 `ReviewPageOutputDTO.ocr_summary`；實際欄位由 OCR 管線／Integration 填入。
    """

    application_id: UUID
    ocr_summary: dict[str, Any] = Field(default_factory=dict)
