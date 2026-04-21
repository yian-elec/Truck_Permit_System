"""
Page Model 契約版本（Value Object）。

責任：讓前端與 App 層能對「同一 API 路徑下區塊集合是否演進」做快取失效或相容處理；
領域上僅保證為正整數 semver 式主版本，不涉 HTTP。
"""

from __future__ import annotations

from dataclasses import dataclass

from ..errors import InvalidPageModelCompositionError


@dataclass(frozen=True, order=True)
class ModelContractVersion:
    """
    Page Model JSON 契約的主版本號。

    責任：聚合根在組版完成後攜帶此值，供回應本體標註；當區塊目錄有重大變更時應遞增。
    """

    major: int

    def __post_init__(self) -> None:
        if self.major < 1:
            raise InvalidPageModelCompositionError(
                "ModelContractVersion.major must be >= 1"
            )
