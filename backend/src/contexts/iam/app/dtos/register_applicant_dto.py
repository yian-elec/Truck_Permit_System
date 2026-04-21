"""
register_applicant_dto — UC-IAM-01 註冊申請人輸入／輸出 DTO。
"""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class RegisterApplicantInputDTO(BaseModel):
    """
    註冊申請人輸入。

    責任：承載 API／用例邊界之欄位與基本長度驗證；重複檢查於服務內搭配 Infra。
    """

    display_name: str = Field(..., min_length=1, max_length=100, description="顯示姓名")
    email: Optional[EmailStr] = Field(None, description="Email（可選，若提供則小寫正規化後儲存）")
    mobile: Optional[str] = Field(None, max_length=30, description="手機號碼")
    password: str = Field(..., min_length=8, max_length=128, description="明文密碼（服務內雜湊）")


class RegisterApplicantOutputDTO(BaseModel):
    """註冊成功後回傳之使用者識別與顯示資訊。"""

    user_id: UUID
    display_name: str
    email: Optional[str] = None
    mobile: Optional[str] = None
    status: str
