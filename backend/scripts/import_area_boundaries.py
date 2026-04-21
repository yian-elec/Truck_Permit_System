#!/usr/bin/env python3
"""
將行政區界 GeoJSON（FeatureCollection）寫入 `routing.area_boundaries`。

前置：PostgreSQL + PostGIS、已執行 init_db 建表。

範例（內政部開放資料 Shapefile 先轉 WGS84 GeoJSON）::

  ogr2ogr -f GeoJSON -t_srs EPSG:4326 towns.geojson TOWN_MOI.shp
  python scripts/import_area_boundaries.py --geojson towns.geojson --name-key TOWNNAME

若無 name-key，預設依序嘗試 TOWNNAME、COUNTYNAME、name。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from uuid import uuid4

from sqlalchemy import text

from shared.core.db.connection import get_session


def _pick_name(props: dict, name_key: str | None) -> str:
    if name_key and props.get(name_key):
        return str(props[name_key]).strip()[:100]
    for k in ("TOWNNAME", "COUNTYNAME", "name"):
        v = props.get(k)
        if v and str(v).strip():
            return str(v).strip()[:100]
    raise ValueError("無法自 properties 取得區名，請傳 --name-key")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--geojson", required=True, type=Path, help="GeoJSON 檔案路徑")
    p.add_argument("--name-key", default=None, help="區名字段（properties）")
    p.add_argument("--source-type", default="ogr_import", help="寫入 source_type")
    p.add_argument("--source-ref", default="", help="寫入 source_ref（可為檔名）")
    args = p.parse_args()

    raw = json.loads(args.geojson.read_text(encoding="utf-8"))
    feats = raw.get("features") or []
    if not feats:
        print("GeoJSON 無 features", file=sys.stderr)
        return 1

    ref = args.source_ref or args.geojson.name
    inserted = 0
    with get_session() as session:
        for feat in feats:
            geom = feat.get("geometry")
            props = feat.get("properties") or {}
            if not geom:
                continue
            name = _pick_name(props, args.name_key)
            gj = json.dumps(geom, separators=(",", ":"))
            aid = uuid4()
            session.execute(
                text(
                    """
                    INSERT INTO routing.area_boundaries
                      (area_id, area_name, area_code, geom, is_active, source_type, source_ref)
                    VALUES
                      (:id, :name, :code,
                       ST_Multi(ST_SetSRID(ST_GeomFromGeoJSON(:gj), 4326)),
                       true, :st, :ref)
                    """
                ),
                {
                    "id": aid,
                    "name": name,
                    "code": props.get("TOWNCODE") or props.get("code"),
                    "gj": gj,
                    "st": args.source_type[:30],
                    "ref": ref[:255] if ref else None,
                },
            )
            inserted += 1
    print(f"inserted {inserted} rows into routing.area_boundaries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
