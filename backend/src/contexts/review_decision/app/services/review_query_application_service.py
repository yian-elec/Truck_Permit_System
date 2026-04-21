"""
審查唯讀用例服務（UC-REV-02、任務列表、儀表板、決策／評論／稽核軌跡）。

責任：組裝跨 context 讀模型；不修改聚合狀態。
"""

from __future__ import annotations

from uuid import UUID

from src.contexts.review_decision.app.dtos import (
    AuditTrailEntryDTO,
    CommentSummaryDTO,
    DecisionSummaryDTO,
    ReviewDashboardDTO,
    ReviewOcrSummaryDTO,
    ReviewPageOutputDTO,
    ReviewTaskSummaryDTO,
    SupplementItemSummaryDTO,
    SupplementRequestSummaryDTO,
)
from src.contexts.review_decision.app.services.review_service_context import (
    ReviewServiceContext,
)
from src.contexts.review_decision.infra.schema.decisions import Decisions
from src.contexts.review_decision.infra.schema.review_comments import ReviewComments
from src.contexts.review_decision.infra.schema.review_tasks import ReviewTasks


class ReviewQueryApplicationService:
    """審查查詢面用例實作。"""

    def __init__(self, ctx: ReviewServiceContext) -> None:
        self._c = ctx

    def list_tasks(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ReviewTaskSummaryDTO]:
        """承辦工作台：分頁列出審查任務。"""
        rows = self._c.tasks.list_recent(limit=limit, offset=offset)
        return [_task_row_to_summary(r) for r in rows]

    def get_dashboard(self) -> ReviewDashboardDTO:
        """
        審查儀表板計數。

        責任：初版以 `list_recent` 子集統計；資料量上升時請改 SQL `COUNT`。
        """
        rows = self._c.tasks.list_recent(limit=5_000, offset=0)
        open_rows = [r for r in rows if r.status != "closed"]
        closed = [r for r in rows if r.status == "closed"]
        pending_assign = [r for r in open_rows if r.assignee_user_id is None]
        in_review = [r for r in open_rows if r.status == "in_review"]
        return ReviewDashboardDTO(
            total_open_tasks=len(open_rows),
            pending_assignment_tasks=len(pending_assign),
            in_review_tasks=len(in_review),
            closed_tasks_in_window=len(closed),
        )

    def get_review_page(
        self,
        application_id: UUID,
    ) -> ReviewPageOutputDTO:
        """
        UC-REV-02：審核頁聚合模型。

        責任：`applicant_user_id=None` 允許承辦讀取完整案件明細（授權由 API 層處理）。
        """
        detail = self._c.application_queries.get_application(
            application_id,
            applicant_user_id=None,
        )
        plan = self._c.route_plans.get_latest_route_plan(application_id)
        plan_dict = plan.model_dump(mode="json") if plan is not None else None

        dec_rows = self._c.decisions.list_by_application_id(application_id)
        decisions = [_decision_row_to_summary(d) for d in dec_rows]

        com_rows = self._c.comments.list_by_application_id(application_id)
        comments = [_comment_row_to_summary(c) for c in com_rows]

        sup_summaries = self._list_supplement_summaries(application_id)

        return ReviewPageOutputDTO(
            application=detail,
            route_plan=plan_dict,
            ocr_summary=None,
            decisions=decisions,
            comments=comments,
            supplement_requests=sup_summaries,
        )

    def get_ocr_summary_for_application(self, application_id: UUID) -> ReviewOcrSummaryDTO:
        """
        取得 OCR 彙總（對應 GET …/ocr-summary）。

        責任：初版自審核頁模型之預留欄位組裝；日後可改為直連 OCR 讀取埠以避免重複查詢。
        """
        page = self.get_review_page(application_id)
        blob = page.ocr_summary if isinstance(page.ocr_summary, dict) else {}
        return ReviewOcrSummaryDTO(application_id=application_id, ocr_summary=dict(blob))

    def list_decisions(self, application_id: UUID) -> list[DecisionSummaryDTO]:
        """案件決策歷史。"""
        rows = self._c.decisions.list_by_application_id(application_id)
        return [_decision_row_to_summary(r) for r in rows]

    def list_comments(self, application_id: UUID) -> list[CommentSummaryDTO]:
        """案件評論時間序列。"""
        rows = self._c.comments.list_by_application_id(application_id)
        return [_comment_row_to_summary(r) for r in rows]

    def get_audit_trail(self, application_id: UUID) -> list[AuditTrailEntryDTO]:
        """
        稽核軌跡：合併決策、評論與（若可取得）案件狀態歷程，依時間排序。

        責任：狀態歷程來自 Application 查詢服務之 timeline。
        """
        entries: list[AuditTrailEntryDTO] = []

        for d in self._c.decisions.list_by_application_id(application_id):
            entries.append(
                AuditTrailEntryDTO(
                    entry_type="decision",
                    occurred_at=d.decided_at,
                    payload={
                        "decision_id": str(d.decision_id),
                        "decision_type": d.decision_type,
                        "decided_by": str(d.decided_by),
                        "reason": d.reason,
                    },
                ),
            )

        for c in self._c.comments.list_by_application_id(application_id):
            entries.append(
                AuditTrailEntryDTO(
                    entry_type="comment",
                    occurred_at=c.created_at,
                    payload={
                        "comment_id": str(c.comment_id),
                        "comment_type": c.comment_type,
                        "created_by": str(c.created_by),
                        "content": c.content,
                    },
                ),
            )

        timeline = self._c.application_queries.get_timeline(
            application_id,
            applicant_user_id=None,
        )
        for h in timeline:
            entries.append(
                AuditTrailEntryDTO(
                    entry_type="status_change",
                    occurred_at=h.created_at,
                    payload={
                        "history_id": str(h.history_id),
                        "from_status": h.from_status,
                        "to_status": h.to_status,
                        "changed_by": str(h.changed_by) if h.changed_by else None,
                        "reason": h.reason,
                    },
                ),
            )

        entries.sort(key=lambda e: e.occurred_at)
        return entries

    def _list_supplement_summaries(
        self,
        application_id: UUID,
    ) -> list[SupplementRequestSummaryDTO]:
        reqs = self._c.supplements.list_requests_by_application_id(application_id)
        out: list[SupplementRequestSummaryDTO] = []
        for r in reqs:
            item_rows = self._c.supplements.list_items_for_request(r.supplement_request_id)
            out.append(
                SupplementRequestSummaryDTO(
                    supplement_request_id=r.supplement_request_id,
                    application_id=r.application_id,
                    requested_by=r.requested_by,
                    deadline_at=r.deadline_at,
                    status=r.status,
                    message=r.message,
                    created_at=r.created_at,
                    updated_at=r.updated_at,
                    items=[
                        SupplementItemSummaryDTO(
                            supplement_item_id=i.supplement_item_id,
                            item_code=i.item_code,
                            item_name=i.item_name,
                            required_action=i.required_action,
                            note=i.note,
                            created_at=i.created_at,
                        )
                        for i in item_rows
                    ],
                ),
            )
        return out


def _task_row_to_summary(r: ReviewTasks) -> ReviewTaskSummaryDTO:
    return ReviewTaskSummaryDTO(
        review_task_id=r.review_task_id,
        application_id=r.application_id,
        stage=r.stage,
        status=r.status,
        assignee_user_id=r.assignee_user_id,
        due_at=r.due_at,
        created_at=r.created_at,
        updated_at=r.updated_at,
    )


def _decision_row_to_summary(d: Decisions) -> DecisionSummaryDTO:
    return DecisionSummaryDTO(
        decision_id=d.decision_id,
        application_id=d.application_id,
        decision_type=d.decision_type,
        selected_candidate_id=d.selected_candidate_id,
        override_id=d.override_id,
        approved_start_at=d.approved_start_at,
        approved_end_at=d.approved_end_at,
        reason=d.reason,
        decided_by=d.decided_by,
        decided_at=d.decided_at,
        created_at=d.created_at,
    )


def _comment_row_to_summary(c: ReviewComments) -> CommentSummaryDTO:
    return CommentSummaryDTO(
        comment_id=c.comment_id,
        application_id=c.application_id,
        comment_type=c.comment_type,
        content=c.content,
        created_by=c.created_by,
        created_at=c.created_at,
    )
