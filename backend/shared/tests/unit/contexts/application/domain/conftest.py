"""
Application Domain 測試共用 fixture 與工廠函式。

隔離：僅使用標準庫與 `src.contexts.application.domain`，無 DB／檔案／網路。
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from src.contexts.application.domain.entities import (
    ApplicantProfile,
    Application,
    ChecklistItem,
    CompanyProfile,
)
from src.contexts.application.domain.value_objects import (
    ApplicantType,
    ApplicantTypeCode,
    DeliveryMethod,
    DeliveryMethodCode,
    PermitPeriod,
    ReasonType,
    SourceChannel,
    SourceChannelCode,
)

pytestmark = pytest.mark.unit

UTC = timezone.utc


def fixed_now() -> datetime:
    """固定牆上時鐘，避免測試依賴真實時間。"""
    return datetime(2026, 4, 7, 12, 0, 0, tzinfo=UTC)


def default_period(*, days: int = 7) -> PermitPeriod:
    """建立合法許可期間（曆日數 = days）。"""
    start = datetime(2026, 5, 1, 0, 0, 0, tzinfo=UTC)
    end = start + timedelta(days=days - 1)
    end = end.replace(hour=23, minute=59, second=59)
    return PermitPeriod(start_at=start, end_at=end)


@pytest.fixture
def now() -> datetime:
    return fixed_now()


@pytest.fixture
def application_id() -> UUID:
    return uuid4()


@pytest.fixture
def applicant_user_id() -> UUID:
    return uuid4()


def open_minimal_draft(
    *,
    application_id: UUID,
    applicant_user_id: UUID | None,
    now: datetime,
    applicant_type: ApplicantType | None = None,
) -> Application:
    """最小可送件路徑之草稿（自然人）；不含 profile／車／附件／consent。"""
    at = applicant_type or ApplicantType(ApplicantTypeCode.NATURAL_PERSON.value)
    return Application.open_draft(
        application_id=application_id,
        application_no="APP-2026-000001",
        applicant_user_id=applicant_user_id,
        applicant_type=at,
        reason_type=ReasonType("construction_transport"),
        reason_detail=None,
        requested_period=default_period(days=7),
        delivery_method=DeliveryMethod(DeliveryMethodCode.ONLINE.value),
        source_channel=SourceChannel(SourceChannelCode.WEB.value),
        now=now,
    )


def natural_applicant_profile(*, application_id: UUID, now: datetime) -> ApplicantProfile:
    return ApplicantProfile(
        application_id=application_id,
        name="王小明",
        id_no="A123456789",
        gender="male",
        email="ming@example.com",
        mobile="0912000111",
        phone_area=None,
        phone_no=None,
        phone_ext=None,
        address_county=None,
        address_district=None,
        address_detail=None,
        created_at=now,
        updated_at=now,
    )


def company_profile_complete(*, application_id: UUID, now: datetime) -> CompanyProfile:
    return CompanyProfile(
        application_id=application_id,
        company_name="測試物流股份有限公司",
        tax_id="12345678",
        principal_name="負責人",
        contact_name="聯絡人",
        contact_mobile="0222333444",
        contact_phone=None,
        address="台北市",
        created_at=now,
        updated_at=now,
    )


def required_checklist_item(code: str, name: str = "doc") -> ChecklistItem:
    return ChecklistItem.seed(
        item_code=code,
        item_name=name,
        is_required=True,
        source="service_template",
    )
