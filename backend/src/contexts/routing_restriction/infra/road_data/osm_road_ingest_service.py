"""
Overpass 抓取 → road_source_batches + road_edges 持久化。
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, List, Mapping, Optional
from uuid import UUID, uuid4

import httpx
from geoalchemy2.elements import WKTElement
from sqlalchemy import func, select

from shared.core.config import settings
from shared.core.db.connection import get_session
from shared.core.logger.logger import logger

from src.contexts.routing_restriction.domain.value_objects.geo_point import GeoPoint
from src.contexts.routing_restriction.infra.road_data.bbox_and_signature import (
    bbox_pad,
    bbox_polygon_wkt,
    compute_query_signature,
    point_wkt,
)
from src.contexts.routing_restriction.infra.road_data.osm_way_parser import try_parse_way_for_road_edge
from src.contexts.routing_restriction.infra.road_data.overpass_query import (
    build_overpass_highway_query,
)
from src.contexts.routing_restriction.infra.schema.road_edges import RoadEdges
from src.contexts.routing_restriction.infra.schema.road_source_batches import RoadSourceBatches

SOURCE_OSM_OVERPASS = "osm_overpass"


class OsmRoadIngestService:
    """道路資料層：抓 OSM、寫 batches／edges。"""

    def __init__(
        self,
        *,
        overpass_url: str | None = None,
        timeout_s: float | None = None,
        client: httpx.Client | None = None,
    ) -> None:
        self._url = overpass_url or settings.overpass_url
        self._timeout = timeout_s if timeout_s is not None else settings.overpass_timeout_s
        self._own_client = client is None
        self._client = client or httpx.Client(timeout=self._timeout)

    def close(self) -> None:
        if self._own_client:
            self._client.close()

    def fetch_parse_and_persist(
        self,
        origin: GeoPoint,
        destination: GeoPoint,
    ) -> tuple[UUID | None, str | None]:
        """
        回傳 (batch_id, ingest_error)。

        成功時 ingest_error 為 None；失敗時 batch_id 為 None，ingest_error 為簡短說明（供 no_route 展示）。
        """
        pad = settings.road_fetch_bbox_pad_deg
        south, west, north, east = bbox_pad(origin, destination, pad_deg=pad)
        sig = compute_query_signature(
            origin,
            destination,
            south,
            west,
            north,
            east,
            query_version=settings.overpass_query_version,
        )
        poly_wkt = bbox_polygon_wkt(south, west, north, east)
        o_wkt = point_wkt(origin.longitude, origin.latitude)
        d_wkt = point_wkt(destination.longitude, destination.latitude)
        timeout_int = max(1, int(self._timeout))
        query = build_overpass_highway_query(south, west, north, east, timeout_s=timeout_int)
        now = datetime.now(timezone.utc)

        try:
            r = self._client.post(
                self._url,
                content=query.encode("utf-8"),
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            r.raise_for_status()
            payload = r.json()
        except (httpx.HTTPError, ValueError, TypeError) as e:
            logger.warn(
                f"Overpass fetch failed: {e}",
                context="Routing",
                overpass_url=self._url,
            )
            self._insert_failed_batch(
                sig=sig,
                poly_wkt=poly_wkt,
                o_wkt=o_wkt,
                d_wkt=d_wkt,
                query_text=query,
                now=now,
                error=str(e)[:2000],
            )
            return None

        elements = list(payload.get("elements") or [])
        logger.info(
            "Overpass response received",
            context="Routing",
            element_count=len(elements),
            query_signature_prefix=sig[:16],
        )
        bid = self._persist_success(
            elements=elements,
            sig=sig,
            poly_wkt=poly_wkt,
            o_wkt=o_wkt,
            d_wkt=d_wkt,
            query_text=query,
            now=now,
        )
        return bid, None

    def _insert_failed_batch(
        self,
        *,
        sig: str,
        poly_wkt: str,
        o_wkt: str,
        d_wkt: str,
        query_text: str,
        now: datetime,
        error: str,
    ) -> None:
        batch_id = uuid4()
        with get_session() as session:
            b = RoadSourceBatches(
                batch_id=batch_id,
                source_type=SOURCE_OSM_OVERPASS,
                query_signature=sig,
                bbox_geom=WKTElement(poly_wkt, srid=4326),
                origin_point=WKTElement(o_wkt, srid=4326),
                destination_point=WKTElement(d_wkt, srid=4326),
                query_text=query_text,
                source_generated_at=None,
                fetched_at=now,
                status="failed",
                record_count=0,
                parse_skipped_count=0,
                error_message=error,
                created_at=now,
                updated_at=now,
            )
            session.add(b)

    def _persist_success(
        self,
        *,
        elements: List[Mapping[str, Any]],
        sig: str,
        poly_wkt: str,
        o_wkt: str,
        d_wkt: str,
        query_text: str,
        now: datetime,
    ) -> UUID:
        batch_id = uuid4()
        skipped = 0
        rows: List[dict[str, Any]] = []
        seen_way: set[int] = set()

        for el in elements:
            if el.get("type") != "way":
                continue
            parsed, did_skip = try_parse_way_for_road_edge(el)
            if did_skip or parsed is None:
                skipped += 1
                continue
            wid = parsed["osm_way_id"]
            if wid in seen_way:
                skipped += 1
                continue
            seen_way.add(wid)
            rows.append(parsed)

        with get_session() as session:
            batch = RoadSourceBatches(
                batch_id=batch_id,
                source_type=SOURCE_OSM_OVERPASS,
                query_signature=sig,
                bbox_geom=WKTElement(poly_wkt, srid=4326),
                origin_point=WKTElement(o_wkt, srid=4326),
                destination_point=WKTElement(d_wkt, srid=4326),
                query_text=query_text,
                source_generated_at=None,
                fetched_at=now,
                status="parsed",
                record_count=len(rows),
                parse_skipped_count=skipped,
                error_message=None,
                created_at=now,
                updated_at=now,
            )
            session.add(batch)
            session.flush()

            for p in rows:
                eid = uuid4()
                bbox_el = WKTElement(p["bbox_wkt"], srid=4326) if p.get("bbox_wkt") else None
                re = RoadEdges(
                    road_edge_id=eid,
                    batch_id=batch_id,
                    source_type=SOURCE_OSM_OVERPASS,
                    osm_element_type=p["osm_element_type"],
                    osm_way_id=p["osm_way_id"],
                    segment_index=p["segment_index"],
                    road_name=p["road_name"],
                    road_ref=p["road_ref"],
                    highway_type=p["highway_type"],
                    geom=WKTElement(p["line_wkt"], srid=4326),
                    bbox_geom=bbox_el,
                    node_count=p["node_count"],
                    length_m=p["length_m"],
                    raw_tags_json=p["raw_tags_json"],
                    raw_payload_fragment=p["raw_payload_fragment"],
                    is_active=True,
                    fetched_at=now,
                    created_at=now,
                    updated_at=now,
                )
                session.add(re)
        logger.info(
            "road_edges persist ok",
            context="Routing",
            batch_id=str(batch_id),
            record_count=len(rows),
            parse_skipped_count=skipped,
        )
        return batch_id


def load_overpass_elements_for_batch(batch_id: UUID) -> List[Mapping[str, Any]]:
    """
    由 road_edges 還原可供 `parse_overpass_response_for_routing` 使用之 way elements（含 tags、geometry、nodes）。

    以 ST_AsText(geom) 還原座標，並組出與 Overpass 相近之 geometry 陣列。
    """
    from src.contexts.routing_restriction.infra.repositories.geometry_wkt import (
        parse_linestring_wkt,
    )

    out: List[Mapping[str, Any]] = []
    with get_session() as session:
        stmt = (
            select(
                RoadEdges.osm_way_id,
                RoadEdges.raw_tags_json,
                RoadEdges.raw_payload_fragment,
                func.ST_AsText(RoadEdges.geom).label("gwkt"),
            )
            .where(
                RoadEdges.batch_id == batch_id,
                RoadEdges.is_active.is_(True),
            )
            .order_by(RoadEdges.osm_way_id)
        )
        for row in session.execute(stmt):
            wkt = row.gwkt
            tags = dict(row.raw_tags_json or {})
            frag = row.raw_payload_fragment or {}
            nodes = frag.get("nodes")
            rg = parse_linestring_wkt(wkt)
            ring = rg.rings[0]
            geometry = [{"lat": p.latitude, "lon": p.longitude} for p in ring]
            if not nodes or len(nodes) != len(geometry):
                continue
            out.append(
                {
                    "type": "way",
                    "id": int(row.osm_way_id),
                    "nodes": nodes,
                    "tags": tags,
                    "geometry": geometry,
                }
            )
    return out
