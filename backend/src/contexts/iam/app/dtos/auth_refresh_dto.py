"""
auth_refresh_dto — POST /auth/refresh 輸入／輸出（UC refresh）。
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class IamRefreshInputDTO(BaseModel):
    """Refresh 請求本文：傳登入／MFA 回傳之 refresh_token 或 refresh_token_jti。"""

    refresh_token: str = Field(..., min_length=1, description="不透明 refresh 或 JTI")


class IamRefreshOutputDTO(BaseModel):
    """輪替 access／refresh 後回傳（與登入成功欄位對齊）。"""

    access_token: str
    refresh_token: Optional[str] = None
    session_id: UUID
    access_token_jti: str
    refresh_token_jti: Optional[str] = None
    expires_at: datetime
