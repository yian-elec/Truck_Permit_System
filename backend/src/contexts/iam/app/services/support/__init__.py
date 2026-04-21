"""
support — 應用層共用基礎設施（非 UC 用例服務）。

責任邊界：
- ORM 列與 Domain 之組裝／轉換（`iam_orm_mapping`）。
- 單一 SQLAlchemy Session 內之權限展開查詢（`iam_permission_session`）。
- 開發／測試用之連接埠實作（`stub_token_issuer`）。

用例流程請使用同層之 `*_service.py` 與 `IamServiceFactory`。
"""

from __future__ import annotations

from src.contexts.iam.app.services.support.iam_orm_mapping import (
    applicant_domain_to_users_row,
    domain_mfa_from_orm,
    domain_user_from_orm,
    map_role_assignment_row,
)
from src.contexts.iam.app.services.support.iam_permission_session import session_user_has_permission
from src.contexts.iam.app.services.support.jwt_token_issuer import JwtTokenIssuer
from src.contexts.iam.app.services.support.stub_token_issuer import StubTokenIssuer

__all__ = [
    "JwtTokenIssuer",
    "StubTokenIssuer",
    "applicant_domain_to_users_row",
    "domain_mfa_from_orm",
    "domain_user_from_orm",
    "map_role_assignment_row",
    "session_user_has_permission",
]
