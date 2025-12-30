import 'package:flutter/material.dart';
import '../core/constants/app_constants.dart';

class EmptyState extends StatelessWidget {
  final String title;
  final String? subtitle;
  final IconData icon;
  final VoidCallback? onAction;
  final String? actionLabel;
  final Widget? action;
  
  const EmptyState({
    super.key,
    required this.title,
    this.subtitle,
    required this.icon,
    this.onAction,
    this.actionLabel,
    this.action,
  });
  
  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(AppSizes.paddingXl),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              icon,
              size: 80,
              color: AppColors.grey400,
            ),
            const SizedBox(height: AppSizes.paddingLg),
            Text(
              title,
              style: const TextStyle(
                fontSize: AppSizes.fontXl,
                fontWeight: FontWeight.w600,
              ),
              textAlign: TextAlign.center,
            ),
            if (subtitle != null) ...[
              const SizedBox(height: AppSizes.paddingSm),
              Text(
                subtitle!,
                style: TextStyle(
                  fontSize: AppSizes.fontMd,
                  color: AppColors.grey600,
                ),
                textAlign: TextAlign.center,
              ),
            ],
            if (onAction != null && actionLabel != null) ...[
              const SizedBox(height: AppSizes.paddingLg),
              ElevatedButton.icon(
                onPressed: onAction,
                icon: const Icon(Icons.add),
                label: Text(actionLabel!),
              ),
            ],
            if (action != null) ...[
              const SizedBox(height: AppSizes.paddingLg),
              action!,
            ],
          ],
        ),
      ),
    );
  }
}
