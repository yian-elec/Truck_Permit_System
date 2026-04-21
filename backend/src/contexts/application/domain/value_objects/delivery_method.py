"""
送件／領件方式（Value Object）。

責任：封裝 application.applications.delivery_method 之合法值集合，
與 UI／表單選項對齊並防止任意字串。
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from ..errors import InvalidDomainValueError


class DeliveryMethodCode(StrEnum):
    """領域預設之送達方式代碼；實務可隨產品擴充。"""

    ONLINE = "online"
    MAIL = "mail"
    COUNTER = "counter"
    OTHER = "other"


@dataclass(frozen=True)
class DeliveryMethod:
    """
    申請人選擇之許可證或通知送達方式。

    責任：與 persistence 之 varchar(30) 對齊；未知代碼拒絕以維持封閉列舉語意。
    """

    value: str

    def __post_init__(self) -> None:
        allowed = {c.value for c in DeliveryMethodCode}
        v = (self.value or "").strip().lower()
        if v not in allowed:
            raise InvalidDomainValueError(
                f"Invalid delivery_method: {self.value!r}; expected one of {sorted(allowed)}",
            )
        object.__setattr__(self, "value", v)
