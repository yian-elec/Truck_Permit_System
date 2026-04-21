"""
Nominatim（OSM）地理編碼 Adapter。

與 UC-ROUTE-01 GeocodingPort 對齊；須遵守
https://operations.osmfoundation.org/policies/nominatim/（自訂 User-Agent、合理逾時）。

**結果選取（第一版定版）**

- 請求固定 ``limit=1``。
- 若 API 仍回傳多筆：只取 JSON 陣列**第一筆**，不重排、不做距離二次排序、不做 POI 啟發式。
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from src.contexts.routing_restriction.app.services.ports.outbound import GeocodeResolution
from src.contexts.routing_restriction.domain.value_objects.geo_point import GeoPoint

logger = logging.getLogger(__name__)


def _parse_first_lat_lon(data: Any) -> tuple[float, float] | None:
    if not isinstance(data, list) or len(data) == 0:
        return None
    first: Any = data[0]
    if not isinstance(first, dict):
        return None
    raw_lat = first.get("lat")
    raw_lon = first.get("lon")
    if raw_lat is None or raw_lon is None:
        return None
    try:
        return float(raw_lat), float(raw_lon)
    except (TypeError, ValueError):
        return None


class NominatimGeocodingPort:
    """以 Nominatim ``/search`` API 解析地址文字為 WGS84 單點。"""

    def __init__(
        self,
        *,
        base_url: str,
        timeout_s: float,
        user_agent: str,
    ) -> None:
        self._base = base_url.rstrip("/")
        self._timeout = timeout_s
        self._user_agent = user_agent.strip()

    def resolve_point(self, address_text: str) -> GeocodeResolution:
        if not (address_text or "").strip():
            return GeocodeResolution(
                None, failure_reason="geocoding_failed: nominatim_no_result"
            )

        params = {
            "q": address_text.strip(),
            "format": "jsonv2",
            "limit": 1,
        }
        headers = {"User-Agent": self._user_agent}

        try:
            with httpx.Client(timeout=self._timeout) as client:
                r = client.get(f"{self._base}/search", params=params, headers=headers)
        except httpx.TimeoutException as exc:
            logger.warning("nominatim timeout: %s", exc)
            return GeocodeResolution(
                None, failure_reason="geocoding_failed: nominatim_timeout"
            )
        except httpx.RequestError as exc:
            logger.warning("nominatim request error: %s", exc)
            return GeocodeResolution(
                None, failure_reason="geocoding_failed: nominatim_http_error"
            )

        if r.status_code != 200:
            logger.warning(
                "nominatim http %s: %s",
                r.status_code,
                (r.text or "")[:200],
            )
            return GeocodeResolution(
                None, failure_reason="geocoding_failed: nominatim_http_error"
            )

        try:
            data = r.json()
        except ValueError as exc:
            logger.warning("nominatim invalid json: %s", exc)
            return GeocodeResolution(
                None, failure_reason="geocoding_failed: nominatim_http_error"
            )

        lat_lon = _parse_first_lat_lon(data)
        if lat_lon is None:
            return GeocodeResolution(
                None, failure_reason="geocoding_failed: nominatim_no_result"
            )
        lat, lon = lat_lon
        return GeocodeResolution(GeoPoint(latitude=lat, longitude=lon), None)
