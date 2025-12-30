import 'package:flutter/material.dart';
import '../../core/constants/app_constants.dart';
import '../../core/utils/validators.dart';

class ForgotPasswordScreen extends StatefulWidget {
  const ForgotPasswordScreen({super.key});
  
  @override
  State<ForgotPasswordScreen> createState() => _ForgotPasswordScreenState();
}

class _ForgotPasswordScreenState extends State<ForgotPasswordScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  bool _isLoading = false;
  bool _emailSent = false;
  
  @override
  void dispose() {
    _emailController.dispose();
    super.dispose();
  }
  
  Future<void> _handleResetPassword() async {
    if (!_formKey.currentState!.validate()) return;
    
    setState(() => _isLoading = true);
    
    // Simulate API call
    await Future.delayed(const Duration(seconds: 2));
    
    if (mounted) {
      setState(() {
        _isLoading = false;
        _emailSent = true;
      });
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Color(0xFF3B82F6),
              Color(0xFF8B5CF6),
              Color(0xFFEC4899),
            ],
          ),
        ),
        child: SafeArea(
          child: Center(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(AppSizes.paddingLg),
              child: Card(
                elevation: 8,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(AppSizes.radiusLg),
                ),
                child: Container(
                  constraints: const BoxConstraints(maxWidth: 450),
                  padding: const EdgeInsets.all(AppSizes.paddingXl),
                  child: _emailSent ? _buildSuccessContent() : _buildFormContent(),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
  
  Widget _buildFormContent() {
    return Form(
      key: _formKey,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Back Button
          Align(
            alignment: Alignment.centerLeft,
            child: IconButton(
              icon: const Icon(Icons.arrow_back),
              onPressed: () => Navigator.of(context).pop(),
            ),
          ),
          
          // Icon
          Container(
            width: 80,
            height: 80,
            decoration: BoxDecoration(
              color: AppColors.warning.withValues(alpha: 0.1),
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.lock_reset,
              size: 40,
              color: AppColors.warning,
            ),
          ),
          const SizedBox(height: AppSizes.paddingLg),
          
          // Title
          Text(
            'Forgot Password?',
            style: Theme.of(context).textTheme.headlineMedium?.copyWith(
              fontWeight: FontWeight.bold,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: AppSizes.paddingSm),
          
          // Description
          Text(
            "No worries! Enter your email address and we'll send you a link to reset your password.",
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              color: AppColors.grey600,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: AppSizes.paddingXl),
          
          // Email Field
          TextFormField(
            controller: _emailController,
            decoration: InputDecoration(
              labelText: 'Email Address',
              prefixIcon: const Icon(Icons.email),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(AppSizes.radiusMd),
              ),
            ),
            validator: Validators.validateEmail,
            keyboardType: TextInputType.emailAddress,
            textInputAction: TextInputAction.done,
            onFieldSubmitted: (_) => _handleResetPassword(),
          ),
          const SizedBox(height: AppSizes.paddingLg),
          
          // Reset Button
          ElevatedButton(
            onPressed: _isLoading ? null : _handleResetPassword,
            style: ElevatedButton.styleFrom(
              padding: const EdgeInsets.symmetric(vertical: AppSizes.paddingMd),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(AppSizes.radiusMd),
              ),
            ),
            child: _isLoading
                ? const SizedBox(
                    height: 20,
                    width: 20,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Text(
                    'Send Reset Link',
                    style: TextStyle(
                      fontSize: AppSizes.fontLg,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
          ),
          const SizedBox(height: AppSizes.paddingMd),
          
          // Back to Login
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Back to Login'),
          ),
        ],
      ),
    );
  }
  
  Widget _buildSuccessContent() {
    return Column(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // Success Icon
        Container(
          width: 100,
          height: 100,
          decoration: BoxDecoration(
            color: AppColors.success.withValues(alpha: 0.1),
            shape: BoxShape.circle,
          ),
          child: const Icon(
            Icons.mark_email_read,
            size: 50,
            color: AppColors.success,
          ),
        ),
        const SizedBox(height: AppSizes.paddingLg),
        
        // Title
        Text(
          'Check Your Email',
          style: Theme.of(context).textTheme.headlineMedium?.copyWith(
            fontWeight: FontWeight.bold,
          ),
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: AppSizes.paddingSm),
        
        // Description
        Text(
          'We have sent a password reset link to:',
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
            color: AppColors.grey600,
          ),
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: AppSizes.paddingSm),
        
        // Email
        Text(
          _emailController.text,
          style: Theme.of(context).textTheme.bodyLarge?.copyWith(
            fontWeight: FontWeight.bold,
          ),
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: AppSizes.paddingLg),
        
        // Info Box
        Container(
          padding: const EdgeInsets.all(AppSizes.paddingMd),
          decoration: BoxDecoration(
            color: AppColors.info.withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(AppSizes.radiusMd),
            border: Border.all(
              color: AppColors.info.withValues(alpha: 0.3),
            ),
          ),
          child: Row(
            children: [
              const Icon(Icons.info, color: AppColors.info),
              const SizedBox(width: AppSizes.paddingSm),
              Expanded(
                child: Text(
                  "Didn't receive the email? Check your spam folder or try again.",
                  style: TextStyle(
                    fontSize: AppSizes.fontSm,
                    color: AppColors.grey700,
                  ),
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: AppSizes.paddingXl),
        
        // Resend Button
        OutlinedButton(
          onPressed: () {
            setState(() => _emailSent = false);
          },
          style: OutlinedButton.styleFrom(
            padding: const EdgeInsets.symmetric(vertical: AppSizes.paddingMd),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(AppSizes.radiusMd),
            ),
          ),
          child: const Text('Try Different Email'),
        ),
        const SizedBox(height: AppSizes.paddingSm),
        
        // Back to Login
        ElevatedButton(
          onPressed: () => Navigator.of(context).pop(),
          style: ElevatedButton.styleFrom(
            padding: const EdgeInsets.symmetric(vertical: AppSizes.paddingMd),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(AppSizes.radiusMd),
            ),
          ),
          child: const Text(
            'Back to Login',
            style: TextStyle(
              fontSize: AppSizes.fontLg,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
      ],
    );
  }
}


class ResetPasswordScreen extends StatefulWidget {
  final String token;
  
  const ResetPasswordScreen({super.key, required this.token});
  
  @override
  State<ResetPasswordScreen> createState() => _ResetPasswordScreenState();
}

class _ResetPasswordScreenState extends State<ResetPasswordScreen> {
  final _formKey = GlobalKey<FormState>();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();
  bool _obscurePassword = true;
  bool _obscureConfirmPassword = true;
  bool _isLoading = false;
  bool _resetSuccess = false;
  
  @override
  void dispose() {
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }
  
  Future<void> _handleResetPassword() async {
    if (!_formKey.currentState!.validate()) return;
    
    setState(() => _isLoading = true);
    
    // Simulate API call
    await Future.delayed(const Duration(seconds: 2));
    
    if (mounted) {
      setState(() {
        _isLoading = false;
        _resetSuccess = true;
      });
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Color(0xFF3B82F6),
              Color(0xFF8B5CF6),
              Color(0xFFEC4899),
            ],
          ),
        ),
        child: SafeArea(
          child: Center(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(AppSizes.paddingLg),
              child: Card(
                elevation: 8,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(AppSizes.radiusLg),
                ),
                child: Container(
                  constraints: const BoxConstraints(maxWidth: 450),
                  padding: const EdgeInsets.all(AppSizes.paddingXl),
                  child: _resetSuccess ? _buildSuccessContent() : _buildFormContent(),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
  
  Widget _buildFormContent() {
    return Form(
      key: _formKey,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Icon
          Container(
            width: 80,
            height: 80,
            decoration: BoxDecoration(
              color: AppColors.primary.withValues(alpha: 0.1),
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.lock,
              size: 40,
              color: AppColors.primary,
            ),
          ),
          const SizedBox(height: AppSizes.paddingLg),
          
          // Title
          Text(
            'Create New Password',
            style: Theme.of(context).textTheme.headlineMedium?.copyWith(
              fontWeight: FontWeight.bold,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: AppSizes.paddingSm),
          
          // Description
          Text(
            'Your new password must be different from your previous passwords.',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              color: AppColors.grey600,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: AppSizes.paddingXl),
          
          // New Password Field
          TextFormField(
            controller: _passwordController,
            obscureText: _obscurePassword,
            decoration: InputDecoration(
              labelText: 'New Password',
              prefixIcon: const Icon(Icons.lock),
              suffixIcon: IconButton(
                icon: Icon(
                  _obscurePassword ? Icons.visibility : Icons.visibility_off,
                ),
                onPressed: () {
                  setState(() => _obscurePassword = !_obscurePassword);
                },
              ),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(AppSizes.radiusMd),
              ),
            ),
            validator: Validators.validatePassword,
            textInputAction: TextInputAction.next,
          ),
          const SizedBox(height: AppSizes.paddingMd),
          
          // Confirm Password Field
          TextFormField(
            controller: _confirmPasswordController,
            obscureText: _obscureConfirmPassword,
            decoration: InputDecoration(
              labelText: 'Confirm New Password',
              prefixIcon: const Icon(Icons.lock),
              suffixIcon: IconButton(
                icon: Icon(
                  _obscureConfirmPassword ? Icons.visibility : Icons.visibility_off,
                ),
                onPressed: () {
                  setState(() => _obscureConfirmPassword = !_obscureConfirmPassword);
                },
              ),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(AppSizes.radiusMd),
              ),
            ),
            validator: (value) => Validators.validatePasswordMatch(
              _passwordController.text,
              value,
            ),
            textInputAction: TextInputAction.done,
            onFieldSubmitted: (_) => _handleResetPassword(),
          ),
          const SizedBox(height: AppSizes.paddingSm),
          
          // Password Requirements
          Container(
            padding: const EdgeInsets.all(AppSizes.paddingSm),
            decoration: BoxDecoration(
              color: AppColors.grey100,
              borderRadius: BorderRadius.circular(AppSizes.radiusSm),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Password must contain:',
                  style: TextStyle(
                    fontSize: AppSizes.fontSm,
                    fontWeight: FontWeight.bold,
                    color: AppColors.grey700,
                  ),
                ),
                const SizedBox(height: 4),
                _buildRequirement('At least 8 characters'),
                _buildRequirement('One uppercase letter'),
                _buildRequirement('One lowercase letter'),
                _buildRequirement('One number'),
              ],
            ),
          ),
          const SizedBox(height: AppSizes.paddingLg),
          
          // Reset Button
          ElevatedButton(
            onPressed: _isLoading ? null : _handleResetPassword,
            style: ElevatedButton.styleFrom(
              padding: const EdgeInsets.symmetric(vertical: AppSizes.paddingMd),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(AppSizes.radiusMd),
              ),
            ),
            child: _isLoading
                ? const SizedBox(
                    height: 20,
                    width: 20,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Text(
                    'Reset Password',
                    style: TextStyle(
                      fontSize: AppSizes.fontLg,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildRequirement(String text) {
    return Padding(
      padding: const EdgeInsets.only(left: 8, top: 2),
      child: Row(
        children: [
          Icon(
            Icons.check_circle,
            size: 14,
            color: AppColors.grey400,
          ),
          const SizedBox(width: 4),
          Text(
            text,
            style: TextStyle(
              fontSize: AppSizes.fontXs,
              color: AppColors.grey600,
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildSuccessContent() {
    return Column(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // Success Icon
        Container(
          width: 100,
          height: 100,
          decoration: BoxDecoration(
            color: AppColors.success.withValues(alpha: 0.1),
            shape: BoxShape.circle,
          ),
          child: const Icon(
            Icons.check_circle,
            size: 50,
            color: AppColors.success,
          ),
        ),
        const SizedBox(height: AppSizes.paddingLg),
        
        // Title
        Text(
          'Password Reset!',
          style: Theme.of(context).textTheme.headlineMedium?.copyWith(
            fontWeight: FontWeight.bold,
          ),
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: AppSizes.paddingSm),
        
        // Description
        Text(
          'Your password has been reset successfully. You can now sign in with your new password.',
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
            color: AppColors.grey600,
          ),
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: AppSizes.paddingXl),
        
        // Back to Login Button
        ElevatedButton(
          onPressed: () {
            // Pop back to login screen
            Navigator.of(context).popUntil((route) => route.isFirst);
          },
          style: ElevatedButton.styleFrom(
            padding: const EdgeInsets.symmetric(vertical: AppSizes.paddingMd),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(AppSizes.radiusMd),
            ),
          ),
          child: const Text(
            'Sign In',
            style: TextStyle(
              fontSize: AppSizes.fontLg,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
      ],
    );
  }
}
