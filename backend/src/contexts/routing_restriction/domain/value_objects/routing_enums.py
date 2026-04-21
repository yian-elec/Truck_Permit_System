"""
Routing_Restriction — 領域列舉與封閉字彙。

責任：與持久化 varchar 欄位對齊之合法取值，避免任意字串污染聚合；集中表達規則類型、命中嚴重度、
申請／計畫狀態與無路原因碼，供值物件與領域服務共用。
"""

from __future__ import annotations

from enum import StrEnum


class RuleType(StrEnum):
    """
    限制規則類型（對應規格與 KML 轉檔後之 rule_type）。

    責任：
    - **FORBIDDEN_ZONE / FORBIDDEN_ROAD**：硬性禁止，優先於一般 warning。
    - **EXCEPTION_ROAD**：例外可通行路段，於檢核時可覆蓋與該路段相關之部分限制（見領域服務）。
    - **NARROW_ROAD**：狹窄路段，通常產生 warning 或額外風險加權。
    - **WARNING_ZONE**：僅警示，不單獨使路線不可行（除非產品另定政策）。
    """

    FORBIDDEN_ZONE = "forbidden_zone"
    FORBIDDEN_ROAD = "forbidden_road"
    EXCEPTION_ROAD = "exception_road"
    NARROW_ROAD = "narrow_road"
    WARNING_ZONE = "warning_zone"


class HitSeverity(StrEnum):
    """
    規則命中（RuleHit）之嚴重度。

    責任：支援「forbidden 優先於 warning」之排序與可行性判定；與 RuleType 搭配使用
    （例如 forbidden_zone 通常對應 FORBIDDEN 嚴重度）。
    """

    FORBIDDEN = "forbidden"
    WARNING = "warning"


class RouteRequestStatus(StrEnum):
    """
    路線申請（RouteRequest）生命週期狀態。

    責任：約束 UC-ROUTE-01 流程：草稿／地理編碼中／就緒／失敗／已送規劃等語意。
    """

    PENDING_GEOCODE = "pending_geocode"
    GEOCODING = "geocoding"
    READY_TO_PLAN = "ready_to_plan"
    GEOCODE_FAILED = "geocode_failed"
    PLANNING_QUEUED = "planning_queued"
    CANCELLED = "cancelled"


class RoutePlanStatus(StrEnum):
    """
    路線規劃聚合（RoutePlan）狀態。

    責任：表達候選產生中、可選線、無可行路線、承辦調線後等；與 map_version／planning_version 並存
    以支援稽核與重算。
    """

    PLANNING = "planning"
    CANDIDATES_READY = "candidates_ready"
    NO_ROUTE = "no_route"
    CANDIDATE_SELECTED = "candidate_selected"
    OFFICER_ADJUSTED = "officer_adjusted"


class RoutingDirection(StrEnum):
    """
    規則適用之行車方向（若資料來源有區分單向限制）。

    責任：與 Infra 之 direction varchar 對齊；未知時使用 ANY。
    """

    ANY = "any"
    FORWARD = "forward"
    BACKWARD = "backward"
    BOTH = "both"


class NoRouteReasonCode(StrEnum):
    """
    無任何可行候選時之結構化原因（禁止只回空列表）。

    責任：供 API 與前端顯示；與人類可讀訊息一併置於領域結果物件中。
    """

    ALL_CANDIDATES_FORBIDDEN = "all_candidates_forbidden"
    ROUTING_PROVIDER_EMPTY = "routing_provider_empty"
    RULE_DATA_MISSING = "rule_data_missing"
    GEOMETRY_INVALID = "geometry_invalid"
    UNKNOWN = "unknown"
