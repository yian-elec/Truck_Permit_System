"""
response_utils — IAM API 專用之回應包裝。

`shared.api.api_wrapper.api_response_with_logging` 對 Pydantic v2 預設 `model_dump()` 會保留 UUID 等型別，
`JSONResponse` 序列化時拋錯。此處在 IAM 邊界改為 `model_dump(mode=\"json\")`，僅動本 context API 層。
"""

from __future__ import annotations

from typing import Any, Callable

from fastapi import Request
from fastapi.responses import JSONResponse

from shared.api.wrapper import api_response_with_logging


def wrap_iam_use_case_response(request: Request, fn: Callable[[], Any]) -> JSONResponse:
    """執行同步用例並包裝；成功時將 Pydantic 輸出轉為 JSON 相容 dict。"""
    try:
        result = fn()
        if hasattr(result, "model_dump"):
            result = result.model_dump(mode="json")
        return api_response_with_logging(result, request)
    except Exception as exc:  # noqa: BLE001
        return api_response_with_logging(exc, request)
