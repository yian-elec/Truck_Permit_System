"""出站埠（Geocoding、路網、空間檢核）匯出。"""

from .outbound import (
    GeocodeResolution,
    GeocodingPort,
    NoopSpatialRuleHitPort,
    RoutingProviderPort,
    SpatialRuleHitPort,
    StubGeocodingPort,
    StubRoutingProviderPort,
)

__all__ = [
    "GeocodeResolution",
    "GeocodingPort",
    "NoopSpatialRuleHitPort",
    "RoutingProviderPort",
    "SpatialRuleHitPort",
    "StubGeocodingPort",
    "StubRoutingProviderPort",
]
