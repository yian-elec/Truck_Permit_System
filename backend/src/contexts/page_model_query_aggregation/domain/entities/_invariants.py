"""
Page Model 聚合共用不變條件（純領域函式）。

責任：集中檢查區塊代碼唯一、排序唯一、前置依賴封閉於聚合內，避免四個聚合根重複實作。
"""

from __future__ import annotations

from ..errors import (
    DuplicateSectionOrderError,
    InvalidPageModelCompositionError,
    PrerequisiteSectionMissingError,
)
from .page_model_section_spec import PageModelSectionSpec


def assert_closed_section_graph(sections: tuple[PageModelSectionSpec, ...]) -> None:
    """
    斷言區塊列表滿足聚合不變條件。

    責任：
    - 區塊代碼不重複
    - 排序序號不重複
    - 各區塊之前置區塊均存在於同一列表中
    """
    if not sections:
        raise InvalidPageModelCompositionError("Page model must contain at least one section")

    codes = [s.section_code for s in sections]
    if len(codes) != len(set(codes)):
        raise InvalidPageModelCompositionError("Duplicate PageSectionCode in same page model")

    orders = [s.sort_order for s in sections]
    if len(orders) != len(set(orders)):
        dup = next(o for o in orders if orders.count(o) > 1)
        raise DuplicateSectionOrderError(
            f"Duplicate sort_order {dup} in page model",
            sort_order=dup,
        )

    code_set = set(codes)
    for spec in sections:
        for pre in spec.prerequisite_section_codes:
            if pre not in code_set:
                raise PrerequisiteSectionMissingError(
                    f"Section {spec.section_code.value} requires prerequisite {pre.value}",
                    section=spec.section_code.value,
                    missing_prerequisite=pre.value,
                )
