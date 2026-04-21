"""
草稿與主檔／申請人資料更新（UC-APP-01、UC-APP-02）及同意條款。

責任：僅處理案件建立、PATCH 主檔與 profile、consent；不涵蓋車輛／附件／送件。
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.contexts.application.domain.entities import Application
from src.contexts.application.domain.value_objects import (
    ApplicantType,
    DeliveryMethod,
    PermitPeriod,
    ReasonType,
    SourceChannel,
    ensure_utc_aware,
)

from ..dtos import (
    ApplicationDetailDTO,
    CreateDraftApplicationInputDTO,
    CreateDraftApplicationOutputDTO,
    PatchApplicationInputDTO,
    PatchApplicationProfilesInputDTO,
)
from ..errors import ApplicationAppError
from ._application_no import generate_application_no
from ._checklist_template import default_checklist_items_for_heavy_truck_permit
from .application_mappers import application_to_detail_dto
from .application_service_context import ApplicationServiceContext, raise_domain_as_app


class DraftApplicationService:
    """UC-APP-01／UC-APP-02 與同意條款之專責服務。"""

    def __init__(self, ctx: ApplicationServiceContext) -> None:
        self._c = ctx

    def create_draft(
        self,
        dto: CreateDraftApplicationInputDTO,
        *,
        applicant_user_id: UUID | None,
    ) -> CreateDraftApplicationOutputDTO:
        now = datetime.now(timezone.utc)
        application_id = uuid4()
        application_no: str | None = None
        for _ in range(8):
            candidate = generate_application_no()
            if self._c.repo.get_by_application_no(candidate) is None:
                application_no = candidate
                break
        if application_no is None:
            raise ApplicationAppError("無法產生唯一案件編號，請稍後再試", details=None)

        period = PermitPeriod(
            start_at=ensure_utc_aware(dto.requested_start_at),
            end_at=ensure_utc_aware(dto.requested_end_at),
        )
        app = Application.open_draft(
            application_id=application_id,
            application_no=application_no,
            applicant_user_id=applicant_user_id,
            applicant_type=ApplicantType(dto.applicant_type),
            reason_type=ReasonType(dto.reason_type),
            reason_detail=dto.reason_detail,
            requested_period=period,
            delivery_method=DeliveryMethod(dto.delivery_method),
            source_channel=SourceChannel(dto.source_channel),
            now=now,
        )
        items = default_checklist_items_for_heavy_truck_permit()
        raise_domain_as_app(lambda: app.initialize_checklist(items, now=now))
        self._c.save(app)
        return CreateDraftApplicationOutputDTO(
            application_id=app.application_id,
            application_no=app.application_no,
            status=app.status.value,
        )

    def update_draft_application(
        self,
        application_id: UUID,
        *,
        patch: PatchApplicationInputDTO | None = None,
        profiles: PatchApplicationProfilesInputDTO | None = None,
        applicant_user_id: UUID | None,
    ) -> ApplicationDetailDTO:
        app = self._c.load(application_id)
        self._c.ensure_applicant(app, applicant_user_id)
        now = datetime.now(timezone.utc)
        if patch is not None and any(
            v is not None
            for v in (
                patch.reason_type,
                patch.reason_detail,
                patch.requested_start_at,
                patch.requested_end_at,
                patch.delivery_method,
            )
        ):
            self._c.apply_patch_core(app, patch, now)
        if profiles is not None:
            self._c.apply_profiles(app, profiles, now)
        self._c.save(app)
        views = self._c.read.list_attachment_summaries(application_id)
        return application_to_detail_dto(app, attachment_views=views)

    def record_consent(
        self,
        application_id: UUID,
        *,
        applicant_user_id: UUID | None,
    ) -> ApplicationDetailDTO:
        app = self._c.load(application_id)
        self._c.ensure_applicant(app, applicant_user_id)
        now = datetime.now(timezone.utc)
        raise_domain_as_app(lambda: app.record_consent_accepted(now=now))
        self._c.save(app)
        views = self._c.read.list_attachment_summaries(application_id)
        return application_to_detail_dto(app, attachment_views=views)
