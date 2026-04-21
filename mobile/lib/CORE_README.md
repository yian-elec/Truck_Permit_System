# Core 模組使用說明

## 概述

Core 模組提供應用程式的核心基礎設施，包括 HTTP 客戶端、儲存服務、路由、日誌、依賴注入等。

## 初始化

在 `main.dart` 中初始化應用程式：

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'core/initializer.dart';
import 'core/core.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // 初始化核心服務
  await AppInitializer.initialize(
    storageType: StorageType.sharedPreferences, // 或 StorageType.hive
  );
  
  runApp(
    const ProviderScope(
      child: MyApp(),
    ),
  );
}
```

## 使用方式

### 1. HTTP 客戶端

```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'core/core.dart';

// 在 Widget 中使用
final httpClient = ref.watch(httpClientProvider);

// 發送 GET 請求
final response = await httpClient.get('/api/users');

// 發送 POST 請求
final response = await httpClient.post(
  '/api/users',
  data: {'name': 'John'},
);
```

### 2. 儲存服務

```dart
import 'core/core.dart';

// 儲存字串
await StorageService.instance.setString('key', 'value');

// 讀取字串
final value = await StorageService.instance.getString('key');

// 儲存其他類型
await StorageService.instance.setInt('count', 10);
await StorageService.instance.setBool('isLoggedIn', true);
```

### 3. 日誌系統

```dart
import 'core/core.dart';

AppLogger.d('Debug 訊息');
AppLogger.i('Info 訊息');
AppLogger.w('Warning 訊息');
AppLogger.e('Error 訊息', error, stackTrace);
```

### 4. 路由

```dart
import 'core/core.dart';
import 'package:go_router/go_router.dart';

// 在 MaterialApp 中使用
MaterialApp.router(
  routerConfig: AppRouter.router,
)

// 導航
context.go('/home');
context.push('/profile');
```

### 5. 事件匯流排

```dart
import 'core/core.dart';

// 發送事件
AppEventBus.fire(MyEvent(data: 'some data'));

// 訂閱事件
AppEventBus.on<MyEvent>().listen((event) {
  print('收到事件: ${event.data}');
});
```

### 6. 依賴注入

```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'core/core.dart';

// 使用 Provider
final httpClient = ref.watch(httpClientProvider);
final storageService = ref.watch(storageServiceProvider);
final config = ref.watch(appConfigProvider);
```

## 配置

### 環境配置

在運行時指定環境：

```bash
# 開發環境
flutter run --dart-define=ENV=development

# 測試環境
flutter run --dart-define=ENV=staging

# 生產環境
flutter run --dart-define=ENV=production
```

或在程式碼中自訂配置：

```dart
await AppInitializer.initialize(
  config: AppConfig(
    environment: AppEnvironment.development,
    baseUrl: 'https://api.example.com',
    enableLogging: true,
  ),
);
```


