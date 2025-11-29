import 'package:flutter/material.dart';
import '../core/constants/app_constants.dart';

class LoadingIndicator extends StatelessWidget {
  final String? message;
  final double size;
  
  const LoadingIndicator({
    super.key,
    this.message,
    this.size = 40,
  });
  
  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          SizedBox(
            width: size,
            height: size,
            child: const CircularProgressIndicator(
              strokeWidth: 3,
            ),
          ),
          if (message != null) ...[
            const SizedBox(height: AppSizes.paddingMd),
            Text(
              message!,
              style: TextStyle(
                color: AppColors.grey600,
                fontSize: AppSizes.fontMd,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ],
      ),
    );
  }
}
