"""
車輛相關 DTO。
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AddVehicleInputDTO(BaseModel):
    """UC-APP-03 新增車輛輸入。"""

    model_config = ConfigDict(str_strip_whitespace=True)

    plate_no: str = Field(..., max_length=20)
    vehicle_kind: str = Field(..., max_length=50)
    gross_weight_ton: Decimal | None = None
    license_valid_until: date | None = None
    trailer_plate_no: str | None = Field(None, max_length=20)


class PatchVehicleInputDTO(BaseModel):
    """部分更新車輛。"""

    model_config = ConfigDict(str_strip_whitespace=True)

    plate_no: str | None = Field(None, max_length=20)
    vehicle_kind: str | None = Field(None, max_length=50)
    gross_weight_ton: Decimal | None = None
    license_valid_until: date | None = None
    trailer_plate_no: str | None = Field(None, max_length=20)


class VehicleDTO(BaseModel):
    """車輛輸出。"""

    vehicle_id: UUID
    application_id: UUID
    plate_no: str
    vehicle_kind: str
    gross_weight_ton: Decimal | None
    license_valid_until: date | None
    trailer_plate_no: str | None
    is_primary: bool
    created_at: datetime
    updated_at: datetime
