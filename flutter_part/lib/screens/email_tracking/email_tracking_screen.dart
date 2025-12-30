import 'package:flutter/material.dart';
import '../../core/utils/api_client.dart';
import '../../services/advanced_services.dart';
import '../../models/advanced_models.dart';
import '../../widgets/loading_indicator.dart';
import '../../widgets/empty_state.dart';

class EmailTrackingScreen extends StatefulWidget {
  const EmailTrackingScreen({super.key});

  @override
  State<EmailTrackingScreen> createState() => _EmailTrackingScreenState();
}

class _EmailTrackingScreenState extends State<EmailTrackingScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  late EmailTrackingService _service;
  
  List<TrackedEmail> _emails = [];
  List<EmailSequence> _sequences = [];
  Map<String, dynamic>? _analytics;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _service = EmailTrackingService(ApiClient());
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);
    try {
      final results = await Future.wait([
        _service.getTrackedEmails(),
        _service.getSequences(),
        _service.getAnalytics(),
      ]);
      setState(() {
        _emails = results[0] as List<TrackedEmail>;
        _sequences = results[1] as List<EmailSequence>;
        _analytics = results[2] as Map<String, dynamic>;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
    }
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: NestedScrollView(
        headerSliverBuilder: (context, innerBoxIsScrolled) => [
          SliverAppBar(
            expandedHeight: 180,
            floating: false,
            pinned: true,
            flexibleSpace: FlexibleSpaceBar(
              title: const Text('Email Tracking'),
              background: Container(
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: [
                      Colors.blue.shade700,
                      Colors.cyan.shade600,
                    ],
                  ),
                ),
                child: SafeArea(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const SizedBox(height: 40),
                        _buildAnalyticsRow(),
                      ],
                    ),
                  ),
                ),
              ),
            ),
            bottom: TabBar(
              controller: _tabController,
              indicatorColor: Colors.white,
              tabs: const [
                Tab(text: 'Sent Emails'),
                Tab(text: 'Sequences'),
                Tab(text: 'Templates'),
              ],
            ),
          ),
        ],
        body: _isLoading
            ? const LoadingIndicator(message: 'Loading email data...')
            : RefreshIndicator(
                onRefresh: _loadData,
                child: TabBarView(
                  controller: _tabController,
                  children: [
                    _buildEmailsTab(),
                    _buildSequencesTab(),
                    _buildTemplatesTab(),
                  ],
                ),
              ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _showComposeDialog(),
        icon: const Icon(Icons.edit),
        label: const Text('Compose'),
        backgroundColor: Colors.blue,
      ),
    );
  }

  Widget _buildAnalyticsRow() {
    final sent = _analytics?['total_sent'] ?? _emails.length;
    final opened = _analytics?['total_opened'] ?? _emails.fold<int>(0, (sum, e) => sum + e.openCount);
    final clicked = _analytics?['total_clicked'] ?? _emails.fold<int>(0, (sum, e) => sum + e.clickCount);

    return Row(
      children: [
        _buildStatCard('$sent', 'Sent', Icons.send),
        const SizedBox(width: 12),
        _buildStatCard('$opened', 'Opens', Icons.visibility),
        const SizedBox(width: 12),
        _buildStatCard('$clicked', 'Clicks', Icons.touch_app),
      ],
    );
  }

  Widget _buildStatCard(String value, String label, IconData icon) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Colors.white.withValues(alpha: 0.2),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Row(
          children: [
            Icon(icon, color: Colors.white, size: 20),
            const SizedBox(width: 8),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  value,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  label,
                  style: TextStyle(
                    color: Colors.white.withValues(alpha: 0.8),
                    fontSize: 11,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEmailsTab() {
    if (_emails.isEmpty) {
      return EmptyState(
        icon: Icons.email_outlined,
        title: 'No Tracked Emails',
        subtitle: 'Send your first tracked email',
        action: ElevatedButton.icon(
          onPressed: () => _showComposeDialog(),
          icon: const Icon(Icons.edit),
          label: const Text('Compose Email'),
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _emails.length,
      itemBuilder: (context, index) {
        final email = _emails[index];
        return _buildEmailCard(email);
      },
    );
  }

  Widget _buildEmailCard(TrackedEmail email) {
    Color statusColor;
    IconData statusIcon;
    String statusText;

    if (email.openCount > 0) {
      statusColor = Colors.green;
      statusIcon = Icons.visibility;
      statusText = 'Opened ${email.openCount}x';
    } else {
      statusColor = Colors.grey;
      statusIcon = Icons.schedule;
      statusText = 'Not opened';
    }

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
                  backgroundColor: Colors.blue.shade50,
                  child: Text(
                    email.toEmail.isNotEmpty ? email.toEmail[0].toUpperCase() : '?',
                    style: TextStyle(color: Colors.blue.shade700),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        email.toEmail,
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
                      Text(
                        email.subject,
                        style: TextStyle(color: Colors.grey.shade600),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: statusColor.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(statusIcon, size: 14, color: statusColor),
                      const SizedBox(width: 4),
                      Text(
                        statusText,
                        style: TextStyle(
                          color: statusColor,
                          fontSize: 11,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Icon(Icons.send, size: 14, color: Colors.grey.shade600),
                const SizedBox(width: 4),
                Text(
                  _formatDate(email.sentAt),
                  style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
                ),
                if (email.clickCount > 0) ...[
                  const SizedBox(width: 16),
                  Icon(Icons.touch_app, size: 14, color: Colors.blue),
                  const SizedBox(width: 4),
                  Text(
                    '${email.clickCount} clicks',
                    style: const TextStyle(color: Colors.blue, fontSize: 12),
                  ),
                ],
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSequencesTab() {
    if (_sequences.isEmpty) {
      return const EmptyState(
        icon: Icons.auto_mode,
        title: 'No Email Sequences',
        subtitle: 'Create automated email sequences',
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _sequences.length,
      itemBuilder: (context, index) {
        final sequence = _sequences[index];
        return _buildSequenceCard(sequence);
      },
    );
  }

  Widget _buildSequenceCard(EmailSequence sequence) {
    Color statusColor;
    switch (sequence.status) {
      case 'active':
        statusColor = Colors.green;
        break;
      case 'paused':
        statusColor = Colors.orange;
        break;
      default:
        statusColor = Colors.grey;
    }

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: Colors.blue.shade50,
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Icon(Icons.auto_mode, color: Colors.blue.shade700),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        sequence.name,
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                      Text(
                        sequence.description,
                        style: TextStyle(color: Colors.grey.shade600),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: statusColor.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    sequence.status.toUpperCase(),
                    style: TextStyle(
                      color: statusColor,
                      fontWeight: FontWeight.bold,
                      fontSize: 11,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                _buildSequenceStat(Icons.email, '${sequence.stepsCount} steps'),
                const SizedBox(width: 16),
                _buildSequenceStat(Icons.people, '${sequence.enrolledCount} enrolled'),
              ],
            ),
            const Divider(height: 24),
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                if (sequence.status == 'active')
                  TextButton.icon(
                    onPressed: () => _service.pauseSequence(sequence.id).then((_) => _loadData()),
                    icon: const Icon(Icons.pause, size: 18),
                    label: const Text('Pause'),
                  )
                else
                  ElevatedButton.icon(
                    onPressed: () => _service.activateSequence(sequence.id).then((_) => _loadData()),
                    icon: const Icon(Icons.play_arrow, size: 18),
                    label: const Text('Activate'),
                  ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSequenceStat(IconData icon, String label) {
    return Row(
      children: [
        Icon(icon, size: 16, color: Colors.grey.shade600),
        const SizedBox(width: 4),
        Text(
          label,
          style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
        ),
      ],
    );
  }

  Widget _buildTemplatesTab() {
    return const EmptyState(
      icon: Icons.description_outlined,
      title: 'Email Templates',
      subtitle: 'Create reusable email templates',
    );
  }

  String _formatDate(DateTime date) {
    final now = DateTime.now();
    final diff = now.difference(date);

    if (diff.inMinutes < 60) {
      return '${diff.inMinutes}m ago';
    } else if (diff.inHours < 24) {
      return '${diff.inHours}h ago';
    } else if (diff.inDays < 7) {
      return '${diff.inDays}d ago';
    } else {
      return '${date.day}/${date.month}/${date.year}';
    }
  }

  void _showComposeDialog() {
    final toController = TextEditingController();
    final subjectController = TextEditingController();
    final bodyController = TextEditingController();

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => Padding(
        padding: EdgeInsets.only(
          left: 16,
          right: 16,
          top: 16,
          bottom: MediaQuery.of(context).viewInsets.bottom + 16,
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.email, color: Colors.blue),
                const SizedBox(width: 8),
                const Text(
                  'Compose Email',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                const Spacer(),
                IconButton(
                  onPressed: () => Navigator.pop(context),
                  icon: const Icon(Icons.close),
                ),
              ],
            ),
            const SizedBox(height: 16),
            TextField(
              controller: toController,
              decoration: const InputDecoration(
                labelText: 'To',
                prefixIcon: Icon(Icons.person),
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: subjectController,
              decoration: const InputDecoration(
                labelText: 'Subject',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: bodyController,
              decoration: const InputDecoration(
                labelText: 'Message',
                border: OutlineInputBorder(),
                alignLabelWithHint: true,
              ),
              maxLines: 5,
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () {
                      // Use AI to generate
                    },
                    icon: const Icon(Icons.auto_awesome),
                    label: const Text('AI Generate'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () async {
                      if (toController.text.isNotEmpty && 
                          subjectController.text.isNotEmpty) {
                        Navigator.pop(context);
                        await _service.sendEmail(
                          toEmail: toController.text,
                          subject: subjectController.text,
                          body: bodyController.text,
                        );
                        await _loadData();
                        if (!context.mounted) return;
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('Email sent!')),
                        );
                      }
                    },
                    icon: const Icon(Icons.send),
                    label: const Text('Send'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.blue,
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
