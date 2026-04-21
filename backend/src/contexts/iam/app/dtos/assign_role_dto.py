"""
assign_role_dto — UC-IAM-04 指派角色輸入／輸出 DTO。
"""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AssignRoleRequestBodyDTO(BaseModel):
    """
    HTTP 請求本文：對應 POST /admin/users/{userId}/roles。

    路徑參數提供 target user；操作者由 API 自 JWT 注入 `AssignRoleInputDTO.operator_user_id`。
    """

    role_code: str = Field(..., min_length=1, max_length=50, description="角色代碼")
    assignment_id: UUID = Field(..., description="指派列主鍵 UUID")
    scope_type: Optional[str] = Field(None, max_length=50, description="範圍類型，須與 scope_id 成對")
    scope_id: Optional[str] = Field(None, max_length=100, description="範圍識別")


class AssignRoleInputDTO(BaseModel):
    """
    指派角色輸入。

    責任：由 API 傳入操作者、目標使用者、角色與可選 scope；assignment_id 為新 UUID（新建或更新同一業務鍵時由呼叫端產生）。
    """

    operator_user_id: UUID = Field(..., description="執行指派的操作者（需具 iam.assign_roles）")
    target_user_id: UUID = Field(..., description="被指派的使用者")
    role_code: str = Field(..., min_length=1, max_length=50, description="角色代碼")
    assignment_id: UUID = Field(..., description="此筆指派列之主鍵（新建或更新皆傳新 UUID）")
    scope_type: Optional[str] = Field(None, max_length=50, description="範圍類型，與 scope_id 成對")
    scope_id: Optional[str] = Field(None, max_length=100, description="範圍識別")


class AssignRoleOutputDTO(BaseModel):
    """指派完成後回傳之指派識別與角色代碼。"""

    assignment_id: UUID
    target_user_id: UUID
    role_code: str
    scope_type: Optional[str] = None
    scope_id: Optional[str] = None
