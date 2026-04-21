"""
申請公司資料實體。

責任：封裝 `application.company_profiles` 之領域欄位，對應規格 5.1 **CompanyProfile**
（company_name、tax_id、principal_name、contact_name 等）。當 **ApplicantType** 為法人／公司時，
**Application** 聚合於送件前檢查應驗證 `minimum_complete_for_company()` 所定義之核心欄位。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class CompanyProfile:
    """
    公司／法人申請主體之資料。

    責任：與 ApplicantProfile 分離，避免將公司欄位塞入自然人模型；由 Application 依 applicant_type 決定送件檢查策略。
    """

    application_id: UUID
    company_name: str | None
    tax_id: str | None
    principal_name: str | None
    contact_name: str | None
    contact_mobile: str | None
    contact_phone: str | None
    address: str | None
    created_at: datetime
    updated_at: datetime

    def minimum_complete_for_company(self) -> bool:
        """
        公司申請送件所需之最低欄位是否齊備。

        責任：公司名稱與統一編號為核心識別；聯絡人與電話可依產品再收緊。
        """
        cn = (self.company_name or "").strip()
        tid = (self.tax_id or "").strip()
        if not cn or not tid:
            return False
        contact_ok = bool(
            (self.contact_mobile or "").strip() or (self.contact_phone or "").strip()
        )
        return contact_ok
