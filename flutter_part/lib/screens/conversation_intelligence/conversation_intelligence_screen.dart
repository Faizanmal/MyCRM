import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/utils/api_client.dart';
import '../../providers/enterprise_providers.dart';
import '../../widgets/loading_indicator.dart';
import '../../widgets/empty_state.dart';

class ConversationIntelligenceScreen extends StatefulWidget {
  const ConversationIntelligenceScreen({super.key});

  @override
  State<ConversationIntelligenceScreen> createState() => _ConversationIntelligenceScreenState();
}

class _ConversationIntelligenceScreenState extends State<ConversationIntelligenceScreen>
    with SingleTickerProviderStateMixin {
  late ConversationIntelligenceProvider _provider;
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _provider = ConversationIntelligenceProvider(ApiClient());
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
          title: const Text('Conversation Intelligence'),
          flexibleSpace: Container(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [Colors.teal.shade700, Colors.cyan.shade500],
              ),
            ),
          ),
          bottom: TabBar(
            controller: _tabController,
            indicatorColor: Colors.white,
            tabs: const [
              Tab(text: 'Overview', icon: Icon(Icons.insights)),
              Tab(text: 'Conversations', icon: Icon(Icons.chat)),
              Tab(text: 'Coaching', icon: Icon(Icons.school)),
            ],
          ),
        ),
        body: Consumer<ConversationIntelligenceProvider>(
          builder: (context, provider, _) {
            return TabBarView(
              controller: _tabController,
              children: [
                _buildOverviewTab(provider),
                _buildConversationsTab(provider),
                _buildCoachingTab(provider),
              ],
            );
          },
        ),
      ),
    );
  }

  Widget _buildOverviewTab(ConversationIntelligenceProvider provider) {
    return RefreshIndicator(
      onRefresh: _loadData,
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildInsightsHeader(provider),
            const SizedBox(height: 20),
            _buildTalkMetrics(provider),
            const SizedBox(height: 20),
            _buildTopicsCard(provider),
            const SizedBox(height: 20),
            _buildCompetitorMentions(provider),
            const SizedBox(height: 20),
            _buildTopPerformers(provider),
          ],
        ),
      ),
    );
  }

  Widget _buildInsightsHeader(ConversationIntelligenceProvider provider) {
    return Card(
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: [Colors.teal.shade700, Colors.cyan.shade500],
          ),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Conversation Insights',
              style: TextStyle(color: Colors.white70, fontSize: 14),
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '${provider.totalConversations}',
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 42,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const Text(
                        'Conversations Analyzed',
                        style: TextStyle(color: Colors.white70),
                      ),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 0.2),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Column(
                    children: [
                      const Icon(Icons.trending_up, color: Colors.white, size: 32),
                      const SizedBox(height: 4),
                      Text(
                        '+${provider.weeklyGrowth}%',
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTalkMetrics(ConversationIntelligenceProvider provider) {
    return Row(
      children: [
        Expanded(
          child: _buildMetricCard(
            'Avg Talk Ratio',
            '${provider.avgTalkRatio}%',
            Icons.mic,
            Colors.blue,
            'Target: 40-60%',
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildMetricCard(
            'Avg Call Duration',
            '${provider.avgCallDuration}m',
            Icons.timer,
            Colors.orange,
            'Target: 15-30m',
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildMetricCard(
            'Questions/Call',
            provider.avgQuestionsPerCall.toString(),
            Icons.help,
            Colors.purple,
            'Target: 5-10',
          ),
        ),
      ],
    );
  }

  Widget _buildMetricCard(String label, String value, IconData icon, Color color, String target) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          children: [
            Icon(icon, color: color, size: 24),
            const SizedBox(height: 8),
            Text(
              value,
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
            Text(
              label,
              style: TextStyle(
                fontSize: 10,
                color: Colors.grey.shade600,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 4),
            Text(
              target,
              style: TextStyle(
                fontSize: 9,
                color: Colors.grey.shade500,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTopicsCard(ConversationIntelligenceProvider provider) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Top Discussion Topics',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: provider.topTopics.map((topic) => Chip(
                label: Text(topic['name'] as String),
                backgroundColor: Colors.teal.shade50,
                avatar: CircleAvatar(
                  backgroundColor: Colors.teal,
                  child: Text(
                    '${topic['count']}',
                    style: const TextStyle(fontSize: 10, color: Colors.white),
                  ),
                ),
              )).toList(),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCompetitorMentions(ConversationIntelligenceProvider provider) {
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
                  'Competitor Mentions',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                TextButton(
                  onPressed: () {},
                  child: const Text('View All'),
                ),
              ],
            ),
            const Divider(),
            ...provider.competitorMentions.map((competitor) => Padding(
              padding: const EdgeInsets.symmetric(vertical: 8),
              child: Row(
                children: [
                  CircleAvatar(
                    backgroundColor: Colors.red.shade50,
                    radius: 16,
                    child: Icon(Icons.business, color: Colors.red.shade700, size: 16),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(competitor['name'] as String),
                  ),
                  Text(
                    '${competitor['count']} mentions',
                    style: TextStyle(
                      color: Colors.grey.shade600,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ],
              ),
            )),
          ],
        ),
      ),
    );
  }

  Widget _buildTopPerformers(ConversationIntelligenceProvider provider) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Top Performers',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const Divider(),
            ...provider.topPerformers.asMap().entries.map((entry) {
              final index = entry.key;
              final performer = entry.value;
              return ListTile(
                contentPadding: EdgeInsets.zero,
                leading: Stack(
                  children: [
                    CircleAvatar(
                      backgroundColor: Colors.teal.shade100,
                      child: Text(
                        (performer['name'] as String).substring(0, 1),
                        style: TextStyle(color: Colors.teal.shade700),
                      ),
                    ),
                    if (index < 3)
                      Positioned(
                        right: -2,
                        bottom: -2,
                        child: Container(
                          padding: const EdgeInsets.all(4),
                          decoration: BoxDecoration(
                            color: index == 0 ? Colors.amber : index == 1 ? Colors.grey : Colors.brown,
                            shape: BoxShape.circle,
                          ),
                          child: Text(
                            '${index + 1}',
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 10,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                      ),
                  ],
                ),
                title: Text(performer['name'] as String),
                subtitle: Text('${performer['calls']} calls analyzed'),
                trailing: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Text(
                      '${performer['score']}',
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        color: Colors.teal.shade700,
                        fontSize: 18,
                      ),
                    ),
                    const Text('Score', style: TextStyle(fontSize: 11)),
                  ],
                ),
              );
            }),
          ],
        ),
      ),
    );
  }

  Widget _buildConversationsTab(ConversationIntelligenceProvider provider) {
    if (provider.isLoading) {
      return const LoadingIndicator(message: 'Loading conversations...');
    }

    if (provider.conversations.isEmpty) {
      return const EmptyState(
        icon: Icons.chat_outlined,
        title: 'No Conversations',
        subtitle: 'Analyzed conversations will appear here',
      );
    }

    return RefreshIndicator(
      onRefresh: () => provider.loadConversations(),
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: provider.conversations.length,
        itemBuilder: (context, index) {
          return _buildConversationCard(provider.conversations[index], provider);
        },
      ),
    );
  }

  Widget _buildConversationCard(dynamic conversation, ConversationIntelligenceProvider provider) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        onTap: () => _showConversationDetail(conversation),
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  CircleAvatar(
                    backgroundColor: Colors.teal.shade50,
                    child: Icon(Icons.headset_mic, color: Colors.teal.shade700),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          conversation['title'] ?? 'Untitled Conversation',
                          style: const TextStyle(fontWeight: FontWeight.bold),
                        ),
                        Text(
                          '${conversation['rep_name']} • ${conversation['duration']}min',
                          style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
                        ),
                      ],
                    ),
                  ),
                  _buildScoreBadge(conversation['score'] ?? 0),
                ],
              ),
              const Divider(height: 24),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  _buildConversationStat('Talk Ratio', '${conversation['talk_ratio'] ?? 50}%'),
                  _buildConversationStat('Questions', '${conversation['questions'] ?? 0}'),
                  _buildConversationStat('Keywords', '${conversation['keywords']?.length ?? 0}'),
                ],
              ),
              if (conversation['topics'] != null && (conversation['topics'] as List).isNotEmpty) ...[
                const SizedBox(height: 12),
                Wrap(
                  spacing: 6,
                  runSpacing: 6,
                  children: (conversation['topics'] as List).take(3).map((topic) => Chip(
                    label: Text(topic, style: const TextStyle(fontSize: 11)),
                    padding: EdgeInsets.zero,
                    materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                    backgroundColor: Colors.grey.shade100,
                  )).toList(),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildScoreBadge(int score) {
    Color color;
    if (score >= 80) {
      color = Colors.green;
    } else if (score >= 60) {
      color = Colors.orange;
    } else {
      color = Colors.red;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: color.withValues(alpha: 0.5)),
      ),
      child: Text(
        score.toString(),
        style: TextStyle(
          color: color,
          fontWeight: FontWeight.bold,
          fontSize: 16,
        ),
      ),
    );
  }

  Widget _buildConversationStat(String label, String value) {
    return Column(
      children: [
        Text(
          value,
          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
        ),
        Text(
          label,
          style: TextStyle(color: Colors.grey.shade600, fontSize: 11),
        ),
      ],
    );
  }

  Widget _buildCoachingTab(ConversationIntelligenceProvider provider) {
    return RefreshIndicator(
      onRefresh: _loadData,
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildCoachingOverview(provider),
            const SizedBox(height: 20),
            _buildSkillsAssessment(provider),
            const SizedBox(height: 20),
            _buildImprovementAreas(provider),
            const SizedBox(height: 20),
            _buildCoachingRecommendations(provider),
          ],
        ),
      ),
    );
  }

  Widget _buildCoachingOverview(ConversationIntelligenceProvider provider) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.teal.shade50,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Icon(Icons.school, color: Colors.teal.shade700, size: 28),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Team Coaching Score',
                        style: TextStyle(fontSize: 16),
                      ),
                      Text(
                        '78/100',
                        style: TextStyle(
                          fontSize: 28,
                          fontWeight: FontWeight.bold,
                          color: Colors.teal.shade700,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),
            ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: LinearProgressIndicator(
                value: 0.78,
                minHeight: 10,
                backgroundColor: Colors.grey.shade200,
                valueColor: AlwaysStoppedAnimation(Colors.teal.shade700),
              ),
            ),
            const SizedBox(height: 8),
            Text(
              '+5 points from last month',
              style: TextStyle(color: Colors.green.shade700),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSkillsAssessment(ConversationIntelligenceProvider provider) {
    final skills = [
      {'name': 'Discovery Questions', 'score': 85, 'change': 5},
      {'name': 'Active Listening', 'score': 72, 'change': 3},
      {'name': 'Objection Handling', 'score': 68, 'change': -2},
      {'name': 'Value Proposition', 'score': 80, 'change': 8},
      {'name': 'Closing Techniques', 'score': 65, 'change': 4},
    ];

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Skills Assessment',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const Divider(),
            ...skills.map((skill) => Padding(
              padding: const EdgeInsets.symmetric(vertical: 8),
              child: Column(
                children: [
                  Row(
                    children: [
                      Expanded(child: Text(skill['name'] as String)),
                      Text(
                        '${skill['score']}',
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
                      const SizedBox(width: 8),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                        decoration: BoxDecoration(
                          color: (skill['change'] as int) >= 0 
                              ? Colors.green.shade50 
                              : Colors.red.shade50,
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(
                              (skill['change'] as int) >= 0 
                                  ? Icons.arrow_upward 
                                  : Icons.arrow_downward,
                              size: 12,
                              color: (skill['change'] as int) >= 0 
                                  ? Colors.green 
                                  : Colors.red,
                            ),
                            Text(
                              '${(skill['change'] as int).abs()}',
                              style: TextStyle(
                                fontSize: 11,
                                color: (skill['change'] as int) >= 0 
                                    ? Colors.green 
                                    : Colors.red,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  LinearProgressIndicator(
                    value: (skill['score'] as int) / 100,
                    backgroundColor: Colors.grey.shade200,
                    valueColor: AlwaysStoppedAnimation(_getScoreColor(skill['score'] as int)),
                  ),
                ],
              ),
            )),
          ],
        ),
      ),
    );
  }

  Color _getScoreColor(int score) {
    if (score >= 80) return Colors.green;
    if (score >= 60) return Colors.orange;
    return Colors.red;
  }

  Widget _buildImprovementAreas(ConversationIntelligenceProvider provider) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Areas for Improvement',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const Divider(),
            _buildImprovementItem(
              'Reduce Talk Time',
              'Average talk ratio is 65%. Aim for 40-60% to improve engagement.',
              Icons.mic_off,
              Colors.orange,
            ),
            _buildImprovementItem(
              'Ask More Questions',
              'Average 3 questions per call. Top performers ask 7-10.',
              Icons.help,
              Colors.blue,
            ),
            _buildImprovementItem(
              'Handle Objections Better',
              'Only 45% of objections are addressed effectively.',
              Icons.warning,
              Colors.red,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildImprovementItem(String title, String description, IconData icon, Color color) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: color.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(icon, color: color, size: 20),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: const TextStyle(fontWeight: FontWeight.w600)),
                Text(
                  description,
                  style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCoachingRecommendations(ConversationIntelligenceProvider provider) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.lightbulb, color: Colors.amber.shade700),
                const SizedBox(width: 8),
                const Text(
                  'AI Coaching Recommendations',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const Divider(),
            _buildRecommendation(
              'Practice Discovery Framework',
              'Focus on SPIN selling technique to improve questioning skills.',
              'View Training',
            ),
            _buildRecommendation(
              'Competitor Battle Cards',
              'Review updated battle cards for handling competitor objections.',
              'Open Cards',
            ),
            _buildRecommendation(
              'Call Review Session',
              'Schedule 1:1 with manager to review recent calls.',
              'Schedule',
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRecommendation(String title, String description, String action) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: const TextStyle(fontWeight: FontWeight.w600)),
                Text(
                  description,
                  style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
                ),
              ],
            ),
          ),
          TextButton(
            onPressed: () {},
            child: Text(action),
          ),
        ],
      ),
    );
  }

  void _showConversationDetail(dynamic conversation) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.8,
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
            Text(
              conversation['title'] ?? 'Conversation Details',
              style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text(
              '${conversation['rep_name']} • ${conversation['date']}',
              style: TextStyle(color: Colors.grey.shade600),
            ),
            const SizedBox(height: 24),
            // Add more detailed conversation analysis here
            const Text('Detailed analysis would be shown here...'),
          ],
        ),
      ),
    );
  }
}
