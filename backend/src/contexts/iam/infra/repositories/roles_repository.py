"""
roles_repository — iam.roles 唯讀查詢。

僅使用 `shared.core.db.connection.get_session`。
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import select

from shared.core.db.connection import get_session

from src.contexts.iam.infra.repositories._orm_detach import detach_optional
from src.contexts.iam.infra.schema.roles import Roles


class RolesRepository:
    """角色主檔讀取（UC-IAM-04 驗證 role 存在）。"""

    def get_by_role_code(self, role_code: str) -> Optional[Roles]:
        with get_session() as session:
            row = session.get(Roles, role_code)
            return detach_optional(session, row)
