"""
頁面區塊代碼（Value Object）。

責任：以穩定、可版本化的字串識別「Page Model 中的一個邏輯區塊」；
App 層可將此代碼對應到實際從各下游 context 查回並填入的 payload slot。
本 VO 不引用其他 context 的型別，僅承載本 BC 內部契約識別。
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from ..errors import InvalidPageModelCompositionError

_SLUG_RE = re.compile(r"^[a-z][a-z0-9]*(\.[a-z][a-z0-9_]*)+$")
_MAX_LEN = 128


@dataclass(frozen=True, order=True)
class PageSectionCode:
    """
    區塊代碼（階層式 slug，例如 `applicant.editor.case_core`）。

    責任：
    - 限制字元集與長度，避免任意字串污染目錄
    - 作為 `PageModelSectionSpec` 與前置依賴關聯的主鍵語意
    """

    value: str

    def __post_init__(self) -> None:
        v = self.value.strip()
        if not v or len(v) > _MAX_LEN:
            raise InvalidPageModelCompositionError(
                f"PageSectionCode must be 1..{_MAX_LEN} non-empty chars"
            )
        if not _SLUG_RE.fullmatch(v):
            raise InvalidPageModelCompositionError(
                "PageSectionCode must match dotted slug pattern "
                "(e.g. applicant.home.service_overview)"
            )
        object.__setattr__(self, "value", v)

    def __str__(self) -> str:
        return self.value
