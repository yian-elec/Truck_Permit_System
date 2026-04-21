import 'package:shared_preferences/shared_preferences.dart';
import 'package:hive_flutter/hive_flutter.dart';

/// 儲存服務抽象介面
abstract class IStorageService {
  Future<void> setString(String key, String value);
  Future<String?> getString(String key);
  Future<void> setInt(String key, int value);
  Future<int?> getInt(String key);
  Future<void> setBool(String key, bool value);
  Future<bool?> getBool(String key);
  Future<void> setDouble(String key, double value);
  Future<double?> getDouble(String key);
  Future<void> setStringList(String key, List<String> value);
  Future<List<String>?> getStringList(String key);
  Future<void> remove(String key);
  Future<void> clear();
  Future<bool> containsKey(String key);
}

/// SharedPreferences 儲存服務實作
class SharedPreferencesStorageService implements IStorageService {
  late final SharedPreferences _prefs;

  /// 初始化
  Future<void> init() async {
    _prefs = await SharedPreferences.getInstance();
  }

  @override
  Future<void> setString(String key, String value) async {
    await _prefs.setString(key, value);
  }

  @override
  Future<String?> getString(String key) async {
    return _prefs.getString(key);
  }

  @override
  Future<void> setInt(String key, int value) async {
    await _prefs.setInt(key, value);
  }

  @override
  Future<int?> getInt(String key) async {
    return _prefs.getInt(key);
  }

  @override
  Future<void> setBool(String key, bool value) async {
    await _prefs.setBool(key, value);
  }

  @override
  Future<bool?> getBool(String key) async {
    return _prefs.getBool(key);
  }

  @override
  Future<void> setDouble(String key, double value) async {
    await _prefs.setDouble(key, value);
  }

  @override
  Future<double?> getDouble(String key) async {
    return _prefs.getDouble(key);
  }

  @override
  Future<void> setStringList(String key, List<String> value) async {
    await _prefs.setStringList(key, value);
  }

  @override
  Future<List<String>?> getStringList(String key) async {
    return _prefs.getStringList(key);
  }

  @override
  Future<void> remove(String key) async {
    await _prefs.remove(key);
  }

  @override
  Future<void> clear() async {
    await _prefs.clear();
  }

  @override
  Future<bool> containsKey(String key) async {
    return _prefs.containsKey(key);
  }
}

/// Hive 儲存服務實作
class HiveStorageService implements IStorageService {
  static const String _boxName = 'app_storage';
  Box? _box;

  /// 初始化
  Future<void> init() async {
    await Hive.initFlutter();
    _box = await Hive.openBox(_boxName);
  }

  Box get box {
    if (_box == null) {
      throw Exception('HiveStorageService not initialized. Call init() first.');
    }
    return _box!;
  }

  @override
  Future<void> setString(String key, String value) async {
    await box.put(key, value);
  }

  @override
  Future<String?> getString(String key) async {
    return box.get(key) as String?;
  }

  @override
  Future<void> setInt(String key, int value) async {
    await box.put(key, value);
  }

  @override
  Future<int?> getInt(String key) async {
    return box.get(key) as int?;
  }

  @override
  Future<void> setBool(String key, bool value) async {
    await box.put(key, value);
  }

  @override
  Future<bool?> getBool(String key) async {
    return box.get(key) as bool?;
  }

  @override
  Future<void> setDouble(String key, double value) async {
    await box.put(key, value);
  }

  @override
  Future<double?> getDouble(String key) async {
    return box.get(key) as double?;
  }

  @override
  Future<void> setStringList(String key, List<String> value) async {
    await box.put(key, value);
  }

  @override
  Future<List<String>?> getStringList(String key) async {
    return box.get(key) as List<String>?;
  }

  @override
  Future<void> remove(String key) async {
    await box.delete(key);
  }

  @override
  Future<void> clear() async {
    await box.clear();
  }

  @override
  Future<bool> containsKey(String key) async {
    return box.containsKey(key);
  }
}

/// 儲存服務工廠
class StorageService {
  static IStorageService? _instance;

  /// 初始化儲存服務
  static Future<void> initialize({StorageType type = StorageType.sharedPreferences}) async {
    switch (type) {
      case StorageType.sharedPreferences:
        _instance = SharedPreferencesStorageService();
        await (_instance as SharedPreferencesStorageService).init();
        break;
      case StorageType.hive:
        _instance = HiveStorageService();
        await (_instance as HiveStorageService).init();
        break;
    }
  }

  static IStorageService get instance {
    if (_instance == null) {
      throw Exception('StorageService not initialized. Call StorageService.initialize() first.');
    }
    return _instance!;
  }
}

/// 儲存類型
enum StorageType {
  sharedPreferences,
  hive,
}

