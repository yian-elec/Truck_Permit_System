"""
Application API — 回應包裝。

責任：Pydantic v2 之 `model_dump()` 預設會保留 `UUID`／`datetime` 等 Python 型別，
`JSONResponse` 無法直接序列化；成功回應改以 `model_dump(mode="json")` 再交
`api_response_with_logging`，與 OpenAPI／客戶端 JSON 契約一致。
"""

from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse

from shared.api.wrapper import api_response_with_logging
from shared.errors.base_error.base_error import BaseError


def application_api_response(result: object, request: Request) -> JSONResponse:
    """
    將成功資料或錯誤物件包裝為統一 `{data, error}` 信封。

    - `BaseError`／其他 `Exception`：維持既有狀態碼與訊息行為。
    - 具 `model_dump` 之 Pydantic 模型：以 JSON 相容模式序列化後再包裝。
    """
    if isinstance(result, BaseError):
        return api_response_with_logging(result, request)
    if isinstance(result, Exception):
        return api_response_with_logging(result, request)
    if hasattr(result, "model_dump"):
        return api_response_with_logging(
            result.model_dump(mode="json"),
            request,
        )
    return api_response_with_logging(result, request)
