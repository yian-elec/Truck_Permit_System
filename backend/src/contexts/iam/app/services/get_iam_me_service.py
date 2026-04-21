"""
get_iam_me_service — 依使用者識別讀取 iam.users 公開欄位（對應 GET /auth/me）。
"""

from __future__ import annotations

from uuid import UUID

from shared.core.db.connection import get_session

from src.contexts.iam.app.dtos.auth_me_dto import IamMeOutputDTO
from src.contexts.iam.app.errors import IamUserNotFoundError
from src.contexts.iam.infra.schema.users import Users


class GetIamMeService:
    """查詢當前 IAM 使用者基本資料。"""

    def execute(self, user_id: UUID) -> IamMeOutputDTO:
        with get_session() as session:
            row = session.get(Users, user_id)
            if row is None:
                raise IamUserNotFoundError()
            return IamMeOutputDTO(
                user_id=row.user_id,
                account_type=row.account_type,
                status=row.status,
                display_name=row.display_name,
                email=row.email,
                mobile=row.mobile,
                mfa_enabled=bool(row.mfa_enabled),
                username=row.username,
            )
