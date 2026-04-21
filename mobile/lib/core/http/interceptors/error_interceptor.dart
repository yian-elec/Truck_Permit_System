import 'package:dio/dio.dart';
import '../../logger/app_logger.dart';

/// 錯誤攔截器 - 統一處理錯誤
class ErrorInterceptor extends Interceptor {
  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    AppLogger.e(
      'HTTP Error: ${err.message}',
      err,
      err.stackTrace,
    );

    // 可以在這裡添加統一的錯誤處理邏輯
    // 例如：發送錯誤報告、顯示錯誤提示等

    handler.next(err);
  }
}


