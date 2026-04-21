"""
NoRouteExplanation — 無可行路線時之結構化說明（值物件）。

責任：滿足「無可行路線時要回傳原因，不可只回空」之產品規則；與 RoutePlan 之 NO_ROUTE
狀態並存，供 API 直接序列化。
"""

from __future__ import annotations

from dataclasses import dataclass

from .routing_enums import NoRouteReasonCode


@dataclass(frozen=True)
class NoRouteExplanation:
    """
    無路原因碼與人類可讀訊息。

    責任：**code** 供程式分支與 i18n 鍵；**message** 為預設展示字串（可含技術細節摘要）。
    """

    code: NoRouteReasonCode
    message: str
