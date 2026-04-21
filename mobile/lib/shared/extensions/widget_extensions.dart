import 'package:flutter/material.dart';
import '../constants/app_constants.dart';

/// Widget 擴充方法
extension WidgetExtensions on Widget {
  /// 添加 Padding
  Widget padding({
    double? all,
    double? horizontal,
    double? vertical,
    double? top,
    double? bottom,
    double? left,
    double? right,
  }) {
    return Padding(
      padding: EdgeInsets.only(
        top: top ?? vertical ?? all ?? 0,
        bottom: bottom ?? vertical ?? all ?? 0,
        left: left ?? horizontal ?? all ?? 0,
        right: right ?? horizontal ?? all ?? 0,
      ),
      child: this,
    );
  }

  /// 添加小間距 Padding
  Widget paddingSmall() {
    return padding(all: AppConstants.paddingSmall);
  }

  /// 添加中等間距 Padding
  Widget paddingMedium() {
    return padding(all: AppConstants.paddingMedium);
  }

  /// 添加大間距 Padding
  Widget paddingLarge() {
    return padding(all: AppConstants.paddingLarge);
  }

  /// 添加圓角
  Widget rounded({
    double? radius,
    double? topLeft,
    double? topRight,
    double? bottomLeft,
    double? bottomRight,
  }) {
    return ClipRRect(
      borderRadius: BorderRadius.only(
        topLeft: Radius.circular(topLeft ?? radius ?? 0),
        topRight: Radius.circular(topRight ?? radius ?? 0),
        bottomLeft: Radius.circular(bottomLeft ?? radius ?? 0),
        bottomRight: Radius.circular(bottomRight ?? radius ?? 0),
      ),
      child: this,
    );
  }

  /// 添加小圓角
  Widget roundedSmall() {
    return rounded(radius: AppConstants.borderRadiusSmall);
  }

  /// 添加中等圓角
  Widget roundedMedium() {
    return rounded(radius: AppConstants.borderRadiusMedium);
  }

  /// 添加大圓角
  Widget roundedLarge() {
    return rounded(radius: AppConstants.borderRadiusLarge);
  }

  /// 添加陰影
  Widget shadow({
    Color? color,
    double? blurRadius,
    double? spreadRadius,
    Offset? offset,
  }) {
    return Container(
      decoration: BoxDecoration(
        boxShadow: [
          BoxShadow(
            color: color ?? Colors.black.withValues(alpha: 0.1),
            blurRadius: blurRadius ?? 4.0,
            spreadRadius: spreadRadius ?? 0.0,
            offset: offset ?? const Offset(0, 2),
          ),
        ],
      ),
      child: this,
    );
  }

  /// 置中
  Widget center() {
    return Center(child: this);
  }

  /// 置左
  Widget alignLeft() {
    return Align(alignment: Alignment.centerLeft, child: this);
  }

  /// 置右
  Widget alignRight() {
    return Align(alignment: Alignment.centerRight, child: this);
  }

  /// 置頂
  Widget alignTop() {
    return Align(alignment: Alignment.topCenter, child: this);
  }

  /// 置底
  Widget alignBottom() {
    return Align(alignment: Alignment.bottomCenter, child: this);
  }

  /// 添加寬度限制
  Widget width(double width) {
    return SizedBox(width: width, child: this);
  }

  /// 添加高度限制
  Widget height(double height) {
    return SizedBox(height: height, child: this);
  }

  /// 添加尺寸限制
  Widget size(double width, double height) {
    return SizedBox(width: width, height: height, child: this);
  }

  /// 添加點擊事件
  Widget onTap(VoidCallback? onTap, {bool opaque = true}) {
    return GestureDetector(
      onTap: onTap,
      behavior: opaque ? HitTestBehavior.opaque : HitTestBehavior.deferToChild,
      child: this,
    );
  }

  /// 添加長按事件
  Widget onLongPress(VoidCallback? onLongPress) {
    return GestureDetector(
      onLongPress: onLongPress,
      child: this,
    );
  }
}

