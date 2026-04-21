"""
案件編號產生（App 層）。

責任：產生符合 schema `application_no varchar(30) unique` 之字串；實務可改接序號表或 Redis。
"""

from __future__ import annotations

from datetime import datetime, timezone


def generate_application_no() -> str:
    """
    產生新的對外案件編號。

    責任：格式 HTP-YYYYMMDD-XXXXXXXX（總長度 < 30）；碰撞機率極低，仍建議搭配 DB unique 重試。
    """
    day = datetime.now(timezone.utc).strftime("%Y%m%d")
    from uuid import uuid4

    suffix = uuid4().hex[:8].upper()
    return f"HTP-{day}-{suffix}"
