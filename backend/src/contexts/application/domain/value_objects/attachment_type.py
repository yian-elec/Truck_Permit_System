"""
附件類型代碼（Value Object）。

責任：對應 application.attachments.attachment_type 與 checklist item 所要求之文件類型，
集中長度與字元約束，避免空字串或過長代碼進入聚合。
"""

from __future__ import annotations

from dataclasses import dataclass

from ..errors import InvalidDomainValueError


@dataclass(frozen=True)
class AttachmentType:
    """
    附件類型之穩定代碼（例如身分證明、行照）。

    責任：與「必備附件未齊不得送件」之 checklist／上傳清單比對時使用同一型別。
    """

    code: str

    def __post_init__(self) -> None:
        c = (self.code or "").strip()
        if not c or len(c) > 50:
            raise InvalidDomainValueError(
                "AttachmentType.code must be non-empty and at most 50 characters",
            )
        object.__setattr__(self, "code", c)
