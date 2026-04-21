"""
quick_test_ai.py - 快速測試 AI Service
用於驗證 AI Service 是否正常工作
"""

import asyncio
import sys
import os

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.services.ai import ai_service
from shared.core.config import settings


async def quick_test():
    """快速測試 AI Service"""
    print("🤖 AI Service 快速測試\n")
    
    # 檢查 API Key
    if not settings.ai.openai_api_key or settings.ai.openai_api_key == "your-openai-api-key-here":
        print("❌ 錯誤: 未設定有效的 OPENAI_API_KEY")
        print("\n請按照以下步驟設定:")
        print("1. 複製環境變數範例: cp docs/env.example .env")
        print("2. 編輯 .env 文件")
        print("3. 設定 OPENAI_API_KEY=你的-api-key")
        print("\n或直接在終端設定:")
        print("   export OPENAI_API_KEY='你的-api-key'  # Mac/Linux")
        print("   $env:OPENAI_API_KEY='你的-api-key'    # Windows PowerShell")
        return False
    
    print(f"✅ 已檢測到 OpenAI API Key")
    print(f"📋 預設模型: {settings.ai.default_model}\n")
    
    try:
        print("正在測試基礎對話功能...")
        response = await ai_service.chat(
            message="請用一句話說明什麼是 AI",
            model="gpt-3.5-turbo"
        )
        
        print(f"\n問題: 請用一句話說明什麼是 AI")
        print(f"回答: {response.message}")
        print(f"\n模型: {response.model}")
        print(f"完成原因: {response.finish_reason}")
        
        print("\n✅ AI Service 測試成功！")
        print("\n💡 提示: 查看 examples/ai_service_example.py 獲取更多使用範例")
        return True
        
    except Exception as e:
        print(f"\n❌ 測試失敗: {str(e)}")
        print("\n可能的原因:")
        print("1. OpenAI API Key 無效或已過期")
        print("2. 網路連接問題")
        print("3. API 配額不足")
        print("4. 防火牆阻止連接")
        return False


if __name__ == "__main__":
    result = asyncio.run(quick_test())
    sys.exit(0 if result else 1)

