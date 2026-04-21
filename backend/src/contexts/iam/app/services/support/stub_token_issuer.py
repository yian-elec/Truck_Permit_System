"""
stub_token_issuer — 開發／測試用之 TokenIssuerPort 實作。

責任：產生隨機 JTI 與佔位 token 字串；正式環境應換成 JWT／HSM 等 Infra adapter。
"""

from __future__ import annotations

import uuid

from src.contexts.iam.app.services.support.refresh_token_presentation import format_stub_refresh_token
from src.contexts.iam.domain.ports.policy_ports import TokenIssuerPort
from src.contexts.iam.domain.value_objects import UserId


class StubTokenIssuer(TokenIssuerPort):
    """不簽署真實 JWT，僅保證 JTI 唯一與 TTL 數值合理。"""

    def issue_access_token(
        self,
        *,
        user_id: UserId,
        session_hint: str | None = None,
    ) -> tuple[str, str, int]:
        jti = str(uuid.uuid4())
        token = f"stub-access-{jti}"
        return jti, token, 3600

    def issue_refresh_token(
        self,
        *,
        user_id: UserId,
        access_jti: str,
    ) -> tuple[str | None, int | None]:
        _ = user_id
        _ = access_jti
        rjti = str(uuid.uuid4())
        return rjti, 86_400

    def present_refresh_token(self, *, refresh_jti: str) -> str:
        return format_stub_refresh_token(refresh_jti)
