"""
UC-OPS-03 — 稽核 DTO。
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class RecordAuditLogInputDTO(BaseModel):
    """關鍵交易完成後寫入稽核。"""

    actor_user_id: Optional[UUID] = Field(None, description="人類操作者；系統帳可為 null")
    actor_type: str = Field(..., min_length=1, max_length=30)
    action_code: str = Field(..., min_length=1, max_length=100)
    resource_type: str = Field(..., min_length=1, max_length=50)
    resource_id: str = Field(..., min_length=1, max_length=100)
    before_snapshot: Optional[dict[str, Any] | list[Any]] = None
    after_snapshot: Optional[dict[str, Any] | list[Any]] = None
    client_ip: Optional[str] = Field(None, description="IPv4／IPv6 字串，可為 null")


class RecordAuditLogOutputDTO(BaseModel):
    audit_log_id: UUID
    created_at: datetime


class AuditLogListItemDTO(BaseModel):
    audit_log_id: UUID
    actor_user_id: Optional[UUID]
    actor_type: str
    action_code: str
    resource_type: str
    resource_id: str
    before_json: Optional[dict[str, Any] | list[Any]] = None
    after_json: Optional[dict[str, Any] | list[Any]] = None
    client_ip: Optional[str] = None
    created_at: datetime
