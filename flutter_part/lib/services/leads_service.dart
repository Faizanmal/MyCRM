import '../core/constants/api_constants.dart';
import '../core/utils/api_client.dart';
import '../models/crm_models.dart';

class LeadsService {
  final ApiClient _apiClient = ApiClient();
  
  Future<List<Lead>> getLeads({
    int page = 1,
    int pageSize = 20,
    String? search,
    String? status,
    String? source,
  }) async {
    try {
      final queryParams = {
        'page': page.toString(),
        'page_size': pageSize.toString(),
        if (search != null && search.isNotEmpty) 'search': search,
        if (status != null && status.isNotEmpty) 'status': status,
        if (source != null && source.isNotEmpty) 'source': source,
      };
      
      final response = await _apiClient.get(
        ApiConstants.leads,
        queryParameters: queryParams,
      );
      
      if (response.statusCode == 200) {
        final data = response.data;
        final results = data['results'] as List;
        return results.map((json) => Lead.fromJson(json)).toList();
      }
      
      return [];
    } catch (e) {
      rethrow;
    }
  }
  
  Future<Lead?> getLead(int id) async {
    try {
      final response = await _apiClient.get(ApiConstants.leadDetail(id));
      
      if (response.statusCode == 200) {
        return Lead.fromJson(response.data);
      }
      
      return null;
    } catch (e) {
      rethrow;
    }
  }
  
  Future<Lead?> createLead(Lead lead) async {
    try {
      final response = await _apiClient.post(
        ApiConstants.leads,
        data: lead.toJson(),
      );
      
      if (response.statusCode == 201) {
        return Lead.fromJson(response.data);
      }
      
      return null;
    } catch (e) {
      rethrow;
    }
  }
  
  Future<Lead?> updateLead(int id, Lead lead) async {
    try {
      final response = await _apiClient.put(
        ApiConstants.leadDetail(id),
        data: lead.toJson(),
      );
      
      if (response.statusCode == 200) {
        return Lead.fromJson(response.data);
      }
      
      return null;
    } catch (e) {
      rethrow;
    }
  }
  
  Future<bool> deleteLead(int id) async {
    try {
      final response = await _apiClient.delete(ApiConstants.leadDetail(id));
      return response.statusCode == 204;
    } catch (e) {
      rethrow;
    }
  }
  
  Future<Contact?> convertLead(int id) async {
    try {
      final response = await _apiClient.post(
        '${ApiConstants.leadDetail(id)}convert/',
      );
      
      if (response.statusCode == 200) {
        return Contact.fromJson(response.data);
      }
      
      return null;
    } catch (e) {
      rethrow;
    }
  }
}
