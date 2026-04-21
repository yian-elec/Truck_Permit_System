/// 應用程式統一例外類別
class AppException implements Exception {
  final String message;
  final String? code;
  final dynamic originalError;
  final StackTrace? stackTrace;

  const AppException({
    required this.message,
    this.code,
    this.originalError,
    this.stackTrace,
  });

  /// 網路錯誤
  factory AppException.network({
    String message = '網路連線失敗',
    dynamic originalError,
    StackTrace? stackTrace,
  }) {
    return AppException(
      message: message,
      code: 'NETWORK_ERROR',
      originalError: originalError,
      stackTrace: stackTrace,
    );
  }

  /// 伺服器錯誤
  factory AppException.server({
    String message = '伺服器錯誤',
    int? statusCode,
    dynamic originalError,
    StackTrace? stackTrace,
  }) {
    return AppException(
      message: message,
      code: 'SERVER_ERROR_${statusCode ?? 'UNKNOWN'}',
      originalError: originalError,
      stackTrace: stackTrace,
    );
  }

  /// 超時錯誤
  factory AppException.timeout({
    String message = '請求超時',
    dynamic originalError,
    StackTrace? stackTrace,
  }) {
    return AppException(
      message: message,
      code: 'TIMEOUT_ERROR',
      originalError: originalError,
      stackTrace: stackTrace,
    );
  }

  /// 取消錯誤
  factory AppException.cancelled({
    String message = '請求已取消',
    dynamic originalError,
    StackTrace? stackTrace,
  }) {
    return AppException(
      message: message,
      code: 'CANCELLED_ERROR',
      originalError: originalError,
      stackTrace: stackTrace,
    );
  }

  /// 驗證錯誤
  factory AppException.validation({
    String message = '資料驗證失敗',
    String? code,
    dynamic originalError,
    StackTrace? stackTrace,
  }) {
    return AppException(
      message: message,
      code: code ?? 'VALIDATION_ERROR',
      originalError: originalError,
      stackTrace: stackTrace,
    );
  }

  /// 未授權錯誤
  factory AppException.unauthorized({
    String message = '未授權',
    dynamic originalError,
    StackTrace? stackTrace,
  }) {
    return AppException(
      message: message,
      code: 'UNAUTHORIZED_ERROR',
      originalError: originalError,
      stackTrace: stackTrace,
    );
  }

  /// 未知錯誤
  factory AppException.unknown({
    String message = '未知錯誤',
    dynamic originalError,
    StackTrace? stackTrace,
  }) {
    return AppException(
      message: message,
      code: 'UNKNOWN_ERROR',
      originalError: originalError,
      stackTrace: stackTrace,
    );
  }

  @override
  String toString() => 'AppException: $message${code != null ? ' ($code)' : ''}';
}


