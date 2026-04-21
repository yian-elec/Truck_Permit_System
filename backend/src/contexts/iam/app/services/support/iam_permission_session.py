"""
iam_permission_session — 以單一 SQLAlchemy Session 查詢使用者是否擁有某 permission_code。

責任：支援 UC-IAM-04 操作者授權；不寫業務規則，僅表 JOIN 展開。
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.contexts.iam.infra.schema.permissions import Permissions
from src.contexts.iam.infra.schema.role_assignments import RoleAssignments
from src.contexts.iam.infra.schema.role_permissions import RolePermissions


def session_user_has_permission(session: Session, user_id: UUID, permission_code: str) -> bool:
    """
    若該使用者的任一角色指派可透過 role_permissions 對應到指定 permission_code，則為 True。
    """
    stmt = (
        select(Permissions.permission_code)
        .join(RolePermissions, RolePermissions.permission_code == Permissions.permission_code)
        .join(RoleAssignments, RoleAssignments.role_code == RolePermissions.role_code)
        .where(
            RoleAssignments.user_id == user_id,
            Permissions.permission_code == permission_code,
        )
        .limit(1)
    )
    return session.scalars(stmt).first() is not None
