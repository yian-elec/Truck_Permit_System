"""
依 Settings 組裝 UC-ROUTE-01 使用之 GeocodingPort（stub / Nominatim）。
"""

from __future__ import annotations

from shared.core.config import settings

from src.contexts.routing_restriction.app.services.ports.outbound import (
    GeocodingPort,
    StubGeocodingPort,
)
from src.contexts.routing_restriction.infra.geocoding.nominatim_geocoding_port import (
    NominatimGeocodingPort,
)


def build_geocoding_port_from_settings() -> GeocodingPort:
    if settings.geocoding_mode == "nominatim":
        ua = (settings.nominatim_user_agent or "").strip()
        if not ua:
            raise ValueError(
                "NOMINATIM_USER_AGENT is required when GEOCODING_MODE=nominatim "
                "(see https://operations.osmfoundation.org/policies/nominatim/)"
            )
        return NominatimGeocodingPort(
            base_url=settings.nominatim_base_url,
            timeout_s=settings.nominatim_timeout_s,
            user_agent=ua,
        )
    return StubGeocodingPort()
