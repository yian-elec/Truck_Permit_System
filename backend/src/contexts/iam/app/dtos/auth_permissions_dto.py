"""
auth_permissions_dto — GET /auth/me/permissions 有效權限清單。
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class IamPermissionsOutputDTO(BaseModel):
    """經角色指派展開後之 permission_code 列表（去重）。"""

    permission_codes: list[str] = Field(default_factory=list, description="權限代碼，如 iam.view_self")
