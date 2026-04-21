"""
將 ParsedKmlDocument 寫入 routing.map_layers、restriction_rules、rule_geometries、rule_time_windows。
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from geoalchemy2.elements import WKTElement

from shared.core.db.connection import get_session

from src.contexts.routing_restriction.infra.kml.classify import (
    ClassifiedRule,
    extract_weight_ton,
    infer_rule_type,
    is_all_day_description,
)
from src.contexts.routing_restriction.infra.kml.parser import CoordRing, ParsedKmlDocument
from src.contexts.routing_restriction.infra.schema.map_layers import MapLayers
from src.contexts.routing_restriction.infra.schema.restriction_rules import RestrictionRules
from src.contexts.routing_restriction.infra.schema.rule_geometries import RuleGeometries
from src.contexts.routing_restriction.infra.schema.rule_time_windows import RuleTimeWindows


def _ring_wkt(ring: CoordRing) -> str:
    pts = list(ring)
    if len(pts) >= 3 and pts[0] != pts[-1]:
        pts = pts + [pts[0]]
    return ",".join(f"{lon} {lat}" for lon, lat in pts)


def _polygon_wkt(rings: list[CoordRing]) -> str:
    if not rings:
        raise ValueError("empty polygon rings")
    # WKT: POLYGON((outer ring)[,(holes)...]) — each ring needs its own parentheses.
    rings_wkt = [f"({_ring_wkt(r)})" for r in rings]
    return "POLYGON(" + ",".join(rings_wkt) + ")"


def _linestring_wkt(line: CoordRing) -> str:
    if len(line) < 2:
        raise ValueError("linestring needs >= 2 points")
    body = ",".join(f"{lon} {lat}" for lon, lat in line)
    return f"LINESTRING({body})"


def _classify_placemark(pm, geom_kind: str) -> ClassifiedRule:
    rt = infer_rule_type(geom_kind, pm.name, pm.description, pm.folder_trail)
    wt = extract_weight_ton(pm.description, pm.folder_trail)
    trt = pm.description.strip() if pm.description else None
    day = "all" if is_all_day_description(pm.description) else "custom"
    return ClassifiedRule(
        rule_type=rt,
        rule_name=(pm.name or "rule")[:255],
        weight_limit_ton=wt,
        time_rule_text=trt,
        day_type=day,
    )


def write_kml_import(parsed: ParsedKmlDocument) -> dict:
    """
    單一交易寫入；回傳統計與 layer_id。

    每個 Placemark 一筆 restriction_rule；同一 Placemark 之多塊幾何寫入多筆 rule_geometries。
    """
    if not parsed.placemarks:
        raise ValueError("No placemarks with geometry found in KML")

    layer_id = uuid4()
    now = datetime.now(timezone.utc)
    ver = f"import-{now.strftime('%Y%m%dT%H%M%S')}"[:50]
    code = f"kml_{uuid4().hex[:12]}"[:50]
    layer_name = (parsed.document_name or "KML import")[:100]

    stats = {"rules": 0, "geometries": 0, "time_windows": 0, "warnings": []}

    with get_session() as session:
        layer = MapLayers(
            layer_id=layer_id,
            layer_code=code,
            layer_name=layer_name,
            layer_type="restriction_import",
            source_type="kml",
            source_ref=None,
            version_no=ver,
            is_active=False,
            published_at=None,
            created_at=now,
            updated_at=now,
        )
        session.add(layer)

        for pm in parsed.placemarks:
            first_kind = pm.geometry_parts[0][0].lower()
            geom_kind = "linestring" if first_kind == "linestring" else "polygon"
            cr = _classify_placemark(pm, geom_kind)

            rule_id = uuid4()
            rule = RestrictionRules(
                rule_id=rule_id,
                layer_id=layer_id,
                rule_name=cr.rule_name,
                rule_type=cr.rule_type.value,
                weight_limit_ton=cr.weight_limit_ton,
                direction="any",
                time_rule_text=cr.time_rule_text,
                effective_from=None,
                effective_to=None,
                priority=100,
                is_active=True,
                created_at=now,
                updated_at=now,
            )
            session.add(rule)
            stats["rules"] += 1

            for geom_tag, rings_data in pm.geometry_parts:
                gtag = geom_tag.lower()
                if gtag == "polygon":
                    wkt = _polygon_wkt(rings_data)
                    geom_el = WKTElement(wkt, srid=4326)
                    rg = RuleGeometries(
                        geometry_id=uuid4(),
                        rule_id=rule_id,
                        geom=geom_el,
                        bbox=None,
                        created_at=now,
                    )
                    session.add(rg)
                    stats["geometries"] += 1
                elif gtag == "linestring":
                    for line in rings_data:
                        wkt = _linestring_wkt(line)
                        geom_el = WKTElement(wkt, srid=4326)
                        rg = RuleGeometries(
                            geometry_id=uuid4(),
                            rule_id=rule_id,
                            geom=geom_el,
                            bbox=None,
                            created_at=now,
                        )
                        session.add(rg)
                        stats["geometries"] += 1

            tw = RuleTimeWindows(
                time_window_id=uuid4(),
                rule_id=rule_id,
                day_type=cr.day_type,
                start_time=None,
                end_time=None,
                month_mask=None,
                exclude_holiday=False,
                note=None,
                created_at=now,
            )
            session.add(tw)
            stats["time_windows"] += 1

        session.commit()

    return {
        "layer_id": str(layer_id),
        "layer_code": code,
        "version_no": ver,
        "stats": stats,
    }
