"""
送件前檢查與送件（UC-APP-05、UC-APP-06）。

責任：評估 readiness、狀態轉 submitted 與事件發布。路線需求／自動規劃由審查端處理，送件不查 routing.route_requests。
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from shared.core.logger.logger import logger

from ..dtos import SubmissionCheckResultDTO, SubmitApplicationOutputDTO
from .application_service_context import ApplicationServiceContext, raise_domain_as_app


class SubmissionApplicationService:
    """UC-APP-05／UC-APP-06 專責服務。"""

    def __init__(self, ctx: ApplicationServiceContext) -> None:
        self._c = ctx

    def submission_check(
        self,
        application_id: UUID,
        *,
        applicant_user_id: UUID | None,
    ) -> SubmissionCheckResultDTO:
        app = self._c.load(application_id)
        self._c.ensure_applicant(app, applicant_user_id)
        readiness = app.evaluate_submission_readiness(
            max_permit_calendar_days=self._c.max_permit_calendar_days,
        )
        return SubmissionCheckResultDTO(
            can_submit=readiness.can_submit,
            missing_reason_codes=list(readiness.missing_reason_codes),
        )

    def submit_application(
        self,
        application_id: UUID,
        *,
        applicant_user_id: UUID | None,
        changed_by: UUID | None = None,
    ) -> SubmitApplicationOutputDTO:
        app = self._c.load(application_id)
        self._c.ensure_applicant(app, applicant_user_id)
        now = datetime.now(timezone.utc)
        actor = changed_by if changed_by is not None else applicant_user_id
        raise_domain_as_app(
            lambda: app.submit(
                now=now,
                changed_by=actor,
                max_permit_calendar_days=self._c.max_permit_calendar_days,
                history_id=uuid4(),
            )
        )
        self._c.save(app)
        self._c.events.publish(
            "ApplicationSubmitted",
            {
                "application_id": str(application_id),
                "application_no": app.application_no,
                "submitted_at": app.submitted_at.isoformat() if app.submitted_at else None,
            },
        )
        self._ensure_pending_review_task(application_id)

        assert app.submitted_at is not None
        return SubmitApplicationOutputDTO(
            application_no=app.application_no,
            status=app.status.value,
            submitted_at=app.submitted_at,
        )

    @staticmethod
    def _ensure_pending_review_task(application_id: UUID) -> None:
        """
        送件後於 review_tasks 建立待審列，供後台「待審任務」顯示。

        初版事件匯流使用 Noop publisher，故在此同步呼叫審查用例；失敗不阻擋送件（已持久化）。
        """
        try:
            from src.contexts.review_decision.api.dependencies import get_review_api_bundle
            from src.contexts.review_decision.app.dtos import CreateReviewTaskInputDTO

            bundle = get_review_api_bundle()
            bundle.r_cmd.create_pending_review_task(CreateReviewTaskInputDTO(application_id=application_id))
        except Exception as exc:
            logger.api_error(
                "ReviewTaskSyncFailed",
                str(exc),
                application_id=str(application_id),
            )
