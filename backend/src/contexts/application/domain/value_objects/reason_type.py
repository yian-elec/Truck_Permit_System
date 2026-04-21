"""
申請事由類型（Value Object）。

責任：對應 reason_type varchar(50)；事由細節文字置於 Aggregate 之 reason_detail（可為 null）。
"""

from __future__ import annotations

from dataclasses import dataclass

from ..errors import InvalidDomainValueError


@dataclass(frozen=True)
class ReasonType:
    """
    申請事由分類代碼。

    責任：長度與非空校驗；實際列舉值由監理法規／產品設定決定，Domain 僅防呆格式。
    """

    value: str

    def __post_init__(self) -> None:
        v = (self.value or "").strip()
        if not v or len(v) > 50:
            raise InvalidDomainValueError(
                "ReasonType must be non-empty and at most 50 characters",
            )
        object.__setattr__(self, "value", v)
