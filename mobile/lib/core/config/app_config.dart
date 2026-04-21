/// 應用程式環境配置
enum AppEnvironment {
  development,
  staging,
  production,
}

/// 應用程式配置類別
class AppConfig {
  final AppEnvironment environment;
  final String baseUrl;
  final String apiVersion;
  final bool enableLogging;
  final int connectTimeout;
  final int receiveTimeout;

  const AppConfig({
    required this.environment,
    required this.baseUrl,
    this.apiVersion = 'v1',
    this.enableLogging = true,
    this.connectTimeout = 30000,
    this.receiveTimeout = 30000,
  });

  /// 開發環境配置
  static const AppConfig development = AppConfig(
    environment: AppEnvironment.development,
    baseUrl: 'https://api-dev.example.com',
    apiVersion: 'v1',
    enableLogging: true,
    connectTimeout: 30000,
    receiveTimeout: 30000,
  );

  /// 測試環境配置
  static const AppConfig staging = AppConfig(
    environment: AppEnvironment.staging,
    baseUrl: 'https://api-staging.example.com',
    apiVersion: 'v1',
    enableLogging: true,
    connectTimeout: 30000,
    receiveTimeout: 30000,
  );

  /// 生產環境配置
  static const AppConfig production = AppConfig(
    environment: AppEnvironment.production,
    baseUrl: 'https://api.example.com',
    apiVersion: 'v1',
    enableLogging: false,
    connectTimeout: 30000,
    receiveTimeout: 30000,
  );

  /// 根據環境變數取得配置
  static AppConfig fromEnvironment() {
    const env = String.fromEnvironment('ENV', defaultValue: 'development');
    switch (env.toLowerCase()) {
      case 'production':
        return production;
      case 'staging':
        return staging;
      default:
        return development;
    }
  }

  bool get isDevelopment => environment == AppEnvironment.development;
  bool get isStaging => environment == AppEnvironment.staging;
  bool get isProduction => environment == AppEnvironment.production;
}


