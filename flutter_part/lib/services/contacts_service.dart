import '../core/constants/api_constants.dart';
import '../core/utils/api_client.dart';
import '../models/crm_models.dart';

class ContactsService {
  final ApiClient _apiClient = ApiClient();
  
  // Get all contacts
  Future<List<Contact>> getContacts({
    int page = 1,
    int pageSize = 20,
    String? search,
    String? status,
  }) async {
    try {
      final queryParams = {
        'page': page.toString(),
        'page_size': pageSize.toString(),
        if (search != null && search.isNotEmpty) 'search': search,
        if (status != null && status.isNotEmpty) 'status': status,
      };
      
      final response = await _apiClient.get(
        ApiConstants.contacts,
        queryParameters: queryParams,
      );
      
      if (response.statusCode == 200) {
        final data = response.data;
        final results = data['results'] as List;
        return results.map((json) => Contact.fromJson(json)).toList();
      }
      
      return [];
    } catch (e) {
      rethrow;
    }
  }
  
  // Get single contact
  Future<Contact?> getContact(int id) async {
    try {
      final response = await _apiClient.get(ApiConstants.contactDetail(id));
      
      if (response.statusCode == 200) {
        return Contact.fromJson(response.data);
      }
      
      return null;
    } catch (e) {
      rethrow;
    }
  }
  
  // Create contact
  Future<Contact?> createContact(Contact contact) async {
    try {
      final response = await _apiClient.post(
        ApiConstants.contacts,
        data: contact.toJson(),
      );
      
      if (response.statusCode == 201) {
        return Contact.fromJson(response.data);
      }
      
      return null;
    } catch (e) {
      rethrow;
    }
  }
  
  // Update contact
  Future<Contact?> updateContact(int id, Contact contact) async {
    try {
      final response = await _apiClient.put(
        ApiConstants.contactDetail(id),
        data: contact.toJson(),
      );
      
      if (response.statusCode == 200) {
        return Contact.fromJson(response.data);
      }
      
      return null;
    } catch (e) {
      rethrow;
    }
  }
  
  // Delete contact
  Future<bool> deleteContact(int id) async {
    try {
      final response = await _apiClient.delete(ApiConstants.contactDetail(id));
      return response.statusCode == 204;
    } catch (e) {
      rethrow;
    }
  }
}
