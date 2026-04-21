"""
管理端：限制規則 CRUD 狀態、圖資 layer 列表與發布。

責任：DTO ↔ ORM 轉換、呼叫 RestrictionRulesRepository／MapLayersRepository；
幾何與時間窗子表維護由匯入流程或專用 API 擴充，此處僅處理主檔欄位。
"""

from __future__ import annotations

from uuid import UUID, uuid4

from src.contexts.routing_restriction.app.dtos.restriction_admin_dtos import (
    CreateRestrictionRuleInputDTO,
    MapLayerListItemDTO,
    PatchRestrictionRuleInputDTO,
    RestrictionRuleDetailDTO,
    RestrictionRuleListItemDTO,
)
from src.contexts.routing_restriction.app.errors import to_routing_app_error
from src.contexts.routing_restriction.infra.repositories.map_layers_repository import (
    MapLayersRepository,
)
from src.contexts.routing_restriction.infra.repositories.restriction_rules_repository import (
    RestrictionRulesRepository,
)
from src.contexts.routing_restriction.infra.schema.restriction_rules import RestrictionRules


class RestrictionAdminApplicationService:
    """限制規則與圖資 layer 管理服務。"""

    def __init__(
        self,
        *,
        rules: RestrictionRulesRepository | None = None,
        map_layers: MapLayersRepository | None = None,
    ) -> None:
        self._rules = rules or RestrictionRulesRepository()
        self._layers = map_layers or MapLayersRepository()

    def list_rules(
        self,
        *,
        layer_id: UUID | None = None,
        is_active: bool | None = None,
    ) -> list[RestrictionRuleListItemDTO]:
        rows = self._rules.list_rules(layer_id=layer_id, is_active=is_active)
        return [_rule_to_list_dto(r) for r in rows]

    def get_rule(self, rule_id: UUID) -> RestrictionRuleDetailDTO | None:
        row = self._rules.get_by_id(rule_id)
        if row is None:
            return None
        return _rule_to_detail_dto(row)

    def create_rule(self, dto: CreateRestrictionRuleInputDTO) -> RestrictionRuleDetailDTO:
        try:
            rid = uuid4()
            row = RestrictionRules(
                rule_id=rid,
                layer_id=dto.layer_id,
                rule_name=dto.rule_name,
                rule_type=dto.rule_type,
                weight_limit_ton=dto.weight_limit_ton,
                direction=dto.direction,
                time_rule_text=dto.time_rule_text,
                effective_from=dto.effective_from,
                effective_to=dto.effective_to,
                priority=dto.priority,
                is_active=True,
            )
            self._rules.save_standalone(row)
            loaded = self._rules.get_by_id(rid)
            if loaded is None:
                raise LookupError("restriction rule not found after create")
            return _rule_to_detail_dto(loaded)
        except Exception as exc:
            raise to_routing_app_error(exc) from exc

    def patch_rule(
        self,
        rule_id: UUID,
        dto: PatchRestrictionRuleInputDTO,
    ) -> RestrictionRuleDetailDTO | None:
        try:
            updated = self._rules.patch_fields(
                rule_id,
                rule_name=dto.rule_name,
                weight_limit_ton=dto.weight_limit_ton,
                priority=dto.priority,
                time_rule_text=dto.time_rule_text,
                effective_from=dto.effective_from,
                effective_to=dto.effective_to,
            )
            if updated is None:
                return None
            loaded = self._rules.get_by_id(rule_id)
            return _rule_to_detail_dto(loaded) if loaded else None
        except Exception as exc:
            raise to_routing_app_error(exc) from exc

    def activate_rule(self, rule_id: UUID) -> RestrictionRuleDetailDTO | None:
        try:
            row = self._rules.set_active(rule_id, is_active=True)
            if row is None:
                return None
            loaded = self._rules.get_by_id(rule_id)
            return _rule_to_detail_dto(loaded) if loaded else None
        except Exception as exc:
            raise to_routing_app_error(exc) from exc

    def deactivate_rule(self, rule_id: UUID) -> RestrictionRuleDetailDTO | None:
        try:
            row = self._rules.set_active(rule_id, is_active=False)
            if row is None:
                return None
            loaded = self._rules.get_by_id(rule_id)
            return _rule_to_detail_dto(loaded) if loaded else None
        except Exception as exc:
            raise to_routing_app_error(exc) from exc

    def list_map_layers(self) -> list[MapLayerListItemDTO]:
        rows = self._layers.list_all_recent()
        return [
            MapLayerListItemDTO(
                layer_id=r.layer_id,
                layer_code=r.layer_code,
                layer_name=r.layer_name,
                version_no=r.version_no,
                is_active=bool(r.is_active),
                published_at=r.published_at,
            )
            for r in rows
        ]

    def publish_map_layer(self, layer_id: UUID) -> MapLayerListItemDTO | None:
        try:
            row = self._layers.publish_layer(layer_id)
            if row is None:
                return None
            return MapLayerListItemDTO(
                layer_id=row.layer_id,
                layer_code=row.layer_code,
                layer_name=row.layer_name,
                version_no=row.version_no,
                is_active=bool(row.is_active),
                published_at=row.published_at,
            )
        except Exception as exc:
            raise to_routing_app_error(exc) from exc


def _rule_to_list_dto(row: RestrictionRules) -> RestrictionRuleListItemDTO:
    return RestrictionRuleListItemDTO(
        rule_id=row.rule_id,
        layer_id=row.layer_id,
        rule_name=row.rule_name,
        rule_type=row.rule_type,
        weight_limit_ton=row.weight_limit_ton,
        priority=row.priority,
        is_active=bool(row.is_active),
        updated_at=row.updated_at,
    )


def _rule_to_detail_dto(row: RestrictionRules) -> RestrictionRuleDetailDTO:
    return RestrictionRuleDetailDTO(
        rule_id=row.rule_id,
        layer_id=row.layer_id,
        rule_name=row.rule_name,
        rule_type=row.rule_type,
        weight_limit_ton=row.weight_limit_ton,
        direction=row.direction,
        time_rule_text=row.time_rule_text,
        effective_from=row.effective_from,
        effective_to=row.effective_to,
        priority=row.priority,
        is_active=bool(row.is_active),
        created_at=row.created_at,
        updated_at=row.updated_at,
    )
