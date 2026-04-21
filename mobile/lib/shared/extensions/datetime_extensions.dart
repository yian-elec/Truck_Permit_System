import '../utils/formatters.dart';

/// DateTime 擴充方法
extension DateTimeExtensions on DateTime {
  /// 格式化為日期字串
  String toDateString({String pattern = 'yyyy-MM-dd'}) {
    return Formatters.formatDate(this, pattern: pattern);
  }

  /// 格式化為時間字串
  String toTimeString({String pattern = 'HH:mm:ss'}) {
    return Formatters.formatTime(this, pattern: pattern);
  }

  /// 格式化為日期時間字串
  String toDateTimeString({String pattern = 'yyyy-MM-dd HH:mm:ss'}) {
    return Formatters.formatDateTime(this, pattern: pattern);
  }

  /// 格式化為相對時間字串
  String toRelativeTimeString() {
    return Formatters.formatRelativeTime(this);
  }

  /// 檢查是否為今天
  bool get isToday {
    final now = DateTime.now();
    return year == now.year && month == now.month && day == now.day;
  }

  /// 檢查是否為昨天
  bool get isYesterday {
    final yesterday = DateTime.now().subtract(const Duration(days: 1));
    return year == yesterday.year && month == yesterday.month && day == yesterday.day;
  }

  /// 檢查是否為本週
  bool get isThisWeek {
    final now = DateTime.now();
    final weekStart = now.subtract(Duration(days: now.weekday - 1));
    return isAfter(weekStart.subtract(const Duration(days: 1))) && isBefore(now.add(const Duration(days: 1)));
  }

  /// 檢查是否為本月
  bool get isThisMonth {
    final now = DateTime.now();
    return year == now.year && month == now.month;
  }

  /// 檢查是否為今年
  bool get isThisYear {
    return year == DateTime.now().year;
  }

  /// 取得年齡
  int get age {
    final now = DateTime.now();
    int age = now.year - year;
    if (now.month < month || (now.month == month && now.day < day)) {
      age--;
    }
    return age;
  }

  /// 取得開始時間（00:00:00）
  DateTime get startOfDay {
    return DateTime(year, month, day);
  }

  /// 取得結束時間（23:59:59）
  DateTime get endOfDay {
    return DateTime(year, month, day, 23, 59, 59, 999);
  }
}


