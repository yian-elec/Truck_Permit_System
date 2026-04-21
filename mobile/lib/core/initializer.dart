import 'config/app_config.dart';
import 'logger/app_logger.dart';
import 'storage/storage_service.dart';

/// 應用程式初始化器
class AppInitializer {
  /// 初始化應用程式核心服務
  static Future<void> initialize({
    AppConfig? config,
    StorageType storageType = StorageType.sharedPreferences,
  }) async {
    // 1. 初始化配置
    final appConfig = config ?? AppConfig.fromEnvironment();

    // 2. 初始化日誌系統
    AppLogger.initialize(appConfig);

    // 3. 初始化儲存服務
    await StorageService.initialize(type: storageType);

    AppLogger.i('應用程式初始化完成');
  }
}

