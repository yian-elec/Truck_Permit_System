"""
Permit_Document 應用層整合測試 — 共用 fixture。

隔離策略：
- **permit** schema 由父層 `permit_postgres_env` 每次重建並 seed；
- 整合測試 DB 可能僅含 **permit** 表，故 **UC-PERMIT-01** 前置以符合 **PermitIssuanceLoadPort**
  之 stub 注入，仍走真實 **PermitCommandApplicationService** 與 Repository；
- **UC-PERMIT-03** 僅依賴 **permit.*** seed，使用預設 **PermitIssuanceContextReader** 無妨（查詢不觸發 issuance）。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest

from src.contexts.permit_document.app.errors import PermitNotFoundAppError
from src.contexts.permit_document.app.services.integrations import PermitIssuanceSnapshot

pytestmark = pytest.mark.integration

SEED_PERMIT_ID = UUID("bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbb01")
SEED_APPLICATION_ID = UUID("11111111-1111-4111-8111-111111111101")
SEED_DOCUMENT_ID = UUID("dddddddd-dddd-4ddd-8ddd-dddddddddd01")
SEED_FILE_ID = UUID("eeeeeeee-eeee-4eee-8eee-eeeeeeeeee01")


@dataclass
class StubPermitIssuanceReader:
    """測試用：依 application_id 對照 **PermitIssuanceSnapshot**（不讀其他 context 表）。"""

    snapshots: dict[UUID, PermitIssuanceSnapshot]

    def load(self, application_id: UUID) -> PermitIssuanceSnapshot:
        snap = self.snapshots.get(application_id)
        if snap is None:
            raise PermitNotFoundAppError("申請案件不存在", {"application_id": str(application_id)})
        return snap


def _std_period() -> tuple[datetime, datetime]:
    start = datetime(2026, 6, 1, tzinfo=timezone.utc)
    end = datetime(2026, 6, 30, 23, 59, 59, tzinfo=timezone.utc)
    return start, end


def make_approved_snapshot(
    application_id: UUID,
    *,
    application_no: str = "INTAPP-001",
    selected_candidate_id: UUID | None = None,
) -> PermitIssuanceSnapshot:
    start, end = _std_period()
    cid = selected_candidate_id if selected_candidate_id is not None else uuid4()
    return PermitIssuanceSnapshot(
        application_id=application_id,
        application_approved=True,
        approved_start_at=start,
        approved_end_at=end,
        selected_candidate_id=cid,
        override_id=None,
        application_no=application_no,
    )


def make_submitted_snapshot(application_id: UUID) -> PermitIssuanceSnapshot:
    start, end = _std_period()
    return PermitIssuanceSnapshot(
        application_id=application_id,
        application_approved=False,
        approved_start_at=start,
        approved_end_at=end,
        selected_candidate_id=uuid4(),
        override_id=None,
        application_no="SUB-001",
    )


def make_approved_without_route_snapshot(application_id: UUID) -> PermitIssuanceSnapshot:
    start, end = _std_period()
    return PermitIssuanceSnapshot(
        application_id=application_id,
        application_approved=True,
        approved_start_at=start,
        approved_end_at=end,
        selected_candidate_id=None,
        override_id=None,
        application_no="NOROUTE-01",
    )


@pytest.fixture
def permit_application_services(permit_postgres_env: None):
    """預設組合（查詢用例不需 stub issuance）。"""
    from src.contexts.permit_document.app.services import (
        PermitCommandApplicationService,
        PermitQueryApplicationService,
        PermitServiceContext,
        build_default_permit_service_context_dependencies,
    )

    auth, storage = build_default_permit_service_context_dependencies()
    ctx = PermitServiceContext(authorization=auth, object_storage=storage)
    return (
        PermitCommandApplicationService(ctx),
        PermitQueryApplicationService(ctx),
        ctx,
    )


@pytest.fixture
def permit_application_services_with_stub_issuance(permit_postgres_env: None):
    """回傳 `build(reader)` → `(cmd, qry, ctx)`，供 UC-PERMIT-01 等需控制 issuance 快照之測試。"""

    from src.contexts.permit_document.app.services import (
        PermitCommandApplicationService,
        PermitQueryApplicationService,
        PermitServiceContext,
        build_default_permit_service_context_dependencies,
    )

    auth, storage = build_default_permit_service_context_dependencies()

    def build(reader: StubPermitIssuanceReader):
        ctx = PermitServiceContext(
            issuance_reader=reader,
            authorization=auth,
            object_storage=storage,
        )
        return (
            PermitCommandApplicationService(ctx),
            PermitQueryApplicationService(ctx),
            ctx,
        )

    return build
