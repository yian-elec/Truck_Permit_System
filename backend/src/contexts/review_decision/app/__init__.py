"""
Review_Decision bounded context — 應用層。

標準目錄（與 Application context 對齊）：
- **dtos/**：資料傳輸物件（依子領域分檔 `review_*_dtos.py`，由 `dtos/__init__.py` 匯出）。
- **errors/**：應用層錯誤型別與領域例外映射（`review_app_errors.py`）。
- **services/**：用例服務（命令／查詢分離）、`ReviewServiceContext`、對外埠 `ports/`、
  對應 `application_mappers` 之 `review_mappers.py`、路由就緒度組裝 `review_route_readiness.py`。

不含 HTTP 路由；API 層應呼叫 `ReviewCommandApplicationService`／`ReviewQueryApplicationService`。
"""
