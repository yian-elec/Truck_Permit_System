"""
assign_role_service — UC-IAM-04 指派角色。

責任：
- 驗證操作者是否具 `iam.assign_roles`（透過 Session JOIN 查詢）。
- 驗證目標使用者與角色主檔存在。
- 呼叫 Domain `User.assign_or_update_role` 後，於同一交易內同步 `iam.role_assignments`。
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from shared.core.db.connection import get_session
from shared.core.logger.logger import logger

from src.contexts.iam.app.dtos.assign_role_dto import AssignRoleInputDTO, AssignRoleOutputDTO
from src.contexts.iam.app.errors import (
    IamAssignRoleForbiddenError,
    IamInputValidationError,
    IamRoleNotFoundError,
    IamUserNotFoundError,
)
from src.contexts.iam.app.services.ports.audit_log_port import AuditLogPort, IamAuditRecord
from src.contexts.iam.app.services.support.iam_orm_mapping import domain_user_from_orm
from src.contexts.iam.app.services.support.noop_audit_log_port import NoopAuditLogPort
from src.contexts.iam.app.services.support.iam_permission_session import session_user_has_permission
from src.contexts.iam.domain.errors import (
    InvalidAssignmentScopePairError,
    OfficerAdminRequiresMfaError,
    OfficerAdminRequiresRoleError,
)
from src.contexts.iam.domain.value_objects import AssignmentScope, RoleAssignmentId, RoleCode
from src.contexts.iam.infra.schema.role_assignments import RoleAssignments
from src.contexts.iam.infra.schema.roles import Roles
from src.contexts.iam.infra.schema.users import Users


def _scopes_equal(a: AssignmentScope, b: AssignmentScope) -> bool:
    return (a.scope_type, a.scope_id) == (b.scope_type, b.scope_id)


class AssignRoleService:
    """指派角色用例服務。"""

    def __init__(self, audit: AuditLogPort | None = None) -> None:
        self._audit: AuditLogPort = audit or NoopAuditLogPort()

    def execute(self, inp: AssignRoleInputDTO) -> AssignRoleOutputDTO:
        now = datetime.now(timezone.utc)

        try:
            scope = AssignmentScope(scope_type=inp.scope_type, scope_id=inp.scope_id)
        except InvalidAssignmentScopePairError as e:
            raise IamInputValidationError(str(e)) from e

        with get_session() as session:
            if not session_user_has_permission(session, inp.operator_user_id, "iam.assign_roles"):
                raise IamAssignRoleForbiddenError()

            target = session.get(Users, inp.target_user_id)
            if target is None:
                raise IamUserNotFoundError("Target user not found")

            role_row = session.get(Roles, inp.role_code)
            if role_row is None:
                raise IamRoleNotFoundError()

            assigns = list(
                session.scalars(
                    select(RoleAssignments).where(RoleAssignments.user_id == target.user_id)
                ).all()
            )
            domain_user = domain_user_from_orm(target, assigns)

            try:
                domain_user.assign_or_update_role(
                    assignment_id=RoleAssignmentId(str(inp.assignment_id)),
                    role_code=RoleCode(inp.role_code),
                    scope=scope,
                    now=now,
                )
            except (OfficerAdminRequiresRoleError, OfficerAdminRequiresMfaError) as e:
                raise IamInputValidationError(str(e)) from e

            self._persist_assignment_replace(session, target.user_id, inp.role_code, scope, domain_user)

            logger.info(
                "iam.audit assign_role",
                operator=str(inp.operator_user_id),
                target=str(inp.target_user_id),
                role=inp.role_code,
                assignment_id=str(inp.assignment_id),
            )

            out = AssignRoleOutputDTO(
                assignment_id=inp.assignment_id,
                target_user_id=inp.target_user_id,
                role_code=inp.role_code,
                scope_type=scope.scope_type,
                scope_id=scope.scope_id,
            )

        try:
            self._audit.append(
                IamAuditRecord(
                    actor_user_id=inp.operator_user_id,
                    actor_type="human",
                    action_code="iam.assign_role",
                    resource_type="iam.user",
                    resource_id=str(inp.target_user_id),
                    after_snapshot={
                        "role_code": inp.role_code,
                        "assignment_id": str(inp.assignment_id),
                        "scope_type": scope.scope_type,
                        "scope_id": scope.scope_id,
                    },
                )
            )
        except Exception:
            logger.warning("iam.assign_role ops audit append failed", exc_info=True)

        return out

    @staticmethod
    def _persist_assignment_replace(
        session: Session,
        user_id: UUID,
        role_code: str,
        scope: AssignmentScope,
        domain_user,
    ) -> None:
        """刪除同一業務鍵之舊列後插入 Domain 更新後之指派列。"""
        stmt = delete(RoleAssignments).where(
            RoleAssignments.user_id == user_id,
            RoleAssignments.role_code == role_code,
        )
        if scope.scope_type is None and scope.scope_id is None:
            stmt = stmt.where(
                RoleAssignments.scope_type.is_(None),
                RoleAssignments.scope_id.is_(None),
            )
        else:
            stmt = stmt.where(
                RoleAssignments.scope_type == scope.scope_type,
                RoleAssignments.scope_id == scope.scope_id,
            )
        session.execute(stmt)

        picked = None
        for a in domain_user.role_assignments:
            if a.role_code.value == role_code and _scopes_equal(a.scope, scope):
                picked = a
                break
        if picked is None:
            raise IamInputValidationError("Domain did not produce expected role assignment")

        session.add(
            RoleAssignments(
                assignment_id=UUID(picked.assignment_id.value),
                user_id=user_id,
                role_code=picked.role_code.value,
                scope_type=picked.scope.scope_type,
                scope_id=picked.scope.scope_id,
                created_at=picked.created_at,
                updated_at=picked.updated_at,
            )
        )
