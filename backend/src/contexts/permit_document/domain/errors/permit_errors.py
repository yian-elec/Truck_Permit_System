"""
Permit_Document context 專屬領域錯誤。

責任：表達許可證建立前提、路線綁定、文件版本與工作狀態機等違反不變條件時的語意化例外；
僅依賴 shared 之 DomainError 基底，不依賴 Infra、App、API 或其他 context。
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from shared.errors.domain_error.domain_error import DomainError


class PermitDomainError(DomainError):
    """
    Permit_Document 領域錯誤基底。

    責任：統一本 bounded context 內業務規則違例的父類型，供 App 層對應 HTTP／錯誤碼。
    """

    pass


class InvalidPermitValueError(PermitDomainError):
    """
    值物件或欄位格式／範圍不符合領域約束。

    責任：例如 permit_no 長度非法、route_summary 為空、狀態字串不在白名單等。
    """

    pass


class InvalidPermitStateError(PermitDomainError):
    """
    許可聚合目前狀態不允許所請求的領域行為。

    責任：例如尚未核准卻嘗試建立 Permit、已廢止狀態下仍嘗試標記核發完成等。
    """

    def __init__(
        self,
        message: str,
        *,
        current_status: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        d = dict(details or {})
        if current_status is not None:
            d["current_status"] = current_status
        super().__init__(message, d if d else None)


class PermitCreationPreconditionError(PermitDomainError):
    """
    違反「僅核准案可建 permit」或「須綁定最終路線」等建立前提。

    責任：與 InvalidPermitStateError 分離，讓 App 層可區分「資料未就緒」與「聚合內狀態錯誤」。
    """

    pass


class PermitDocumentStateError(PermitDomainError):
    """
    單一文件實體（permit.documents）之狀態轉移不合法。

    責任：例如對已 SUPERSEDED 版本再次標記為 ACTIVE。
    """

    def __init__(
        self,
        message: str,
        *,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, details)


class DocumentJobStateError(PermitDomainError):
    """
    文件產製工作單（document_jobs）之狀態轉移不合法。

    責任：例如已完成之 job 再次標記為處理中。
    """

    def __init__(
        self,
        message: str,
        *,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, details)
