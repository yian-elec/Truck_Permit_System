"""
申請人類型（Value Object）。

責任：區分自然人／法人或其他申請主體，供 ApplicantProfile／CompanyProfile 何者必填之領域規則使用。
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from ..errors import InvalidDomainValueError


class ApplicantTypeCode(StrEnum):
    """與 applicant_type varchar(30) 對齊之封閉集合（可擴充）。"""

    NATURAL_PERSON = "natural_person"
    COMPANY = "company"
    GOVERNMENT = "government"
    OTHER = "other"


@dataclass(frozen=True)
class ApplicantType:
    """
    案件上之申請人類別。

    責任：由 Aggregate 持有；送件前基本資料完整性可依此決定應校驗自然人或公司欄位。
    """

    value: str

    def __post_init__(self) -> None:
        allowed = {c.value for c in ApplicantTypeCode}
        v = (self.value or "").strip().lower()
        if v not in allowed:
            raise InvalidDomainValueError(
                f"Invalid applicant_type: {self.value!r}; expected one of {sorted(allowed)}",
            )
        object.__setattr__(self, "value", v)

    def is_company(self) -> bool:
        return self.value == ApplicantTypeCode.COMPANY.value

    def is_natural_person(self) -> bool:
        return self.value == ApplicantTypeCode.NATURAL_PERSON.value
