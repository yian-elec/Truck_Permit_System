"""
check_ai_config.py - 检查 AI 配置
"""

import sys
import os

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from shared.core.config import settings

print("=" * 60)
print("🔍 檢查 AI Service 配置")
print("=" * 60)

# 檢查 API Key
if not settings.ai.openai_api_key or settings.ai.openai_api_key == "your-openai-api-key-here":
    print("❌ OpenAI API Key 未設定")
    print("\n請按照以下步驟設定:")
    print("1. 創建或編輯 .env 文件")
    print("2. 添加: OPENAI_API_KEY=your-actual-api-key-here")
    print("3. 在 https://platform.openai.com/api-keys 取得 API Key")
    print("\n或直接在終端設定:")
    print("   $env:OPENAI_API_KEY='your-api-key'  # Windows PowerShell")
    sys.exit(1)

print(f"✅ OpenAI API Key: {settings.ai.openai_api_key[:8]}...{settings.ai.openai_api_key[-4:]}")
print(f"✅ 預設模型: {settings.ai.default_model}")
print(f"✅ 預設溫度: {settings.ai.default_temperature}")
print(f"✅ 最大 tokens: {settings.ai.default_max_tokens}")
print("\n✅ 配置檢查通過！")
print("\n💡 現在可以運行測試:")
print("   python -m pytest src/tests/shared/integration/test_ai_service_integration.py -v -s")

