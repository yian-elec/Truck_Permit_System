"""
service_factory — IAM 應用層用例服務組裝點。

責任：集中注入 TokenIssuerPort、MfaSenderPort、AuthProviderPort、RegistrationNotifierPort、AuditLogPort 等，
供 API 或背景工作取得一致的服務實例。

環境變數（可選）：
- `IAM_REGISTRATION_NOTIFY=1`：註冊後以 logger 模擬驗證通知。
- `IAM_APPEND_OPS_AUDIT=1`：註冊／指派角色成功後附加寫入 `ops.audit_logs`（需 ops schema）。
"""

from __future__ import annotations

import os
from typing import Optional

from src.contexts.iam.app.services.assign_role_service import AssignRoleService
from src.contexts.iam.app.services.get_iam_me_service import GetIamMeService
from src.contexts.iam.app.services.get_iam_permissions_service import GetIamPermissionsService
from src.contexts.iam.app.services.login_iam_service import LoginIamService
from src.contexts.iam.app.services.logout_iam_service import LogoutIamService
from src.contexts.iam.app.services.ports.audit_log_port import AuditLogPort
from src.contexts.iam.app.services.ports.registration_notifier_port import (
    NoopRegistrationNotifierPort,
    RegistrationNotifierPort,
)
from src.contexts.iam.app.services.refresh_iam_service import RefreshIamService
from src.contexts.iam.app.services.register_applicant_service import RegisterApplicantService
from src.contexts.iam.app.services.support.logging_registration_notifier import (
    LoggingRegistrationNotifierPort,
)
from src.contexts.iam.app.services.support.noop_audit_log_port import NoopAuditLogPort
from src.contexts.iam.app.services.support.jwt_token_issuer import JwtTokenIssuer
from src.contexts.iam.app.services.support.stub_token_issuer import StubTokenIssuer
from src.contexts.iam.app.services.verify_mfa_service import VerifyMfaService
from src.contexts.iam.domain.ports.policy_ports import MfaSenderPort, TokenIssuerPort


def _env_truthy(key: str) -> bool:
    return os.environ.get(key, "").strip().lower() in ("1", "true", "yes", "on")


def _default_registration_notifier() -> RegistrationNotifierPort:
    if _env_truthy("IAM_REGISTRATION_NOTIFY"):
        return LoggingRegistrationNotifierPort()
    return NoopRegistrationNotifierPort()


def _default_audit_port() -> AuditLogPort:
    if _env_truthy("IAM_APPEND_OPS_AUDIT"):
        from src.contexts.iam.infra.adapters.ops_audit_log_adapter import OpsAuditLogAdapter

        return OpsAuditLogAdapter()
    return NoopAuditLogPort()


class IamServiceFactory:
    """
    IAM 用例服務工廠。

    預設使用 JwtTokenIssuer（與 AuthMiddleware 同一套 JWT）；測試可注入 StubTokenIssuer。
    環境變數 `IAM_USE_STUB_TOKEN=1` 時改用 Stub（舊有不透明 access 字串）。
    """

    def __init__(
        self,
        *,
        token_issuer: Optional[TokenIssuerPort] = None,
        mfa_sender: Optional[MfaSenderPort] = None,
        registration_notifier: Optional[RegistrationNotifierPort] = None,
        audit: Optional[AuditLogPort] = None,
    ) -> None:
        if token_issuer is not None:
            self._token_issuer = token_issuer
        elif _env_truthy("IAM_USE_STUB_TOKEN"):
            self._token_issuer = StubTokenIssuer()
        else:
            self._token_issuer = JwtTokenIssuer()
        self._mfa_sender = mfa_sender
        notifier = (
            registration_notifier if registration_notifier is not None else _default_registration_notifier()
        )
        audit_port = audit if audit is not None else _default_audit_port()

        self.register_applicant = RegisterApplicantService(notifier=notifier, audit=audit_port)
        self.login_iam = LoginIamService(self._token_issuer, self._mfa_sender)
        self.verify_mfa = VerifyMfaService(self._token_issuer)
        self.assign_role = AssignRoleService(audit=audit_port)
        self.get_me = GetIamMeService()
        self.get_permissions = GetIamPermissionsService()
        self.logout = LogoutIamService()
        self.refresh = RefreshIamService(self._token_issuer)
