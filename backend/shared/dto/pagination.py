"""Shared pagination DTOs for list endpoints."""

from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    """Query parameters for offset/limit style paging."""

    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)


class PaginatedMeta(BaseModel):
    """Metadata returned with a page of results."""

    total: int = Field(ge=0)
    offset: int = Field(ge=0)
    limit: int = Field(ge=1)
