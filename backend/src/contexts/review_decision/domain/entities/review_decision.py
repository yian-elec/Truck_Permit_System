"""
ReviewDecision — 決策聚合根（單筆決策紀錄）。

責任：
- 封裝一筆寫入 **review.decisions** 的領域意義：決策類型、候選／調線參照、核准期間、理由、決策者與時間。
- 透過 **類別工廠方法** `record_approve`／`record_reject`／`record_supplement` 建立，於內部校驗
  **路由就緒度**、**候選與 override 互斥**、**理由與人員**，並呼叫 **ReviewWorkflowPolicy**
  檢查與歷史決策之相容性。

說明：聚合為 **不可變** 決策紀錄（建立後不修改）；若需撤銷應由 App 另建補償交易或新規格支援。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.contexts.review_decision.domain.errors import ReviewDecisionRuleError
from src.contexts.review_decision.domain.services.review_workflow_policy import (
    ReviewWorkflowPolicy,
)
from src.contexts.review_decision.domain.value_objects import (
    ApprovalRouteReadiness,
    ApprovedPeriod,
    DecisionType,
)


@dataclass(frozen=True)
class ReviewDecision:
    """
    單筆審查決策（聚合根）。

    責任：欄位對齊 infra schema；**decision_type** 與其他欄位組合必須語意一致
    （例如 REJECT 不應帶核准期間）。
    """

    decision_id: UUID
    application_id: UUID
    decision_type: DecisionType
    selected_candidate_id: UUID | None
    override_id: UUID | None
    approved_period: ApprovedPeriod | None
    reason: str
    decided_by: UUID
    decided_at: datetime
    created_at: datetime

    @classmethod
    def record_approve(
        cls,
        *,
        decision_id: UUID,
        application_id: UUID,
        readiness: ApprovalRouteReadiness,
        approved_period: ApprovedPeriod,
        reason: str,
        decided_by: UUID,
        decided_at: datetime,
        created_at: datetime,
        selected_candidate_id: UUID | None,
        override_id: UUID | None,
        prior_decision_types_in_order: tuple[DecisionType, ...] = (),
    ) -> ReviewDecision:
        """
        UC-REV-04：核准案件。

        責任：
        - 驗證 **理由與決策者**、**核准期間**（ApprovedPeriod 自建構子保證起訖）。
        - 驗證 **ApprovalRouteReadiness**（必須有 plan；無合法路線時不得核准，除非政策允許豁免）。
        - **selected_candidate_id** 與 **override_id** 至多一個非空（避免雙重來源）；若未豁免，
          至少一個非空以標示「核准依據」。
        - 與 **prior_decision_types_in_order** 通過 ReviewWorkflowPolicy 互斥檢查。
        """
        ReviewWorkflowPolicy.require_reason_and_actor(
            reason=reason, actor_user_id=decided_by
        )
        ReviewWorkflowPolicy.assert_new_decision_compatible_with_history(
            prior_decision_types_in_order=prior_decision_types_in_order,
            new_decision=DecisionType.APPROVE,
        )

        if not readiness.satisfies_approval_invariants():
            raise ReviewDecisionRuleError(
                "cannot approve: route plan or viable route requirements not satisfied"
            )

        if selected_candidate_id is not None and override_id is not None:
            raise ReviewDecisionRuleError(
                "cannot set both selected_candidate_id and override_id on approval"
            )

        if not readiness.allows_approval_without_viable_route:
            if selected_candidate_id is None and override_id is None:
                raise ReviewDecisionRuleError(
                    "approval requires selected_candidate_id or override_id "
                    "when viable route is required"
                )

        return cls(
            decision_id=decision_id,
            application_id=application_id,
            decision_type=DecisionType.APPROVE,
            selected_candidate_id=selected_candidate_id,
            override_id=override_id,
            approved_period=approved_period,
            reason=reason.strip(),
            decided_by=decided_by,
            decided_at=decided_at,
            created_at=created_at,
        )

    @classmethod
    def record_reject(
        cls,
        *,
        decision_id: UUID,
        application_id: UUID,
        reason: str,
        decided_by: UUID,
        decided_at: datetime,
        created_at: datetime,
        prior_decision_types_in_order: tuple[DecisionType, ...] = (),
    ) -> ReviewDecision:
        """
        UC-REV-05：駁回案件。

        責任：不得帶入候選、override 或核准期間；必須理由與決策者；通過歷史互斥檢查。
        """
        ReviewWorkflowPolicy.require_reason_and_actor(
            reason=reason, actor_user_id=decided_by
        )
        ReviewWorkflowPolicy.assert_new_decision_compatible_with_history(
            prior_decision_types_in_order=prior_decision_types_in_order,
            new_decision=DecisionType.REJECT,
        )

        return cls(
            decision_id=decision_id,
            application_id=application_id,
            decision_type=DecisionType.REJECT,
            selected_candidate_id=None,
            override_id=None,
            approved_period=None,
            reason=reason.strip(),
            decided_by=decided_by,
            decided_at=decided_at,
            created_at=created_at,
        )

    @classmethod
    def record_supplement(
        cls,
        *,
        decision_id: UUID,
        application_id: UUID,
        reason: str,
        decided_by: UUID,
        decided_at: datetime,
        created_at: datetime,
        prior_decision_types_in_order: tuple[DecisionType, ...] = (),
    ) -> ReviewDecision:
        """
        UC-REV-03：發出補件時一併寫入之 **decision(type=supplement)**。

        責任：與 SupplementRequest 聚合搭配；決策紀錄本身不內嵌 items（items 屬 SupplementRequest）。
        仍須理由與決策者，並通過與駁回／核准後狀態之互斥檢查。
        """
        ReviewWorkflowPolicy.require_reason_and_actor(
            reason=reason, actor_user_id=decided_by
        )
        ReviewWorkflowPolicy.assert_new_decision_compatible_with_history(
            prior_decision_types_in_order=prior_decision_types_in_order,
            new_decision=DecisionType.SUPPLEMENT,
        )

        return cls(
            decision_id=decision_id,
            application_id=application_id,
            decision_type=DecisionType.SUPPLEMENT,
            selected_candidate_id=None,
            override_id=None,
            approved_period=None,
            reason=reason.strip(),
            decided_by=decided_by,
            decided_at=decided_at,
            created_at=created_at,
        )
