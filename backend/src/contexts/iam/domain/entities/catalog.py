"""
catalog.py — IAM 主資料實體（角色／權限目錄）

對應 iam.roles、iam.permissions、iam.role_permissions 的領域模型（非 User 聚合內）。
用於 UC-IAM-04「驗證 role 存在」及權限展開時的型別承載；變更頻率低，通常由管理功能維護。
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from ..value_objects import PermissionCode, RoleCode


@dataclass(frozen=True)
class RoleDefinition:
    """
    角色定義（對應 iam.roles）。

    責任：
    - 保存 role_code 與顯示用 role_name、說明；作為指派前「角色存在」的領域物件。
    """

    role_code: RoleCode
    role_name: str
    created_at: datetime
    updated_at: datetime
    description: Optional[str] = None


@dataclass(frozen=True)
class PermissionDefinition:
    """
    權限定義（對應 iam.permissions）。

    責任：
    - 保存 permission_code 與說明；與 RoleDefinition 分離，利於細粒度授權與稽核描述。
    """

    permission_code: PermissionCode
    description: str
    created_at: datetime


@dataclass(frozen=True)
class RolePermissionGrant:
    """
    角色—權限授予關係（對應 iam.role_permissions 單列）。

    責任：
    - 表達某角色擁有某權限；展開 EffectivePermissionSet 時由 App 收集多筆 Grant 後轉成 VO。
    """

    role_code: RoleCode
    permission_code: PermissionCode
