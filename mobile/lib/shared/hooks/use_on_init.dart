import 'package:flutter/material.dart';

/// 類似 React 的 useEffect，只在初始化時執行一次
void useOnInit(VoidCallback callback) {
  // 使用 useEffect 並傳入空依賴陣列
  useEffect(() {
    callback();
  }, const []);
}

/// 類似 React 的 useEffect
void useEffect(VoidCallback? effect, List<Object?> keys) {
  // 這是一個簡化版本，實際使用時建議使用 flutter_hooks 套件
  // 這裡提供一個基本的實現概念
  if (effect != null) {
    effect();
  }
}

