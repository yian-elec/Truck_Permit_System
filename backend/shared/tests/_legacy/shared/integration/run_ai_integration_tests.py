"""
run_ai_integration_tests.py - 運行 AI Service 整合測試
實際調用 OpenAI API 並生成詳細報告
"""

import sys
import os
import pytest
from datetime import datetime

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from shared.core.config import settings


def check_prerequisites():
    """檢查測試前置條件"""
    print("\n" + "=" * 80)
    print("🔍 檢查測試前置條件")
    print("=" * 80)
    
    issues = []
    
    # 檢查 OpenAI API Key
    if not settings.ai.openai_api_key or settings.ai.openai_api_key == "your-openai-api-key-here":
        issues.append("❌ OpenAI API Key 未設定")
        print("❌ OpenAI API Key 未設定")
        print("   請在 .env 文件中設定: OPENAI_API_KEY=your-api-key")
    else:
        print("✅ OpenAI API Key 已設定")
    
    # 檢查配置
    print(f"✅ 預設模型: {settings.ai.default_model}")
    print(f"✅ 預設溫度: {settings.ai.default_temperature}")
    print(f"✅ 最大 tokens: {settings.ai.default_max_tokens}")
    
    if issues:
        print("\n⚠️  發現問題，測試將跳過")
        return False
    
    print("\n✅ 前置條件檢查通過")
    return True


def print_test_header():
    """打印測試標題"""
    print("\n" + "=" * 80)
    print("🤖 AI Service 整合測試")
    print("=" * 80)
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"測試環境: {settings.environment}")
    print(f"AI 模型: {settings.ai.default_model}")
    print("=" * 80)


def run_tests():
    """運行測試"""
    # 檢查前置條件
    if not check_prerequisites():
        print("\n❌ 測試中止：前置條件未滿足")
        print("\n💡 提示:")
        print("   1. 確保已在 .env 文件中設定 OPENAI_API_KEY")
        print("   2. 在 https://platform.openai.com/api-keys 取得 API Key")
        print("   3. 確保 API Key 有足夠的配額")
        return False
    
    # 打印測試標題
    print_test_header()
    
    # 運行 pytest
    test_file = os.path.join(
        os.path.dirname(__file__),
        "test_ai_service_integration.py"
    )
    
    print("\n🚀 開始運行測試...\n")
    
    # 運行測試並收集結果
    exit_code = pytest.main([
        test_file,
        "-v",  # 詳細輸出
        "-s",  # 顯示 print 輸出
        "--tb=short",  # 簡短的錯誤回溯
        "--color=yes",  # 彩色輸出
    ])
    
    # 生成總結
    print("\n" + "=" * 80)
    if exit_code == 0:
        print("🎉 所有測試通過！")
        print("\n✅ AI Service 整合測試完成")
        print("   - 所有功能正常運作")
        print("   - OpenAI API 連接正常")
        print("   - 服務已準備好用於生產環境")
    else:
        print("⚠️  部分測試失敗")
        print("\n💡 可能的原因:")
        print("   1. OpenAI API Key 無效或已過期")
        print("   2. API 配額不足")
        print("   3. 網路連接問題")
        print("   4. API 速率限制")
    print("=" * 80)
    
    return exit_code == 0


def main():
    """主函數"""
    try:
        success = run_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  測試被用戶中斷")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 測試運行失敗: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

