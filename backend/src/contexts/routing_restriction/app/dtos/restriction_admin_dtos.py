"""
管理端限制規則與圖資 layer 相關 DTO。

責任：對齊 Admin API 契約之輸入輸出。
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RestrictionRuleListItemDTO(BaseModel):
    """規則列表項。"""

    rule_id: UUID
    layer_id: UUID
    rule_name: str
    rule_type: str
    weight_limit_ton: Decimal | None
    priority: int
    is_active: bool
    updated_at: datetime


class RestrictionRuleDetailDTO(BaseModel):
    """規則明細。"""

    rule_id: UUID
    layer_id: UUID
    rule_name: str
    rule_type: str
    weight_limit_ton: Decimal | None
    direction: str | None
    time_rule_text: str | None
    effective_from: date | None
    effective_to: date | None
    priority: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class CreateRestrictionRuleInputDTO(BaseModel):
    """建立規則（最小欄位；幾何另由匯入或後續 API 附加）。"""

    model_config = ConfigDict(str_strip_whitespace=True)

    layer_id: UUID
    rule_name: str = Field(..., min_length=1, max_length=255)
    rule_type: str = Field(..., min_length=1, max_length=50)
    weight_limit_ton: Decimal | None = None
    direction: str | None = Field(None, max_length=20)
    time_rule_text: str | None = None
    effective_from: date | None = None
    effective_to: date | None = None
    priority: int = Field(100, ge=0)


class PatchRestrictionRuleInputDTO(BaseModel):
    """部分更新規則。"""

    model_config = ConfigDict(str_strip_whitespace=True)

    rule_name: str | None = Field(None, max_length=255)
    weight_limit_ton: Decimal | None = None
    priority: int | None = Field(None, ge=0)
    time_rule_text: str | None = None
    effective_from: date | None = None
    effective_to: date | None = None


class MapLayerListItemDTO(BaseModel):
    """圖資 layer 列表項。"""

    layer_id: UUID
    layer_code: str
    layer_name: str
    version_no: str
    is_active: bool
    published_at: datetime | None
