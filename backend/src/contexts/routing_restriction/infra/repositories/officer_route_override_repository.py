"""
OfficerRouteOverrideRepository — routing.officer_route_overrides 寫入。

責任：承辦人工改線紀錄持久化。
"""

from __future__ import annotations

from uuid import UUID

from geoalchemy2.elements import WKTElement
from sqlalchemy import select

from shared.core.db.connection import get_session

from src.contexts.routing_restriction.domain.entities.officer_route_override import (
    OfficerRouteOverride,
)
from src.contexts.routing_restriction.infra.repositories.geometry_wkt import (
    route_geometry_linestring_to_wkt,
)
from src.contexts.routing_restriction.infra.schema.officer_route_overrides import (
    OfficerRouteOverrides,
)


class OfficerRouteOverrideRepository:
    def list_by_application_id(self, application_id: UUID) -> list[OfficerRouteOverrides]:
        """依案件列出人工改線紀錄（新→舊）。"""
        with get_session() as session:
            rows = session.scalars(
                select(OfficerRouteOverrides)
                .where(OfficerRouteOverrides.application_id == application_id)
                .order_by(OfficerRouteOverrides.created_at.desc())
            ).all()
            return list(rows)

    def save(self, entity: OfficerRouteOverride) -> None:
        with get_session() as session:
            row = OfficerRouteOverrides(
                override_id=entity.override_id,
                application_id=entity.application_id,
                base_candidate_id=entity.base_candidate_id,
                override_geom=WKTElement(
                    route_geometry_linestring_to_wkt(entity.override_geom),
                    srid=4326,
                ),
                override_reason=entity.override_reason,
                created_by=entity.created_by,
                created_at=entity.created_at,
            )
            session.add(row)
