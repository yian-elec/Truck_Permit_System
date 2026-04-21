"""
RouteCandidate — 候選路線實體（隸屬 RoutePlan 聚合一致性邊界）。

DDD 說明：規格 6.1 將 RouteCandidate 與 RouteRequest／RoutePlan 並列描述；在實作上**以 RoutePlan
為聚合根**統一維護候選集合與不變條件，本類為**實體**（具 candidate_id、生命週期隸屬計畫），
而非獨立聚合根，以避免跨聚合循環與重複不變式。

責任：保存排序、距離、時間、分數、完整路線幾何、摘要、路段集合與規則檢核命中列表；
支援在領域服務寫入 rule_hits 後重新評估是否仍含不可豁免之 FORBIDDEN 命中。
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from src.contexts.routing_restriction.domain.errors import RoutingInvalidValueError
from src.contexts.routing_restriction.domain.value_objects.route_geometry import RouteGeometry
from src.contexts.routing_restriction.domain.value_objects.route_score import RouteScore
from src.contexts.routing_restriction.domain.value_objects.rule_hit import RuleHit
from src.contexts.routing_restriction.domain.value_objects.routing_enums import HitSeverity

from .route_segment import RouteSegment


@dataclass
class RouteCandidate:
    """
    單一候選路線（對應 routing.route_candidates + segments + rule_hits 之核心領域狀態）。

    責任：
    - **line_geometry**：對應規格 6.1 之 geometry（完整候選路徑）；路段拆解見 **segments**。
    - 維護 **candidate_rank** 與 provider 回傳之 distance／duration。
    - **score** 於規則檢核後由領域服務寫入或更新（持久化欄位為 numeric；建立當下可為空直至 UC-ROUTE-02 完成）。
    - **rule_hits** 為可變集合，但應僅由聚合方法或領域服務批次更新以維持一致性。
    """

    candidate_id: UUID
    route_plan_id: UUID
    candidate_rank: int
    distance_m: int
    duration_s: int
    line_geometry: RouteGeometry
    score: Optional[RouteScore] = None
    summary_text: Optional[str] = None
    area_road_sequence: Optional[List[str]] = None
    segments: List[RouteSegment] = field(default_factory=list)
    rule_hits: List[RuleHit] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        if self.candidate_rank < 0:
            raise RoutingInvalidValueError("candidate_rank must be non-negative")
        if self.distance_m < 0 or self.duration_s < 0:
            raise RoutingInvalidValueError("distance_m and duration_s must be non-negative")

    def replace_rule_hits(self, hits: List[RuleHit]) -> RouteCandidate:
        """
        以新命中列表取代舊有列表（不可變風格，回傳新實例）。

        責任：避免呼叫端直接篡改 list 繞過不變條件；供領域服務在套用例外路段後使用。
        """
        return replace(self, rule_hits=list(hits))

    def replace_score(self, score: RouteScore) -> RouteCandidate:
        """寫入計分結果後回傳新實例。"""
        return replace(self, score=score)

    def has_unsuppressed_forbidden_hit(self) -> bool:
        """
        是否仍存在嚴重度為 FORBIDDEN 之命中（已假設例外路段邏輯已先套用）。

        責任：供判定該候選是否對申請人／審查視為不可行。
        """
        return any(h.severity == HitSeverity.FORBIDDEN for h in self.rule_hits)

    def segment_is_exception(self, segment_index: int) -> bool:
        """依序號檢查該路段是否標記為例外可通行。"""
        if segment_index < 0 or segment_index >= len(self.segments):
            return False
        return self.segments[segment_index].is_exception_road
