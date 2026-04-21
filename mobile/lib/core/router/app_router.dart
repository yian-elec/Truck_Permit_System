import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../shared/constants/route_names.dart';
import '../../test_page.dart';

/// 應用程式路由配置
class AppRouter {
  static final GoRouter router = GoRouter(
    initialLocation: RouteNames.home,
    routes: [
      // 在這裡添加你的路由
      GoRoute(
        path: RouteNames.home,
        name: RouteNames.home,
        builder: (context, state) => const TestPage(),
      ),
      // 可以添加更多路由...
    ],
    errorBuilder: (context, state) => Scaffold(
      body: Center(
        child: Text('Page not found: ${state.uri}'),
      ),
    ),
    // 可以添加重定向邏輯
    redirect: (context, state) {
      // 例如：檢查登入狀態
      // final isLoggedIn = ...;
      // if (!isLoggedIn && state.uri.path != '/login') {
      //   return '/login';
      // }
      return null;
    },
  );
}

