"""
車輛用例（UC-APP-03）。

責任：新增／更新／移除車輛；主檔與附件變更由其他專責服務處理。
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.contexts.application.domain.value_objects import VehiclePlate

from ..dtos import AddVehicleInputDTO, PatchVehicleInputDTO, VehicleDTO
from .application_mappers import vehicle_entity_to_dto
from .application_service_context import ApplicationServiceContext, raise_domain_as_app


class VehicleApplicationService:
    """UC-APP-03 專責服務。"""

    def __init__(self, ctx: ApplicationServiceContext) -> None:
        self._c = ctx

    def add_vehicle(
        self,
        application_id: UUID,
        dto: AddVehicleInputDTO,
        *,
        applicant_user_id: UUID | None,
    ) -> list[VehicleDTO]:
        app = self._c.load(application_id)
        self._c.ensure_applicant(app, applicant_user_id)
        now = datetime.now(timezone.utc)
        trailer_raw = (dto.trailer_plate_no or "").strip()
        trailer = VehiclePlate(trailer_raw) if trailer_raw else None
        raise_domain_as_app(
            lambda: app.add_vehicle(
                plate_no=VehiclePlate(dto.plate_no.strip()),
                vehicle_kind=dto.vehicle_kind.strip(),
                gross_weight_ton=dto.gross_weight_ton,
                license_valid_until=dto.license_valid_until,
                trailer_plate_no=trailer,
                now=now,
                vehicle_id=uuid4(),
            )
        )
        self._c.save(app)
        return [vehicle_entity_to_dto(v) for v in app.vehicles]

    def update_vehicle(
        self,
        application_id: UUID,
        vehicle_id: UUID,
        dto: PatchVehicleInputDTO,
        *,
        applicant_user_id: UUID | None,
    ) -> list[VehicleDTO]:
        app = self._c.load(application_id)
        self._c.ensure_applicant(app, applicant_user_id)
        now = datetime.now(timezone.utc)
        plate = VehiclePlate(dto.plate_no.strip()) if dto.plate_no else None
        trailer: VehiclePlate | None = None
        if dto.trailer_plate_no is not None:
            ts = dto.trailer_plate_no.strip()
            if ts:
                trailer = VehiclePlate(ts)
        raise_domain_as_app(
            lambda: app.update_vehicle(
                vehicle_id,
                plate_no=plate,
                vehicle_kind=dto.vehicle_kind,
                gross_weight_ton=dto.gross_weight_ton,
                license_valid_until=dto.license_valid_until,
                trailer_plate_no=trailer if dto.trailer_plate_no is not None else None,
                now=now,
            )
        )
        self._c.save(app)
        return [vehicle_entity_to_dto(v) for v in app.vehicles]

    def remove_vehicle(
        self,
        application_id: UUID,
        vehicle_id: UUID,
        *,
        applicant_user_id: UUID | None,
    ) -> list[VehicleDTO]:
        app = self._c.load(application_id)
        self._c.ensure_applicant(app, applicant_user_id)
        now = datetime.now(timezone.utc)
        raise_domain_as_app(lambda: app.remove_vehicle(vehicle_id, now=now))
        self._c.save(app)
        return [vehicle_entity_to_dto(v) for v in app.vehicles]
