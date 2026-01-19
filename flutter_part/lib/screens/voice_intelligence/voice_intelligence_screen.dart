import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/utils/api_client.dart';
import '../../providers/enterprise_providers.dart';
import '../../models/enterprise_models.dart';
import '../../widgets/loading_indicator.dart';
import '../../widgets/empty_state.dart';

class VoiceIntelligenceScreen extends StatefulWidget {
  const VoiceIntelligenceScreen({super.key});

  @override
  State<VoiceIntelligenceScreen> createState() => _VoiceIntelligenceScreenState();
}

class _VoiceIntelligenceScreenState extends State<VoiceIntelligenceScreen>
    with SingleTickerProviderStateMixin {
  late VoiceIntelligenceProvider _provider;
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _provider = VoiceIntelligenceProvider(ApiClient());
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
          title: const Text('Voice Intelligence'),
          flexibleSpace: Container(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [Colors.deepPurple.shade700, Colors.purple.shade500],
              ),
            ),
          ),
          bottom: TabBar(
            controller: _tabController,
            indicatorColor: Colors.white,
            tabs: const [
              Tab(text: 'Dashboard', icon: Icon(Icons.dashboard)),
              Tab(text: 'Recordings', icon: Icon(Icons.mic)),
              Tab(text: 'Insights', icon: Icon(Icons.lightbulb)),
            ],
          ),
        ),
        body: Consumer<VoiceIntelligenceProvider>(
          builder: (context, provider, _) {
            return TabBarView(
              controller: _tabController,
              children: [
                _buildDashboardTab(provider),
                _buildRecordingsTab(provider),
                _buildInsightsTab(provider),
              ],
            );
          },
        ),
      ),
    );
  }

  Widget _buildDashboardTab(VoiceIntelligenceProvider provider) {
    return RefreshIndicator(
      onRefresh: _loadData,
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildCallStats(provider),
            const SizedBox(height: 20),
            _buildSentimentOverview(provider),
            const SizedBox(height: 20),
            _buildTopKeywords(provider),
            const SizedBox(height: 20),
            _buildRecentCalls(provider),
          ],
        ),
      ),
    );
  }

  Widget _buildCallStats(VoiceIntelligenceProvider provider) {
    return Row(
      children: [
        Expanded(
          child: _buildStatCard(
            'Total Calls',
            provider.recordings.length.toString(),
            Icons.call,
            Colors.blue,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildStatCard(
            'Analyzed',
            provider.analyses.length.toString(),
            Icons.analytics,
            Colors.green,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildStatCard(
            'Avg Duration',
            '${provider.avgDuration}m',
            Icons.timer,
            Colors.orange,
          ),
        ),
      ],
    );
  }

  Widget _buildStatCard(String label, String value, IconData icon, Color color) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Icon(icon, color: color, size: 28),
            const SizedBox(height: 8),
            Text(
              value,
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
            Text(
              label,
              style: TextStyle(
                fontSize: 11,
                color: Colors.grey.shade600,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSentimentOverview(VoiceIntelligenceProvider provider) {
    final positive = provider.analyses.where((a) => a.sentiment == 'positive').length;
    final negative = provider.analyses.where((a) => a.sentiment == 'negative').length;
    final neutral = provider.analyses.length - positive - negative;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Call Sentiment Overview',
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
            const SizedBox(height: 20),
            ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: Row(
                children: [
                  Expanded(
                    flex: positive > 0 ? positive : 1,
                    child: Container(height: 8, color: Colors.green),
                  ),
                  Expanded(
                    flex: neutral > 0 ? neutral : 1,
                    child: Container(height: 8, color: Colors.grey),
                  ),
                  Expanded(
                    flex: negative > 0 ? negative : 1,
                    child: Container(height: 8, color: Colors.red),
                  ),
                ],
              ),
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
          radius: 24,
          child: Icon(icon, color: color),
        ),
        const SizedBox(height: 8),
        Text(
          count.toString(),
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
        Text(label, style: TextStyle(color: Colors.grey.shade600, fontSize: 12)),
      ],
    );
  }

  Widget _buildTopKeywords(VoiceIntelligenceProvider provider) {
    final keywords = provider.topKeywords;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Top Keywords',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            if (keywords.isEmpty)
              const Center(
                child: Padding(
                  padding: EdgeInsets.all(20),
                  child: Text('No keywords analyzed yet'),
                ),
              )
            else
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: keywords.take(15).map((kw) => Chip(
                  label: Text(kw['word'] as String),
                  avatar: CircleAvatar(
                    backgroundColor: Colors.deepPurple.shade100,
                    child: Text(
                      (kw['count'] as int).toString(),
                      style: const TextStyle(fontSize: 11),
                    ),
                  ),
                )).toList(),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildRecentCalls(VoiceIntelligenceProvider provider) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Recent Calls',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                TextButton(
                  onPressed: () => _tabController.animateTo(1),
                  child: const Text('View All'),
                ),
              ],
            ),
            const Divider(),
            if (provider.recordings.isEmpty)
              const Padding(
                padding: EdgeInsets.all(20),
                child: Center(child: Text('No calls recorded yet')),
              )
            else
              ...provider.recordings.take(5).map((r) => _buildCallTile(r)),
          ],
        ),
      ),
    );
  }

  Widget _buildCallTile(VoiceRecording recording) {
    return ListTile(
      contentPadding: EdgeInsets.zero,
      leading: CircleAvatar(
        backgroundColor: Colors.deepPurple.shade50,
        child: Icon(
          recording.callType == 'inbound' ? Icons.call_received : Icons.call_made,
          color: Colors.deepPurple,
        ),
      ),
      title: Text(recording.contactName ?? 'Unknown Contact'),
      subtitle: Text(
        '${_formatDuration(recording.duration)} • ${_formatDate(recording.createdAt)}',
      ),
      trailing: recording.isAnalyzed
          ? const Icon(Icons.check_circle, color: Colors.green, size: 20)
          : const Icon(Icons.pending, color: Colors.orange, size: 20),
    );
  }

  Widget _buildRecordingsTab(VoiceIntelligenceProvider provider) {
    if (provider.isLoading) {
      return const LoadingIndicator(message: 'Loading recordings...');
    }

    if (provider.recordings.isEmpty) {
      return const EmptyState(
        icon: Icons.mic_off_outlined,
        title: 'No Recordings',
        subtitle: 'Call recordings will appear here',
      );
    }

    return RefreshIndicator(
      onRefresh: () => provider.loadRecordings(),
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: provider.recordings.length,
        itemBuilder: (context, index) {
          return _buildRecordingCard(provider.recordings[index], provider);
        },
      ),
    );
  }

  Widget _buildRecordingCard(VoiceRecording recording, VoiceIntelligenceProvider provider) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        onTap: () => _showRecordingDetails(recording, provider),
        borderRadius: BorderRadius.circular(12),
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
                      color: Colors.deepPurple.shade50,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Icon(
                      recording.callType == 'inbound' ? Icons.call_received : Icons.call_made,
                      color: Colors.deepPurple,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          recording.contactName ?? 'Unknown Contact',
                          style: const TextStyle(fontWeight: FontWeight.bold),
                        ),
                        Text(
                          recording.phoneNumber ?? 'No phone',
                          style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
                        ),
                      ],
                    ),
                  ),
                  if (recording.isAnalyzed)
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: Colors.green.shade100,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: const Text(
                        'Analyzed',
                        style: TextStyle(color: Colors.green, fontSize: 11),
                      ),
                    ),
                ],
              ),
              const Divider(height: 24),
              Row(
                children: [
                  _buildRecordingInfo(Icons.timer, _formatDuration(recording.duration)),
                  const SizedBox(width: 16),
                  _buildRecordingInfo(Icons.calendar_today, _formatDate(recording.createdAt)),
                  const Spacer(),
                  if (!recording.isAnalyzed)
                    TextButton.icon(
                      onPressed: () => provider.analyzeRecording(recording.id),
                      icon: const Icon(Icons.auto_fix_high, size: 18),
                      label: const Text('Analyze'),
                    )
                  else
                    TextButton.icon(
                      onPressed: () => _showRecordingDetails(recording, provider),
                      icon: const Icon(Icons.visibility, size: 18),
                      label: const Text('View'),
                    ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildRecordingInfo(IconData icon, String text) {
    return Row(
      children: [
        Icon(icon, size: 16, color: Colors.grey.shade600),
        const SizedBox(width: 4),
        Text(
          text,
          style: TextStyle(color: Colors.grey.shade700, fontSize: 13),
        ),
      ],
    );
  }

  Widget _buildInsightsTab(VoiceIntelligenceProvider provider) {
    if (provider.isLoading) {
      return const LoadingIndicator(message: 'Loading insights...');
    }

    if (provider.analyses.isEmpty) {
      return const EmptyState(
        icon: Icons.lightbulb_outline,
        title: 'No Insights Yet',
        subtitle: 'Analyze calls to generate insights',
      );
    }

    return RefreshIndicator(
      onRefresh: () => provider.loadAnalyses(),
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: provider.analyses.length,
        itemBuilder: (context, index) {
          return _buildAnalysisCard(provider.analyses[index]);
        },
      ),
    );
  }

  Widget _buildAnalysisCard(VoiceAnalysis analysis) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                CircleAvatar(
                  backgroundColor: _getSentimentColor(analysis.sentiment).withOpacity(0.2),
                  child: Icon(
                    _getSentimentIcon(analysis.sentiment),
                    color: _getSentimentColor(analysis.sentiment),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Call Analysis',
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
                      Text(
                        _formatDate(analysis.analyzedAt),
                        style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
                      ),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: _getSentimentColor(analysis.sentiment).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    analysis.sentiment.toUpperCase(),
                    style: TextStyle(
                      color: _getSentimentColor(analysis.sentiment),
                      fontWeight: FontWeight.bold,
                      fontSize: 11,
                    ),
                  ),
                ),
              ],
            ),
            if (analysis.summary != null) ...[
              const SizedBox(height: 16),
              const Text(
                'Summary',
                style: TextStyle(fontWeight: FontWeight.w600),
              ),
              const SizedBox(height: 4),
              Text(
                analysis.summary!,
                style: TextStyle(color: Colors.grey.shade700),
              ),
            ],
            if (analysis.keyMoments.isNotEmpty) ...[
              const Divider(height: 24),
              const Text(
                'Key Moments',
                style: TextStyle(fontWeight: FontWeight.w600),
              ),
              const SizedBox(height: 12),
              ...analysis.keyMoments.map((moment) => _buildKeyMoment(moment)),
            ],
            if (analysis.actionItems.isNotEmpty) ...[
              const Divider(height: 24),
              const Text(
                'Action Items',
                style: TextStyle(fontWeight: FontWeight.w600),
              ),
              const SizedBox(height: 12),
              ...analysis.actionItems.map((item) => Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Row(
                  children: [
                    const Icon(Icons.task_alt, size: 18, color: Colors.blue),
                    const SizedBox(width: 8),
                    Expanded(child: Text(item)),
                  ],
                ),
              )),
            ],
            const Divider(height: 24),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildMetricBadge('Talk Time', '${analysis.talkRatio}%', Icons.mic),
                _buildMetricBadge('Listen Time', '${100 - analysis.talkRatio}%', Icons.hearing),
                _buildMetricBadge('Questions', analysis.questionsAsked.toString(), Icons.help),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildKeyMoment(KeyMoment moment) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.grey.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.grey.shade200),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: Colors.deepPurple.shade100,
              borderRadius: BorderRadius.circular(4),
            ),
            child: Text(
              _formatDuration(moment.timestamp),
              style: TextStyle(
                color: Colors.deepPurple.shade700,
                fontSize: 11,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  moment.type.toUpperCase(),
                  style: TextStyle(
                    color: Colors.grey.shade600,
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(moment.description),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMetricBadge(String label, String value, IconData icon) {
    return Column(
      children: [
        Icon(icon, color: Colors.deepPurple, size: 20),
        const SizedBox(height: 4),
        Text(
          value,
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        Text(
          label,
          style: TextStyle(color: Colors.grey.shade600, fontSize: 11),
        ),
      ],
    );
  }

  void _showRecordingDetails(VoiceRecording recording, VoiceIntelligenceProvider provider) {
    final analysis = provider.analyses.firstWhere(
      (a) => a.recordingId == recording.id,
      orElse: () => VoiceAnalysis(
        id: 0,
        recordingId: recording.id,
        sentiment: 'neutral',
        talkRatio: 50,
        questionsAsked: 0,
        keyMoments: [],
        actionItems: [],
        analyzedAt: DateTime.now(),
      ),
    );

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.7,
        minChildSize: 0.5,
        maxChildSize: 0.95,
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
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.deepPurple.shade50,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Icon(Icons.mic, color: Colors.deepPurple),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        recording.contactName ?? 'Unknown Contact',
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(
                        '${_formatDuration(recording.duration)} • ${_formatDate(recording.createdAt)}',
                        style: TextStyle(color: Colors.grey.shade600),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),
            // Audio player placeholder
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.grey.shade100,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Row(
                children: [
                  IconButton(
                    onPressed: () {},
                    icon: const Icon(Icons.play_circle_filled, size: 40),
                    color: Colors.deepPurple,
                  ),
                  Expanded(
                    child: Column(
                      children: [
                        Slider(
                          value: 0,
                          onChanged: (v) {},
                          activeColor: Colors.deepPurple,
                        ),
                        Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 16),
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              const Text('0:00'),
                              Text(_formatDuration(recording.duration)),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            if (recording.transcript != null) ...[
              const SizedBox(height: 24),
              const Text(
                'Transcript',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.grey.shade50,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.grey.shade200),
                ),
                child: Text(
                  recording.transcript!,
                  style: const TextStyle(height: 1.5),
                ),
              ),
            ],
            if (recording.isAnalyzed) ...[
              const SizedBox(height: 24),
              _buildAnalysisCard(analysis),
            ],
          ],
        ),
      ),
    );
  }

  Color _getSentimentColor(String sentiment) {
    switch (sentiment.toLowerCase()) {
      case 'positive':
        return Colors.green;
      case 'negative':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  IconData _getSentimentIcon(String sentiment) {
    switch (sentiment.toLowerCase()) {
      case 'positive':
        return Icons.sentiment_satisfied;
      case 'negative':
        return Icons.sentiment_dissatisfied;
      default:
        return Icons.sentiment_neutral;
    }
  }

  String _formatDuration(int seconds) {
    final minutes = seconds ~/ 60;
    final secs = seconds % 60;
    return '$minutes:${secs.toString().padLeft(2, '0')}';
  }

  String _formatDate(DateTime date) {
    return '${date.day}/${date.month}/${date.year}';
  }
}
