"""
Routing_Restriction API — 回應包裝。

責任：成功回應之 Pydantic 模型以 `model_dump(mode="json")` 序列化後，交
`shared.api.api_response_with_logging` 產生統一 `{data, error}` 信封；`BaseError` 與其他例外
維持與 Application／Ops API 相同行為。
"""

from __future__ import annotations

from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse

from shared.api import api_response_with_logging
from shared.errors.base_error.base_error import BaseError


def routing_api_response(result: Any, request: Request) -> JSONResponse:
    """
    將用例結果或例外轉為 JSONResponse。

    - 單一 Pydantic 模型：JSON 相容 dict。
    - Pydantic 模型列表：逐筆 `model_dump(mode="json")`。
    - 其餘可 JSON 序列化值：原樣傳入包裝器。
    """
    if isinstance(result, BaseError):
        return api_response_with_logging(result, request)
    if isinstance(result, Exception):
        return api_response_with_logging(result, request)
    if hasattr(result, "model_dump"):
        return api_response_with_logging(result.model_dump(mode="json"), request)
    if isinstance(result, list):
        if not result:
            return api_response_with_logging([], request)
        if hasattr(result[0], "model_dump"):
            return api_response_with_logging(
                [item.model_dump(mode="json") for item in result],
                request,
            )
        return api_response_with_logging(result, request)
    return api_response_with_logging(result, request)
