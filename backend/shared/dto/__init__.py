"""
shared dto - 共用 DTO
提供跨 context 的共用資料傳輸物件
"""

from shared.dto.pagination import PaginatedMeta, PaginationParams
from shared.dto.standard_response import ErrorBody, StandardResponse

__all__ = [
    "PaginationParams",
    "PaginatedMeta",
    "ErrorBody",
    "StandardResponse",
]
