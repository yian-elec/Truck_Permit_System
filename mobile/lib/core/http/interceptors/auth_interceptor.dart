import 'package:dio/dio.dart';
import '../../storage/storage_service.dart';

/// 認證攔截器 - 自動添加 Token
class AuthInterceptor extends Interceptor {
  final IStorageService storageService;
  final String tokenKey;

  AuthInterceptor({
    required this.storageService,
    this.tokenKey = 'auth_token',
  });

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) async {
    // 從儲存中取得 Token
    final token = await storageService.getString(tokenKey);
    if (token != null && token.isNotEmpty) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    handler.next(options);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    // 如果收到 401 未授權，可以清除 Token 並導向登入頁
    if (err.response?.statusCode == 401) {
      storageService.remove(tokenKey);
    }
    handler.next(err);
  }
}

