"""
refresh_iam_service — POST /auth/refresh（refresh 輪替 access／refresh JTI）。

責任：
- 以 refresh_token（不透明或 JTI）解析出 refresh_token_jti，查 `iam.sessions`。
- 驗證未撤銷且未過期、且該列有啟用 refresh。
- 呼叫 `TokenIssuerPort` 簽發新 access／refresh，更新同列 session。
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session as OrmSession

from shared.core.db.connection import get_session
from shared.core.logger.logger import logger

from src.contexts.iam.app.dtos.auth_refresh_dto import IamRefreshInputDTO, IamRefreshOutputDTO
from src.contexts.iam.app.errors import IamRefreshTokenInvalidError
from src.contexts.iam.app.services.support.refresh_token_presentation import parse_presented_refresh_token
from src.contexts.iam.app.services.support.session_expiry import compute_session_expires_at
from src.contexts.iam.domain.ports.policy_ports import TokenIssuerPort
from src.contexts.iam.domain.value_objects import UserId
from src.contexts.iam.infra.schema.sessions import Sessions


class RefreshIamService:
    """Refresh 用例服務。"""

    def __init__(self, token_issuer: TokenIssuerPort) -> None:
        self._token_issuer = token_issuer

    def execute(self, inp: IamRefreshInputDTO) -> IamRefreshOutputDTO:
        now = datetime.now(timezone.utc)
        presented = parse_presented_refresh_token(inp.refresh_token)
        if not presented:
            raise IamRefreshTokenInvalidError("Empty refresh token after normalization")

        with get_session() as session:
            row = self._find_session_by_refresh_jti(session, presented)
            if row is None:
                raise IamRefreshTokenInvalidError("Unknown refresh token")

            if row.revoked_at is not None:
                raise IamRefreshTokenInvalidError("Session revoked")

            if row.refresh_token_jti is None:
                raise IamRefreshTokenInvalidError("Refresh not enabled for this session")

            if now >= row.expires_at:
                raise IamRefreshTokenInvalidError("Session expired")

            user_id_vo = UserId(str(row.user_id))
            access_jti, access_token, ttl_sec = self._token_issuer.issue_access_token(
                user_id=user_id_vo,
                session_hint=str(row.session_id),
            )
            new_refresh_jti, refresh_ttl = self._token_issuer.issue_refresh_token(
                user_id=user_id_vo,
                access_jti=access_jti,
            )

            row.access_token_jti = access_jti
            row.refresh_token_jti = new_refresh_jti
            row.issued_at = now
            row.expires_at = compute_session_expires_at(
                now,
                access_ttl_seconds=ttl_sec,
                refresh_jti=new_refresh_jti,
                refresh_ttl_seconds=refresh_ttl,
            )

            refresh_opaque = (
                self._token_issuer.present_refresh_token(refresh_jti=new_refresh_jti)
                if new_refresh_jti
                else None
            )

            logger.info(
                "iam.audit refresh_success",
                user_id=str(row.user_id),
                session_id=str(row.session_id),
            )

            return IamRefreshOutputDTO(
                access_token=access_token,
                refresh_token=refresh_opaque,
                session_id=row.session_id,
                access_token_jti=access_jti,
                refresh_token_jti=new_refresh_jti,
                expires_at=row.expires_at,
            )

    @staticmethod
    def _find_session_by_refresh_jti(session: OrmSession, refresh_jti: str) -> Sessions | None:
        return session.scalars(
            select(Sessions).where(Sessions.refresh_token_jti == refresh_jti).limit(1)
        ).first()
