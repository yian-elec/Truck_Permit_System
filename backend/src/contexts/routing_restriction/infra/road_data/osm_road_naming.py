"""
OSM tags → 持久化／候選共用路名（與道路資料層計畫一致）。

規則定死：tags["name"] → tags["ref"] → fallback（預設「未命名道路」）。
"""

from __future__ import annotations

from typing import Any, Mapping

from shared.core.config import settings


def way_has_osm_name_or_ref(tags: Mapping[str, Any]) -> bool:
    """
    是否具備 road_name_from_osm_tags 所採用之 name 或 ref（非空字串）。

    不採 name:zh／name:en；與路名解析門檻一致，供 MVP 組圖時排除「僅 fallback」之 way。
    """

    name = tags.get("name")
    if isinstance(name, str) and name.strip():
        return True
    ref = tags.get("ref")
    if isinstance(ref, str) and ref.strip():
        return True
    return False


def road_name_from_osm_tags(tags: Mapping[str, Any]) -> str:
    """非空字串；不採 name:zh／name:en。"""
    fb = settings.osm_road_name_fallback
    name = tags.get("name")
    if isinstance(name, str) and name.strip():
        return name.strip()
    ref = tags.get("ref")
    if isinstance(ref, str) and ref.strip():
        return ref.strip()
    return fb


def road_ref_for_column(tags: Mapping[str, Any]) -> str | None:
    """僅 ref 欄位；無則 None。"""
    ref = tags.get("ref")
    if isinstance(ref, str) and ref.strip():
        return ref.strip()[:100]
    return None
