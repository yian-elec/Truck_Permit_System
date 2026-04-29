"""
審查寫入命令 DTO（補件、核准、駁回、評論）。

責任：對應 POST 類用例之請求／回應形狀；與領域驗證銜接於 Command 服務。
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RequestSupplementInputDTO(BaseModel):
    """UC-REV-03：發出補件。"""

    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=200)
    message: str = Field(min_length=1, max_length=20_000)
    deadline_at: datetime | None = None
    decision_reason: str = Field(
        min_length=1,
        max_length=20_000,
        description="寫入 review.decisions(type=supplement) 之理由，與補件說明可分開或相同",
    )


class RequestSupplementOutputDTO(BaseModel):
    """補件建立後回傳主鍵與關聯決策。"""

    supplement_request_id: UUID
    decision_id: UUID
    application_status: str


class ApproveApplicationInputDTO(BaseModel):
    """UC-REV-04：核准。"""

    reason: str = Field(min_length=1, max_length=20_000)
    approved_start_at: datetime | None = None
    approved_end_at: datetime | None = None
    selected_candidate_id: UUID | None = None
    override_id: UUID | None = None


class ApproveApplicationOutputDTO(BaseModel):
    decision_id: UUID
    application_status: str


class RejectApplicationInputDTO(BaseModel):
    """UC-REV-05：駁回。"""

    reason: str = Field(min_length=1, max_length=20_000)


class RejectApplicationOutputDTO(BaseModel):
    decision_id: UUID
    application_status: str


class AddCommentInputDTO(BaseModel):
    """新增評論；類型須為 internal / supplement / decision_note。"""

    model_config = ConfigDict(str_strip_whitespace=True)

    comment_type: str = Field(max_length=30)
    content: str = Field(min_length=1, max_length=50_000)


class AddCommentOutputDTO(BaseModel):
    comment_id: UUID
    application_id: UUID
    comment_type: str
    created_at: datetime
