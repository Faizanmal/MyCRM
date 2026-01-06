import 'package:flutter/foundation.dart';
import '../core/utils/api_client.dart';
import '../models/social_models.dart';
import '../services/social_service.dart';

import '../services/offline_sync_service.dart';

class SocialSellingProvider extends ChangeNotifier {
  final SocialSellingService _service;
  final OfflineSyncService _offlineService = OfflineSyncService();

  List<SocialProfile> _profiles = [];
  List<SocialPost> _recentPosts = [];
  List<SocialContentTemplate> _contentLibrary = [];
  SocialMetrics? _metrics;

  bool _isLoading = false;
  String? _error;

  SocialSellingProvider(ApiClient apiClient) : _service = SocialSellingService(apiClient);

  List<SocialProfile> get profiles => _profiles;
  List<SocialPost> get recentPosts => _recentPosts;
  List<SocialContentTemplate> get contentLibrary => _contentLibrary;
  SocialMetrics? get metrics => _metrics;
  bool get isLoading => _isLoading;
  String? get error => _error;

  Future<void> loadDashboard() async {
    _setLoading(true);
    try {
      await Future.wait([
        _loadProfiles(),
        _loadMetrics(),
        _loadRecentPosts(),
      ]);
    } finally {
      _setLoading(false);
    }
  }

  Future<void> _loadProfiles() async {
    try {
      if (_offlineService.isOnline) {
        _profiles = await _service.getProfiles();
        // Cache profiles
        await _offlineService.cacheSocialData('profiles', {
          'items': _profiles.map((p) => {
            'id': p.id,
            'platform': p.platform,
            'username': p.username,
            'profile_url': p.profileUrl,
            'avatar_url': p.avatarUrl,
            'is_connected': p.isConnected,
            'last_sync_at': p.lastSyncAt?.toIso8601String(),
          }).toList(),
        });
      } else {
        // Load from cache
        final cached = _offlineService.getSocialData('profiles');
        if (cached != null) {
          final items = cached['items'] as List;
          _profiles = items.map((json) => SocialProfile.fromJson(json)).toList();
        }
      }
    } catch (e) {
      _error = e.toString();
    }
  }

  Future<void> _loadMetrics() async {
    try {
      _metrics = await _service.getMetrics();
    } catch (e) {
      _error = e.toString();
    }
  }

  Future<void> _loadRecentPosts() async {
    try {
      _recentPosts = await _service.getRecentPosts();
    } catch (e) {
      _error = e.toString();
    }
  }

  Future<void> loadContentLibrary() async {
    _setLoading(true);
    try {
      _contentLibrary = await _service.getContentLibrary();
    } catch (e) {
      _error = e.toString();
    } finally {
      _setLoading(false);
    }
  }

  Future<void> connectLinkedIn() async {
    _setLoading(true);
    try {
      await _service.connectLinkedIn();
      await _loadProfiles();
    } catch (e) {
      _error = e.toString();
    } finally {
      _setLoading(false);
    }
  }

  Future<void> shareContent(String content, String platform) async {
    _setLoading(true);
    try {
      await _service.shareContent(platform: platform, content: content);
      await _loadRecentPosts();
      await _loadMetrics();
    } catch (e) {
      _error = e.toString();
    } finally {
      _setLoading(false);
    }
  }

  void _setLoading(bool value) {
    _isLoading = value;
    if (value) _error = null;
    notifyListeners();
  }
}
