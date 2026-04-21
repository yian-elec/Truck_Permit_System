"""
將路段 (路名, 區名) 序列壓縮為可讀 `area_road_sequence`（純函式、無 I/O）。
"""

from __future__ import annotations


def format_area_road_sequence(
    items: list[tuple[str | None, str | None]],
    *,
    unnamed_label: str,
) -> list[str]:
    """
    - 換區且區名有值時先輸出區名，再輸出路名。
    - 同區連續同名路合併為單一條目。
    - 僅連續同區且路名相同（含皆為未命名）時合併；不略過短未命名路段。
    - `area_name` 為 None 時不插入區名，仍輸出路名。
    """
    out: list[str] = []
    last_emitted_area: str | None = None
    prev_road: str | None = None
    prev_area: str | None = None

    for road_name, area_name in items:
        r = (road_name or "").strip() or unnamed_label
        a = area_name.strip() if area_name and area_name.strip() else None

        if a is not None and a != last_emitted_area:
            out.append(a)
            last_emitted_area = a

        if prev_road is not None and r == prev_road and a == prev_area:
            continue
        out.append(r)
        prev_road = r
        prev_area = a

    return out
