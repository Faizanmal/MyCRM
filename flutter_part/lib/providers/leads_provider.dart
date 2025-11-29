import 'package:flutter/material.dart';
import '../models/crm_models.dart';
import '../services/leads_service.dart';

class LeadsProvider with ChangeNotifier {
  final LeadsService _leadsService = LeadsService();
  
  final List<Lead> _leads = [];
  bool _isLoading = false;
  String? _error;
  int _currentPage = 1;
  bool _hasMore = true;
  
  List<Lead> get leads => _leads;
  bool get isLoading => _isLoading;
  String? get error => _error;
  bool get hasMore => _hasMore;
  
  Future<void> fetchLeads({
    bool refresh = false,
    String? search,
    String? status,
    String? source,
  }) async {
    if (refresh) {
      _currentPage = 1;
      _leads.clear();
      _hasMore = true;
    }
    
    if (_isLoading || !_hasMore) return;
    
    _isLoading = true;
    _error = null;
    notifyListeners();
    
    try {
      final newLeads = await _leadsService.getLeads(
        page: _currentPage,
        search: search,
        status: status,
        source: source,
      );
      
      if (newLeads.isEmpty) {
        _hasMore = false;
      } else {
        _leads.addAll(newLeads);
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
  
  Future<bool> createLead(Lead lead) async {
    try {
      final newLead = await _leadsService.createLead(lead);
      if (newLead != null) {
        _leads.insert(0, newLead);
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
  
  Future<bool> updateLead(int id, Lead lead) async {
    try {
      final updatedLead = await _leadsService.updateLead(id, lead);
      if (updatedLead != null) {
        final index = _leads.indexWhere((l) => l.id == id);
        if (index != -1) {
          _leads[index] = updatedLead;
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
  
  Future<bool> deleteLead(int id) async {
    try {
      final success = await _leadsService.deleteLead(id);
      if (success) {
        _leads.removeWhere((l) => l.id == id);
        notifyListeners();
      }
      return success;
    } catch (e) {
      _error = e.toString();
      notifyListeners();
      return false;
    }
  }
  
  Future<Contact?> convertLead(int id) async {
    try {
      final contact = await _leadsService.convertLead(id);
      if (contact != null) {
        _leads.removeWhere((l) => l.id == id);
        notifyListeners();
      }
      return contact;
    } catch (e) {
      _error = e.toString();
      notifyListeners();
      return null;
    }
  }
  
  void clearError() {
    _error = null;
    notifyListeners();
  }
}
