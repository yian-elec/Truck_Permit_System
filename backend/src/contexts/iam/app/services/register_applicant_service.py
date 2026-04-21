"""
register_applicant_service — UC-IAM-01 註冊申請人。

責任：
- 驗證 Email／手機是否重複（Infra 查詢）。
- 雜湊密碼後呼叫 Domain `User.register_applicant`。
- 單一交易寫入 `iam.users`。
"""

from __future__ import annotations

import bcrypt
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import select

from shared.core.db.connection import get_session
from shared.core.logger.logger import logger

from src.contexts.iam.app.dtos.register_applicant_dto import (
    RegisterApplicantInputDTO,
    RegisterApplicantOutputDTO,
)
from src.contexts.iam.app.errors import (
    IamEmailAlreadyRegisteredError,
    IamInputValidationError,
    IamMobileAlreadyRegisteredError,
)
from src.contexts.iam.app.services.ports.audit_log_port import AuditLogPort, IamAuditRecord
from src.contexts.iam.app.services.ports.registration_notifier_port import (
    NoopRegistrationNotifierPort,
    RegistrationNotifierPort,
)
from src.contexts.iam.app.services.support.iam_orm_mapping import applicant_domain_to_users_row
from src.contexts.iam.app.services.support.noop_audit_log_port import NoopAuditLogPort
from src.contexts.iam.domain.entities import User as DomainUser
from src.contexts.iam.domain.errors import InvalidCredentialInvariantError, InvalidDisplayNameError
from src.contexts.iam.domain.value_objects import AccountStatus, UserId
from src.contexts.iam.infra.schema.users import Users


class RegisterApplicantService:
    """申請人註冊用例服務。"""

    def __init__(
        self,
        *,
        notifier: RegistrationNotifierPort | None = None,
        audit: AuditLogPort | None = None,
    ) -> None:
        self._notifier: RegistrationNotifierPort = notifier or NoopRegistrationNotifierPort()
        self._audit: AuditLogPort = audit or NoopAuditLogPort()

    def execute(self, inp: RegisterApplicantInputDTO) -> RegisterApplicantOutputDTO:
        email_norm = str(inp.email).strip().lower() if inp.email is not None else None
        mobile_norm = inp.mobile.strip() if inp.mobile else None

        password_hash = bcrypt.hashpw(inp.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        uid = uuid4()
        now = datetime.now(timezone.utc)

        try:
            # 立即標為 ACTIVE：目前無「待審／驗證信」之啟用 API，pending 會導致註冊後無法登入。
            domain_user = DomainUser.register_applicant(
                user_id=UserId(str(uid)),
                display_name=inp.display_name,
                email=email_norm,
                mobile=mobile_norm,
                password_hash=password_hash,
                now=now,
                initial_status=AccountStatus.ACTIVE,
            )
        except InvalidDisplayNameError as e:
            raise IamInputValidationError(str(e)) from e
        except InvalidCredentialInvariantError as e:
            raise IamInputValidationError(str(e)) from e

        with get_session() as session:
            if email_norm and session.scalars(select(Users).where(Users.email == email_norm).limit(1)).first():
                raise IamEmailAlreadyRegisteredError()
            if mobile_norm and session.scalars(select(Users).where(Users.mobile == mobile_norm).limit(1)).first():
                raise IamMobileAlreadyRegisteredError()

            row = applicant_domain_to_users_row(domain_user, uid)
            session.add(row)

        logger.info(
            "iam.audit register_applicant",
            user_id=str(uid),
            email=email_norm or "",
        )

        try:
            self._notifier.send_registration_verification_notice(
                user_id=uid,
                display_name=domain_user.display_name,
                email=domain_user.email,
                mobile=domain_user.mobile,
            )
        except Exception:
            logger.warning("iam.register notifier failed", exc_info=True)

        try:
            self._audit.append(
                IamAuditRecord(
                    actor_user_id=None,
                    actor_type="system",
                    action_code="iam.register_applicant",
                    resource_type="iam.user",
                    resource_id=str(uid),
                    after_snapshot={
                        "display_name": domain_user.display_name,
                        "email": domain_user.email,
                        "mobile": domain_user.mobile,
                        "status": domain_user.status.value,
                    },
                )
            )
        except Exception:
            logger.warning("iam.register ops audit append failed", exc_info=True)

        return RegisterApplicantOutputDTO(
            user_id=uid,
            display_name=domain_user.display_name,
            email=domain_user.email,
            mobile=domain_user.mobile,
            status=domain_user.status.value,
        )
