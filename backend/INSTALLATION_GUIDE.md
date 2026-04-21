# 完整安裝指南

## 📋 系統需求

- Python 3.10+
- PostgreSQL 12+
- Git
- (可選) OpenAI API Key（如需使用 AI Service）

## 🚀 完整安裝步驟

### 1. 克隆專案

```bash
git clone <your-repo-url>
cd backend
```

### 2. 創建虛擬環境

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. 安裝依賴

```bash
pip install -r requirements.txt
```

### 4. 環境配置

```bash
# 複製環境變數範例
cp docs/env.example .env
```

編輯 `.env` 文件，設定以下必需配置：

```env
# 資料庫設定（必需）
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your-password
DB_NAME=base_project

# JWT 設定（必需）
JWT_SECRET=your-super-secret-jwt-key-here

# OpenAI 設定（可選，使用 AI Service 時需要）
OPENAI_API_KEY=sk-your-openai-api-key-here
```

### 5. 初始化資料庫

確保 PostgreSQL 服務正在運行，然後執行：

```bash
python -c "from src.core.db.init_db import init_db; init_db()"
```

### 6. 啟動服務

```bash
# 開發模式
uvicorn main:app --reload

# 或直接運行
python main.py
```

### 7. 驗證安裝

訪問以下 URL：

- API 文檔: http://localhost:8000/docs
- 健康檢查: http://localhost:8000/health

## 🧪 測試 AI Service（可選）

如果你設定了 OpenAI API Key：

```bash
python examples/quick_test_ai.py
```

## 📝 常見問題

### Q: 資料庫連接失敗

**解決方案**：
1. 確認 PostgreSQL 服務正在運行
2. 檢查 `.env` 中的資料庫配置
3. 確認資料庫用戶有創建資料庫的權限

### Q: 模組導入錯誤

**解決方案**：
1. 確認虛擬環境已啟動
2. 重新安裝依賴：`pip install -r requirements.txt`
3. 檢查 Python 版本是否為 3.10+

### Q: AI Service 測試失敗

**解決方案**：
1. 檢查 OPENAI_API_KEY 是否正確設定
2. 確認網路連接正常
3. 檢查 OpenAI API 配額

## 🔧 開發工具設定

### VS Code

推薦安裝擴展：
- Python
- Pylance
- Python Test Explorer

### PyCharm

配置：
1. 設定 Python 解釋器為虛擬環境
2. 啟用自動 import 優化
3. 配置測試運行器為 pytest

## 🎯 下一步

安裝完成後，你可以：

1. **查看 API 文檔**: http://localhost:8000/docs
2. **運行測試**: `pytest`
3. **使用 AI Service**: 查看 [AI Service 文檔](src/shared/services/ai/README.md)
4. **創建新的 Context**: 參考 User Context 的結構

## 📚 相關文檔

- [README](README.md) - 專案概述
- [AI Service 快速開始](src/shared/services/ai/QUICKSTART.md)
- [AI Service 完整文檔](src/shared/services/ai/README.md)
- [使用範例](examples/)

## 🆘 需要幫助？

如果遇到問題：
1. 檢查環境變數設定
2. 查看日誌輸出
3. 參考文檔和範例
4. 提交 Issue

---

**祝你開發愉快！🎉**

