import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/utils/api_client.dart';
import '../../providers/social_provider.dart';
import '../../models/social_models.dart';
import '../../widgets/loading_indicator.dart';
import '../../widgets/empty_state.dart';

class SocialSellingScreen extends StatefulWidget {
  const SocialSellingScreen({super.key});

  @override
  State<SocialSellingScreen> createState() => _SocialSellingScreenState();
}

class _SocialSellingScreenState extends State<SocialSellingScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  late SocialSellingProvider _provider;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _provider = SocialSellingProvider(ApiClient());
    _loadData();
  }

  Future<void> _loadData() async {
    await _provider.loadDashboard();
    await _provider.loadContentLibrary();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider.value(
      value: _provider,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Social Selling'),
          bottom: TabBar(
            controller: _tabController,
            tabs: const [
              Tab(text: 'Dashboard'),
              Tab(text: 'Content Library'),
            ],
          ),
        ),
        body: Consumer<SocialSellingProvider>(
          builder: (context, provider, _) {
            if (provider.isLoading && provider.profiles.isEmpty) {
              return const LoadingIndicator(message: 'Loading social data...');
            }

            return TabBarView(
              controller: _tabController,
              children: [
                _buildDashboardTab(provider),
                _buildContentLibraryTab(provider),
              ],
            );
          },
        ),
        floatingActionButton: FloatingActionButton(
          onPressed: () => _showComposeDialog(context),
          child: const Icon(Icons.edit),
        ),
      ),
    );
  }

  Widget _buildDashboardTab(SocialSellingProvider provider) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        _buildMetricsCards(provider.metrics),
        const SizedBox(height: 24),
        const Text(
          'Connected Accounts',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 12),
        _buildAccountsList(provider),
        const SizedBox(height: 24),
        const Text(
          'Recent Posts',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 12),
        _buildRecentPosts(provider),
      ],
    );
  }

  Widget _buildMetricsCards(SocialMetrics? metrics) {
    if (metrics == null) return const SizedBox.shrink();

    return Row(
      children: [
        Expanded(
          child: _buildMetricCard(
            'SSI Score',
            metrics.socialSellingIndex.toStringAsFixed(1),
            Icons.speed,
            Colors.blue,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildMetricCard(
            'Engagements',
            metrics.totalEngagements.toString(),
            Icons.thumb_up,
            Colors.orange,
          ),
        ),
      ],
    );
  }

  Widget _buildMetricCard(String label, String value, IconData icon, Color color) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Icon(icon, color: color, size: 28),
            const SizedBox(height: 8),
            Text(
              value,
              style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            Text(
              label,
              style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAccountsList(SocialSellingProvider provider) {
    if (provider.profiles.isEmpty) {
      return Card(
        child: ListTile(
          leading: const Icon(Icons.link_off),
          title: const Text('No accounts connected'),
          trailing: TextButton(
            onPressed: () => provider.connectLinkedIn(),
            child: const Text('Connect LinkedIn'),
          ),
        ),
      );
    }

    return Column(
      children: provider.profiles.map((profile) => Card(
        child: ListTile(
          leading: const CircleAvatar(
            backgroundColor: Colors.blue,
            child: Icon(Icons.person, color: Colors.white),
          ),
          title: Text(profile.username),
          subtitle: Text(profile.platform.toUpperCase()),
          trailing: const Icon(Icons.check_circle, color: Colors.green),
        ),
      )).toList(),
    );
  }

  Widget _buildRecentPosts(SocialSellingProvider provider) {
    if (provider.recentPosts.isEmpty) {
      return const EmptyState(
        icon: Icons.post_add,
        title: 'No posts yet',
        subtitle: 'Start sharing content to see analytics',
      );
    }

    return Column(
      children: provider.recentPosts.map((post) => Card(
        margin: const EdgeInsets.only(bottom: 12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(post.content, maxLines: 2, overflow: TextOverflow.ellipsis),
              const SizedBox(height: 12),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  _buildPostStat(Icons.thumb_up_outlined, post.likes),
                  _buildPostStat(Icons.comment_outlined, post.comments),
                  _buildPostStat(Icons.share_outlined, post.shares),
                  _buildPostStat(Icons.visibility_outlined, post.impressions),
                ],
              ),
            ],
          ),
        ),
      )).toList(),
    );
  }

  Widget _buildPostStat(IconData icon, int count) {
    return Row(
      children: [
        Icon(icon, size: 16, color: Colors.grey),
        const SizedBox(width: 4),
        Text('$count', style: const TextStyle(color: Colors.grey)),
      ],
    );
  }

  Widget _buildContentLibraryTab(SocialSellingProvider provider) {
    if (provider.contentLibrary.isEmpty) {
      return const EmptyState(
        icon: Icons.library_books,
        title: 'Library Empty',
        subtitle: 'No templates available',
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: provider.contentLibrary.length,
      itemBuilder: (context, index) {
        final template = provider.contentLibrary[index];
        return Card(
          margin: const EdgeInsets.only(bottom: 12),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      template.title,
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                    ),
                    Chip(
                      label: Text(
                        template.category,
                        style: const TextStyle(fontSize: 10),
                      ),
                      padding: EdgeInsets.zero,
                      materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Text(template.body, maxLines: 3, overflow: TextOverflow.ellipsis),
                const SizedBox(height: 12),
                Align(
                  alignment: Alignment.centerRight,
                  child: ElevatedButton.icon(
                    onPressed: () => _showComposeDialog(context, initialContent: template.body),
                    icon: const Icon(Icons.share, size: 16),
                    label: const Text('Use Template'),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  void _showComposeDialog(BuildContext context, {String? initialContent}) {
    final controller = TextEditingController(text: initialContent);
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (context) => Padding(
        padding: EdgeInsets.only(
          bottom: MediaQuery.of(context).viewInsets.bottom,
          left: 16, right: 16, top: 16,
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text('Compose Post', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
            const SizedBox(height: 16),
            TextField(
              controller: controller,
              maxLines: 5,
              decoration: const InputDecoration(
                hintText: 'What do you want to share?',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () {
                if (controller.text.isNotEmpty) {
                  _provider.shareContent(controller.text, 'linkedin');
                  Navigator.pop(context);
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Posting to LinkedIn...')),
                  );
                }
              },
              child: const Text('Post to LinkedIn'),
            ),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }
}
