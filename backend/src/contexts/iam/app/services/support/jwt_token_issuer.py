"""
jwt_token_issuer — 以專案 JWTHandler 同一套 secret／algorithm 簽發 access JWT。

與 AuthMiddleware 驗證邏輯一致；refresh 仍使用不透明字串（與 Stub 相同）。
"""

from __future__ import annotations

import time
import uuid
from uuid import UUID

import jwt
from sqlalchemy import select

from shared.core.config import settings
from shared.core.db.connection import get_session

from src.contexts.iam.app.services.support.refresh_token_presentation import format_stub_refresh_token
from src.contexts.iam.domain.ports.policy_ports import TokenIssuerPort
from src.contexts.iam.domain.value_objects import UserId
from src.contexts.iam.infra.schema.role_assignments import RoleAssignments


def _role_codes_for_user(user_uuid: UUID) -> list[str]:
    with get_session() as session:
        rows = list(
            session.scalars(
                select(RoleAssignments.role_code).where(RoleAssignments.user_id == user_uuid)
            ).all()
        )
    # 無角色指派（一般申請人）：給予預設 role 供中介層通過
    codes = list(dict.fromkeys([r for r in rows if r]))
    return codes if codes else ["user"]


class JwtTokenIssuer(TokenIssuerPort):
    """簽發可通過 JWTHandler / AuthMiddleware 的 access token。"""

    def issue_access_token(
        self,
        *,
        user_id: UserId,
        session_hint: str | None = None,
    ) -> tuple[str, str, int]:
        _ = session_hint
        jti = str(uuid.uuid4())
        uid = UUID(user_id.value)
        roles = _role_codes_for_user(uid)

        ttl_sec = max(60, int(settings.security.jwt_expire_seconds))
        now = int(time.time())
        payload = {
            "sub": user_id.value,
            "iat": now,
            "exp": now + ttl_sec,
            "roles": roles,
            "jti": jti,
        }
        token = jwt.encode(
            payload,
            settings.security.jwt_secret,
            algorithm=settings.security.jwt_algorithm,
        )
        if isinstance(token, bytes):
            token = token.decode("utf-8")
        return jti, token, ttl_sec

    def issue_refresh_token(
        self,
        *,
        user_id: UserId,
        access_jti: str,
    ) -> tuple[str | None, int | None]:
        _ = user_id
        _ = access_jti
        rjti = str(uuid.uuid4())
        return rjti, int(settings.security.jwt_refresh_expire_seconds)

    def present_refresh_token(self, *, refresh_jti: str) -> str:
        return format_stub_refresh_token(refresh_jti)
