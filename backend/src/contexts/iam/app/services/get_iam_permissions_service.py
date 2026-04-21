"""
get_iam_permissions_service — 展開使用者經角色指派可得之 permission_code 清單。
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select

from shared.core.db.connection import get_session

from src.contexts.iam.app.dtos.auth_permissions_dto import IamPermissionsOutputDTO
from src.contexts.iam.infra.schema.permissions import Permissions
from src.contexts.iam.infra.schema.role_assignments import RoleAssignments
from src.contexts.iam.infra.schema.role_permissions import RolePermissions


class GetIamPermissionsService:
    """對應 GET /auth/me/permissions。"""

    def execute(self, user_id: UUID) -> IamPermissionsOutputDTO:
        stmt = (
            select(Permissions.permission_code)
            .distinct()
            .join(RolePermissions, RolePermissions.permission_code == Permissions.permission_code)
            .join(RoleAssignments, RoleAssignments.role_code == RolePermissions.role_code)
            .where(RoleAssignments.user_id == user_id)
            .order_by(Permissions.permission_code)
        )
        with get_session() as session:
            codes = list(session.scalars(stmt).all())
        return IamPermissionsOutputDTO(permission_codes=codes)
