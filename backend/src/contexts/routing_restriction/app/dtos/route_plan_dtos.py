"""
路線規劃讀寫模型 DTO：候選、路段、規則命中、無路說明、承辦操作輸入。

責任：供 UC-ROUTE-02～05 與查詢 API 序列化；不含領域行為。
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class GeoPointDTO(BaseModel):
    """單點座標（WGS84）。"""

    latitude: float
    longitude: float


class RouteSegmentDTO(BaseModel):
    """路段讀取模型。"""

    segment_id: UUID
    seq_no: int
    road_name: str | None
    distance_m: int
    duration_s: int
    instruction_text: str | None
    is_exception_road: bool


class RouteRuleHitDTO(BaseModel):
    """規則命中讀取模型。"""

    rule_id: UUID
    rule_type: str
    hit_type: str
    segment_id: UUID | None
    detail_text: str | None


class RouteCandidateDTO(BaseModel):
    """候選路線讀取模型。"""

    candidate_id: UUID
    candidate_rank: int
    distance_m: int
    duration_s: int
    score: Decimal
    summary_text: str | None
    area_road_sequence: list[str] | None = None
    segments: list[RouteSegmentDTO]
    rule_hits: list[RouteRuleHitDTO]


class NoRouteExplanationDTO(BaseModel):
    """無可行路線之結構化說明。"""

    code: str
    message: str


class OfficerOverrideSummaryDTO(BaseModel):
    """人工改線紀錄摘要（供承辦核准時選擇 override_id）。"""

    override_id: UUID
    base_candidate_id: UUID | None = None
    override_reason: str
    created_at: datetime


class RoutePlanDetailDTO(BaseModel):
    """單一路線規劃完整讀取模型（UC-ROUTE-03）。"""

    route_plan_id: UUID
    application_id: UUID
    route_request_id: UUID
    status: str
    planning_version: str
    map_version: str
    selected_candidate_id: UUID | None
    candidates: list[RouteCandidateDTO]
    no_route: NoRouteExplanationDTO | None
    origin_text: str | None = Field(
        default=None,
        description="路線申請之起點地址／描述（與 routing.route_requests 對齊）",
    )
    destination_text: str | None = Field(
        default=None,
        description="路線申請之迄點（到達點）地址／描述",
    )
    origin_geo: GeoPointDTO | None = Field(
        default=None,
        description="起點經地理編碼後之 WGS84 座標；尚無則 null",
    )
    destination_geo: GeoPointDTO | None = Field(
        default=None,
        description="迄點經地理編碼後之 WGS84 座標；尚無則 null",
    )
    officer_overrides: list[OfficerOverrideSummaryDTO] = Field(
        default_factory=list,
        description="本案歷次人工改線（新→舊），核准時可擇一 override_id",
    )


class SelectCandidateInputDTO(BaseModel):
    """UC-ROUTE-04：選定候選。"""

    candidate_id: UUID


class OfficerOverrideInputDTO(BaseModel):
    """UC-ROUTE-05：人工改線（幾何以 WKT LINESTRING 傳入，由服務轉領域）。"""

    model_config = ConfigDict(str_strip_whitespace=True)

    override_line_wkt: str = Field(..., min_length=10, description="SRID4326 LINESTRING WKT")
    override_reason: str = Field(..., min_length=1)
    base_candidate_id: UUID | None = None


class PatchItinerarySegmentInputDTO(BaseModel):
    """覆寫「已選候選」之路段列：路名可空；距離／時間須非負，且總距離須大於 0。"""

    model_config = ConfigDict(str_strip_whitespace=True)

    road_name: str | None = None
    distance_m: int = Field(ge=0)
    duration_s: int = Field(ge=0)


class PatchSelectedItineraryInputDTO(BaseModel):
    """
    承辦依已選路線改寫分段：依距離比例切分候選 LINESTRING；
    規則命中於寫入後依新路段重算（ST_Intersects）。
    """

    segments: list[PatchItinerarySegmentInputDTO] = Field(min_length=1)

    @model_validator(mode="after")
    def _total_distance_positive(self) -> PatchSelectedItineraryInputDTO:
        if sum(s.distance_m for s in self.segments) <= 0:
            raise ValueError("segments 之 distance_m 總和須為正")
        return self


class RouteRuleHitQueryDTO(BaseModel):
    """規則命中列表（可依計畫篩選）。"""

    route_plan_id: UUID
    hits: list[RouteRuleHitDTO]


class RoutePlanCreatedOutputDTO(BaseModel):
    """UC-ROUTE-02 或承辦 replan 完成後回傳之新計畫識別。"""

    route_plan_id: UUID
