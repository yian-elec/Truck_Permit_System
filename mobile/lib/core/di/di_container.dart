import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../config/app_config.dart';
import '../http/http_client.dart';
import '../http/interceptors/auth_interceptor.dart';
import '../http/interceptors/error_interceptor.dart';
import '../storage/storage_service.dart';
import '../logger/app_logger.dart';

/// 應用程式配置 Provider
final appConfigProvider = Provider<AppConfig>((ref) {
  return AppConfig.fromEnvironment();
});

/// 儲存服務 Provider
final storageServiceProvider = Provider<IStorageService>((ref) {
  return StorageService.instance;
});

/// HTTP 客戶端 Provider
final httpClientProvider = Provider<AppHttpClient>((ref) {
  final config = ref.watch(appConfigProvider);
  final storageService = ref.watch(storageServiceProvider);

  return AppHttpClient(
    config: config,
    interceptors: [
      AuthInterceptor(storageService: storageService),
      ErrorInterceptor(),
    ],
  );
});

/// 日誌服務 Provider
final loggerProvider = Provider<void>((ref) {
  final config = ref.watch(appConfigProvider);
  AppLogger.initialize(config);
});

