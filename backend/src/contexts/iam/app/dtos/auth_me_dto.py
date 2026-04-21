"""
auth_me_dto — GET /auth/me 回傳之 IAM 使用者摘要（不含敏感欄位）。
"""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class IamMeOutputDTO(BaseModel):
    """當前登入者於 iam.users 之公開欄位摘要。"""

    user_id: UUID
    account_type: str = Field(..., max_length=30)
    status: str = Field(..., max_length=30)
    display_name: str = Field(..., max_length=100)
    email: Optional[str] = None
    mobile: Optional[str] = None
    mfa_enabled: bool
    username: Optional[str] = Field(None, max_length=100)
