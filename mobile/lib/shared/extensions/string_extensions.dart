import '../utils/validators.dart';
import '../utils/formatters.dart';

/// String 擴充方法
extension StringExtensions on String {
  /// 檢查是否為有效的 Email
  bool get isValidEmail => Validators.isValidEmail(this);

  /// 檢查是否為有效的手機號碼
  bool get isValidPhone => Validators.isValidPhone(this);

  /// 檢查是否為有效的 URL
  bool get isValidUrl => Validators.isValidUrl(this);

  /// 檢查是否為空字串（去除空白後）
  bool get isEmptyOrWhitespace => trim().isEmpty;

  /// 檢查是否不為空字串
  bool get isNotEmptyOrWhitespace => !isEmptyOrWhitespace;

  /// 首字母大寫
  String get capitalize {
    if (isEmpty) return this;
    return '${this[0].toUpperCase()}${substring(1)}';
  }

  /// 每個單字首字母大寫
  String get capitalizeWords {
    if (isEmpty) return this;
    return split(' ').map((word) => word.capitalize).join(' ');
  }

  /// 移除所有空白
  String get removeWhitespace => replaceAll(RegExp(r'\s+'), '');

  /// 安全截取字串
  String safeSubstring(int start, [int? end]) {
    if (start < 0) start = 0;
    if (start >= length) return '';
    if (end != null) {
      if (end < 0) end = 0;
      if (end > length) end = length;
      if (end <= start) return '';
    }
    return substring(start, end);
  }

  /// 格式化手機號碼
  String get formattedPhone => Formatters.formatPhoneNumber(this);

  /// 轉換為整數（安全）
  int? toInt() {
    if (isEmpty) return null;
    return int.tryParse(this);
  }

  /// 轉換為浮點數（安全）
  double? toDouble() {
    if (isEmpty) return null;
    return double.tryParse(this);
  }

  /// 轉換為布林值
  bool toBool({bool defaultValue = false}) {
    if (isEmpty) return defaultValue;
    final lowerValue = toLowerCase();
    return lowerValue == 'true' || lowerValue == '1' || lowerValue == 'yes';
  }
}

