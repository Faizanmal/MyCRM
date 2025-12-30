import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';

/// Push notification service for handling local and remote notifications
class PushNotificationService {
  static final PushNotificationService _instance = PushNotificationService._internal();
  factory PushNotificationService() => _instance;
  PushNotificationService._internal();

  final FlutterLocalNotificationsPlugin _localNotifications = FlutterLocalNotificationsPlugin();
  final StreamController<NotificationPayload> _notificationController = StreamController<NotificationPayload>.broadcast();
  
  Stream<NotificationPayload> get onNotification => _notificationController.stream;
  
  bool _isInitialized = false;

  /// Initialize the notification service
  Future<void> initialize() async {
    if (_isInitialized) return;

    // Android initialization
    const androidSettings = AndroidInitializationSettings('@mipmap/ic_launcher');
    
    // iOS initialization
    final iosSettings = DarwinInitializationSettings(
      requestAlertPermission: true,
      requestBadgePermission: true,
      requestSoundPermission: true,
      onDidReceiveLocalNotification: _onDidReceiveLocalNotification,
    );

    final initSettings = InitializationSettings(
      android: androidSettings,
      iOS: iosSettings,
    );

    await _localNotifications.initialize(
      initSettings,
      onDidReceiveNotificationResponse: _onNotificationTapped,
    );

    // Create notification channels for Android
    await _createNotificationChannels();

    _isInitialized = true;
    debugPrint('Push notification service initialized');
  }

  /// Create notification channels for Android
  Future<void> _createNotificationChannels() async {
    const channels = [
      AndroidNotificationChannel(
        'leads',
        'Lead Notifications',
        description: 'Notifications about new and updated leads',
        importance: Importance.high,
      ),
      AndroidNotificationChannel(
        'deals',
        'Deal Notifications',
        description: 'Notifications about deal updates and closings',
        importance: Importance.high,
      ),
      AndroidNotificationChannel(
        'tasks',
        'Task Notifications',
        description: 'Task reminders and due date alerts',
        importance: Importance.high,
      ),
      AndroidNotificationChannel(
        'messages',
        'Message Notifications',
        description: 'New messages and communications',
        importance: Importance.high,
      ),
      AndroidNotificationChannel(
        'system',
        'System Notifications',
        description: 'System updates and sync status',
        importance: Importance.low,
      ),
    ];

    for (final channel in channels) {
      await _localNotifications
          .resolvePlatformSpecificImplementation<AndroidFlutterLocalNotificationsPlugin>()
          ?.createNotificationChannel(channel);
    }
  }

  /// Request notification permissions
  Future<bool> requestPermissions() async {
    // iOS permissions
    final iosResult = await _localNotifications
        .resolvePlatformSpecificImplementation<IOSFlutterLocalNotificationsPlugin>()
        ?.requestPermissions(alert: true, badge: true, sound: true);

    // Android permissions (Android 13+)
    final androidResult = await _localNotifications
        .resolvePlatformSpecificImplementation<AndroidFlutterLocalNotificationsPlugin>()
        ?.requestNotificationsPermission();

    return (iosResult ?? true) && (androidResult ?? true);
  }

  /// Show a local notification
  Future<void> showNotification({
    required int id,
    required String title,
    required String body,
    String? channel,
    Map<String, dynamic>? payload,
    NotificationPriority priority = NotificationPriority.defaultPriority,
  }) async {
    final androidDetails = AndroidNotificationDetails(
      channel ?? 'system',
      channel ?? 'System Notifications',
      importance: _mapPriority(priority),
      priority: Priority.high,
      showWhen: true,
      icon: '@mipmap/ic_launcher',
    );

    const iosDetails = DarwinNotificationDetails(
      presentAlert: true,
      presentBadge: true,
      presentSound: true,
    );

    final details = NotificationDetails(
      android: androidDetails,
      iOS: iosDetails,
    );

    await _localNotifications.show(
      id,
      title,
      body,
      details,
      payload: payload != null ? jsonEncode(payload) : null,
    );
  }

  /// Schedule a notification for later
  Future<void> scheduleNotification({
    required int id,
    required String title,
    required String body,
    required DateTime scheduledTime,
    String? channel,
    Map<String, dynamic>? payload,
  }) async {
    final androidDetails = AndroidNotificationDetails(
      channel ?? 'tasks',
      channel ?? 'Task Notifications',
      importance: Importance.high,
      priority: Priority.high,
    );

    const iosDetails = DarwinNotificationDetails(
      presentAlert: true,
      presentBadge: true,
      presentSound: true,
    );

    final details = NotificationDetails(
      android: androidDetails,
      iOS: iosDetails,
    );

    // Use zonedSchedule for timezone-aware scheduling
    // For simplicity, using show with a delay here
    final delay = scheduledTime.difference(DateTime.now());
    if (delay.isNegative) return;

    Future.delayed(delay, () {
      showNotification(
        id: id,
        title: title,
        body: body,
        channel: channel,
        payload: payload,
      );
    });
  }

  /// Cancel a specific notification
  Future<void> cancelNotification(int id) async {
    await _localNotifications.cancel(id);
  }

  /// Cancel all notifications
  Future<void> cancelAllNotifications() async {
    await _localNotifications.cancelAll();
  }

  /// Get pending notifications
  Future<List<PendingNotificationRequest>> getPendingNotifications() async {
    return await _localNotifications.pendingNotificationRequests();
  }

  /// Show a lead notification
  Future<void> showLeadNotification({
    required String leadName,
    required String action,
    String? assignee,
    int? leadId,
  }) async {
    await showNotification(
      id: DateTime.now().millisecondsSinceEpoch % 100000,
      title: 'Lead $action',
      body: assignee != null 
        ? '$leadName has been assigned to $assignee'
        : '$leadName - $action',
      channel: 'leads',
      payload: {'type': 'lead', 'id': leadId},
      priority: NotificationPriority.high,
    );
  }

  /// Show a deal notification
  Future<void> showDealNotification({
    required String dealName,
    required String status,
    double? amount,
    int? dealId,
  }) async {
    final amountStr = amount != null ? ' - \$${amount.toStringAsFixed(0)}' : '';
    await showNotification(
      id: DateTime.now().millisecondsSinceEpoch % 100000,
      title: 'Deal $status',
      body: '$dealName$amountStr',
      channel: 'deals',
      payload: {'type': 'deal', 'id': dealId},
      priority: NotificationPriority.high,
    );
  }

  /// Show a task reminder
  Future<void> showTaskReminder({
    required String taskTitle,
    required String dueTime,
    int? taskId,
  }) async {
    await showNotification(
      id: DateTime.now().millisecondsSinceEpoch % 100000,
      title: 'Task Reminder',
      body: '$taskTitle - Due $dueTime',
      channel: 'tasks',
      payload: {'type': 'task', 'id': taskId},
      priority: NotificationPriority.high,
    );
  }

  /// Show a sync status notification
  Future<void> showSyncNotification({
    required int synced,
    required int pending,
  }) async {
    await showNotification(
      id: 99999, // Fixed ID for sync notifications
      title: 'Sync Complete',
      body: '$synced items synced, $pending pending',
      channel: 'system',
      priority: NotificationPriority.low,
    );
  }

  Importance _mapPriority(NotificationPriority priority) {
    switch (priority) {
      case NotificationPriority.low:
        return Importance.low;
      case NotificationPriority.defaultPriority:
        return Importance.defaultImportance;
      case NotificationPriority.high:
        return Importance.high;
      case NotificationPriority.urgent:
        return Importance.max;
    }
  }

  void _onNotificationTapped(NotificationResponse response) {
    if (response.payload != null) {
      try {
        final payload = jsonDecode(response.payload!) as Map<String, dynamic>;
        _notificationController.add(NotificationPayload(
          type: payload['type'] as String?,
          id: payload['id'] as int?,
          data: payload,
        ));
      } catch (e) {
        debugPrint('Error parsing notification payload: $e');
      }
    }
  }

  void _onDidReceiveLocalNotification(int id, String? title, String? body, String? payload) {
    // Handle iOS foreground notifications (older iOS versions)
    debugPrint('iOS notification received: $title');
  }

  /// Dispose resources
  void dispose() {
    _notificationController.close();
  }
}

/// Notification priority levels
enum NotificationPriority {
  low,
  defaultPriority,
  high,
  urgent,
}

/// Notification payload for handling taps
class NotificationPayload {
  final String? type;
  final int? id;
  final Map<String, dynamic>? data;

  NotificationPayload({this.type, this.id, this.data});
}
