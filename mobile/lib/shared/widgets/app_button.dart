import 'package:flutter/material.dart';
import '../constants/app_constants.dart';

/// 應用程式按鈕樣式
enum AppButtonStyle {
  primary,
  secondary,
  outline,
  text,
  danger,
}

/// 應用程式按鈕尺寸
enum AppButtonSize {
  small,
  medium,
  large,
}

/// 應用程式通用按鈕
class AppButton extends StatelessWidget {
  final String text;
  final VoidCallback? onPressed;
  final AppButtonStyle style;
  final AppButtonSize size;
  final bool isLoading;
  final bool isFullWidth;
  final IconData? icon;
  final Color? backgroundColor;
  final Color? textColor;
  final double? width;
  final double? height;

  const AppButton({
    super.key,
    required this.text,
    this.onPressed,
    this.style = AppButtonStyle.primary,
    this.size = AppButtonSize.medium,
    this.isLoading = false,
    this.isFullWidth = false,
    this.icon,
    this.backgroundColor,
    this.textColor,
    this.width,
    this.height,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final foregroundColor = textColor ?? _getForegroundColor(colorScheme);
    final buttonStyle = _getButtonStyle(theme);
    final buttonSize = _getButtonSize();

    Widget button = ElevatedButton(
      onPressed: isLoading ? null : onPressed,
      style: buttonStyle,
      child: isLoading
          ? SizedBox(
              width: buttonSize.iconSize,
              height: buttonSize.iconSize,
              child: CircularProgressIndicator(
                strokeWidth: 2,
                valueColor: AlwaysStoppedAnimation<Color>(foregroundColor),
              ),
            )
          : Row(
              mainAxisSize: isFullWidth ? MainAxisSize.max : MainAxisSize.min,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                if (icon != null) ...[
                  Icon(icon, size: buttonSize.iconSize, color: foregroundColor),
                  SizedBox(width: buttonSize.spacing),
                ],
                Text(
                  text,
                  style: TextStyle(
                    fontSize: buttonSize.fontSize,
                    fontWeight: FontWeight.w600,
                    color: foregroundColor,
                  ),
                ),
              ],
            ),
    );

    if (width != null || height != null || isFullWidth) {
      button = SizedBox(
        width: isFullWidth ? double.infinity : width,
        height: height ?? buttonSize.height,
        child: button,
      );
    }

    return button;
  }

  ButtonStyle _getButtonStyle(ThemeData theme) {
    final colorScheme = theme.colorScheme;
    final backgroundColor = this.backgroundColor ?? _getBackgroundColor(colorScheme);
    final foregroundColor = textColor ?? _getForegroundColor(colorScheme);

    switch (style) {
      case AppButtonStyle.primary:
        return ElevatedButton.styleFrom(
          backgroundColor: backgroundColor,
          foregroundColor: foregroundColor,
          elevation: 2,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(AppConstants.borderRadiusMedium),
          ),
        );
      case AppButtonStyle.secondary:
        return ElevatedButton.styleFrom(
          backgroundColor: colorScheme.secondary,
          foregroundColor: colorScheme.onSecondary,
          elevation: 2,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(AppConstants.borderRadiusMedium),
          ),
        );
      case AppButtonStyle.outline:
        return OutlinedButton.styleFrom(
          foregroundColor: foregroundColor,
          side: BorderSide(color: backgroundColor, width: 2),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(AppConstants.borderRadiusMedium),
          ),
        );
      case AppButtonStyle.text:
        return TextButton.styleFrom(
          foregroundColor: foregroundColor,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(AppConstants.borderRadiusMedium),
          ),
        );
      case AppButtonStyle.danger:
        return ElevatedButton.styleFrom(
          backgroundColor: Colors.red,
          foregroundColor: Colors.white,
          elevation: 2,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(AppConstants.borderRadiusMedium),
          ),
        );
    }
  }

  Color _getBackgroundColor(ColorScheme colorScheme) {
    switch (style) {
      case AppButtonStyle.primary:
        return colorScheme.primary;
      case AppButtonStyle.secondary:
        return colorScheme.secondary;
      case AppButtonStyle.outline:
      case AppButtonStyle.text:
        return Colors.transparent;
      case AppButtonStyle.danger:
        return Colors.red;
    }
  }

  Color _getForegroundColor(ColorScheme colorScheme) {
    switch (style) {
      case AppButtonStyle.primary:
        return colorScheme.onPrimary;
      case AppButtonStyle.secondary:
        return colorScheme.onSecondary;
      case AppButtonStyle.outline:
        return colorScheme.primary;
      case AppButtonStyle.text:
        return colorScheme.primary;
      case AppButtonStyle.danger:
        return Colors.white;
    }
  }

  _ButtonSize _getButtonSize() {
    switch (size) {
      case AppButtonSize.small:
        return const _ButtonSize(
          height: 32,
          fontSize: 14,
          iconSize: 16,
          spacing: 4,
        );
      case AppButtonSize.medium:
        return const _ButtonSize(
          height: 44,
          fontSize: 16,
          iconSize: 20,
          spacing: 8,
        );
      case AppButtonSize.large:
        return const _ButtonSize(
          height: 56,
          fontSize: 18,
          iconSize: 24,
          spacing: 12,
        );
    }
  }
}

class _ButtonSize {
  final double height;
  final double fontSize;
  final double iconSize;
  final double spacing;

  const _ButtonSize({
    required this.height,
    required this.fontSize,
    required this.iconSize,
    required this.spacing,
  });
}

