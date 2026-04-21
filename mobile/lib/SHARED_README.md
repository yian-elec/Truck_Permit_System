# Shared 模組使用說明

## 概述

Shared 模組提供跨 Context 的通用資源，包括 Widgets、工具函數、擴充方法、常數等。

## 使用方式

### 1. Widgets

#### AppButton

```dart
import 'shared/shared.dart';

AppButton(
  text: '點擊我',
  onPressed: () {
    print('按鈕被點擊');
  },
  style: AppButtonStyle.primary,
  size: AppButtonSize.medium,
  isLoading: false,
  isFullWidth: true,
  icon: Icons.add,
)
```

#### AppCard

```dart
import 'shared/shared.dart';

AppCard(
  padding: EdgeInsets.all(16),
  margin: EdgeInsets.all(8),
  onTap: () {
    print('卡片被點擊');
  },
  child: Text('卡片內容'),
)
```

#### AppLoader

```dart
import 'shared/shared.dart';

// 簡單載入指示器
AppLoader()

// 帶訊息的載入指示器
AppLoader(message: '載入中...')

// 全螢幕載入覆蓋層
AppLoadingOverlay(
  isLoading: true,
  message: '載入中...',
  child: YourContent(),
)
```

### 2. 驗證工具

```dart
import 'shared/shared.dart';

// Email 驗證
if (Validators.isValidEmail('user@example.com')) {
  print('有效的 Email');
}

// 手機號碼驗證
if (Validators.isValidPhone('0912345678')) {
  print('有效的手機號碼');
}

// 密碼強度驗證
if (Validators.isStrongPassword('MyP@ssw0rd')) {
  print('強密碼');
}
```

### 3. 格式化工具

```dart
import 'shared/shared.dart';

// 日期格式化
Formatters.formatDate(DateTime.now()); // '2024-01-01'
Formatters.formatDateTime(DateTime.now()); // '2024-01-01 12:00:00'
Formatters.formatRelativeTime(DateTime.now().subtract(Duration(hours: 2))); // '2 小時前'

// 貨幣格式化
Formatters.formatCurrency(1000); // 'NT$1000.00'

// 數字格式化
Formatters.formatNumber(1234567); // '1,234,567'

// 檔案大小格式化
Formatters.formatFileSize(1024 * 1024); // '1.00 MB'
```

### 4. 轉換工具

```dart
import 'shared/shared.dart';

// 字串轉數字
Converters.toInt('123'); // 123
Converters.toDouble('12.34'); // 12.34
Converters.toBool('true'); // true

// 數字轉字串
Converters.intToString(123); // '123'
Converters.doubleToString(12.34, decimals: 2); // '12.34'

// 列表與字串互轉
Converters.listToString(['a', 'b', 'c']); // 'a, b, c'
Converters.stringToList('a, b, c'); // ['a', 'b', 'c']
```

### 5. 擴充方法

#### String 擴充

```dart
import 'shared/shared.dart';

final email = 'user@example.com';
if (email.isValidEmail) {
  print('有效的 Email');
}

final phone = '0912345678';
if (phone.isValidPhone) {
  print('有效的手機號碼');
}

'hello world'.capitalize; // 'Hello world'
'hello world'.capitalizeWords; // 'Hello World'
'hello world'.removeWhitespace; // 'helloworld'
```

#### DateTime 擴充

```dart
import 'shared/shared.dart';

final date = DateTime.now();

date.toDateString(); // '2024-01-01'
date.toTimeString(); // '12:00:00'
date.toRelativeTimeString(); // '剛剛'

if (date.isToday) {
  print('今天');
}

date.age; // 計算年齡
```

#### Widget 擴充

```dart
import 'shared/shared.dart';

Text('Hello')
  .padding(all: 16)
  .rounded(radius: 8)
  .shadow()
  .onTap(() {
    print('被點擊');
  });

// 快捷方法
Text('Hello').paddingSmall();
Text('Hello').paddingMedium();
Text('Hello').roundedSmall();
Text('Hello').center();
```

### 6. 常數

```dart
import 'shared/shared.dart';

// UI 尺寸
AppConstants.paddingSmall; // 8.0
AppConstants.paddingMedium; // 16.0
AppConstants.borderRadiusMedium; // 8.0

// 動畫時長
AppConstants.animationDurationShort; // Duration(milliseconds: 200)

// 儲存 Key
AppConstants.keyAuthToken; // 'auth_token'
AppConstants.keyUserId; // 'user_id'

// 路由名稱
RouteNames.home; // '/'
RouteNames.login; // '/login'
```

### 7. 錯誤處理

```dart
import 'shared/shared.dart';

try {
  // 某些操作
} on AppException catch (e) {
  print(e.message);
  print(e.code);
  
  // 根據錯誤類型處理
  if (e.code == 'NETWORK_ERROR') {
    // 處理網路錯誤
  } else if (e.code == 'SERVER_ERROR_404') {
    // 處理伺服器錯誤
  }
}
```

### 8. Hooks

```dart
import 'shared/shared.dart';

// 在 StatefulWidget 中使用
class MyWidget extends StatefulWidget {
  @override
  State<MyWidget> createState() => _MyWidgetState();
}

class _MyWidgetState extends State<MyWidget> {
  @override
  void initState() {
    super.initState();
    useOnInit(() {
      // 只在初始化時執行一次
      print('Widget 初始化');
    });
  }
  
  @override
  Widget build(BuildContext context) {
    return Container();
  }
}
```

## 最佳實踐

1. **使用擴充方法**：優先使用擴充方法而非工具函數，程式碼更簡潔
2. **使用常數**：避免硬編碼數值，使用 `AppConstants` 中的常數
3. **統一錯誤處理**：使用 `AppException` 統一處理錯誤
4. **重用 Widgets**：使用 `AppButton`、`AppCard` 等統一風格的 Widgets


