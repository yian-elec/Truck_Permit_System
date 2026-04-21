"""
UC-OPS-02 — 通知作業 DTO。
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CreateNotificationJobInputDTO(BaseModel):
    """建立通知作業（submitted／supplement／approved／rejected 等事件觸發）。"""

    channel: str = Field(..., min_length=1, max_length=30)
    recipient: str = Field(..., min_length=1, max_length=255)
    template_code: str = Field(..., min_length=1, max_length=50)
    payload: dict[str, Any] = Field(..., description="模板變數，須非空 mapping")


class CreateNotificationJobOutputDTO(BaseModel):
    notification_job_id: UUID
    status: str


class DispatchNotificationInputDTO(BaseModel):
    """對既有 notification job 套用模板並呼叫 provider。"""

    notification_job_id: UUID


class DispatchNotificationOutputDTO(BaseModel):
    notification_job_id: UUID
    status: str
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None


class NotificationJobListItemDTO(BaseModel):
    notification_job_id: UUID
    channel: str
    recipient: str
    template_code: str
    status: str
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
