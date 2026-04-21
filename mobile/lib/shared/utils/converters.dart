/// 轉換工具類別
class Converters {
  /// 字串轉整數（安全轉換）
  static int? toInt(String? value) {
    if (value == null || value.isEmpty) return null;
    return int.tryParse(value);
  }

  /// 字串轉浮點數（安全轉換）
  static double? toDouble(String? value) {
    if (value == null || value.isEmpty) return null;
    return double.tryParse(value);
  }

  /// 字串轉布林值
  static bool toBool(String? value, {bool defaultValue = false}) {
    if (value == null || value.isEmpty) return defaultValue;
    final lowerValue = value.toLowerCase();
    return lowerValue == 'true' || lowerValue == '1' || lowerValue == 'yes';
  }

  /// 整數轉字串
  static String intToString(int? value, {String defaultValue = ''}) {
    return value?.toString() ?? defaultValue;
  }

  /// 浮點數轉字串
  static String doubleToString(double? value, {String defaultValue = '', int? decimals}) {
    if (value == null) return defaultValue;
    if (decimals != null) {
      return value.toStringAsFixed(decimals);
    }
    return value.toString();
  }

  /// 布林值轉字串
  static String boolToString(bool? value, {String defaultValue = ''}) {
    return value?.toString() ?? defaultValue;
  }

  /// 列表轉字串（用分隔符連接）
  static String listToString(List<String>? list, {String separator = ', '}) {
    if (list == null || list.isEmpty) return '';
    return list.join(separator);
  }

  /// 字串轉列表（用分隔符分割）
  static List<String> stringToList(String? value, {String separator = ','}) {
    if (value == null || value.isEmpty) return [];
    return value.split(separator).map((e) => e.trim()).where((e) => e.isNotEmpty).toList();
  }

  /// Map 轉查詢字串
  static String mapToQueryString(Map<String, dynamic>? map) {
    if (map == null || map.isEmpty) return '';
    return map.entries
        .map((e) => '${Uri.encodeComponent(e.key)}=${Uri.encodeComponent(e.value.toString())}')
        .join('&');
  }

  /// 查詢字串轉 Map
  static Map<String, String> queryStringToMap(String? queryString) {
    if (queryString == null || queryString.isEmpty) return {};
    final uri = Uri.parse('?$queryString');
    return uri.queryParameters;
  }
}


