"""
稽核用 JSON 快照（Value Object）。

責任：包裝 ops.audit_logs.before_json / after_json 的結構化內容；
領域不解析業務欄位，僅保證型別為可巢狀的 mapping／list 結構（jsonb 語意）。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..errors import InvalidDomainValueError


def _is_json_like(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, (str, int, float, bool)):
        return True
    if isinstance(value, list):
        return all(_is_json_like(v) for v in value)
    if isinstance(value, dict):
        return all(isinstance(k, str) and _is_json_like(v) for k, v in value.items())
    return False


@dataclass(frozen=True)
class AuditJsonSnapshot:
    """
    稽核前／後狀態快照；允許 None 表示未提供。

    用途：UC-OPS-03 記錄關鍵交易 before／after，供 review／admin 查詢。
    """

    raw: dict[str, Any] | list[Any] | None

    def __post_init__(self) -> None:
        if self.raw is not None and not _is_json_like(self.raw):
            raise InvalidDomainValueError("AuditJsonSnapshot must be JSON-like dict/list or None")
