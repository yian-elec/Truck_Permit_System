import 'package:event_bus/event_bus.dart';

/// 全域事件匯流排
class AppEventBus {
  static final EventBus _instance = EventBus();

  /// 取得事件匯流排實例
  static EventBus get instance => _instance;

  /// 發送事件
  static void fire<T>(T event) {
    _instance.fire(event);
  }

  /// 訂閱事件
  static Stream<T> on<T>() {
    return _instance.on<T>();
  }

  /// 取消訂閱
  static void destroy() {
    // EventBus 沒有 destroy 方法，但可以在需要時重新創建
    // 或者使用 StreamSubscription 來管理訂閱
  }
}


