"""
送件前檢查與送件結果 DTO。
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class SubmissionCheckResultDTO(BaseModel):
    """UC-APP-05 送件前檢查結果。"""

    can_submit: bool = Field(..., description="是否已滿足送件條件")
    missing_reason_codes: list[str] = Field(
        default_factory=list,
        description="缺漏原因代碼（領域 evaluate_submission_readiness 併可含 incomplete_route 等由 App 層補上）",
    )


class SubmitApplicationOutputDTO(BaseModel):
    """UC-APP-06 送件成功回應。"""

    application_no: str
    status: str
    submitted_at: datetime


class SupplementResponseOutputDTO(BaseModel):
    """UC-APP-07 補件回覆完成。"""

    application_id: UUID
    status: str
    message: str = "補件已送出，將重新進入審查流程"
