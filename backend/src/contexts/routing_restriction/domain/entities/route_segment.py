"""
RouteSegment — 候選路線之路段實體。

責任：將候選線拆成有序路段，供規則命中綁定 segment、以及標記 is_exception_road（例外可通行）
以支援「exception_road 覆蓋部分限制」之領域規則。具身分（segment_id）與隸屬之 candidate。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from src.contexts.routing_restriction.domain.value_objects.route_geometry import RouteGeometry
from src.contexts.routing_restriction.domain.errors import RoutingInvalidValueError


@dataclass
class RouteSegment:
    """
    單一路段（對應 routing.route_segments 之領域模型）。

    責任：保存距離、時間、幾何、轉向描述；**is_exception_road** 由規劃／匯入流程標記，
    供 RestrictionEvaluationService 在套用規則後抑制與該路段衝突之部分禁止命中。
    """

    segment_id: UUID
    candidate_id: UUID
    seq_no: int
    distance_m: int
    duration_s: int
    geometry: RouteGeometry
    road_name: str | None = None
    instruction_text: str | None = None
    is_exception_road: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        if self.seq_no < 0:
            raise RoutingInvalidValueError("seq_no must be non-negative")
        if self.distance_m < 0 or self.duration_s < 0:
            raise RoutingInvalidValueError("distance_m and duration_s must be non-negative")
