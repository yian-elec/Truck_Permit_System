"""
Permit_Document — Application 層套件。

目錄約定：
- **dtos/** — 命令／查詢邊界之輸入輸出型別。
- **errors/** — 應用層例外與領域錯誤對應。
- **services/** — 用例服務（`*_application_service`）、ORM 映射、**PermitServiceContext**；
  **services/ports/** — 出站 Protocol 與開發用 **default_adapters**；
  **services/integrations/** — 跨 context 讀取（如核准與路線快照）。

與 HTTP 之組合請見 `api` 模組。
"""
