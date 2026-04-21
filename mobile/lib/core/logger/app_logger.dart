import 'package:logger/logger.dart';
import '../config/app_config.dart';

/// 應用程式日誌管理器
class AppLogger {
  static Logger? _instance;

  /// 初始化日誌系統
  static void initialize(AppConfig config) {
    _instance = Logger(
      printer: PrettyPrinter(
        methodCount: config.isDevelopment ? 2 : 0,
        errorMethodCount: 8,
        lineLength: 120,
        colors: true,
        printEmojis: true,
      ),
      level: config.enableLogging ? Level.debug : Level.off,
    );
  }

  static Logger get _log {
    if (_instance == null) {
      throw Exception('AppLogger not initialized. Call AppLogger.initialize() first.');
    }
    return _instance!;
  }

  /// Debug 日誌
  static void d(dynamic message, [dynamic error, StackTrace? stackTrace]) {
    _log.d(message, error: error, stackTrace: stackTrace);
  }

  /// Info 日誌
  static void i(dynamic message, [dynamic error, StackTrace? stackTrace]) {
    _log.i(message, error: error, stackTrace: stackTrace);
  }

  /// Warning 日誌
  static void w(dynamic message, [dynamic error, StackTrace? stackTrace]) {
    _log.w(message, error: error, stackTrace: stackTrace);
  }

  /// Error 日誌
  static void e(dynamic message, [dynamic error, StackTrace? stackTrace]) {
    _log.e(message, error: error, stackTrace: stackTrace);
  }

  /// Fatal 日誌
  static void f(dynamic message, [dynamic error, StackTrace? stackTrace]) {
    _log.f(message, error: error, stackTrace: stackTrace);
  }
}

