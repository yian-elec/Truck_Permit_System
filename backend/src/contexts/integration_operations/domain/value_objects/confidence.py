"""
OCR 信心分數（Value Object）。

責任：對應 ops.ocr_results.confidence numeric(5,4)，語意為 0～1 的機率或信心，
於領域層拒絕超出範圍或精度不符的值。
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from ..errors import InvalidDomainValueError


@dataclass(frozen=True)
class Confidence:
    """
    不可變的信心分數，最多四位小數。

    用途：由 OCR 解析流程寫入 OcrResult，供下游規則判斷是否採信欄位值。
    """

    value: Decimal

    def __post_init__(self) -> None:
        v = self.value
        if not isinstance(v, Decimal):
            v = Decimal(str(v))
        if v < 0 or v > 1:
            raise InvalidDomainValueError("Confidence must be between 0 and 1 inclusive")
        quantized = v.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
        if quantized != v:
            raise InvalidDomainValueError("Confidence supports at most 4 decimal places")
        object.__setattr__(self, "value", quantized)

    @classmethod
    def from_float(cls, x: float) -> "Confidence":
        """由浮點數建立（仍受四位小數與範圍約束）。"""
        return cls(Decimal(str(x)))
