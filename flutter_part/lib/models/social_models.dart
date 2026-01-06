class SocialProfile {
  final String id;
  final String platform; // 'linkedin', 'twitter'
  final String username;
  final String profileUrl;
  final String? avatarUrl;
  final bool isConnected;
  final DateTime? lastSyncAt;

  SocialProfile({
    required this.id,
    required this.platform,
    required this.username,
    required this.profileUrl,
    this.avatarUrl,
    required this.isConnected,
    this.lastSyncAt,
  });

  factory SocialProfile.fromJson(Map<String, dynamic> json) {
    return SocialProfile(
      id: json['id']?.toString() ?? '',
      platform: json['platform'] ?? 'linkedin',
      username: json['username'] ?? '',
      profileUrl: json['profile_url'] ?? '',
      avatarUrl: json['avatar_url'],
      isConnected: json['is_connected'] ?? false,
      lastSyncAt: json['last_sync_at'] != null
          ? DateTime.parse(json['last_sync_at'])
          : null,
    );
  }
}

class SocialPost {
  final String id;
  final String content;
  final String platform;
  final DateTime publishedAt;
  final int likes;
  final int comments;
  final int shares;
  final int impressions;

  SocialPost({
    required this.id,
    required this.content,
    required this.platform,
    required this.publishedAt,
    required this.likes,
    required this.comments,
    required this.shares,
    required this.impressions,
  });

  factory SocialPost.fromJson(Map<String, dynamic> json) {
    return SocialPost(
      id: json['id']?.toString() ?? '',
      content: json['content'] ?? '',
      platform: json['platform'] ?? 'linkedin',
      publishedAt: DateTime.parse(json['published_at'] ?? DateTime.now().toIso8601String()),
      likes: json['likes'] ?? 0,
      comments: json['comments'] ?? 0,
      shares: json['shares'] ?? 0,
      impressions: json['impressions'] ?? 0,
    );
  }
}

class SocialContentTemplate {
  final String id;
  final String title;
  final String body;
  final String category;
  final List<String> tags;
  final bool isUsed;

  SocialContentTemplate({
    required this.id,
    required this.title,
    required this.body,
    required this.category,
    required this.tags,
    required this.isUsed,
  });

  factory SocialContentTemplate.fromJson(Map<String, dynamic> json) {
    return SocialContentTemplate(
      id: json['id']?.toString() ?? '',
      title: json['title'] ?? '',
      body: json['body'] ?? '',
      category: json['category'] ?? 'general',
      tags: List<String>.from(json['tags'] ?? []),
      isUsed: json['is_used'] ?? false,
    );
  }
}

class SocialMetrics {
  final int totalConnections;
  final int totalPosts;
  final int totalEngagements;
  final double socialSellingIndex;

  SocialMetrics({
    required this.totalConnections,
    required this.totalPosts,
    required this.totalEngagements,
    required this.socialSellingIndex,
  });

  factory SocialMetrics.fromJson(Map<String, dynamic> json) {
    return SocialMetrics(
      totalConnections: json['total_connections'] ?? 0,
      totalPosts: json['total_posts'] ?? 0,
      totalEngagements: json['total_engagements'] ?? 0,
      socialSellingIndex: (json['social_selling_index'] ?? 0).toDouble(),
    );
  }
}
