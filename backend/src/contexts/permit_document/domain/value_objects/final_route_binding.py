"""
FinalRouteBinding — 最終路線綁定值物件。

責任：落實規則「permit 需綁定最終路線」：在建立 Permit 時 **selected_candidate_id** 與 **override_id**
至少其一必須存在（對應「選定候選路線」或「承辦覆寫路線」）；兩者皆空則拒絕。
若兩者皆存在，語意上視為「在候選基礎上另有官方覆寫」，仍滿足「已綁定路線」；App 層可再限制互斥政策。
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from src.contexts.permit_document.domain.errors import PermitCreationPreconditionError


@dataclass(frozen=True)
class FinalRouteBinding:
    """
    許可證所依據之最終路線參照（不可變）。

    責任：保存 `selected_candidate_id`、`override_id`（皆可為 None，但不可兩者皆 None）。
    """

    selected_candidate_id: UUID | None
    override_id: UUID | None

    def __post_init__(self) -> None:
        if self.selected_candidate_id is None and self.override_id is None:
            raise PermitCreationPreconditionError(
                "Permit must bind a final route: "
                "at least one of selected_candidate_id or override_id is required"
            )
