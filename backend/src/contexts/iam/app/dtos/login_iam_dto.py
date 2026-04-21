"""
login_iam_dto — UC-IAM-02 登入輸入／輸出 DTO。
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class LoginIamInputDTO(BaseModel):
    """
    登入輸入：`password` 模式以 identifier（username 或 email）+ 密碼；
    `external` 模式以 IdP provider + assertion（由 AuthProviderPort 驗證）。
    """

    login_mode: Literal["password", "external"] = Field(default="password", description="登入模式")
    identifier: Optional[str] = Field(None, max_length=255, description="帳號或 Email（password 模式）")
    password: Optional[str] = Field(None, max_length=128, description="明文密碼（password 模式）")
    external_provider: Optional[str] = Field(None, max_length=50, description="外部 IdP 代碼（external 模式）")
    credential_assertion: Optional[str] = Field(
        None,
        max_length=2048,
        description="外部憑證／assertion（external 模式）",
    )

    @model_validator(mode="after")
    def validate_mode_fields(self) -> LoginIamInputDTO:
        if self.login_mode == "password":
            ident = (self.identifier or "").strip()
            pwd = self.password or ""
            if not ident or not pwd:
                raise ValueError("password mode requires non-empty identifier and password")
        else:
            ep = (self.external_provider or "").strip()
            ca = (self.credential_assertion or "").strip()
            if not ep or not ca:
                raise ValueError("external mode requires external_provider and credential_assertion")
        return self


class LoginIamOutputDTO(BaseModel):
    """
    登入輸出：若需 MFA 則回傳 challenge；否則回傳 token／session 摘要。

    access_token 實際內容由 TokenIssuerPort 決定，此處可為不透明字串或 JWT。
    """

    mfa_required: bool
    challenge_id: Optional[UUID] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    session_id: Optional[UUID] = None
    access_token_jti: Optional[str] = None
    refresh_token_jti: Optional[str] = None
    expires_at: Optional[datetime] = None
