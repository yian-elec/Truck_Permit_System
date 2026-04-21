"""
ApprovalRouteReadiness — 核准前路由就緒度值物件。

責任：由 **Application 層** 從 Routing context 查詢後組裝，傳入領域核准工廠方法；
Domain **不**直接依賴 Routing／DB，僅根據此 VO 之布林條件落實「核准前必須有 route plan、
無合法路線不得直接核准」等規則。
"""

from __future__ import annotations

from dataclasses import dataclass

from src.contexts.review_decision.domain.errors import ReviewInvalidValueError


@dataclass(frozen=True)
class ApprovalRouteReadiness:
    """
    核准前路由相關前置條件（由 App 填入真偽）。

    責任欄位語意：
    - **has_route_plan**：已存在與本案關聯之路線計畫（對應規格「核准前必須有 route plan」）。
    - **has_selectable_route**：存在可核准之路線結果（已選候選 **或** 承辦 override 視為合法路線來源）。
    - **allows_approval_without_viable_route**：僅在明確允許之例外政策下為 True；預設 False 時
      **has_selectable_route** 必須為 True 才能核准（對應「無合法路線不得直接核准」）。
    """

    has_route_plan: bool
    has_selectable_route: bool
    allows_approval_without_viable_route: bool = False

    def __post_init__(self) -> None:
        if self.allows_approval_without_viable_route and not self.has_route_plan:
            raise ReviewInvalidValueError(
                "cannot waive viable-route requirement without a route plan"
            )

    def satisfies_approval_invariants(self) -> bool:
        """
        是否滿足核准路由相關不變條件。

        責任：集中一處表達規則，供 ReviewDecision 與測試重用。
        """
        if not self.has_route_plan:
            return False
        if self.allows_approval_without_viable_route:
            return True
        return self.has_selectable_route
