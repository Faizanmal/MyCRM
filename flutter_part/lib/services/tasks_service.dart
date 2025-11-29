import '../core/constants/api_constants.dart';
import '../core/utils/api_client.dart';
import '../models/crm_models.dart';

class TasksService {
  final ApiClient _apiClient = ApiClient();
  
  Future<List<Task>> getTasks({
    int page = 1,
    int pageSize = 20,
    String? search,
    String? status,
    String? priority,
  }) async {
    try {
      final queryParams = {
        'page': page.toString(),
        'page_size': pageSize.toString(),
        if (search != null && search.isNotEmpty) 'search': search,
        if (status != null && status.isNotEmpty) 'status': status,
        if (priority != null && priority.isNotEmpty) 'priority': priority,
      };
      
      final response = await _apiClient.get(
        ApiConstants.tasks,
        queryParameters: queryParams,
      );
      
      if (response.statusCode == 200) {
        final data = response.data;
        final results = data['results'] as List;
        return results.map((json) => Task.fromJson(json)).toList();
      }
      
      return [];
    } catch (e) {
      rethrow;
    }
  }
  
  Future<Task?> getTask(int id) async {
    try {
      final response = await _apiClient.get(ApiConstants.taskDetail(id));
      
      if (response.statusCode == 200) {
        return Task.fromJson(response.data);
      }
      
      return null;
    } catch (e) {
      rethrow;
    }
  }
  
  Future<Task?> createTask(Task task) async {
    try {
      final response = await _apiClient.post(
        ApiConstants.tasks,
        data: task.toJson(),
      );
      
      if (response.statusCode == 201) {
        return Task.fromJson(response.data);
      }
      
      return null;
    } catch (e) {
      rethrow;
    }
  }
  
  Future<Task?> updateTask(int id, Task task) async {
    try {
      final response = await _apiClient.put(
        ApiConstants.taskDetail(id),
        data: task.toJson(),
      );
      
      if (response.statusCode == 200) {
        return Task.fromJson(response.data);
      }
      
      return null;
    } catch (e) {
      rethrow;
    }
  }
  
  Future<bool> deleteTask(int id) async {
    try {
      final response = await _apiClient.delete(ApiConstants.taskDetail(id));
      return response.statusCode == 204;
    } catch (e) {
      rethrow;
    }
  }
  
  Future<Task?> markComplete(int id) async {
    try {
      final response = await _apiClient.patch(
        ApiConstants.taskDetail(id),
        data: {'status': 'Completed'},
      );
      
      if (response.statusCode == 200) {
        return Task.fromJson(response.data);
      }
      
      return null;
    } catch (e) {
      rethrow;
    }
  }
}
