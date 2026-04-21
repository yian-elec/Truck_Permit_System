"""
申請人（自然人）資料實體。

責任：封裝 `application.applicant_profiles` 對應之領域欄位與「基本資料完整性」規則之一部分。
規格 5.1 之 **ApplicantProfile.contact** 在 persistence 展開為 email、mobile、phone_*、address_* 等欄位（見 5.2 schema），
本實體直接對齊該表結構以便 Infra 映射；與 **CompanyProfile** 之必填判斷由 **ApplicantType** 與 **Application** 聚合協調。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class ApplicantProfile:
    """
    自然人申請人之聯絡與身分資料。

    責任：UC-APP-02 更新草稿時寫入；送件前檢查自然人必填欄位是否足夠。
    """

    application_id: UUID
    name: str
    id_no: str | None
    gender: str | None
    email: str | None
    mobile: str | None
    phone_area: str | None
    phone_no: str | None
    phone_ext: str | None
    address_county: str | None
    address_district: str | None
    address_detail: str | None
    created_at: datetime
    updated_at: datetime

    def has_meaningful_contact(self) -> bool:
        """是否至少有一種可聯絡方式（手機或 email）。"""
        em = (self.email or "").strip()
        mob = (self.mobile or "").strip()
        return bool(em or mob)

    def minimum_complete_for_natural_person(self) -> bool:
        """
        自然人送件所需之最低欄位是否齊備。

        責任：姓名、身分證號、至少一種聯絡方式；地址細節可依監理實務再擴充規則。
        """
        if not (self.name or "").strip():
            return False
        if not (self.id_no or "").strip():
            return False
        return self.has_meaningful_contact()
