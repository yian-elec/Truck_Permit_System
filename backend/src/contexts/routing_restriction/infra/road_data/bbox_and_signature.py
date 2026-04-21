"""Bbox、query_signature、WKT 輔助（道路資料層）。"""

from __future__ import annotations

import hashlib
import json

from src.contexts.routing_restriction.domain.value_objects.geo_point import GeoPoint


def bbox_pad(
    origin: GeoPoint,
    destination: GeoPoint,
    *,
    pad_deg: float,
) -> tuple[float, float, float, float]:
    south = min(origin.latitude, destination.latitude) - pad_deg
    north = max(origin.latitude, destination.latitude) + pad_deg
    west = min(origin.longitude, destination.longitude) - pad_deg
    east = max(origin.longitude, destination.longitude) + pad_deg
    return south, west, north, east


def bbox_polygon_wkt(south: float, west: float, north: float, east: float) -> str:
    return (
        f"POLYGON(({west} {south}, {east} {south}, {east} {north}, {west} {north}, {west} {south}))"
    )


def point_wkt(lon: float, lat: float) -> str:
    return f"POINT({lon} {lat})"


def compute_query_signature(
    origin: GeoPoint,
    destination: GeoPoint,
    south: float,
    west: float,
    north: float,
    east: float,
    *,
    query_version: str,
) -> str:
    payload = {
        "o_lat": round(origin.latitude, 7),
        "o_lon": round(origin.longitude, 7),
        "d_lat": round(destination.latitude, 7),
        "d_lon": round(destination.longitude, 7),
        "south": round(south, 7),
        "west": round(west, 7),
        "north": round(north, 7),
        "east": round(east, 7),
        "qv": query_version,
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:64]
