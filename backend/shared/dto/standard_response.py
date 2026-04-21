"""Shared envelope DTOs aligned with `shared.api.wrapper` JSON shape."""

from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorBody(BaseModel):
    """Standard error object in API responses."""

    code: str
    message: str
    details: Optional[dict[str, Any]] = None


class StandardResponse(BaseModel, Generic[T]):
    """Generic success/error envelope for typed OpenAPI / internal use."""

    data: Optional[T] = None
    error: Optional[ErrorBody] = Field(default=None)
