"""
申請案件底下之車輛實體。

責任：表達 application.vehicles 之領域狀態（車牌值物件、總重、牌照有效日、是否主車）；
車牌格式與數量上限由 Aggregate 呼叫 VO／常數檢查。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from ..errors import InvalidDomainValueError
from ..value_objects import VehiclePlate


@dataclass
class Vehicle:
    """
    單一綁定於申請案件之車輛。

    責任：UC-APP-03 新增車輛、設定主車；聚合保證至少一台車才可送件。
    """

    vehicle_id: UUID
    application_id: UUID
    plate_no: VehiclePlate
    vehicle_kind: str
    gross_weight_ton: Decimal | None
    license_valid_until: date | None
    trailer_plate_no: VehiclePlate | None
    is_primary: bool
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        kind = (self.vehicle_kind or "").strip()
        if not kind or len(kind) > 50:
            raise InvalidDomainValueError("vehicle_kind must be non-empty and at most 50 chars")
        object.__setattr__(self, "vehicle_kind", kind)
        if self.gross_weight_ton is not None and self.gross_weight_ton < 0:
            raise InvalidDomainValueError("gross_weight_ton cannot be negative")

    @classmethod
    def create(
        cls,
        *,
        application_id: UUID,
        plate_no: VehiclePlate,
        vehicle_kind: str,
        gross_weight_ton: Decimal | None,
        license_valid_until: date | None,
        trailer_plate_no: VehiclePlate | None,
        is_primary: bool,
        now: datetime,
        vehicle_id: UUID | None = None,
    ) -> Vehicle:
        """建立新車輛實體（尚未持久化）。"""
        vid = vehicle_id or uuid4()
        return cls(
            vehicle_id=vid,
            application_id=application_id,
            plate_no=plate_no,
            vehicle_kind=vehicle_kind,
            gross_weight_ton=gross_weight_ton,
            license_valid_until=license_valid_until,
            trailer_plate_no=trailer_plate_no,
            is_primary=is_primary,
            created_at=now,
            updated_at=now,
        )

    def mark_primary(self) -> None:
        """標記為代表車（主車）；由聚合確保同一申請僅一輛主車。"""
        self.is_primary = True

    def mark_secondary(self) -> None:
        """取消主車標記。"""
        self.is_primary = False
