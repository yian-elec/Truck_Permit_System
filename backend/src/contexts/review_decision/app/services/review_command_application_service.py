"""
審查寫入流程用例服務（UC-REV-01、03、04、05、分派、評論）。

責任：
- 呼叫領域工廠建立決策／補件／任務，經 mappers 寫入 review schema；
- 協調 Application 聚合狀態轉移並 `save`；
- 發布整合事件與通知。

交易說明（初版）：
- 各 Repository 內部各自 `get_session()` 提交；**跨表寫入非單一 DB transaction**。
  若需強一致，後續應導入工作單元（共享 Session）或單一 stored procedure。
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.contexts.application.app.errors import ApplicationNotFoundAppError

from src.contexts.application.domain.entities import Application

from src.contexts.review_decision.app.dtos import (
    AddCommentInputDTO,
    AddCommentOutputDTO,
    ApproveApplicationInputDTO,
    ApproveApplicationOutputDTO,
    AssignReviewTaskInputDTO,
    AssignReviewTaskOutputDTO,
    CreateReviewTaskInputDTO,
    CreateReviewTaskOutputDTO,
    RejectApplicationInputDTO,
    RejectApplicationOutputDTO,
    RequestSupplementInputDTO,
    RequestSupplementOutputDTO,
    SupplementItemInputDTO,
)
from src.contexts.review_decision.app.errors import (
    ReviewConflictAppError,
    ReviewNotFoundAppError,
    ReviewValidationAppError,
    raise_application_domain_as_app,
    raise_review_domain_as_app,
)
from src.contexts.review_decision.app.services.ports.outbound import (
    supplement_notification_payload,
)
from src.contexts.review_decision.app.services.review_mappers import (
    domain_review_decision_to_orm,
    domain_review_task_to_orm,
    domain_supplement_request_to_orm,
    orm_review_task_to_domain,
    supplement_item_vo_to_orm,
)
from src.contexts.review_decision.app.services.review_route_readiness import (
    build_approval_route_readiness,
)
from src.contexts.review_decision.app.services.review_service_context import (
    ReviewServiceContext,
)
from src.contexts.review_decision.domain.entities import (
    ReviewDecision,
    ReviewTask,
    SupplementRequest,
)
from src.contexts.review_decision.domain.value_objects import (
    ApprovedPeriod,
    CommentType,
    DecisionType,
    ReviewComment,
    ReviewStage,
    SupplementItem,
    SupplementRequiredAction,
)
from src.contexts.review_decision.infra.schema.review_comments import ReviewComments


class ReviewCommandApplicationService:
    """審查命令面用例實作。"""

    def __init__(self, ctx: ReviewServiceContext) -> None:
        self._c = ctx

    # ------------------------------------------------------------------
    # UC-REV-01
    # ------------------------------------------------------------------

    def create_pending_review_task(self, inp: CreateReviewTaskInputDTO) -> CreateReviewTaskOutputDTO:
        """
        建立待審任務（對應 ApplicationSubmitted 等事件後續處理）。

        責任：產生 **PENDING** 任務列；分派由 `assign_task_for_application` 完成。
        若該案件已有未關閉之任務則回傳既有列（送件／事件重試時冪等）。
        """
        existing_open = self._c.tasks.find_open_task_for_application(inp.application_id)
        if existing_open is not None:
            return CreateReviewTaskOutputDTO(
                review_task_id=existing_open.review_task_id,
                application_id=existing_open.application_id,
                stage=existing_open.stage,
                status=existing_open.status,
            )

        try:
            stage = ReviewStage(inp.stage)
        except ValueError as e:
            raise ReviewValidationAppError(f"不支援的審查階段: {inp.stage!r}") from e

        now = datetime.now(timezone.utc)
        task_id = uuid4()
        task = ReviewTask.open_for_application(
            review_task_id=task_id,
            application_id=inp.application_id,
            stage=stage,
            due_at=inp.due_at,
            now=now,
        )
        self._c.tasks.add(domain_review_task_to_orm(task))
        return CreateReviewTaskOutputDTO(
            review_task_id=task.review_task_id,
            application_id=task.application_id,
            stage=task.stage.value,
            status=task.status.value,
        )

    def assign_task_for_application(
        self,
        application_id: UUID,
        inp: AssignReviewTaskInputDTO,
    ) -> AssignReviewTaskOutputDTO:
        """將案件之開放審查任務分派給承辦（可能伴隨 PENDING→IN_REVIEW）。"""
        row = self._c.tasks.find_open_task_for_application(application_id)
        if row is None:
            raise ReviewNotFoundAppError("此案件沒有開放中的審查任務")

        now = datetime.now(timezone.utc)
        domain_task = orm_review_task_to_domain(row)
        raise_review_domain_as_app(
            lambda: domain_task.assign(inp.assignee_user_id, now),
        )
        updated = self._c.tasks.update_task_row(domain_review_task_to_orm(domain_task))
        if updated is None:
            raise ReviewConflictAppError("無法更新審查任務，請重試")

        self._c.notifications.notify(
            channel="task_assigned",
            payload={
                "application_id": str(application_id),
                "review_task_id": str(domain_task.review_task_id),
                "assignee_user_id": str(inp.assignee_user_id),
            },
        )
        return AssignReviewTaskOutputDTO(
            review_task_id=domain_task.review_task_id,
            assignee_user_id=inp.assignee_user_id,
            status=domain_task.status.value,
        )

    # ------------------------------------------------------------------
    # UC-REV-03
    # ------------------------------------------------------------------

    def request_supplement(
        self,
        application_id: UUID,
        inp: RequestSupplementInputDTO,
        *,
        officer_user_id: UUID,
    ) -> RequestSupplementOutputDTO:
        """發出補件：寫入 supplement + decision(supplement) + 評論 + 更新案件狀態。"""
        prior = self._prior_decision_types(application_id)
        now = datetime.now(timezone.utc)
        decision_id = uuid4()
        supplement_request_id = uuid4()

        items_vo: tuple[SupplementItem, ...] = tuple(
            self._parse_supplement_item_dto(it) for it in inp.items
        )

        sup = raise_review_domain_as_app(
            lambda: SupplementRequest.issue(
                supplement_request_id=supplement_request_id,
                application_id=application_id,
                requested_by=officer_user_id,
                deadline_at=inp.deadline_at,
                message=inp.message,
                items=items_vo,
                now=now,
            ),
        )

        decision = raise_review_domain_as_app(
            lambda: ReviewDecision.record_supplement(
                decision_id=decision_id,
                application_id=application_id,
                reason=inp.decision_reason,
                decided_by=officer_user_id,
                decided_at=now,
                created_at=now,
                prior_decision_types_in_order=prior,
            ),
        )

        self._c.decisions.add(domain_review_decision_to_orm(decision))
        self._c.supplements.add_request(domain_supplement_request_to_orm(sup))
        for it in sup.items:
            self._c.supplements.add_item(
                supplement_item_vo_to_orm(
                    supplement_item_id=uuid4(),
                    supplement_request_id=sup.supplement_request_id,
                    item=it,
                    created_at=now,
                ),
            )

        app = self._load_application(application_id)
        raise_application_domain_as_app(
            lambda: app.enter_supplement_required(
                now=now,
                changed_by=officer_user_id,
                reason=inp.decision_reason,
                history_id=uuid4(),
            ),
        )
        self._c.applications.save(app)

        comment = raise_review_domain_as_app(
            lambda: ReviewComment(
                comment_type=CommentType.SUPPLEMENT,
                content=inp.message,
                author_user_id=officer_user_id,
            ),
        )
        self._c.comments.add(
            ReviewComments(
                comment_id=uuid4(),
                application_id=application_id,
                comment_type=comment.comment_type.value,
                content=comment.content,
                created_by=comment.author_user_id,
            ),
        )

        self._c.notifications.notify(
            channel="supplement_required",
            payload=supplement_notification_payload(
                application_id=application_id,
                supplement_request_id=supplement_request_id,
                message=inp.message,
            ),
        )

        return RequestSupplementOutputDTO(
            supplement_request_id=supplement_request_id,
            decision_id=decision_id,
            application_status=app.status.value,
        )

    # ------------------------------------------------------------------
    # UC-REV-04 / UC-REV-05
    # ------------------------------------------------------------------

    def approve_application(
        self,
        application_id: UUID,
        inp: ApproveApplicationInputDTO,
        *,
        officer_user_id: UUID,
    ) -> ApproveApplicationOutputDTO:
        """核准：校驗路由就緒、寫入決策、案件 approved、關閉審查任務、發布事件。"""
        plan = self._c.route_plans.get_latest_route_plan(application_id)
        readiness = build_approval_route_readiness(
            plan,
            selected_candidate_id=inp.selected_candidate_id,
            override_id=inp.override_id,
        )
        prior = self._prior_decision_types(application_id)
        now = datetime.now(timezone.utc)
        decision_id = uuid4()
        period = ApprovedPeriod(
            start_at=inp.approved_start_at,
            end_at=inp.approved_end_at,
        )

        decision = raise_review_domain_as_app(
            lambda: ReviewDecision.record_approve(
                decision_id=decision_id,
                application_id=application_id,
                readiness=readiness,
                approved_period=period,
                reason=inp.reason,
                decided_by=officer_user_id,
                decided_at=now,
                created_at=now,
                selected_candidate_id=inp.selected_candidate_id,
                override_id=inp.override_id,
                prior_decision_types_in_order=prior,
            ),
        )
        self._c.decisions.add(domain_review_decision_to_orm(decision))

        app = self._load_application(application_id)
        raise_application_domain_as_app(
            lambda: app.approve_by_officer(
                now=now,
                changed_by=officer_user_id,
                reason=inp.reason,
                history_id=uuid4(),
            ),
        )
        self._c.applications.save(app)

        self._close_open_review_task(application_id, now)

        self._c.events.publish(
            "ApplicationApproved",
            {
                "application_id": str(application_id),
                "decision_id": str(decision_id),
                "decided_at": decision.decided_at.isoformat(),
            },
        )

        return ApproveApplicationOutputDTO(
            decision_id=decision_id,
            application_status=app.status.value,
        )

    def reject_application(
        self,
        application_id: UUID,
        inp: RejectApplicationInputDTO,
        *,
        officer_user_id: UUID,
    ) -> RejectApplicationOutputDTO:
        """駁回：寫入決策、案件 rejected、關閉任務、通知。"""
        prior = self._prior_decision_types(application_id)
        now = datetime.now(timezone.utc)
        decision_id = uuid4()

        decision = raise_review_domain_as_app(
            lambda: ReviewDecision.record_reject(
                decision_id=decision_id,
                application_id=application_id,
                reason=inp.reason,
                decided_by=officer_user_id,
                decided_at=now,
                created_at=now,
                prior_decision_types_in_order=prior,
            ),
        )
        self._c.decisions.add(domain_review_decision_to_orm(decision))

        app = self._load_application(application_id)
        raise_application_domain_as_app(
            lambda: app.reject_by_officer(
                now=now,
                changed_by=officer_user_id,
                reason=inp.reason,
                history_id=uuid4(),
            ),
        )
        self._c.applications.save(app)

        self._close_open_review_task(application_id, now)

        self._c.notifications.notify(
            channel="application_rejected",
            payload={
                "application_id": str(application_id),
                "decision_id": str(decision_id),
                "reason": inp.reason,
            },
        )

        return RejectApplicationOutputDTO(
            decision_id=decision_id,
            application_status=app.status.value,
        )

    # ------------------------------------------------------------------
    # UC-REV-06
    # ------------------------------------------------------------------

    def add_comment(
        self,
        application_id: UUID,
        inp: AddCommentInputDTO,
        *,
        author_user_id: UUID,
    ) -> AddCommentOutputDTO:
        """
        新增評論。

        責任：領域校驗內容與類型；授權（是否可寫 internal）應由 API 層與政策服務把關。
        """
        try:
            ctype = CommentType(inp.comment_type)
        except ValueError as e:
            raise ReviewValidationAppError(
                f"不支援的評論類型: {inp.comment_type!r}",
            ) from e

        comment = raise_review_domain_as_app(
            lambda: ReviewComment(
                comment_type=ctype,
                content=inp.content,
                author_user_id=author_user_id,
            ),
        )
        cid = uuid4()
        saved = self._c.comments.add(
            ReviewComments(
                comment_id=cid,
                application_id=application_id,
                comment_type=comment.comment_type.value,
                content=comment.content,
                created_by=comment.author_user_id,
            ),
        )
        return AddCommentOutputDTO(
            comment_id=saved.comment_id,
            application_id=application_id,
            comment_type=comment.comment_type.value,
            created_at=saved.created_at,
        )

    # ------------------------------------------------------------------
    # 內部輔助
    # ------------------------------------------------------------------

    def _load_application(self, application_id: UUID) -> Application:
        app = self._c.applications.get_by_id(application_id)
        if app is None:
            raise ApplicationNotFoundAppError("申請案件不存在", {"application_id": str(application_id)})
        return app

    def _prior_decision_types(self, application_id: UUID) -> tuple[DecisionType, ...]:
        rows = self._c.decisions.list_by_application_id(application_id)
        out: list[DecisionType] = []
        for r in rows:
            try:
                out.append(DecisionType(r.decision_type))
            except ValueError as e:
                raise ReviewValidationAppError(
                    f"資料庫決策類型無法辨識: {r.decision_type!r}",
                ) from e
        return tuple(out)

    def _parse_supplement_item_dto(self, it: SupplementItemInputDTO) -> SupplementItem:
        try:
            action = SupplementRequiredAction(it.required_action)
        except ValueError as e:
            raise ReviewValidationAppError(
                f"不支援的補件動作: {it.required_action!r}",
            ) from e
        return raise_review_domain_as_app(
            lambda: SupplementItem(
                item_code=it.item_code,
                item_name=it.item_name,
                required_action=action,
                note=it.note,
            ),
        )

    def _close_open_review_task(self, application_id: UUID, now: datetime) -> None:
        row = self._c.tasks.find_open_task_for_application(application_id)
        if row is None:
            return
        domain_task = orm_review_task_to_domain(row)
        raise_review_domain_as_app(lambda: domain_task.close(now))
        self._c.tasks.update_task_row(domain_review_task_to_orm(domain_task))
