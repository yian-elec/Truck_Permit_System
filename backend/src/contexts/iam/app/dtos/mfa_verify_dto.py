"""
mfa_verify_dto — UC-IAM-03 驗證 MFA 輸入／輸出 DTO。
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class MfaVerifyInputDTO(BaseModel):
    """使用者提交之 challenge 與一次性驗證碼。"""

    challenge_id: UUID
    code: str = Field(..., min_length=4, max_length=32, description="OTP 明文")


class MfaVerifyOutputDTO(BaseModel):
    """驗證成功後簽發之 token 與工作階段資訊。"""

    access_token: str
    refresh_token: Optional[str] = None
    session_id: UUID
    access_token_jti: str
    refresh_token_jti: Optional[str] = None
    expires_at: datetime
