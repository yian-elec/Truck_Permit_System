/// 驗證工具類別
class Validators {
  /// 驗證 Email
  static bool isValidEmail(String? email) {
    if (email == null || email.isEmpty) return false;
    final emailRegex = RegExp(
      r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    );
    return emailRegex.hasMatch(email);
  }

  /// 驗證手機號碼（台灣格式）
  static bool isValidPhone(String? phone) {
    if (phone == null || phone.isEmpty) return false;
    final phoneRegex = RegExp(r'^09\d{8}$');
    return phoneRegex.hasMatch(phone);
  }

  /// 驗證密碼強度
  /// 至少 8 個字元，包含大小寫字母、數字和特殊字元
  static bool isStrongPassword(String? password) {
    if (password == null || password.length < 8) return false;
    final hasUpperCase = RegExp(r'[A-Z]').hasMatch(password);
    final hasLowerCase = RegExp(r'[a-z]').hasMatch(password);
    final hasDigit = RegExp(r'\d').hasMatch(password);
    final hasSpecialChar = RegExp(r'[!@#$%^&*(),.?":{}|<>]').hasMatch(password);
    return hasUpperCase && hasLowerCase && hasDigit && hasSpecialChar;
  }

  /// 驗證 URL
  static bool isValidUrl(String? url) {
    if (url == null || url.isEmpty) return false;
    try {
      final uri = Uri.parse(url);
      return uri.hasScheme && (uri.scheme == 'http' || uri.scheme == 'https');
    } catch (e) {
      return false;
    }
  }

  /// 驗證是否為空字串
  static bool isEmpty(String? value) {
    return value == null || value.trim().isEmpty;
  }

  /// 驗證是否不為空字串
  static bool isNotEmpty(String? value) {
    return !isEmpty(value);
  }

  /// 驗證數字範圍
  static bool isInRange(num? value, num min, num max) {
    if (value == null) return false;
    return value >= min && value <= max;
  }

  /// 驗證字串長度
  static bool isValidLength(String? value, int min, int max) {
    if (value == null) return false;
    return value.length >= min && value.length <= max;
  }
}


