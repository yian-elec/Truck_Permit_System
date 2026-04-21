"""
policy_ports.py — 驗證、MFA 發送、Token 簽發連接埠

將「會員系統／SSO」「OTP 通道」「JWT／Session Token」隔離在領域外，
領域僅透過 Protocol 描述 App 用例所需能力。
"""

from __future__ import annotations

from typing import Protocol

from ..value_objects import MfaMethod, UserId


class AuthProviderPort(Protocol):
    """
    外部身分驗證連接埠（政府 SSO、既有會員系統等）。

    責任：
    - 依 provider 與 IdP 回傳之 assertion／token 驗證是否對應某 external_subject。
    實作：Infra adapter（HTTP、SAML/OIDC client 等）。
    """

    def verify_external_credential(
        self,
        *,
        provider: str,
        credential_assertion: str,
    ) -> str | None:
        """
        驗證外部憑證。

        Returns:
            驗證成功時回傳標準化之 external_subject；失敗回傳 None。
        """
        ...


class MfaSenderPort(Protocol):
    """
    MFA 挑戰發送連接埠（簡訊／Email OTP 等）。

    責任：
    - 依 method 與 target 發送一次性驗證碼或連結；不負責領域內 code_hash 儲存。
    實作：Infra（簡訊商、郵件服務）。
    """

    def send_challenge(
        self,
        *,
        user_id: UserId,
        method: MfaMethod,
        target: str | None,
        plain_code: str,
    ) -> None:
        """發送明文 OTP（僅在建立 challenge 的流程中由 App 呼叫；領域不保存明文）。"""
        ...


class TokenIssuerPort(Protocol):
    """
    存取權杖簽發連接埠（對應 UC 登入／refresh 後簽發 access／refresh）。

    責任：
    - 產生 JTI、過期時間等，供 Session 聚合建立；領域不處理演算法與金鑰。
    實作：Infra（JWT library、HSM 等）。
    """

    def issue_access_token(
        self,
        *,
        user_id: UserId,
        session_hint: str | None,
    ) -> tuple[str, str, int]:
        """
        Returns:
            (access_token_jti, raw_token_or_placeholder, ttl_seconds) — raw 是否回傳依安全策略。
        """
        ...

    def issue_refresh_token(
        self,
        *,
        user_id: UserId,
        access_jti: str,
    ) -> tuple[str | None, int | None]:
        """若政策啟用 refresh，回傳 (refresh_jti, ttl_seconds)，否則 (None, None)。"""
        ...

    def present_refresh_token(self, *, refresh_jti: str) -> str:
        """回傳給客戶端的不透明 refresh 字串（Stub 可加上前綴；JWT 實作可回傳完整 token）。"""
        ...
