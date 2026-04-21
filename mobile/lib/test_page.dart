import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'core/core.dart';
import 'shared/shared.dart';

/// 測試頁面 - 展示 core 和 shared 模組的功能
class TestPage extends ConsumerStatefulWidget {
  const TestPage({super.key});

  @override
  ConsumerState<TestPage> createState() => _TestPageState();
}

class _TestPageState extends ConsumerState<TestPage> {
  String _storageResult = '';
  String _validationResult = '';
  String _formatResult = '';
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _testStorage();
    _testValidation();
    _testFormatting();
  }

  /// 測試儲存服務
  Future<void> _testStorage() async {
    try {
      final storage = StorageService.instance;
      await storage.setString('test_key', 'test_value');
      final value = await storage.getString('test_key');
      setState(() {
        _storageResult = '儲存測試: ${value ?? "null"}';
      });
      AppLogger.i('儲存測試成功: $value');
    } catch (e) {
      AppLogger.e('儲存測試失敗', e);
      setState(() {
        _storageResult = '儲存測試失敗: $e';
      });
    }
  }

  /// 測試驗證工具
  void _testValidation() {
    final email = 'user@example.com';
    final phone = '0912345678';
    final isValidEmail = Validators.isValidEmail(email);
    final isValidPhone = Validators.isValidPhone(phone);

    setState(() {
      _validationResult = 'Email 驗證: $isValidEmail, 手機驗證: $isValidPhone';
    });
    AppLogger.d('驗證測試: $_validationResult');
  }

  /// 測試格式化工具
  void _testFormatting() {
    final now = DateTime.now();
    final formattedDate = Formatters.formatDate(now);
    final formattedCurrency = Formatters.formatCurrency(1000);
    final formattedNumber = Formatters.formatNumber(1234567);

    setState(() {
      _formatResult = '日期: $formattedDate, 貨幣: $formattedCurrency, 數字: $formattedNumber';
    });
    AppLogger.d('格式化測試: $_formatResult');
  }

  /// 測試 HTTP 客戶端
  Future<void> _testHttpClient() async {
    setState(() {
      _isLoading = true;
    });

    try {
      // 注意：這裡使用一個測試 API，實際使用時請替換為真實的 API
      // final httpClient = ref.read(httpClientProvider);
      // final response = await httpClient.get('/api/test');
      // AppLogger.i('HTTP 測試成功: ${response.data}');
      AppLogger.i('HTTP 客戶端已初始化（跳過實際請求以避免錯誤）');
      
      setState(() {
        _isLoading = false;
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('HTTP 客戶端測試完成（請查看日誌）')),
        );
      }
    } catch (e) {
      AppLogger.e('HTTP 測試失敗', e);
      setState(() {
        _isLoading = false;
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('HTTP 測試失敗: $e')),
        );
      }
    }
  }

  /// 測試事件匯流排
  void _testEventBus() {
    AppEventBus.on<TestEvent>().listen((event) {
      AppLogger.i('收到事件: ${event.message}');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('收到事件: ${event.message}')),
        );
      }
    });

    AppEventBus.fire(TestEvent(message: '測試事件'));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Core & Shared 測試'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // 儲存測試結果
            AppCard(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '儲存服務測試',
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  const SizedBox(height: 8),
                  Text(_storageResult),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // 驗證測試結果
            AppCard(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '驗證工具測試',
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  const SizedBox(height: 8),
                  Text(_validationResult),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // 格式化測試結果
            AppCard(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '格式化工具測試',
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  const SizedBox(height: 8),
                  Text(_formatResult),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // 擴充方法測試
            AppCard(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '擴充方法測試',
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  const SizedBox(height: 8),
                  Text('Email 驗證: ${'user@example.com'.isValidEmail}'),
                  Text('手機驗證: ${'0912345678'.isValidPhone}'),
                  Text('首字母大寫: ${'hello world'.capitalize}'),
                  Text('格式化手機: ${'0912345678'.formattedPhone}'),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // 按鈕測試
            AppButton(
              text: '測試 HTTP 客戶端',
              onPressed: _testHttpClient,
              style: AppButtonStyle.primary,
              isFullWidth: true,
              isLoading: _isLoading,
            ),
            const SizedBox(height: 16),

            AppButton(
              text: '測試事件匯流排',
              onPressed: _testEventBus,
              style: AppButtonStyle.secondary,
              isFullWidth: true,
            ),
            const SizedBox(height: 16),

            AppButton(
              text: '測試載入器',
              onPressed: () {
                showDialog(
                  context: context,
                  builder: (context) => const AlertDialog(
                    content: AppLoader(message: '載入中...'),
                  ),
                );
              },
              style: AppButtonStyle.outline,
              isFullWidth: true,
            ),
          ],
        ),
      ),
    );
  }
}

/// 測試事件
class TestEvent {
  final String message;

  TestEvent({required this.message});
}

