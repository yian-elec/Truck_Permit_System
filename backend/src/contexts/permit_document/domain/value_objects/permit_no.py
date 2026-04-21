"""
PermitNo — 許可證字號值物件。

責任：封裝 `permit.permits.permit_no`（varchar(30) unique）之格式與不變條件，
確保進入 Permit 聚合的字號非空、長度與字元集符合儲存層約束；實際編碼規則（流水號／前綴）
由 App 層產生後傳入，Domain 僅做驗證與承載。
"""

from __future__ import annotations

from dataclasses import dataclass

from src.contexts.permit_document.domain.errors import InvalidPermitValueError

_MAX_LEN = 30


@dataclass(frozen=True)
class PermitNo:
    """
    許可證編號（不可變字串值物件）。

    責任：持有已正規化（strip）之字號，並在建立時驗證長度 ≤ 30、不可為空。
    """

    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not normalized:
            raise InvalidPermitValueError("PermitNo must not be empty")
        if len(normalized) > _MAX_LEN:
            raise InvalidPermitValueError(
                f"PermitNo exceeds max length {_MAX_LEN}: {len(normalized)}"
            )
        object.__setattr__(self, "value", normalized)
