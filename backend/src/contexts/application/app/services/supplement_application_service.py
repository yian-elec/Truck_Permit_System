"""
補件回覆（UC-APP-07）。

責任：協作埠驗證、可編欄位更新、狀態轉 resubmitted；補件單列表待審查 context 接入。
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from ..dtos import SupplementRequestItemDTO, SupplementResponseInputDTO, SupplementResponseOutputDTO
from ..errors import to_app_error
from .application_service_context import ApplicationServiceContext, raise_domain_as_app


class SupplementApplicationService:
    """UC-APP-07 專責服務。"""

    def __init__(self, ctx: ApplicationServiceContext) -> None:
        self._c = ctx

    def list_supplement_requests(
        self,
        application_id: UUID,
        *,
        applicant_user_id: UUID | None,
    ) -> list[SupplementRequestItemDTO]:
        """
        列出補件要求。

        責任：經 SupplementWorkflowPort 讀取 review.supplement_requests 並組成通知列表。
        """
        app = self._c.load(application_id)
        self._c.ensure_applicant(app, applicant_user_id)
        return self._c.supplement.list_supplement_notifications(application_id)

    def supplement_response(
        self,
        application_id: UUID,
        dto: SupplementResponseInputDTO,
        *,
        applicant_user_id: UUID | None,
    ) -> SupplementResponseOutputDTO:
        app = self._c.load(application_id)
        self._c.ensure_applicant(app, applicant_user_id)
        try:
            self._c.supplement.assert_may_finalize_supplement_response(application_id)
        except Exception as e:
            raise to_app_error(e) from e
        now = datetime.now(timezone.utc)
        if dto.patch is not None:
            self._c.apply_patch_core(app, dto.patch, now)
        if dto.profiles is not None:
            self._c.apply_profiles(app, dto.profiles, now)
        raise_domain_as_app(
            lambda: app.finalize_supplement_response(
                now=now,
                changed_by=applicant_user_id,
                history_id=uuid4(),
            )
        )
        self._c.save(app)
        self._c.events.publish(
            "SupplementResponseReceived",
            {"application_id": str(application_id)},
        )
        return SupplementResponseOutputDTO(
            application_id=app.application_id,
            status=app.status.value,
        )
