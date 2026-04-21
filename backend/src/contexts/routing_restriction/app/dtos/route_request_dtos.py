"""
UC-ROUTE-01 相關 DTO：建立路線申請、回傳請求狀態。

責任：與 API 契約對齊；數值校驗由 Pydantic 執行，領域物件於服務內組裝。
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class CreateRouteRequestInputDTO(BaseModel):
    """建立路線申請之輸入。"""

    model_config = ConfigDict(str_strip_whitespace=True)

    origin_text: str = Field(..., min_length=1, max_length=255)
    destination_text: str = Field(..., min_length=1, max_length=255)
    requested_departure_at: datetime | None = None
    vehicle_weight_ton: Decimal | None = Field(None, ge=0)
    vehicle_kind: str | None = Field(None, max_length=50)

    origin_lat: float | None = Field(
        default=None,
        description="起點 WGS84 緯度；須與 origin_lon、destination_lat、destination_lon 四欄齊備，否則僅能全缺（改走文字地理編碼）。",
    )
    origin_lon: float | None = Field(
        default=None,
        description="起點 WGS84 經度；四欄齊備時略過外部 geocode，僅作座標來源。",
    )
    destination_lat: float | None = Field(
        default=None,
        description="終點 WGS84 緯度。",
    )
    destination_lon: float | None = Field(
        default=None,
        description="終點 WGS84 經度。",
    )

    @field_validator("origin_lat", "destination_lat")
    @classmethod
    def _lat_range(cls, v: float | None) -> float | None:
        if v is None:
            return v
        if not -90.0 <= v <= 90.0:
            raise ValueError("latitude must be between -90 and 90")
        return v

    @field_validator("origin_lon", "destination_lon")
    @classmethod
    def _lon_range(cls, v: float | None) -> float | None:
        if v is None:
            return v
        if not -180.0 <= v <= 180.0:
            raise ValueError("longitude must be between -180 and 180")
        return v

    @model_validator(mode="after")
    def _coords_all_or_none(self) -> CreateRouteRequestInputDTO:
        fields = (
            self.origin_lat,
            self.origin_lon,
            self.destination_lat,
            self.destination_lon,
        )
        n = sum(1 for f in fields if f is not None)
        if n not in (0, 4):
            raise ValueError(
                "origin_lat, origin_lon, destination_lat, destination_lon must all "
                "be provided together or all omitted"
            )
        return self


class RouteRequestStatusDTO(BaseModel):
    """路線申請目前狀態（讀取模型）。"""

    route_request_id: UUID
    application_id: UUID
    status: str
    origin_text: str
    destination_text: str
    geocode_failure_reason: str | None = None
    requested_departure_at: datetime | None = None
    vehicle_weight_ton: Decimal | None = None
    vehicle_kind: str | None = None
