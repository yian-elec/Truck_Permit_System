"""
車牌號碼（Value Object）。

責任：集中車牌字串之領域約束（非空、長度、允許字元），供 Vehicle 實體與 UC-APP-03 重用。
實際格式（台灣車牌規則）若需更嚴格，可僅擴充 __post_init__ 之驗證，無需改動實體欄位型別。
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from ..errors import InvalidDomainValueError

# 允許英數、連字號；可依監理機關格式再縮緊
_PLATE_PATTERN = re.compile(r"^[A-Za-z0-9\-]{2,20}$")

# 常見 Unicode 橫線（en dash、em dash、減號等）統一成 ASCII hyphen
_DASH_CHARS = (
    "\u2013",
    "\u2014",
    "\u2212",
    "\u2010",
    "\u2011",
    "\ufe63",
    "\uff0d",
)


def _normalize_plate_input(s: str) -> str:
    """NFKC、大寫、橫線統一、去除空白（與前台 normalizeVehiclePlateInput 對齊）。"""
    t = unicodedata.normalize("NFKC", (s or "").strip()).upper()
    for ch in _DASH_CHARS:
        t = t.replace(ch, "-")
    t = "".join(t.split())
    return t


@dataclass(frozen=True)
class VehiclePlate:
    """
    領域中的車牌識別碼。

    責任：與 application.vehicles.plate_no／trailer_plate_no 對齊之語意封裝。
    """

    value: str

    def __post_init__(self) -> None:
        raw = _normalize_plate_input(self.value)
        if not _PLATE_PATTERN.match(raw):
            raise InvalidDomainValueError(
                "Vehicle plate must be 2–20 chars of letters, digits, or hyphen",
            )
        object.__setattr__(self, "value", raw)
