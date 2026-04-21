"""
verify_mfa_service — UC-IAM-03 驗證 MFA。

責任：
- 驗證 challenge 存在／未過期／未重複使用（Domain）。
- 比對 OTP 與 code_hash（bcrypt）。
- 簽發 token、建立 session、更新最後登入（同一交易）。
"""

from __future__ import annotations

import bcrypt
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import select

from shared.core.db.connection import get_session
from shared.core.logger.logger import logger

from src.contexts.iam.app.dtos.mfa_verify_dto import MfaVerifyInputDTO, MfaVerifyOutputDTO
from src.contexts.iam.app.errors import (
    IamAccountNotAllowedError,
    IamInvalidCredentialsError,
    IamMfaChallengeInvalidError,
    IamUserNotFoundError,
)
from src.contexts.iam.app.services.support.iam_orm_mapping import domain_mfa_from_orm, domain_user_from_orm
from src.contexts.iam.app.services.support.session_expiry import compute_session_expires_at
from src.contexts.iam.domain.errors import (
    InvalidUserStateError,
    MfaChallengeAlreadyVerifiedError,
    MfaChallengeExpiredError,
)
from src.contexts.iam.domain.ports.policy_ports import TokenIssuerPort
from src.contexts.iam.infra.schema.mfa_challenges import MfaChallenges
from src.contexts.iam.infra.schema.role_assignments import RoleAssignments
from src.contexts.iam.infra.schema.sessions import Sessions
from src.contexts.iam.infra.schema.users import Users


class VerifyMfaService:
    """MFA 驗證用例服務。"""

    def __init__(self, token_issuer: TokenIssuerPort) -> None:
        self._token_issuer = token_issuer

    def execute(self, inp: MfaVerifyInputDTO) -> MfaVerifyOutputDTO:
        now = datetime.now(timezone.utc)

        with get_session() as session:
            row = session.get(MfaChallenges, inp.challenge_id)
            if row is None:
                raise IamMfaChallengeInvalidError("Challenge not found")

            dom = domain_mfa_from_orm(row)
            try:
                dom.assert_can_verify(now)
            except MfaChallengeExpiredError as e:
                raise IamMfaChallengeInvalidError(str(e)) from e
            except MfaChallengeAlreadyVerifiedError as e:
                raise IamMfaChallengeInvalidError(str(e)) from e

            if not bcrypt.checkpw(inp.code.encode("utf-8"), row.code_hash.encode("utf-8")):
                raise IamInvalidCredentialsError("Invalid MFA code")

            dom.complete_verification(now)
            row.verified_at = dom.verified_at

            u = session.get(Users, row.user_id)
            if u is None:
                raise IamUserNotFoundError()

            assigns = list(
                session.scalars(
                    select(RoleAssignments).where(RoleAssignments.user_id == u.user_id)
                ).all()
            )
            domain_user = domain_user_from_orm(u, assigns)
            try:
                domain_user.ensure_may_authenticate(now)
            except InvalidUserStateError as e:
                raise IamAccountNotAllowedError(str(e)) from e

            domain_user.record_successful_login(now)
            u.last_login_at = now

            access_jti, access_token, ttl_sec = self._token_issuer.issue_access_token(
                user_id=domain_user.user_id,
                session_hint=None,
            )
            refresh_jti, refresh_ttl = self._token_issuer.issue_refresh_token(
                user_id=domain_user.user_id,
                access_jti=access_jti,
            )

            sid = uuid4()
            expires_at = compute_session_expires_at(
                now,
                access_ttl_seconds=ttl_sec,
                refresh_jti=refresh_jti,
                refresh_ttl_seconds=refresh_ttl,
            )
            session.add(
                Sessions(
                    session_id=sid,
                    user_id=u.user_id,
                    access_token_jti=access_jti,
                    refresh_token_jti=refresh_jti,
                    issued_at=now,
                    expires_at=expires_at,
                    revoked_at=None,
                )
            )

            logger.info(
                "iam.audit mfa_verify_success",
                user_id=str(u.user_id),
                session_id=str(sid),
                challenge_id=str(inp.challenge_id),
            )

            refresh_opaque = (
                self._token_issuer.present_refresh_token(refresh_jti=refresh_jti) if refresh_jti else None
            )

            return MfaVerifyOutputDTO(
                access_token=access_token,
                refresh_token=refresh_opaque,
                session_id=sid,
                access_token_jti=access_jti,
                refresh_token_jti=refresh_jti,
                expires_at=expires_at,
            )
