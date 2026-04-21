"""
KML 2.2 XML → 中介 placemark 結構（不含規則分類）。
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import List, Sequence, Tuple


def _local_tag(tag: str) -> str:
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


CoordRing = List[Tuple[float, float]]  # lon, lat


@dataclass
class ParsedPlacemark:
    """單一 Placemark 與其幾何（可多塊）。"""

    name: str
    description: str
    folder_trail: Tuple[str, ...]
    # (geometry_tag_lower, rings) — polygon: one ring or multiple for multipolygon parts as separate items
    geometry_parts: List[Tuple[str, List[CoordRing]]] = field(default_factory=list)


@dataclass
class ParsedKmlDocument:
    document_name: str
    placemarks: List[ParsedPlacemark]


def _parse_coord_triplets(text: str) -> CoordRing:
    """KML coordinates: lon,lat,alt triplets separated by whitespace (comma inside each triplet)."""
    ring: CoordRing = []
    for chunk in re.split(r"\s+", text.strip()):
        chunk = chunk.strip()
        if not chunk:
            continue
        parts = chunk.split(",")
        if len(parts) < 2:
            continue
        lon = float(parts[0])
        lat = float(parts[1])
        ring.append((lon, lat))
    return ring


def _rings_for_polygon(el: ET.Element) -> List[CoordRing]:
    rings: List[CoordRing] = []
    for lr in el.iter():
        if _local_tag(lr.tag).lower() != "linearring":
            continue
        for coord in lr.iter():
            if _local_tag(coord.tag).lower() == "coordinates":
                if coord.text:
                    r = _parse_coord_triplets(coord.text)
                    if len(r) >= 4:
                        rings.append(r)
    return rings


def _linestring_coords(el: ET.Element) -> CoordRing | None:
    for coord in el.iter():
        if _local_tag(coord.tag).lower() == "coordinates" and coord.text:
            r = _parse_coord_triplets(coord.text)
            if len(r) >= 2:
                return r
    return None


def _collect_geometries(
    node: ET.Element,
    parts: List[Tuple[str, List[CoordRing]]],
) -> None:
    tag = _local_tag(node.tag).lower()
    if tag == "polygon":
        rings = _rings_for_polygon(node)
        if rings:
            parts.append(("polygon", rings))
        return
    if tag == "linestring":
        line = _linestring_coords(node)
        if line:
            parts.append(("linestring", [line]))
        return
    if tag == "multigeometry":
        for child in list(node):
            _collect_geometries(child, parts)
        return
    if tag == "point":
        return
    for child in list(node):
        _collect_geometries(child, parts)


def _placemark_from_element(
    el: ET.Element,
    folder_trail: Tuple[str, ...],
) -> ParsedPlacemark | None:
    name = ""
    desc = ""
    for ch in el:
        lt = _local_tag(ch.tag).lower()
        if lt == "name" and ch.text:
            name = ch.text.strip()
        elif lt == "description" and ch.text:
            desc = ch.text.strip()

    parts: List[Tuple[str, List[CoordRing]]] = []
    for ch in el:
        lt = _local_tag(ch.tag).lower()
        if lt in ("polygon", "linestring", "multigeometry"):
            _collect_geometries(ch, parts)

    if not parts:
        return None
    return ParsedPlacemark(
        name=name or "(未命名)",
        description=desc,
        folder_trail=folder_trail,
        geometry_parts=parts,
    )


def _walk(
    el: ET.Element,
    folder_trail: Tuple[str, ...],
    out: List[ParsedPlacemark],
) -> None:
    tag = _local_tag(el.tag).lower()
    if tag == "folder":
        fname = ""
        rest: List[ET.Element] = []
        for ch in el:
            if _local_tag(ch.tag).lower() == "name" and ch.text:
                fname = ch.text.strip()
            else:
                rest.append(ch)
        trail = folder_trail + (fname,) if fname else folder_trail
        for ch in rest:
            _walk(ch, trail, out)
        return

    if tag == "placemark":
        pm = _placemark_from_element(el, folder_trail)
        if pm:
            out.append(pm)
        return

    for ch in el:
        _walk(ch, folder_trail, out)


def parse_kml(xml_text: str) -> ParsedKmlDocument:
    root = ET.fromstring(xml_text)
    doc_name = "imported_kml"
    placemarks: List[ParsedPlacemark] = []

    # Find Document or use root
    doc_el = root
    if _local_tag(root.tag).lower() == "kml":
        for ch in root:
            if _local_tag(ch.tag).lower() == "document":
                doc_el = ch
                break
    if _local_tag(doc_el.tag).lower() == "document":
        for ch in doc_el:
            if _local_tag(ch.tag).lower() == "name" and ch.text:
                doc_name = ch.text.strip()[:200]
                break

    start = doc_el if _local_tag(doc_el.tag).lower() == "document" else root
    for ch in start:
        _walk(ch, tuple(), placemarks)

    return ParsedKmlDocument(document_name=doc_name, placemarks=placemarks)
