"""
Review_Decision 應用層錯誤型別與領域例外映射。

責任：將 Review 領域例外轉為 HTTP 語意一致之 App 錯誤；供服務層統一 raise，
並可與 Application context 之 `to_app_error` 並用（跨 context 狀態轉移）。
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from shared.errors.base_error.base_error import BaseError

from src.contexts.application.domain.errors import ApplicationDomainError

T = TypeVar("T")


class ReviewAppError(BaseError):
    """
    Review_Decision 應用層錯誤基底。

    責任：預設對應 HTTP 422；子類可覆寫 status_code。
    """

    @property
    def status_code(self) -> int:
        return 422


class ReviewNotFoundAppError(ReviewAppError):
    """審查任務或預期存在之審查資源不存在（404）。"""

    @property
    def status_code(self) -> int:
        return 404


class ReviewValidationAppError(ReviewAppError):
    """輸入或值物件校驗失敗（400）。"""

    @property
    def status_code(self) -> int:
        return 400


class ReviewConflictAppError(ReviewAppError):
    """與目前審查狀態、決策歷史或任務生命週期衝突（409）。"""

    @property
    def status_code(self) -> int:
        return 409


def map_review_domain_exception_to_app(exc: BaseException) -> ReviewAppError:
    """
    將 Review_Decision 領域例外映射為 App 層錯誤。

    責任：區分「輸入不合法」「決策規則」「與歷史互斥」「任務狀態」以利 API 對應狀態碼。
    """
    from src.contexts.review_decision.domain.errors import (
        InvalidReviewTaskStateError,
        InvalidSupplementRequestStateError,
        ReviewDecisionConflictError,
        ReviewDecisionRuleError,
        ReviewDomainError,
        ReviewInvalidValueError,
    )

    if isinstance(exc, ReviewInvalidValueError):
        return ReviewValidationAppError(exc.message, exc.details)
    if isinstance(exc, ReviewDecisionConflictError):
        return ReviewConflictAppError(exc.message, exc.details)
    if isinstance(exc, ReviewDecisionRuleError):
        return ReviewAppError(exc.message, exc.details)
    if isinstance(exc, InvalidReviewTaskStateError):
        return ReviewConflictAppError(exc.message, exc.details)
    if isinstance(exc, InvalidSupplementRequestStateError):
        return ReviewConflictAppError(exc.message, exc.details)
    if isinstance(exc, ReviewDomainError):
        return ReviewAppError(exc.message, exc.details)
    return ReviewAppError(str(exc), None)


def raise_review_domain_as_app(fn: Callable[[], T]) -> T:
    """執行可能拋出 ReviewDomainError 的呼叫，並轉為 App 層錯誤。"""
    from src.contexts.review_decision.domain.errors import ReviewDomainError

    try:
        return fn()
    except ReviewDomainError as e:
        raise map_review_domain_exception_to_app(e) from e


def raise_application_domain_as_app(fn: Callable[[], T]) -> T:
    """
    執行可能拋出 ApplicationDomainError 的呼叫（審查流程中更新案件狀態時使用）。

    責任：重用 Application App 層映射，維持跨 context 錯誤格式一致。
    """
    from src.contexts.application.app.errors import to_app_error

    try:
        return fn()
    except ApplicationDomainError as e:
        raise to_app_error(e) from e
