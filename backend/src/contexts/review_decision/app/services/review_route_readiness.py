"""
由 Routing App 之 RoutePlan 讀模型組裝核准前路由就緒度（ApprovalRouteReadiness）。

責任：將「有無路線計畫、有無可核准路線來源」之判斷與領域值物件對齊；領域本身不依賴 Routing。
"""

from __future__ import annotations

from uuid import UUID

from src.contexts.review_decision.domain.value_objects import ApprovalRouteReadiness
from src.contexts.routing_restriction.app.dtos.route_plan_dtos import RoutePlanDetailDTO


def build_approval_route_readiness(
    plan: RoutePlanDetailDTO | None,
    *,
    selected_candidate_id: UUID | None,
    override_id: UUID | None,
    allows_approval_without_viable_route: bool = False,
) -> ApprovalRouteReadiness:
    """
    依最新路線規劃與本次核准輸入，建立 ApprovalRouteReadiness。

    責任：
    - **has_route_plan**：存在任何與案件關聯之規劃快照即 True。
    - **has_selectable_route**：存在 **override_id**，或 **selected_candidate_id**（含請求指定或 plan 已選）
      且該候選隸屬於當前 plan 之候選列表。
    """
    if plan is None:
        return ApprovalRouteReadiness(
            has_route_plan=False,
            has_selectable_route=False,
            allows_approval_without_viable_route=allows_approval_without_viable_route,
        )

    effective_selected = (
        selected_candidate_id
        if selected_candidate_id is not None
        else plan.selected_candidate_id
    )
    candidate_ids = {c.candidate_id for c in plan.candidates}
    has_selectable = False
    if override_id is not None:
        has_selectable = True
    elif effective_selected is not None and effective_selected in candidate_ids:
        has_selectable = True

    return ApprovalRouteReadiness(
        has_route_plan=True,
        has_selectable_route=has_selectable,
        allows_approval_without_viable_route=allows_approval_without_viable_route,
    )
