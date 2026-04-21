import 'package:intl/intl.dart';

/// 格式化工具類別
class Formatters {
  /// 日期格式化
  static String formatDate(DateTime date, {String pattern = 'yyyy-MM-dd'}) {
    return DateFormat(pattern).format(date);
  }

  /// 時間格式化
  static String formatTime(DateTime date, {String pattern = 'HH:mm:ss'}) {
    return DateFormat(pattern).format(date);
  }

  /// 日期時間格式化
  static String formatDateTime(DateTime date, {String pattern = 'yyyy-MM-dd HH:mm:ss'}) {
    return DateFormat(pattern).format(date);
  }

  /// 相對時間格式化（例如：2 小時前）
  static String formatRelativeTime(DateTime date) {
    final now = DateTime.now();
    final difference = now.difference(date);

    if (difference.inDays > 365) {
      final years = (difference.inDays / 365).floor();
      return '$years 年前';
    } else if (difference.inDays > 30) {
      final months = (difference.inDays / 30).floor();
      return '$months 個月前';
    } else if (difference.inDays > 0) {
      return '${difference.inDays} 天前';
    } else if (difference.inHours > 0) {
      return '${difference.inHours} 小時前';
    } else if (difference.inMinutes > 0) {
      return '${difference.inMinutes} 分鐘前';
    } else {
      return '剛剛';
    }
  }

  /// 貨幣格式化
  static String formatCurrency(num amount, {String symbol = 'NT\$'}) {
    return '$symbol${amount.toStringAsFixed(2)}';
  }

  /// 數字格式化（千分位）
  static String formatNumber(num number, {int decimals = 0}) {
    final formatter = NumberFormat('#,###${decimals > 0 ? '.${'0' * decimals}' : ''}');
    return formatter.format(number);
  }

  /// 百分比格式化
  static String formatPercentage(double value, {int decimals = 2}) {
    return '${(value * 100).toStringAsFixed(decimals)}%';
  }

  /// 檔案大小格式化
  static String formatFileSize(int bytes) {
    if (bytes < 1024) {
      return '$bytes B';
    } else if (bytes < 1024 * 1024) {
      return '${(bytes / 1024).toStringAsFixed(2)} KB';
    } else if (bytes < 1024 * 1024 * 1024) {
      return '${(bytes / (1024 * 1024)).toStringAsFixed(2)} MB';
    } else {
      return '${(bytes / (1024 * 1024 * 1024)).toStringAsFixed(2)} GB';
    }
  }

  /// 手機號碼格式化（台灣格式：09XX-XXX-XXX）
  static String formatPhoneNumber(String phone) {
    if (phone.length != 10) return phone;
    return '${phone.substring(0, 4)}-${phone.substring(4, 7)}-${phone.substring(7)}';
  }
}


