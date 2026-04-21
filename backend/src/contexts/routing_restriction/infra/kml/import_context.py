"""
同步匯入請求內之完整 KML 字串（可能超過 ops.import_jobs.source_ref 255 字元上限）。

使用 ContextVar 避免並發請求互相覆蓋；僅在 MapImportApplicationService 與 ingest 同一呼叫鏈有效。
"""

from __future__ import annotations

import contextvars
from contextvars import Token

_kml_body: contextvars.ContextVar[str | None] = contextvars.ContextVar("kml_import_full_body", default=None)


def push_kml_body(text: str) -> Token:
    """設定本請求完整 KML；回傳 token 供 reset_kml_body。"""
    return _kml_body.set(text)


def reset_kml_body(token: Token) -> None:
    _kml_body.reset(token)


def get_pending_kml_body() -> str | None:
    return _kml_body.get()
