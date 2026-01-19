import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/utils/api_client.dart';
import '../../providers/enterprise_providers.dart';
import '../../models/enterprise_models.dart';
import '../../widgets/loading_indicator.dart';
import '../../widgets/empty_state.dart';

class SocialInboxScreen extends StatefulWidget {
  const SocialInboxScreen({super.key});

  @override
  State<SocialInboxScreen> createState() => _SocialInboxScreenState();
}

class _SocialInboxScreenState extends State<SocialInboxScreen>
    with SingleTickerProviderStateMixin {
  late SocialInboxProvider _provider;
  late TabController _tabController;
  String _selectedPlatform = 'all';

  final List<Map<String, dynamic>> _platforms = [
    {'id': 'all', 'name': 'All', 'icon': Icons.apps, 'color': Colors.grey},
    {'id': 'twitter', 'name': 'Twitter', 'icon': Icons.flutter_dash, 'color': Colors.blue},
    {'id': 'linkedin', 'name': 'LinkedIn', 'icon': Icons.work, 'color': Color(0xFF0077B5)},
    {'id': 'facebook', 'name': 'Facebook', 'icon': Icons.facebook, 'color': Color(0xFF1877F2)},
    {'id': 'instagram', 'name': 'Instagram', 'icon': Icons.camera_alt, 'color': Color(0xFFE4405F)},
  ];

  @override
  void initState() {
    super.initState();
    _provider = SocialInboxProvider(ApiClient());
    _tabController = TabController(length: 3, vsync: this);
    _loadData();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _loadData() async {
    await _provider.loadAll();
  }

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider.value(
      value: _provider,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Social Inbox'),
          flexibleSpace: Container(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [Colors.pink.shade600, Colors.orange.shade400],
              ),
            ),
          ),
          bottom: TabBar(
            controller: _tabController,
            indicatorColor: Colors.white,
            tabs: const [
              Tab(text: 'Inbox', icon: Icon(Icons.inbox)),
              Tab(text: 'Mentions', icon: Icon(Icons.alternate_email)),
              Tab(text: 'Analytics', icon: Icon(Icons.analytics)),
            ],
          ),
        ),
        body: Consumer<SocialInboxProvider>(
          builder: (context, provider, _) {
            return TabBarView(
              controller: _tabController,
              children: [
                _buildInboxTab(provider),
                _buildMentionsTab(provider),
                _buildAnalyticsTab(provider),
              ],
            );
          },
        ),
        floatingActionButton: FloatingActionButton.extended(
          onPressed: _showComposeDialog,
          backgroundColor: Colors.pink,
          icon: const Icon(Icons.create),
          label: const Text('Compose'),
        ),
      ),
    );
  }

  Widget _buildInboxTab(SocialInboxProvider provider) {
    return Column(
      children: [
        _buildPlatformFilter(),
        Expanded(
          child: provider.isLoading
              ? const LoadingIndicator(message: 'Loading messages...')
              : provider.messages.isEmpty
                  ? const EmptyState(
                      icon: Icons.inbox_outlined,
                      title: 'Inbox Empty',
                      subtitle: 'No social messages yet',
                    )
                  : RefreshIndicator(
                      onRefresh: () => provider.loadMessages(
                        platform: _selectedPlatform == 'all' ? null : _selectedPlatform,
                      ),
                      child: ListView.builder(
                        padding: const EdgeInsets.only(bottom: 80),
                        itemCount: provider.messages.length,
                        itemBuilder: (context, index) {
                          return _buildMessageCard(provider.messages[index], provider);
                        },
                      ),
                    ),
        ),
      ],
    );
  }

  Widget _buildPlatformFilter() {
    return Container(
      height: 60,
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 12),
        itemCount: _platforms.length,
        itemBuilder: (context, index) {
          final platform = _platforms[index];
          final isSelected = _selectedPlatform == platform['id'];
          
          return Padding(
            padding: const EdgeInsets.symmetric(horizontal: 4),
            child: FilterChip(
              label: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    platform['icon'] as IconData,
                    size: 18,
                    color: isSelected ? Colors.white : platform['color'] as Color,
                  ),
                  const SizedBox(width: 6),
                  Text(platform['name'] as String),
                ],
              ),
              selected: isSelected,
              onSelected: (selected) {
                setState(() {
                  _selectedPlatform = platform['id'] as String;
                });
                _provider.loadMessages(
                  platform: _selectedPlatform == 'all' ? null : _selectedPlatform,
                );
              },
              selectedColor: platform['color'] as Color,
              labelStyle: TextStyle(
                color: isSelected ? Colors.white : null,
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildMessageCard(SocialMessage message, SocialInboxProvider provider) {
    final platformInfo = _platforms.firstWhere(
      (p) => p['id'] == message.platform,
      orElse: () => _platforms[0],
    );

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
      child: InkWell(
        onTap: () => _showMessageDetail(message, provider),
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  CircleAvatar(
                    backgroundImage: message.authorAvatar != null 
                        ? NetworkImage(message.authorAvatar!)
                        : null,
                    child: message.authorAvatar == null 
                        ? Text(message.authorName.substring(0, 1).toUpperCase())
                        : null,
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Text(
                              message.authorName,
                              style: const TextStyle(fontWeight: FontWeight.bold),
                            ),
                            if (message.authorVerified) ...[
                              const SizedBox(width: 4),
                              Icon(Icons.verified, size: 16, color: Colors.blue),
                            ],
                          ],
                        ),
                        Text(
                          '@${message.authorHandle}',
                          style: TextStyle(color: Colors.grey.shade600, fontSize: 13),
                        ),
                      ],
                    ),
                  ),
                  Icon(
                    platformInfo['icon'] as IconData,
                    color: platformInfo['color'] as Color,
                    size: 20,
                  ),
                  const SizedBox(width: 8),
                  if (!message.isRead)
                    Container(
                      width: 10,
                      height: 10,
                      decoration: const BoxDecoration(
                        color: Colors.blue,
                        shape: BoxShape.circle,
                      ),
                    ),
                ],
              ),
              const SizedBox(height: 12),
              Text(
                message.content,
                maxLines: 3,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  _buildEngagementStat(Icons.favorite_border, message.likesCount),
                  const SizedBox(width: 16),
                  _buildEngagementStat(Icons.repeat, message.sharesCount),
                  const SizedBox(width: 16),
                  _buildEngagementStat(Icons.comment_outlined, message.commentsCount),
                  const Spacer(),
                  Text(
                    _formatTimeAgo(message.createdAt),
                    style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildEngagementStat(IconData icon, int count) {
    return Row(
      children: [
        Icon(icon, size: 16, color: Colors.grey.shade600),
        const SizedBox(width: 4),
        Text(
          count.toString(),
          style: TextStyle(color: Colors.grey.shade600, fontSize: 13),
        ),
      ],
    );
  }

  Widget _buildMentionsTab(SocialInboxProvider provider) {
    final mentions = provider.messages.where((m) => m.isMention).toList();

    if (provider.isLoading) {
      return const LoadingIndicator(message: 'Loading mentions...');
    }

    if (mentions.isEmpty) {
      return const EmptyState(
        icon: Icons.alternate_email,
        title: 'No Mentions',
        subtitle: 'Brand mentions will appear here',
      );
    }

    return RefreshIndicator(
      onRefresh: () => provider.loadMentions(),
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: mentions.length,
        itemBuilder: (context, index) {
          return _buildMentionCard(mentions[index], provider);
        },
      ),
    );
  }

  Widget _buildMentionCard(SocialMessage mention, SocialInboxProvider provider) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                CircleAvatar(
                  child: Text(mention.authorName.substring(0, 1).toUpperCase()),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        mention.authorName,
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
                      Text(
                        '@${mention.authorHandle} • ${_formatTimeAgo(mention.createdAt)}',
                        style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
                      ),
                    ],
                  ),
                ),
                _buildSentimentBadge(mention.sentiment),
              ],
            ),
            const SizedBox(height: 12),
            Text(mention.content),
            const SizedBox(height: 12),
            Row(
              children: [
                OutlinedButton.icon(
                  onPressed: () {},
                  icon: const Icon(Icons.reply, size: 18),
                  label: const Text('Reply'),
                ),
                const SizedBox(width: 8),
                OutlinedButton.icon(
                  onPressed: () {},
                  icon: const Icon(Icons.favorite_border, size: 18),
                  label: const Text('Like'),
                ),
                const SizedBox(width: 8),
                OutlinedButton.icon(
                  onPressed: () {},
                  icon: const Icon(Icons.person_add, size: 18),
                  label: const Text('Add Lead'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSentimentBadge(String? sentiment) {
    Color color;
    IconData icon;
    
    switch (sentiment?.toLowerCase()) {
      case 'positive':
        color = Colors.green;
        icon = Icons.sentiment_satisfied;
        break;
      case 'negative':
        color = Colors.red;
        icon = Icons.sentiment_dissatisfied;
        break;
      default:
        color = Colors.grey;
        icon = Icons.sentiment_neutral;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 16, color: color),
          const SizedBox(width: 4),
          Text(
            sentiment ?? 'Neutral',
            style: TextStyle(color: color, fontSize: 12),
          ),
        ],
      ),
    );
  }

  Widget _buildAnalyticsTab(SocialInboxProvider provider) {
    return RefreshIndicator(
      onRefresh: _loadData,
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildEngagementOverview(),
            const SizedBox(height: 24),
            _buildPlatformBreakdown(provider),
            const SizedBox(height: 24),
            _buildSentimentAnalysis(provider),
            const SizedBox(height: 24),
            _buildResponseMetrics(),
          ],
        ),
      ),
    );
  }

  Widget _buildEngagementOverview() {
    return Card(
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: [Colors.pink.shade600, Colors.orange.shade400],
          ),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'This Week\'s Engagement',
              style: TextStyle(color: Colors.white70, fontSize: 14),
            ),
            const SizedBox(height: 8),
            const Text(
              '12,456',
              style: TextStyle(
                color: Colors.white,
                fontSize: 40,
                fontWeight: FontWeight.bold,
              ),
            ),
            const Text(
              '+18% from last week',
              style: TextStyle(color: Colors.white70),
            ),
            const SizedBox(height: 20),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildEngagementMetric('Messages', '845', Colors.white),
                _buildEngagementMetric('Mentions', '234', Colors.white),
                _buildEngagementMetric('Responses', '456', Colors.white),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEngagementMetric(String label, String value, Color color) {
    return Column(
      children: [
        Text(
          value,
          style: TextStyle(
            color: color,
            fontSize: 24,
            fontWeight: FontWeight.bold,
          ),
        ),
        Text(
          label,
          style: TextStyle(color: color.withOpacity(0.8), fontSize: 12),
        ),
      ],
    );
  }

  Widget _buildPlatformBreakdown(SocialInboxProvider provider) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Platform Breakdown',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            ..._platforms.skip(1).map((platform) {
              final count = provider.messages
                  .where((m) => m.platform == platform['id'])
                  .length;
              final percentage = provider.messages.isEmpty 
                  ? 0.0 
                  : count / provider.messages.length;
              
              return Padding(
                padding: const EdgeInsets.symmetric(vertical: 8),
                child: Column(
                  children: [
                    Row(
                      children: [
                        Icon(
                          platform['icon'] as IconData,
                          color: platform['color'] as Color,
                          size: 20,
                        ),
                        const SizedBox(width: 8),
                        Text(platform['name'] as String),
                        const Spacer(),
                        Text(
                          '$count messages',
                          style: TextStyle(color: Colors.grey.shade600),
                        ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    LinearProgressIndicator(
                      value: percentage,
                      backgroundColor: (platform['color'] as Color).withOpacity(0.2),
                      valueColor: AlwaysStoppedAnimation(platform['color'] as Color),
                    ),
                  ],
                ),
              );
            }),
          ],
        ),
      ),
    );
  }

  Widget _buildSentimentAnalysis(SocialInboxProvider provider) {
    final positive = provider.messages.where((m) => m.sentiment == 'positive').length;
    final negative = provider.messages.where((m) => m.sentiment == 'negative').length;
    final neutral = provider.messages.length - positive - negative;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Sentiment Analysis',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 20),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildSentimentStat('Positive', positive, Colors.green, Icons.sentiment_satisfied),
                _buildSentimentStat('Neutral', neutral, Colors.grey, Icons.sentiment_neutral),
                _buildSentimentStat('Negative', negative, Colors.red, Icons.sentiment_dissatisfied),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSentimentStat(String label, int count, Color color, IconData icon) {
    return Column(
      children: [
        CircleAvatar(
          backgroundColor: color.withOpacity(0.2),
          radius: 28,
          child: Icon(icon, color: color, size: 28),
        ),
        const SizedBox(height: 8),
        Text(
          count.toString(),
          style: TextStyle(
            fontSize: 22,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
        Text(label, style: TextStyle(color: Colors.grey.shade600)),
      ],
    );
  }

  Widget _buildResponseMetrics() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Response Metrics',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            _buildMetricRow('Average Response Time', '2h 15m', Icons.timer),
            _buildMetricRow('Response Rate', '94%', Icons.reply_all),
            _buildMetricRow('Resolution Rate', '87%', Icons.check_circle),
            _buildMetricRow('Customer Satisfaction', '4.6/5', Icons.star),
          ],
        ),
      ),
    );
  }

  Widget _buildMetricRow(String label, String value, IconData icon) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Icon(icon, color: Colors.pink, size: 20),
          const SizedBox(width: 12),
          Text(label),
          const Spacer(),
          Text(
            value,
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
        ],
      ),
    );
  }

  String _formatTimeAgo(DateTime date) {
    final difference = DateTime.now().difference(date);
    if (difference.inDays > 0) {
      return '${difference.inDays}d ago';
    } else if (difference.inHours > 0) {
      return '${difference.inHours}h ago';
    } else if (difference.inMinutes > 0) {
      return '${difference.inMinutes}m ago';
    } else {
      return 'Just now';
    }
  }

  void _showMessageDetail(SocialMessage message, SocialInboxProvider provider) {
    if (!message.isRead) {
      provider.markAsRead(message.id);
    }

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.6,
        minChildSize: 0.4,
        maxChildSize: 0.9,
        expand: false,
        builder: (context, scrollController) => ListView(
          controller: scrollController,
          padding: const EdgeInsets.all(20),
          children: [
            Center(
              child: Container(
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                  color: Colors.grey.shade300,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),
            const SizedBox(height: 20),
            Row(
              children: [
                CircleAvatar(
                  radius: 28,
                  child: Text(
                    message.authorName.substring(0, 1).toUpperCase(),
                    style: const TextStyle(fontSize: 24),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        message.authorName,
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(
                        '@${message.authorHandle}',
                        style: TextStyle(color: Colors.grey.shade600),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),
            Text(
              message.content,
              style: const TextStyle(fontSize: 16, height: 1.5),
            ),
            const SizedBox(height: 20),
            Row(
              children: [
                _buildEngagementStat(Icons.favorite, message.likesCount),
                const SizedBox(width: 20),
                _buildEngagementStat(Icons.repeat, message.sharesCount),
                const SizedBox(width: 20),
                _buildEngagementStat(Icons.comment, message.commentsCount),
              ],
            ),
            const Divider(height: 40),
            const Text(
              'Quick Actions',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                ActionChip(
                  avatar: const Icon(Icons.reply, size: 18),
                  label: const Text('Reply'),
                  onPressed: () {
                    Navigator.pop(context);
                    _showReplyDialog(message);
                  },
                ),
                ActionChip(
                  avatar: const Icon(Icons.person_add, size: 18),
                  label: const Text('Create Lead'),
                  onPressed: () {},
                ),
                ActionChip(
                  avatar: const Icon(Icons.bookmark_add, size: 18),
                  label: const Text('Save'),
                  onPressed: () {},
                ),
                ActionChip(
                  avatar: const Icon(Icons.share, size: 18),
                  label: const Text('Share'),
                  onPressed: () {},
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  void _showComposeDialog() {
    final contentController = TextEditingController();
    String selectedPlatform = 'twitter';

    showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          title: const Text('Compose Message'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              DropdownButtonFormField<String>(
                value: selectedPlatform,
                decoration: const InputDecoration(
                  labelText: 'Platform',
                  border: OutlineInputBorder(),
                ),
                items: _platforms.skip(1).map((p) => DropdownMenuItem(
                  value: p['id'] as String,
                  child: Row(
                    children: [
                      Icon(p['icon'] as IconData, color: p['color'] as Color, size: 20),
                      const SizedBox(width: 8),
                      Text(p['name'] as String),
                    ],
                  ),
                )).toList(),
                onChanged: (value) {
                  setDialogState(() {
                    selectedPlatform = value!;
                  });
                },
              ),
              const SizedBox(height: 16),
              TextField(
                controller: contentController,
                decoration: const InputDecoration(
                  labelText: 'Message',
                  border: OutlineInputBorder(),
                ),
                maxLines: 4,
                maxLength: selectedPlatform == 'twitter' ? 280 : null,
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancel'),
            ),
            ElevatedButton.icon(
              onPressed: () {
                _provider.sendMessage(
                  platform: selectedPlatform,
                  content: contentController.text,
                );
                Navigator.pop(context);
              },
              icon: const Icon(Icons.send),
              label: const Text('Post'),
              style: ElevatedButton.styleFrom(backgroundColor: Colors.pink),
            ),
          ],
        ),
      ),
    );
  }

  void _showReplyDialog(SocialMessage message) {
    final replyController = TextEditingController();

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Reply to @${message.authorHandle}'),
        content: TextField(
          controller: replyController,
          decoration: const InputDecoration(
            labelText: 'Your Reply',
            border: OutlineInputBorder(),
          ),
          maxLines: 4,
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton.icon(
            onPressed: () {
              _provider.replyToMessage(message.id, replyController.text);
              Navigator.pop(context);
            },
            icon: const Icon(Icons.reply),
            label: const Text('Reply'),
            style: ElevatedButton.styleFrom(backgroundColor: Colors.pink),
          ),
        ],
      ),
    );
  }
}
