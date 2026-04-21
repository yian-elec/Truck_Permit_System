"""
auth_logout_dto — POST /auth/logout 撤銷工作階段。
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class IamLogoutRequestBodyDTO(BaseModel):
    """HTTP 請求本文：僅含要撤銷的 session；user_id 由 API 自 JWT 注入用例輸入。"""

    session_id: UUID = Field(..., description="登入／MFA 成功時取得之 session_id")


class IamLogoutInputDTO(BaseModel):
    """登出輸入：當前要撤銷之 session（須屬於當前使用者）。"""

    user_id: UUID = Field(..., description="JWT sub 對應之使用者，由 API 自認證狀態注入")
    session_id: UUID = Field(..., description="登入／MFA 驗證成功時回傳之 session_id")


class IamLogoutOutputDTO(BaseModel):
    """撤銷完成回傳。"""

    session_id: UUID
    revoked_at: datetime
