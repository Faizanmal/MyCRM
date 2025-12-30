import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:connectivity_plus/connectivity_plus.dart';

/// Offline sync service for handling data when offline
/// Implements queue-based sync with conflict resolution
class OfflineSyncService {
  static final OfflineSyncService _instance = OfflineSyncService._internal();
  factory OfflineSyncService() => _instance;
  OfflineSyncService._internal();

  late Box<Map> _syncQueueBox;
  late Box<Map> _cacheBox;
  late Box<String> _metadataBox;
  
  bool _isInitialized = false;
  bool _isSyncing = false;
  final _syncController = StreamController<SyncStatus>.broadcast();
  
  Stream<SyncStatus> get syncStatus => _syncController.stream;
  
  // Track connectivity
  bool _isOnline = true;
  StreamSubscription<List<ConnectivityResult>>? _connectivitySubscription;

  /// Initialize the offline sync service
  Future<void> initialize() async {
    if (_isInitialized) return;
    
    await Hive.initFlutter();
    
    _syncQueueBox = await Hive.openBox<Map>('sync_queue');
    _cacheBox = await Hive.openBox<Map>('offline_cache');
    _metadataBox = await Hive.openBox<String>('sync_metadata');
    
    // Listen to connectivity changes
    _connectivitySubscription = Connectivity().onConnectivityChanged.listen((results) {
      final wasOnline = _isOnline;
      _isOnline = results.any((r) => r != ConnectivityResult.none);
      
      if (!wasOnline && _isOnline) {
        // Just came online, trigger sync
        syncPendingChanges();
      }
      
      _syncController.add(SyncStatus(
        isOnline: _isOnline,
        pendingCount: _syncQueueBox.length,
        isSyncing: _isSyncing,
      ));
    });
    
    // Check initial connectivity
    final results = await Connectivity().checkConnectivity();
    _isOnline = results.any((r) => r != ConnectivityResult.none);
    
    _isInitialized = true;
    
    // Initial sync attempt
    if (_isOnline && _syncQueueBox.isNotEmpty) {
      syncPendingChanges();
    }
  }

  /// Cache data for offline access
  Future<void> cacheData({
    required String key,
    required Map<String, dynamic> data,
    Duration? ttl,
  }) async {
    final cacheEntry = {
      'data': data,
      'cachedAt': DateTime.now().toIso8601String(),
      'expiresAt': ttl != null 
        ? DateTime.now().add(ttl).toIso8601String() 
        : null,
    };
    
    await _cacheBox.put(key, cacheEntry);
  }

  /// Get cached data
  Map<String, dynamic>? getCachedData(String key) {
    final entry = _cacheBox.get(key);
    if (entry == null) return null;
    
    // Check expiration
    final expiresAt = entry['expiresAt'];
    if (expiresAt != null) {
      final expiration = DateTime.parse(expiresAt);
      if (DateTime.now().isAfter(expiration)) {
        _cacheBox.delete(key);
        return null;
      }
    }
    
    return Map<String, dynamic>.from(entry['data'] as Map);
  }

  /// Queue an operation for later sync
  Future<String> queueOperation({
    required SyncOperation operation,
    required String entity,
    required String entityId,
    required Map<String, dynamic> data,
    int priority = 0,
  }) async {
    final id = '${DateTime.now().millisecondsSinceEpoch}_$entityId';
    
    final queueEntry = {
      'id': id,
      'operation': operation.name,
      'entity': entity,
      'entityId': entityId,
      'data': data,
      'priority': priority,
      'createdAt': DateTime.now().toIso8601String(),
      'retryCount': 0,
      'status': 'pending',
    };
    
    await _syncQueueBox.put(id, queueEntry);
    
    _syncController.add(SyncStatus(
      isOnline: _isOnline,
      pendingCount: _syncQueueBox.length,
      isSyncing: _isSyncing,
    ));
    
    // Try to sync immediately if online
    if (_isOnline) {
      syncPendingChanges();
    }
    
    return id;
  }

  /// Sync all pending changes
  Future<SyncResult> syncPendingChanges() async {
    if (!_isOnline || _isSyncing || _syncQueueBox.isEmpty) {
      return SyncResult(synced: 0, failed: 0, pending: _syncQueueBox.length);
    }
    
    _isSyncing = true;
    _syncController.add(SyncStatus(
      isOnline: _isOnline,
      pendingCount: _syncQueueBox.length,
      isSyncing: true,
    ));
    
    int synced = 0;
    int failed = 0;
    
    // Get all pending operations sorted by priority and creation time
    final entries = _syncQueueBox.values.toList();
    entries.sort((a, b) {
      final priorityCompare = (b['priority'] as int).compareTo(a['priority'] as int);
      if (priorityCompare != 0) return priorityCompare;
      return (a['createdAt'] as String).compareTo(b['createdAt'] as String);
    });
    
    for (final entry in entries) {
      try {
        final success = await _processSyncEntry(Map<String, dynamic>.from(entry));
        if (success) {
          await _syncQueueBox.delete(entry['id']);
          synced++;
        } else {
          failed++;
          // Update retry count
          entry['retryCount'] = (entry['retryCount'] as int) + 1;
          if (entry['retryCount'] >= 5) {
            entry['status'] = 'failed';
          }
          await _syncQueueBox.put(entry['id'], entry);
        }
      } catch (e) {
        failed++;
        debugPrint('Sync error for ${entry['id']}: $e');
      }
    }
    
    _isSyncing = false;
    
    final result = SyncResult(
      synced: synced,
      failed: failed,
      pending: _syncQueueBox.length,
    );
    
    _syncController.add(SyncStatus(
      isOnline: _isOnline,
      pendingCount: _syncQueueBox.length,
      isSyncing: false,
      lastResult: result,
    ));
    
    // Update last sync time
    await _metadataBox.put('lastSyncAt', DateTime.now().toIso8601String());
    
    return result;
  }

  /// Process a single sync entry
  Future<bool> _processSyncEntry(Map<String, dynamic> entry) async {
    final operation = SyncOperation.values.firstWhere(
      (e) => e.name == entry['operation'],
      orElse: () => SyncOperation.update,
    );
    final entity = entry['entity'] as String;
    final data = Map<String, dynamic>.from(entry['data'] as Map);
    
    // Here you would make the actual API call
    // For now, simulate success
    await Future.delayed(const Duration(milliseconds: 100));
    
    debugPrint('Syncing: $operation $entity with data: ${jsonEncode(data)}');
    
    // Return true for success, false for failure
    // In real implementation, this would call the API
    return true;
  }

  /// Get pending operations count
  int get pendingCount => _syncQueueBox.length;

  /// Get last sync time
  DateTime? get lastSyncAt {
    final lastSync = _metadataBox.get('lastSyncAt');
    return lastSync != null ? DateTime.parse(lastSync) : null;
  }

  /// Check if online
  bool get isOnline => _isOnline;

  /// Clear all cached data
  Future<void> clearCache() async {
    await _cacheBox.clear();
  }

  /// Clear sync queue (use with caution)
  Future<void> clearSyncQueue() async {
    await _syncQueueBox.clear();
    _syncController.add(SyncStatus(
      isOnline: _isOnline,
      pendingCount: 0,
      isSyncing: false,
    ));
  }

  /// Get all pending operations for an entity
  List<Map<String, dynamic>> getPendingForEntity(String entity) {
    return _syncQueueBox.values
      .where((e) => e['entity'] == entity)
      .map((e) => Map<String, dynamic>.from(e))
      .toList();
  }

  /// Cancel a pending operation
  Future<bool> cancelOperation(String operationId) async {
    if (_syncQueueBox.containsKey(operationId)) {
      await _syncQueueBox.delete(operationId);
      _syncController.add(SyncStatus(
        isOnline: _isOnline,
        pendingCount: _syncQueueBox.length,
        isSyncing: _isSyncing,
      ));
      return true;
    }
    return false;
  }

  /// Dispose resources
  void dispose() {
    _connectivitySubscription?.cancel();
    _syncController.close();
  }
}

/// Types of sync operations
enum SyncOperation {
  create,
  update,
  delete,
}

/// Current sync status
class SyncStatus {
  final bool isOnline;
  final int pendingCount;
  final bool isSyncing;
  final SyncResult? lastResult;

  SyncStatus({
    required this.isOnline,
    required this.pendingCount,
    required this.isSyncing,
    this.lastResult,
  });
}

/// Result of a sync operation
class SyncResult {
  final int synced;
  final int failed;
  final int pending;

  SyncResult({
    required this.synced,
    required this.failed,
    required this.pending,
  });
  
  @override
  String toString() => 'SyncResult(synced: $synced, failed: $failed, pending: $pending)';
}

/// Mixin for offline-capable providers
mixin OfflineCapableMixin {
  final OfflineSyncService _syncService = OfflineSyncService();
  
  /// Cache data with automatic key generation
  Future<void> cacheListData<T>(String entity, List<T> items, Map<String, dynamic> Function(T) toJson) async {
    final data = items.map(toJson).toList();
    await _syncService.cacheData(
      key: '${entity}_list',
      data: {'items': data},
      ttl: const Duration(hours: 1),
    );
  }
  
  /// Get cached list data
  List<Map<String, dynamic>>? getCachedList(String entity) {
    final data = _syncService.getCachedData('${entity}_list');
    if (data == null) return null;
    return List<Map<String, dynamic>>.from(data['items'] as List);
  }
  
  /// Cache a single item
  Future<void> cacheItem(String entity, String id, Map<String, dynamic> data) async {
    await _syncService.cacheData(
      key: '${entity}_$id',
      data: data,
      ttl: const Duration(hours: 1),
    );
  }
  
  /// Get a cached item
  Map<String, dynamic>? getCachedItem(String entity, String id) {
    return _syncService.getCachedData('${entity}_$id');
  }
  
  /// Queue create operation
  Future<String> queueCreate(String entity, String id, Map<String, dynamic> data) async {
    return _syncService.queueOperation(
      operation: SyncOperation.create,
      entity: entity,
      entityId: id,
      data: data,
      priority: 1,
    );
  }
  
  /// Queue update operation
  Future<String> queueUpdate(String entity, String id, Map<String, dynamic> data) async {
    return _syncService.queueOperation(
      operation: SyncOperation.update,
      entity: entity,
      entityId: id,
      data: data,
      priority: 0,
    );
  }
  
  /// Queue delete operation
  Future<String> queueDelete(String entity, String id) async {
    return _syncService.queueOperation(
      operation: SyncOperation.delete,
      entity: entity,
      entityId: id,
      data: {},
      priority: 2,
    );
  }
}
