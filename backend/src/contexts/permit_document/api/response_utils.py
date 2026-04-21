"""
Permit_Document API — 回應包裝。

責任：本 context 之應用層 DTO 多為 **dataclass**（非 Pydantic），成功時轉為 JSON 可序列化
結構後交 `shared.api.api_response_with_logging`；錯誤時與其他 context 相同，支援 **BaseError**。
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


def _permit_dto_to_jsonable(obj: Any) -> Any:
    """將 dataclass／巢狀結構轉為 JSON 相容值（UUID、datetime 等）。"""
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
    if isinstance(obj, list):
        return [_permit_dto_to_jsonable(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _permit_dto_to_jsonable(v) for k, v in obj.items()}
    if is_dataclass(obj) and not isinstance(obj, type):
        raw = asdict(obj)
        return _permit_dto_to_jsonable(raw)
    return obj


def permit_api_response(result: Any, request: Request) -> JSONResponse:
    """
    將許可證用例結果或例外轉為 **JSONResponse**（信封 `{data, error}`）。

    - **BaseError**／其他 **Exception**：交共用包裝器。
    - **dataclass**：經 `_permit_dto_to_jsonable` 後作為 `data`。
    - **list**：逐筆處理（元素為 dataclass 時同樣序列化）。
    """
    if isinstance(result, BaseError):
        return api_response_with_logging(result, request)
    if isinstance(result, Exception):
        return api_response_with_logging(result, request)
    if is_dataclass(result) and not isinstance(result, type):
        return api_response_with_logging(_permit_dto_to_jsonable(result), request)
    if isinstance(result, list):
        if not result:
            return api_response_with_logging([], request)
        el0 = result[0]
        if is_dataclass(el0) and not isinstance(el0, type):
            return api_response_with_logging(
                [_permit_dto_to_jsonable(item) for item in result],
                request,
            )
        return api_response_with_logging(result, request)
    if hasattr(result, "model_dump"):
        return api_response_with_logging(result.model_dump(mode="json"), request)
    return api_response_with_logging(result, request)
