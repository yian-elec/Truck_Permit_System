"""
案件來源通路（Value Object）。

責任：標記申請來自網路、臨櫃、API 等，供稽核與報表；與 source_channel varchar(30) 對齊。
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from ..errors import InvalidDomainValueError


class SourceChannelCode(StrEnum):
    """預設來源通路；可隨通路擴充。"""

    WEB = "web"
    MOBILE = "mobile"
    COUNTER = "counter"
    API = "api"
    IMPORT = "import"


@dataclass(frozen=True)
class SourceChannel:
    """
    建立案件時之來源通路代碼。

    責任：封閉驗證，避免寫入未登記之 channel 字串。
    """

    value: str

    def __post_init__(self) -> None:
        allowed = {c.value for c in SourceChannelCode}
        v = (self.value or "").strip().lower()
        if v not in allowed:
            raise InvalidDomainValueError(
                f"Invalid source_channel: {self.value!r}; expected one of {sorted(allowed)}",
            )
        object.__setattr__(self, "value", v)
