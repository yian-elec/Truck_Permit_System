"""
KML 匯入管線：loader → parser → writer。
"""

from __future__ import annotations

import json

from src.contexts.routing_restriction.infra.kml.loader import load_kml_xml
from src.contexts.routing_restriction.infra.kml.parser import parse_kml
from src.contexts.routing_restriction.infra.kml.writer import write_kml_import


def run_kml_import(source_ref: str) -> str:
    """
    執行完整匯入，回傳人類可讀摘要（供 ops.import_jobs.result_summary）。
    """
    xml_text = load_kml_xml(source_ref)
    parsed = parse_kml(xml_text)
    result = write_kml_import(parsed)
    summary = {
        "layer_id": result["layer_id"],
        "layer_code": result["layer_code"],
        "version_no": result["version_no"],
        "rules": result["stats"]["rules"],
        "geometries": result["stats"]["geometries"],
        "time_windows": result["stats"]["time_windows"],
    }
    return json.dumps(summary, ensure_ascii=False)
