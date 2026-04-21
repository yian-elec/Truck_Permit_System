"""
shared/api - 共用 API 模組
提供統一的 API 回應格式和錯誤處理
"""

from .api_wrapper import APIResponse, api_response, api_response_with_logging
from .responses import (
    combine_responses,
    error_response,
    get_swagger_jwt_example,
    success_response,
)

__all__ = [
    "api_response",
    "api_response_with_logging",
    "APIResponse",
    "success_response",
    "error_response",
    "combine_responses",
    "get_swagger_jwt_example",
]
