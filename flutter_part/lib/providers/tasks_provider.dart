import 'package:flutter/material.dart';
import '../models/crm_models.dart';
import '../services/tasks_service.dart';

class TasksProvider with ChangeNotifier {
  final TasksService _tasksService = TasksService();
  
  final List<Task> _tasks = [];
  bool _isLoading = false;
  String? _error;
  int _currentPage = 1;
  bool _hasMore = true;
  
  List<Task> get tasks => _tasks;
  bool get isLoading => _isLoading;
  String? get error => _error;
  bool get hasMore => _hasMore;
  
  Future<void> fetchTasks({
    bool refresh = false,
    String? search,
    String? status,
    String? priority,
  }) async {
    if (refresh) {
      _currentPage = 1;
      _tasks.clear();
      _hasMore = true;
    }
    
    if (_isLoading || !_hasMore) return;
    
    _isLoading = true;
    _error = null;
    notifyListeners();
    
    try {
      final newTasks = await _tasksService.getTasks(
        page: _currentPage,
        search: search,
        status: status,
        priority: priority,
      );
      
      if (newTasks.isEmpty) {
        _hasMore = false;
      } else {
        _tasks.addAll(newTasks);
        _currentPage++;
      }
      
      _error = null;
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
  
  Future<bool> createTask(Task task) async {
    try {
      final newTask = await _tasksService.createTask(task);
      if (newTask != null) {
        _tasks.insert(0, newTask);
        notifyListeners();
        return true;
      }
      return false;
    } catch (e) {
      _error = e.toString();
      notifyListeners();
      return false;
    }
  }
  
  Future<bool> updateTask(int id, Task task) async {
    try {
      final updatedTask = await _tasksService.updateTask(id, task);
      if (updatedTask != null) {
        final index = _tasks.indexWhere((t) => t.id == id);
        if (index != -1) {
          _tasks[index] = updatedTask;
          notifyListeners();
        }
        return true;
      }
      return false;
    } catch (e) {
      _error = e.toString();
      notifyListeners();
      return false;
    }
  }
  
  Future<bool> deleteTask(int id) async {
    try {
      final success = await _tasksService.deleteTask(id);
      if (success) {
        _tasks.removeWhere((t) => t.id == id);
        notifyListeners();
      }
      return success;
    } catch (e) {
      _error = e.toString();
      notifyListeners();
      return false;
    }
  }
  
  Future<bool> markComplete(int id) async {
    try {
      final completedTask = await _tasksService.markComplete(id);
      if (completedTask != null) {
        final index = _tasks.indexWhere((t) => t.id == id);
        if (index != -1) {
          _tasks[index] = completedTask;
          notifyListeners();
        }
        return true;
      }
      return false;
    } catch (e) {
      _error = e.toString();
      notifyListeners();
      return false;
    }
  }
  
  void clearError() {
    _error = null;
    notifyListeners();
  }
}
