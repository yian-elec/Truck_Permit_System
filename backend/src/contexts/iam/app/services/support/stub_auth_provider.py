"""
stub_auth_provider — 開發／測試用之 AuthProviderPort。

驗證格式：`credential_assertion` 為 `stub:{subject}` 時回傳 `subject`（trimmed）；
否則回傳 None。對應 `external_provider` 應為 `stub`。
"""

from __future__ import annotations

from src.contexts.iam.domain.ports.policy_ports import AuthProviderPort


class StubAuthProviderPort(AuthProviderPort):
    """不呼叫真實 SSO；僅供 UC-IAM-02 external 模式打通管線。"""

    def verify_external_credential(
        self,
        *,
        provider: str,
        credential_assertion: str,
    ) -> str | None:
        pv = (provider or "").strip().lower()
        raw = (credential_assertion or "").strip()
        if pv != "stub" or not raw.startswith("stub:"):
            return None
        subject = raw[5:].strip()
        return subject if subject else None
