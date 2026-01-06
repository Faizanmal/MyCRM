import '../core/constants/api_constants.dart';
import '../core/utils/api_client.dart';
import '../models/social_models.dart';

class SocialSellingService {
  final ApiClient _apiClient;

  SocialSellingService(this._apiClient);

  Future<List<SocialProfile>> getProfiles() async {
    final response = await _apiClient.get(ApiConstants.socialProfiles);
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => SocialProfile.fromJson(json)).toList();
    }
    throw Exception('Failed to load social profiles');
  }

  Future<void> connectLinkedIn() async {
    // In a real app, this would likely open a WebView for OAuth
    final response = await _apiClient.post(ApiConstants.linkedInConnect);
    if (response.statusCode != 200 && response.statusCode != 201) {
      throw Exception('Failed to initiate LinkedIn connection');
    }
  }

  Future<SocialMetrics> getMetrics() async {
    final response = await _apiClient.get(ApiConstants.socialScores);
    if (response.statusCode == 200) {
      return SocialMetrics.fromJson(response.data);
    }
    throw Exception('Failed to load metrics');
  }

  Future<List<SocialPost>> getRecentPosts() async {
    final response = await _apiClient.get(ApiConstants.socialPosts);
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => SocialPost.fromJson(json)).toList();
    }
    throw Exception('Failed to load recent posts');
  }

  Future<List<SocialContentTemplate>> getContentLibrary() async {
    final response = await _apiClient.get(ApiConstants.socialContent);
    if (response.statusCode == 200) {
      final List<dynamic> data = response.data is List ? response.data : response.data['results'] ?? [];
      return data.map((json) => SocialContentTemplate.fromJson(json)).toList();
    }
    throw Exception('Failed to load content library');
  }

  Future<void> shareContent({
    required String platform,
    required String content,
    String? mediaUrl,
  }) async {
    final response = await _apiClient.post(ApiConstants.socialPosts, data: {
      'platform': platform,
      'content': content,
      if (mediaUrl != null) 'media_url': mediaUrl,
    });
    if (response.statusCode != 201) {
      throw Exception('Failed to share content');
    }
  }
}
