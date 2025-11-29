import 'package:flutter/material.dart';
import '../models/crm_models.dart';
import '../services/opportunities_service.dart';

class OpportunitiesProvider with ChangeNotifier {
  final OpportunitiesService _opportunitiesService = OpportunitiesService();
  
  final List<Opportunity> _opportunities = [];
  bool _isLoading = false;
  String? _error;
  int _currentPage = 1;
  bool _hasMore = true;
  
  List<Opportunity> get opportunities => _opportunities;
  bool get isLoading => _isLoading;
  String? get error => _error;
  bool get hasMore => _hasMore;
  
  Future<void> fetchOpportunities({
    bool refresh = false,
    String? search,
    String? stage,
  }) async {
    if (refresh) {
      _currentPage = 1;
      _opportunities.clear();
      _hasMore = true;
    }
    
    if (_isLoading || !_hasMore) return;
    
    _isLoading = true;
    _error = null;
    notifyListeners();
    
    try {
      final newOpportunities = await _opportunitiesService.getOpportunities(
        page: _currentPage,
        search: search,
        stage: stage,
      );
      
      if (newOpportunities.isEmpty) {
        _hasMore = false;
      } else {
        _opportunities.addAll(newOpportunities);
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
  
  Future<bool> createOpportunity(Opportunity opportunity) async {
    try {
      final newOpportunity = await _opportunitiesService.createOpportunity(opportunity);
      if (newOpportunity != null) {
        _opportunities.insert(0, newOpportunity);
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
  
  Future<bool> updateOpportunity(int id, Opportunity opportunity) async {
    try {
      final updatedOpportunity = await _opportunitiesService.updateOpportunity(id, opportunity);
      if (updatedOpportunity != null) {
        final index = _opportunities.indexWhere((o) => o.id == id);
        if (index != -1) {
          _opportunities[index] = updatedOpportunity;
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
  
  Future<bool> deleteOpportunity(int id) async {
    try {
      final success = await _opportunitiesService.deleteOpportunity(id);
      if (success) {
        _opportunities.removeWhere((o) => o.id == id);
        notifyListeners();
      }
      return success;
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
