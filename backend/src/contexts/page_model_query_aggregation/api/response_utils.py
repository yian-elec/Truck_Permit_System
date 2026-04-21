"""
Page_Model_Query_Aggregation API — 回應包裝。

責任：應用層 DTO 為 **dataclass**，成功時轉為 JSON 可序列化結構後交
`shared.api.api_response_with_logging`；錯誤時支援 **BaseError** 與一般例外（與 Permit_Document 模式一致）。
"""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from fastapi import Request
from fastapi.responses import JSONResponse

from shared.api import api_response_with_logging
from shared.errors.base_error.base_error import BaseError


def _page_model_dto_to_jsonable(obj: Any) -> Any:
    """將 dataclass／巢狀結構轉為 JSON 相容值（UUID、tuple→list 等）。"""
    if obj is None:
        return None
    if isinstance(obj, UUID):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, date):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, tuple):
        return [_page_model_dto_to_jsonable(x) for x in obj]
    if isinstance(obj, list):
        return [_page_model_dto_to_jsonable(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _page_model_dto_to_jsonable(v) for k, v in obj.items()}
    if is_dataclass(obj) and not isinstance(obj, type):
        raw = asdict(obj)
        return _page_model_dto_to_jsonable(raw)
    return obj


def page_model_api_response(result: Any, request: Request) -> JSONResponse:
    """
    將 Page Model 用例結果或例外轉為 **JSONResponse**（信封 `{data, error}`）。

    責任：與 `shared.api` 統一回應格式對齊，供 Swagger 與前端一致解析。
    """
    if isinstance(result, BaseError):
        return api_response_with_logging(result, request)
    if isinstance(result, Exception):
        return api_response_with_logging(result, request)
    if is_dataclass(result) and not isinstance(result, type):
        return api_response_with_logging(_page_model_dto_to_jsonable(result), request)
    if isinstance(result, list):
        if not result:
            return api_response_with_logging([], request)
        el0 = result[0]
        if is_dataclass(el0) and not isinstance(el0, type):
            return api_response_with_logging(
                [_page_model_dto_to_jsonable(item) for item in result],
                request,
            )
        return api_response_with_logging(result, request)
    if hasattr(result, "model_dump"):
        return api_response_with_logging(result.model_dump(mode="json"), request)
    return api_response_with_logging(result, request)
