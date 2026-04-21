"""
MVP 路網邊權重：依 OSM highway／service 區分「汽車可通行」與偏好主幹道。

純 haversine 公尺會過度偏好河堤、便道等幾何短路徑；此模組將距離乘以 highway 倍率與
readability 倍率後再給 Dijkstra，並排除明顯非車行或停車場通道等 way。
"""

from __future__ import annotations

from typing import Any, Final, Mapping

from shared.core.config import settings

from src.contexts.routing_restriction.infra.road_data.osm_road_naming import (
    way_has_osm_name_or_ref,
)

# 不納入汽車路網（與 footway／步道／腳踏車專用等對齊）
_EXCLUDED_HIGHWAY: Final[frozenset[str]] = frozenset(
    {
        "footway",
        "path",
        "pedestrian",
        "steps",
        "cycleway",
        "bridleway",
        "elevator",
        "corridor",
        "via_ferrata",
    }
)

_EXCLUDED_SERVICE: Final[frozenset[str]] = frozenset(
    {
        "parking_aisle",
        "driveway",
        "drive-through",
        "emergency_access",
    }
)

# cost = 幾何距離(公尺) × 倍率；倍率愈低愈容易被最短路選中（偏好主幹道）
_HIGHWAY_COST_MULT: Final[dict[str, float]] = {
    "motorway": 0.52,
    "motorway_link": 0.58,
    "trunk": 0.55,
    "trunk_link": 0.6,
    "primary": 0.62,
    "primary_link": 0.68,
    "secondary": 0.78,
    "secondary_link": 0.82,
    "tertiary": 1.22,
    "tertiary_link": 1.28,
    "unclassified": 1.15,
    "residential": 1.45,
    "living_street": 1.65,
    "service": 1.9,
    "road": 1.25,
    "track": 2.3,
    "bus_guideway": 0.75,
}


def mvp_edge_readability_multiplier(tags: Mapping[str, Any]) -> float:
    """具 name/ref 為 1.0，否則為設定之未命名懲罰係數（與 way_has_osm_name_or_ref 一致）。"""
    if way_has_osm_name_or_ref(tags):
        return 1.0
    return float(settings.mvp_routing_readability_unnamed_multiplier)


def mvp_edge_routing_cost_meters(haversine_m: float, tags: Mapping[str, Any]) -> float | None:
    """
    回傳此邊在 Dijkstra 中使用之權重（公尺等價）：距離 × highway 係數 × readability 係數。
    若此 way 不應給一般汽車走則回傳 None。
    """
    m = mvp_motor_edge_cost_multiplier(tags)
    if m is None:
        return None
    return float(haversine_m) * m * mvp_edge_readability_multiplier(tags)


def mvp_motor_edge_weight_meters(haversine_m: float, tags: Mapping[str, Any]) -> float | None:
    """與 `mvp_edge_routing_cost_meters` 相同（舊名保留）。"""
    return mvp_edge_routing_cost_meters(haversine_m, tags)


def mvp_motor_edge_cost_multiplier(tags: Mapping[str, Any]) -> float | None:
    hw_raw = tags.get("highway")
    if hw_raw is None or not str(hw_raw).strip():
        return None
    hw = str(hw_raw).strip().lower()

    if hw in _EXCLUDED_HIGHWAY:
        return None

    if hw == "service":
        svc = (tags.get("service") or "").strip().lower()
        if svc in _EXCLUDED_SERVICE:
            return None

    # 明確禁止一般車輛（常見於步道／部分巷道）
    veh = (tags.get("vehicle") or "").strip().lower()
    motor = (tags.get("motor_vehicle") or "").strip().lower()
    if veh in ("no", "private") or motor in ("no", "private"):
        return None

    if hw in _HIGHWAY_COST_MULT:
        return _HIGHWAY_COST_MULT[hw]

    if hw.endswith("_link"):
        base = hw[:-5]
        if base in _HIGHWAY_COST_MULT:
            # link 略差於本體
            return min(_HIGHWAY_COST_MULT[base] * 1.08, 1.5)

    # 未知 highway 值：保守懲罰，避免誤當主幹道
    return 1.85
