"""
Routing_Restriction 應用層出站埠（Geocoding、路網候選、空間規則命中）。

責任：由 App 服務依賴反轉；預設提供可開發用之 Stub／Noop 實作，正式環境可置換為
Google／OSM／PostGIS 等 Infra Adapter。
"""

from __future__ import annotations

import zlib
from dataclasses import dataclass
from datetime import datetime
from typing import List, Protocol, Sequence

from src.contexts.routing_restriction.domain.entities.route_candidate import RouteCandidate
from src.contexts.routing_restriction.domain.value_objects.geo_point import GeoPoint
from src.contexts.routing_restriction.domain.value_objects.route_geometry import RouteGeometry
from src.contexts.routing_restriction.domain.value_objects.vehicle_constraint import (
    VehicleConstraint,
)


@dataclass(frozen=True)
class GeocodeResolution:
    """地理編碼結果：成功時 point 有值；失敗時附 failure_reason（除錯用）。"""

    point: GeoPoint | None
    failure_reason: str | None = None


class GeocodingPort(Protocol):
    """將地址文字解析為 WGS84 單點；無法解析時 GeocodeResolution.point 為 None。"""

    def resolve_point(self, address_text: str) -> GeocodeResolution:
        ...


class RoutingProviderPort(Protocol):
    """自起訖點取得候選路線（幾何以領域 RouteGeometry LINESTRING 表示）。"""

    def fetch_candidates(
        self,
        origin: GeoPoint,
        destination: GeoPoint,
        *,
        vehicle: VehicleConstraint | None = None,
        departure_at: datetime | None = None,
    ) -> List[RouteCandidate]:
        ...


class SpatialRuleHitPort(Protocol):
    """
    對候選路線附加規則命中（PostGIS 相交等應實作於 Infra）。

    責任：預設 Noop 不寫入命中，供管線打通；正式環境置換為真實檢核。
    """

    def attach_rule_hits(
        self,
        candidates: Sequence[RouteCandidate],
        *,
        vehicle: VehicleConstraint,
        departure_at: datetime | None,
    ) -> List[RouteCandidate]:
        ...


@dataclass
class StubGeocodingPort:
    """
    開發用地理編碼：依字串雜湊產生台灣西北部合法範圍內之固定點。

    責任：不依賴外部 API；**不可**用於正式地址正確性需求。
    """

    def resolve_point(self, address_text: str) -> GeocodeResolution:
        if not (address_text or "").strip():
            return GeocodeResolution(
                None, failure_reason="geocoding_failed: empty_address"
            )
        h = zlib.adler32(address_text.strip().encode("utf-8")) % 1_000_000
        lat = 25.0 + (h % 500) / 10_000.0
        lon = 121.4 + (h // 500 % 500) / 10_000.0
        return GeocodeResolution(GeoPoint(latitude=lat, longitude=lon), None)


class NoopSpatialRuleHitPort:
    """不附加任何命中（候選 rule_hits 保持空）。"""

    def attach_rule_hits(
        self,
        candidates: Sequence[RouteCandidate],
        *,
        vehicle: VehicleConstraint,
        departure_at: datetime | None,
    ) -> List[RouteCandidate]:
        return list(candidates)


class StubRoutingProviderPort:
    """
    開發用路網：產生 1～2 條直線候選（整線為單一路段）。

    責任：驗證 UC-ROUTE-02 管線與持久化；路形不具導航意義。
    """

    def fetch_candidates(
        self,
        origin: GeoPoint,
        destination: GeoPoint,
        *,
        vehicle: VehicleConstraint | None = None,
        departure_at: datetime | None = None,
    ) -> List[RouteCandidate]:
        from uuid import uuid4

        line_a = RouteGeometry.linestring((origin, destination))
        # 第二條：經由微偏移中間點，模擬替代路
        mid = GeoPoint(
            latitude=(origin.latitude + destination.latitude) / 2 + 0.002,
            longitude=(origin.longitude + destination.longitude) / 2 + 0.002,
        )
        line_b = RouteGeometry.linestring((origin, mid, destination))

        out: List[RouteCandidate] = []
        for rank, geom in enumerate((line_a, line_b), start=1):
            cid = uuid4()
            seg_id = uuid4()
            from src.contexts.routing_restriction.domain.entities.route_segment import RouteSegment

            seg = RouteSegment(
                segment_id=seg_id,
                candidate_id=cid,
                seq_no=0,
                distance_m=1200 * rank,
                duration_s=300 * rank,
                geometry=geom,
                road_name=f"示範道路（候選 {rank}）",
                instruction_text="開發用 stub：上線後由路網 API 帶入真實路名與轉向。",
                is_exception_road=False,
            )
            cand = RouteCandidate(
                candidate_id=cid,
                route_plan_id=cid,  # 稍後由服務覆寫為真實 route_plan_id
                candidate_rank=rank,
                distance_m=1200 * rank,
                duration_s=300 * rank,
                line_geometry=geom,
                score=None,
                summary_text=f"stub candidate {rank}",
                segments=[seg],
                rule_hits=[],
            )
            out.append(cand)
        return out
