"""
role_assignments_repository — iam.role_assignments 讀寫。

僅使用 `shared.core.db.connection.get_session`。
"""

from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from sqlalchemy import delete, select

from shared.core.db.connection import get_session

from src.contexts.iam.infra.repositories._orm_detach import detach_all, detach_optional
from src.contexts.iam.infra.schema.role_assignments import RoleAssignments


class RoleAssignmentsRepository:
    """角色指派查詢與異動。"""

    def list_by_user_id(self, user_id: UUID) -> List[RoleAssignments]:
        with get_session() as session:
            rows = list(
                session.scalars(
                    select(RoleAssignments).where(RoleAssignments.user_id == user_id)
                ).all()
            )
            return detach_all(session, rows)

    def find_by_user_role_scope(
        self,
        user_id: UUID,
        role_code: str,
        scope_type: Optional[str],
        scope_id: Optional[str],
    ) -> Optional[RoleAssignments]:
        """業務鍵：使用者 + 角色 + scope（NULL 與 NULL 視為全域）。"""
        with get_session() as session:
            q = select(RoleAssignments).where(
                RoleAssignments.user_id == user_id,
                RoleAssignments.role_code == role_code,
            )
            if scope_type is None:
                q = q.where(RoleAssignments.scope_type.is_(None))
            else:
                q = q.where(RoleAssignments.scope_type == scope_type)
            if scope_id is None:
                q = q.where(RoleAssignments.scope_id.is_(None))
            else:
                q = q.where(RoleAssignments.scope_id == scope_id)
            rows = list(session.scalars(q.limit(1)).all())
            if not rows:
                return None
            return detach_optional(session, rows[0])

    def delete_by_assignment_id(self, assignment_id: UUID) -> None:
        with get_session() as session:
            session.execute(delete(RoleAssignments).where(RoleAssignments.assignment_id == assignment_id))
            # get_session context manager commits on exit

    def add(self, row: RoleAssignments) -> RoleAssignments:
        with get_session() as session:
            session.add(row)
            session.flush()
            session.refresh(row)
            return detach_optional(session, row)
