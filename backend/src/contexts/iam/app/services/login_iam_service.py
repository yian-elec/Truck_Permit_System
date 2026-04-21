"""
login_iam_service — UC-IAM-02 登入（password 與 external 模式）。

責任：
- 查使用者、驗證密碼或外部 IdP assertion、呼叫領域狀態與 MFA 需求判斷。
- 需 MFA 時建立 `iam.mfa_challenges`（可選呼叫 MfaSenderPort）。
- 不需 MFA 時簽發 token、建立 `iam.sessions`、更新最後登入時間。
"""

from __future__ import annotations

import bcrypt
import secrets
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from shared.core.db.connection import get_session
from shared.core.logger.logger import logger

from src.contexts.iam.app.dtos.login_iam_dto import LoginIamInputDTO, LoginIamOutputDTO
from src.contexts.iam.app.errors import IamAccountNotAllowedError, IamInvalidCredentialsError
from src.contexts.iam.app.services.support.iam_orm_mapping import domain_user_from_orm
from src.contexts.iam.app.services.support.session_expiry import compute_session_expires_at
from src.contexts.iam.app.services.support.stub_auth_provider import StubAuthProviderPort
from src.contexts.iam.domain.entities.mfa_challenge import MfaChallenge as DomainMfaChallenge
from src.contexts.iam.domain.errors import InvalidUserStateError
from src.contexts.iam.domain.ports.policy_ports import AuthProviderPort, MfaSenderPort, TokenIssuerPort
from src.contexts.iam.domain.value_objects import MfaChallengeId, MfaMethod, UserId
from src.contexts.iam.infra.schema.mfa_challenges import MfaChallenges
from src.contexts.iam.infra.schema.role_assignments import RoleAssignments
from src.contexts.iam.infra.schema.sessions import Sessions
from src.contexts.iam.infra.schema.users import Users


class LoginIamService:
    """登入用例服務。"""

    def __init__(
        self,
        token_issuer: TokenIssuerPort,
        mfa_sender: MfaSenderPort | None = None,
        auth_provider: AuthProviderPort | None = None,
    ) -> None:
        self._token_issuer = token_issuer
        self._mfa_sender = mfa_sender
        self._auth: AuthProviderPort = auth_provider or StubAuthProviderPort()

    def execute(self, inp: LoginIamInputDTO) -> LoginIamOutputDTO:
        now = datetime.now(timezone.utc)
        if inp.login_mode == "password":
            return self._login_password(inp, now)
        return self._login_external(inp, now)

    def _login_password(self, inp: LoginIamInputDTO, now: datetime) -> LoginIamOutputDTO:
        nid = (inp.identifier or "").strip()

        with get_session() as session:
            u = self._find_user_by_identifier(session, nid)
            if u is None or not u.password_hash:
                raise IamInvalidCredentialsError("Invalid identifier or password")

            if not bcrypt.checkpw(inp.password.encode("utf-8"), u.password_hash.encode("utf-8")):
                raise IamInvalidCredentialsError("Invalid identifier or password")

            return self._continue_after_credential_ok(session, u, now)

    def _login_external(self, inp: LoginIamInputDTO, now: datetime) -> LoginIamOutputDTO:
        prov = (inp.external_provider or "").strip()
        assertion = (inp.credential_assertion or "").strip()
        subject = self._auth.verify_external_credential(provider=prov, credential_assertion=assertion)
        if subject is None:
            raise IamInvalidCredentialsError("Invalid external credential")

        with get_session() as session:
            u = self._find_user_by_external(session, prov, subject)
            if u is None:
                raise IamInvalidCredentialsError("Unknown external identity")

            return self._continue_after_credential_ok(session, u, now)

    def _continue_after_credential_ok(self, session: Session, u: Users, now: datetime) -> LoginIamOutputDTO:
        assigns = list(
            session.scalars(select(RoleAssignments).where(RoleAssignments.user_id == u.user_id)).all()
        )
        domain_user = domain_user_from_orm(u, assigns)

        try:
            domain_user.ensure_may_authenticate(now)
        except InvalidUserStateError as e:
            raise IamAccountNotAllowedError(str(e)) from e

        if domain_user.requires_mfa_challenge_before_tokens():
            return self._start_mfa_challenge(session, u, domain_user.user_id, now)

        return self._complete_login_without_mfa(session, u, domain_user, now)

    @staticmethod
    def _find_user_by_identifier(session: Session, identifier: str) -> Users | None:
        u = session.scalars(select(Users).where(Users.username == identifier).limit(1)).first()
        if u is not None:
            return u
        return session.scalars(
            select(Users).where(Users.email == identifier.lower()).limit(1)
        ).first()

    @staticmethod
    def _find_user_by_external(session: Session, provider: str, subject: str) -> Users | None:
        return session.scalars(
            select(Users)
            .where(
                Users.external_provider == provider,
                Users.external_subject == subject,
            )
            .limit(1)
        ).first()

    def _start_mfa_challenge(
        self,
        session: Session,
        u: Users,
        user_id_vo: UserId,
        now: datetime,
    ) -> LoginIamOutputDTO:
        challenge_uuid = uuid4()
        plain = f"{secrets.randbelow(1_000_000):06d}"
        code_hash = bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        expires_at = now + timedelta(minutes=10)

        dom = DomainMfaChallenge.issue(
            challenge_id=MfaChallengeId(str(challenge_uuid)),
            user_id=user_id_vo,
            method=MfaMethod.SMS,
            code_hash=code_hash,
            expires_at=expires_at,
            created_at=now,
            target=u.mobile,
        )

        session.add(
            MfaChallenges(
                challenge_id=challenge_uuid,
                user_id=u.user_id,
                method=dom.method.value,
                target=dom.target,
                code_hash=dom.code_hash,
                expires_at=dom.expires_at,
                verified_at=dom.verified_at,
                created_at=dom.created_at,
            )
        )

        if self._mfa_sender is not None:
            self._mfa_sender.send_challenge(
                user_id=user_id_vo,
                method=MfaMethod.SMS,
                target=u.mobile,
                plain_code=plain,
            )
        else:
            logger.warning(
                "iam.login mfa challenge created but MfaSenderPort not configured",
                challenge_id=str(challenge_uuid),
            )

        logger.info(
            "iam.audit login_mfa_challenge",
            user_id=str(u.user_id),
            challenge_id=str(challenge_uuid),
        )

        return LoginIamOutputDTO(mfa_required=True, challenge_id=challenge_uuid)

    def _complete_login_without_mfa(
        self,
        session: Session,
        u: Users,
        domain_user,
        now: datetime,
    ) -> LoginIamOutputDTO:
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
            "iam.audit login_success",
            user_id=str(u.user_id),
            session_id=str(sid),
        )

        refresh_opaque = (
            self._token_issuer.present_refresh_token(refresh_jti=refresh_jti) if refresh_jti else None
        )

        return LoginIamOutputDTO(
            mfa_required=False,
            access_token=access_token,
            refresh_token=refresh_opaque,
            session_id=sid,
            access_token_jti=access_jti,
            refresh_token_jti=refresh_jti,
            expires_at=expires_at,
        )
