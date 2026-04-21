"""
依 geometry、Folder/Placemark 名稱與 description 做 MVP 規則分類與欄位抽取。
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional, Tuple

from src.contexts.routing_restriction.domain.value_objects.routing_enums import RuleType


_WEIGHT_RE = re.compile(r"(?P<n>\d+(?:\.\d+)?)\s*噸")


def extract_weight_ton(description: str, folder_trail: Tuple[str, ...]) -> Optional[Decimal]:
    text = " ".join(folder_trail) + " " + (description or "")
    m = _WEIGHT_RE.search(text)
    if m:
        try:
            return Decimal(m.group("n"))
        except Exception:
            return None
    return None


def infer_rule_type(
    geom_tag: str,
    name: str,
    description: str,
    folder_trail: Tuple[str, ...],
) -> RuleType:
    """geometry_tag: polygon | linestring"""
    blob = " ".join(folder_trail) + " " + name + " " + (description or "")
    low = blob.lower()
    if "不予管制" in blob or "得通行" in blob or ("例外" in blob and "禁行" not in blob):
        if geom_tag == "linestring":
            return RuleType.EXCEPTION_ROAD
    if "狭" in blob or "窄" in blob or "narrow" in low:
        if geom_tag == "linestring":
            return RuleType.NARROW_ROAD
    if geom_tag == "linestring":
        if "例外" in blob or "exception" in low:
            return RuleType.EXCEPTION_ROAD
        return RuleType.FORBIDDEN_ROAD
    # polygon default
    if "warning" in low or "警示" in blob:
        return RuleType.WARNING_ZONE
    return RuleType.FORBIDDEN_ZONE


def is_all_day_description(description: str) -> bool:
    d = (description or "").strip()
    if not d:
        return True
    if "全日" in d or "全天" in d:
        return True
    if re.search(r"禁行時段\s*[:：]\s*全日", d):
        return True
    return False


@dataclass
class ClassifiedRule:
    rule_type: RuleType
    rule_name: str
    weight_limit_ton: Optional[Decimal]
    time_rule_text: Optional[str]
    day_type: str
