"""
logout_iam_service — 將指定 session 標記 revoked_at（對應 POST /auth/logout）。
"""

from __future__ import annotations

from datetime import datetime, timezone

from shared.core.db.connection import get_session

from src.contexts.iam.app.dtos.auth_logout_dto import IamLogoutInputDTO, IamLogoutOutputDTO
from src.contexts.iam.app.errors import IamSessionNotFoundError
from src.contexts.iam.infra.schema.sessions import Sessions


class LogoutIamService:
    """撤銷工作階段；若已撤銷則回傳現狀（冪等）。"""

    def execute(self, inp: IamLogoutInputDTO) -> IamLogoutOutputDTO:
        now = datetime.now(timezone.utc)
        with get_session() as session:
            row = session.get(Sessions, inp.session_id)
            if row is None or row.user_id != inp.user_id:
                raise IamSessionNotFoundError()
            if row.revoked_at is None:
                row.revoked_at = now
            return IamLogoutOutputDTO(session_id=row.session_id, revoked_at=row.revoked_at)
