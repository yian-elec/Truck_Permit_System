"""
IAM 應用層 services — 用例流程與 Domain／Infra 協調。

- 根目錄：`register_applicant_service`、`login_iam_service`、`verify_mfa_service`、`assign_role_service`、`service_factory`（一檔一 UC 或一組裝點）。
- `support/`：ORM↔Domain 對照、Session 權限查詢、Stub 連接埠（非用例服務，避免與 UC 混放）。
"""

from __future__ import annotations

from src.contexts.iam.app.services.assign_role_service import AssignRoleService
from src.contexts.iam.app.services.login_iam_service import LoginIamService
from src.contexts.iam.app.services.register_applicant_service import RegisterApplicantService
from src.contexts.iam.app.services.service_factory import IamServiceFactory
from src.contexts.iam.app.services.support.stub_token_issuer import StubTokenIssuer
from src.contexts.iam.app.services.verify_mfa_service import VerifyMfaService

__all__ = [
    "AssignRoleService",
    "IamServiceFactory",
    "LoginIamService",
    "RegisterApplicantService",
    "StubTokenIssuer",
    "VerifyMfaService",
]
