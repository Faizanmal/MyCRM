import '../core/constants/api_constants.dart';
import '../core/utils/api_client.dart';
import '../models/crm_models.dart';

class OpportunitiesService {
  final ApiClient _apiClient = ApiClient();
  
  Future<List<Opportunity>> getOpportunities({
    int page = 1,
    int pageSize = 20,
    String? search,
    String? stage,
  }) async {
    try {
      final queryParams = {
        'page': page.toString(),
        'page_size': pageSize.toString(),
        if (search != null && search.isNotEmpty) 'search': search,
        if (stage != null && stage.isNotEmpty) 'stage': stage,
      };
      
      final response = await _apiClient.get(
        ApiConstants.opportunities,
        queryParameters: queryParams,
      );
      
      if (response.statusCode == 200) {
        final data = response.data;
        final results = data['results'] as List;
        return results.map((json) => Opportunity.fromJson(json)).toList();
      }
      
      return [];
    } catch (e) {
      rethrow;
    }
  }
  
  Future<Opportunity?> getOpportunity(int id) async {
    try {
      final response = await _apiClient.get(ApiConstants.opportunityDetail(id));
      
      if (response.statusCode == 200) {
        return Opportunity.fromJson(response.data);
      }
      
      return null;
    } catch (e) {
      rethrow;
    }
  }
  
  Future<Opportunity?> createOpportunity(Opportunity opportunity) async {
    try {
      final response = await _apiClient.post(
        ApiConstants.opportunities,
        data: opportunity.toJson(),
      );
      
      if (response.statusCode == 201) {
        return Opportunity.fromJson(response.data);
      }
      
      return null;
    } catch (e) {
      rethrow;
    }
  }
  
  Future<Opportunity?> updateOpportunity(int id, Opportunity opportunity) async {
    try {
      final response = await _apiClient.put(
        ApiConstants.opportunityDetail(id),
        data: opportunity.toJson(),
      );
      
      if (response.statusCode == 200) {
        return Opportunity.fromJson(response.data);
      }
      
      return null;
    } catch (e) {
      rethrow;
    }
  }
  
  Future<bool> deleteOpportunity(int id) async {
    try {
      final response = await _apiClient.delete(ApiConstants.opportunityDetail(id));
      return response.statusCode == 204;
    } catch (e) {
      rethrow;
    }
  }
}
