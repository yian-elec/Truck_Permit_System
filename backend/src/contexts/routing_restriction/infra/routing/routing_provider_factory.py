"""
依 Settings 組裝 UC-ROUTE-02 使用之 RoutingProviderPort（original / mvp）。
"""

from __future__ import annotations

from shared.core.config import settings

from src.contexts.routing_restriction.app.services.ports.outbound import (
    RoutingProviderPort,
    StubRoutingProviderPort,
)
from src.contexts.routing_restriction.infra.routing.mvp_routing_provider_port import (
    MvpRoutingProviderPort,
)


def build_routing_provider_from_settings() -> RoutingProviderPort:
    if settings.routing_mode == "mvp":
        return MvpRoutingProviderPort(
            overpass_url=settings.overpass_url,
            timeout_s=settings.overpass_timeout_s,
        )
    return StubRoutingProviderPort()
