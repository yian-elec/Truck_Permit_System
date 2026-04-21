"""
送件前檢查結果（領域值／非持久化實體）。

責任：UC-APP-05 之輸出語意——彙整缺漏代碼與是否可送件；由 Application.evaluate_submission_readiness 產生，
不包含 HTTP 或 DTO 格式。
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SubmissionReadiness:
    """
    送件前檢查之結構化結果。

    責任：`can_submit` 為 True 時，UC-APP-06 仍應再次呼叫聚合之 assert_ready_to_submit 以確保競態前後一致；
    `missing_reason_codes` 供 API 組裝使用者可讀訊息。
    """

    can_submit: bool
    missing_reason_codes: tuple[str, ...] = field(default_factory=tuple)
