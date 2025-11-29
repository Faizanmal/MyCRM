import 'package:flutter/material.dart';
import '../models/crm_models.dart';
import '../services/contacts_service.dart';

class ContactsProvider with ChangeNotifier {
  final ContactsService _contactsService = ContactsService();
  
  final List<Contact> _contacts = [];
  bool _isLoading = false;
  String? _error;
  int _currentPage = 1;
  bool _hasMore = true;
  
  List<Contact> get contacts => _contacts;
  bool get isLoading => _isLoading;
  String? get error => _error;
  bool get hasMore => _hasMore;
  
  Future<void> fetchContacts({
    bool refresh = false,
    String? search,
    String? status,
  }) async {
    if (refresh) {
      _currentPage = 1;
      _contacts.clear();
      _hasMore = true;
    }
    
    if (_isLoading || !_hasMore) return;
    
    _isLoading = true;
    _error = null;
    notifyListeners();
    
    try {
      final newContacts = await _contactsService.getContacts(
        page: _currentPage,
        search: search,
        status: status,
      );
      
      if (newContacts.isEmpty) {
        _hasMore = false;
      } else {
        _contacts.addAll(newContacts);
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
  
  Future<bool> createContact(Contact contact) async {
    try {
      final newContact = await _contactsService.createContact(contact);
      if (newContact != null) {
        _contacts.insert(0, newContact);
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
  
  Future<bool> updateContact(int id, Contact contact) async {
    try {
      final updatedContact = await _contactsService.updateContact(id, contact);
      if (updatedContact != null) {
        final index = _contacts.indexWhere((c) => c.id == id);
        if (index != -1) {
          _contacts[index] = updatedContact;
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
  
  Future<bool> deleteContact(int id) async {
    try {
      final success = await _contactsService.deleteContact(id);
      if (success) {
        _contacts.removeWhere((c) => c.id == id);
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
