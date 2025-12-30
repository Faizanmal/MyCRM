import '../core/constants/api_constants.dart';
import '../core/utils/api_client.dart';

class DashboardService {
  final ApiClient _apiClient = ApiClient();
  
  Future<Map<String, dynamic>?> getDashboardStats() async {
    try {
      final response = await _apiClient.get(ApiConstants.dashboardMetrics);
      
      if (response.statusCode == 200) {
        return response.data as Map<String, dynamic>;
      }
      
      return null;
    } catch (e) {
      rethrow;
    }
  }
  
  Future<Map<String, dynamic>?> getDashboardCharts() async {
    try {
      final response = await _apiClient.get(ApiConstants.salesPipeline);
      
      if (response.statusCode == 200) {
        return response.data as Map<String, dynamic>;
      }
      
      return null;
    } catch (e) {
      rethrow;
    }
  }
  
  Future<List<Map<String, dynamic>>> getRecentActivity({int limit = 10}) async {
    try {
      final response = await _apiClient.get(
        ApiConstants.activityFeed,
        queryParameters: {'limit': limit.toString()},
      );
      
      if (response.statusCode == 200) {
        return List<Map<String, dynamic>>.from(response.data);
      }
      
      return [];
    } catch (e) {
      rethrow;
    }
  }
}
