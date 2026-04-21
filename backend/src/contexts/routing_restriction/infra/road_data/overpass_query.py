"""Overpass QL 組字（highway ways + out geom）。"""


def build_overpass_highway_query(
    south: float,
    west: float,
    north: float,
    east: float,
    *,
    timeout_s: int = 60,
) -> str:
    return (
        f"[out:json][timeout:{timeout_s}];\n"
        f'(\n  way["highway"]({south},{west},{north},{east});\n);\n'
        "out geom;\n"
    )
