"""UC-ROUTE-01 地理編碼 Infra（Nominatim 等）。"""

from src.contexts.routing_restriction.infra.geocoding.geocoding_factory import (
    build_geocoding_port_from_settings,
)

__all__ = ["build_geocoding_port_from_settings"]
