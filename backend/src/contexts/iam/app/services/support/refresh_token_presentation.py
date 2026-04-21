"""
refresh_token_presentation — API 傳入之 refresh 字串與 DB 所存 refresh_token_jti 的對應。

Stub 簽發器使用 `stub-refresh-{jti}` 不透明字串；客戶端亦可直接傳 JTI（與 login 回傳之 refresh_token_jti 一致）。
"""

from __future__ import annotations

STUB_REFRESH_PREFIX = "stub-refresh-"


def format_stub_refresh_token(refresh_jti: str) -> str:
    j = (refresh_jti or "").strip()
    return f"{STUB_REFRESH_PREFIX}{j}"


def parse_presented_refresh_token(presented: str) -> str:
    s = (presented or "").strip()
    if s.startswith(STUB_REFRESH_PREFIX):
        return s[len(STUB_REFRESH_PREFIX) :].strip()
    return s
