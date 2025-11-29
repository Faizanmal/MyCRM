import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../core/constants/api_constants.dart';
import '../core/constants/app_constants.dart';
import '../core/utils/api_client.dart';
import '../models/user_model.dart';

class AuthService {
  final ApiClient _apiClient = ApiClient();
  
  // Login
  Future<Map<String, dynamic>> login(String username, String password) async {
    try {
      final response = await _apiClient.post(
        ApiConstants.login,
        data: {
          'username': username,
          'password': password,
        },
      );
      
      if (response.statusCode == 200) {
        final data = response.data;
        final token = data['access'];
        final refreshToken = data['refresh'];
        final user = User.fromJson(data['user']);
        
        // Save tokens and user data
        await _saveAuthData(token, refreshToken, user);
        
        return {
          'success': true,
          'user': user,
          'token': token,
        };
      }
      
      return {
        'success': false,
        'message': 'Login failed',
      };
    } catch (e) {
      return {
        'success': false,
        'message': e.toString(),
      };
    }
  }
  
  // Register
  Future<Map<String, dynamic>> register({
    required String username,
    required String email,
    required String password,
    String? firstName,
    String? lastName,
  }) async {
    try {
      final response = await _apiClient.post(
        ApiConstants.register,
        data: {
          'username': username,
          'email': email,
          'password': password,
          'first_name': firstName,
          'last_name': lastName,
        },
      );
      
      if (response.statusCode == 201) {
        final data = response.data;
        final token = data['access'];
        final refreshToken = data['refresh'];
        final user = User.fromJson(data['user']);
        
        // Save tokens and user data
        await _saveAuthData(token, refreshToken, user);
        
        return {
          'success': true,
          'user': user,
          'token': token,
        };
      }
      
      return {
        'success': false,
        'message': 'Registration failed',
      };
    } catch (e) {
      return {
        'success': false,
        'message': e.toString(),
      };
    }
  }
  
  // Logout
  Future<void> logout() async {
    try {
      await _apiClient.post(ApiConstants.logout);
    } catch (e) {
      // Ignore errors during logout
    } finally {
      await _clearAuthData();
    }
  }
  
  // Get current user
  Future<User?> getCurrentUser() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final userJson = prefs.getString(AppConstants.userKey);
      
      if (userJson != null) {
        final userData = jsonDecode(userJson);
        return User.fromJson(userData);
      }
      
      return null;
    } catch (e) {
      return null;
    }
  }
  
  // Check if user is authenticated
  Future<bool> isAuthenticated() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString(AppConstants.tokenKey);
    return token != null;
  }
  
  // Get auth token
  Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(AppConstants.tokenKey);
  }
  
  // Fetch user profile from API
  Future<User?> fetchUserProfile() async {
    try {
      final response = await _apiClient.get(ApiConstants.userProfile);
      
      if (response.statusCode == 200) {
        final user = User.fromJson(response.data);
        
        // Update stored user data
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString(AppConstants.userKey, jsonEncode(user.toJson()));
        
        return user;
      }
      
      return null;
    } catch (e) {
      return null;
    }
  }
  
  // Update user profile
  Future<Map<String, dynamic>> updateProfile({
    String? firstName,
    String? lastName,
    String? email,
    String? phone,
  }) async {
    try {
      final response = await _apiClient.patch(
        ApiConstants.userProfile,
        data: {
          if (firstName != null) 'first_name': firstName,
          if (lastName != null) 'last_name': lastName,
          if (email != null) 'email': email,
          if (phone != null) 'phone': phone,
        },
      );
      
      if (response.statusCode == 200) {
        final user = User.fromJson(response.data);
        
        // Update stored user data
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString(AppConstants.userKey, jsonEncode(user.toJson()));
        
        return {
          'success': true,
          'user': user,
        };
      }
      
      return {
        'success': false,
        'message': 'Update failed',
      };
    } catch (e) {
      return {
        'success': false,
        'message': e.toString(),
      };
    }
  }
  
  // Save auth data
  Future<void> _saveAuthData(String token, String refreshToken, User user) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(AppConstants.tokenKey, token);
    await prefs.setString(AppConstants.refreshTokenKey, refreshToken);
    await prefs.setString(AppConstants.userKey, jsonEncode(user.toJson()));
  }
  
  // Clear auth data
  Future<void> _clearAuthData() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(AppConstants.tokenKey);
    await prefs.remove(AppConstants.refreshTokenKey);
    await prefs.remove(AppConstants.userKey);
  }
}
