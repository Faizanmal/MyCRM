import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/utils/api_client.dart';
import '../../providers/advanced_providers.dart';
import '../../models/advanced_models.dart';
import '../../widgets/loading_indicator.dart';
import '../../widgets/empty_state.dart';

class AIInsightsScreen extends StatefulWidget {
  const AIInsightsScreen({super.key});

  @override
  State<AIInsightsScreen> createState() => _AIInsightsScreenState();
}

class _AIInsightsScreenState extends State<AIInsightsScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  late AIInsightsProvider _provider;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _provider = AIInsightsProvider(ApiClient());
    _loadData();
  }

  Future<void> _loadData() async {
    await Future.wait([
      _provider.loadChurnPredictions(),
      _provider.loadChurnStatistics(),
      _provider.loadNextBestActions(),
      _provider.loadGeneratedContent(),
    ]);
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
        body: NestedScrollView(
          headerSliverBuilder: (context, innerBoxIsScrolled) => [
            SliverAppBar(
              expandedHeight: 180,
              floating: false,
              pinned: true,
              flexibleSpace: FlexibleSpaceBar(
                title: const Text('AI Insights'),
                background: Container(
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                      colors: [
                        Colors.purple.shade700,
                        Colors.indigo.shade600,
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
                          Consumer<AIInsightsProvider>(
                            builder: (context, provider, _) {
                              final stats = provider.churnStatistics;
                              return Row(
                                children: [
                                  _buildStatCard(
                                    'Analyzed',
                                    '${stats?['total_analyzed'] ?? provider.churnPredictions.length}',
                                    Icons.analytics,
                                  ),
                                  const SizedBox(width: 12),
                                  _buildStatCard(
                                    'High Risk',
                                    '${stats?['high_risk_count'] ?? provider.churnPredictions.where((p) => p.riskLevel == 'high' || p.riskLevel == 'critical').length}',
                                    Icons.warning,
                                    color: Colors.orange,
                                  ),
                                  const SizedBox(width: 12),
                                  _buildStatCard(
                                    'Actions',
                                    '${provider.nextBestActions.length}',
                                    Icons.lightbulb,
                                  ),
                                ],
                              );
                            },
                          ),
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
                  Tab(text: 'Churn Risk'),
                  Tab(text: 'Actions'),
                  Tab(text: 'Content'),
                ],
              ),
            ),
          ],
          body: Consumer<AIInsightsProvider>(
            builder: (context, provider, _) {
              if (provider.isLoading) {
                return const LoadingIndicator(message: 'Loading AI insights...');
              }

              return RefreshIndicator(
                onRefresh: _loadData,
                child: TabBarView(
                  controller: _tabController,
                  children: [
                    _buildChurnTab(provider),
                    _buildActionsTab(provider),
                    _buildContentTab(provider),
                  ],
                ),
              );
            },
          ),
        ),
        floatingActionButton: Consumer<AIInsightsProvider>(
          builder: (context, provider, _) {
            return FloatingActionButton.extended(
              onPressed: () => _showGenerateContentDialog(context, provider),
              icon: const Icon(Icons.auto_awesome),
              label: const Text('Generate'),
              backgroundColor: Colors.purple,
            );
          },
        ),
      ),
    );
  }

  Widget _buildStatCard(String label, String value, IconData icon, {Color? color}) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.2),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Icon(icon, color: color ?? Colors.white, size: 18),
          const SizedBox(width: 8),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
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
    );
  }

  Widget _buildChurnTab(AIInsightsProvider provider) {
    if (provider.churnPredictions.isEmpty) {
      return EmptyState(
        icon: Icons.analytics_outlined,
        title: 'No Predictions Yet',
        subtitle: 'Run churn analysis to get predictions',
        action: ElevatedButton.icon(
          onPressed: provider.runBulkChurnPrediction,
          icon: const Icon(Icons.play_arrow),
          label: const Text('Analyze All'),
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: provider.churnPredictions.length,
      itemBuilder: (context, index) {
        final prediction = provider.churnPredictions[index];
        return _buildChurnCard(prediction);
      },
    );
  }

  Widget _buildChurnCard(ChurnPrediction prediction) {
    Color riskColor;
    switch (prediction.riskLevel) {
      case 'critical':
        riskColor = Colors.red;
        break;
      case 'high':
        riskColor = Colors.orange;
        break;
      case 'medium':
        riskColor = Colors.yellow.shade700;
        break;
      default:
        riskColor = Colors.green;
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
                  backgroundColor: riskColor.withValues(alpha: 0.2),
                  child: Text(
                    prediction.contact.name.isNotEmpty 
                        ? prediction.contact.name[0].toUpperCase() 
                        : '?',
                    style: TextStyle(color: riskColor),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        prediction.contact.name,
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                      Text(
                        prediction.contact.email,
                        style: TextStyle(color: Colors.grey.shade600),
                      ),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: riskColor.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: riskColor.withValues(alpha: 0.3)),
                  ),
                  child: Text(
                    prediction.riskLevel.toUpperCase(),
                    style: TextStyle(
                      color: riskColor,
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Churn Probability',
                        style: TextStyle(fontSize: 12),
                      ),
                      const SizedBox(height: 4),
                      LinearProgressIndicator(
                        value: prediction.churnProbability,
                        backgroundColor: Colors.grey.shade200,
                        valueColor: AlwaysStoppedAnimation<Color>(riskColor),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 16),
                Text(
                  '${(prediction.churnProbability * 100).toStringAsFixed(1)}%',
                  style: TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    color: riskColor,
                  ),
                ),
              ],
            ),
            if (prediction.recommendedActions.isNotEmpty) ...[
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.purple.shade50,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(Icons.lightbulb, color: Colors.purple.shade700, size: 18),
                        const SizedBox(width: 8),
                        Text(
                          'Recommended Actions',
                          style: TextStyle(
                            color: Colors.purple.shade700,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    ...prediction.recommendedActions.take(3).map((action) => Padding(
                      padding: const EdgeInsets.only(top: 4),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text('• '),
                          Expanded(child: Text(action)),
                        ],
                      ),
                    )),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildActionsTab(AIInsightsProvider provider) {
    if (provider.nextBestActions.isEmpty) {
      return const EmptyState(
        icon: Icons.lightbulb_outline,
        title: 'No Actions Suggested',
        subtitle: 'AI-recommended actions will appear here',
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: provider.nextBestActions.length,
      itemBuilder: (context, index) {
        final action = provider.nextBestActions[index];
        return _buildActionCard(action, provider);
      },
    );
  }

  Widget _buildActionCard(NextBestAction action, AIInsightsProvider provider) {
    Color priorityColor;
    switch (action.priority) {
      case 'urgent':
        priorityColor = Colors.red;
        break;
      case 'high':
        priorityColor = Colors.orange;
        break;
      case 'medium':
        priorityColor = Colors.yellow.shade700;
        break;
      default:
        priorityColor = Colors.blue;
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
                    color: priorityColor.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Icon(
                    _getActionIcon(action.actionType),
                    color: priorityColor,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        action.title,
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                      Text(
                        action.contact.name,
                        style: TextStyle(color: Colors.grey.shade600),
                      ),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: priorityColor.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    action.priority.toUpperCase(),
                    style: TextStyle(
                      color: priorityColor,
                      fontWeight: FontWeight.bold,
                      fontSize: 11,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(action.description),
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: Colors.blue.shade50,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                children: [
                  Icon(Icons.psychology, color: Colors.blue.shade700, size: 18),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      action.reasoning,
                      style: TextStyle(
                        color: Colors.blue.shade700,
                        fontSize: 13,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Text(
                  'Impact Score: ${(action.estimatedImpact * 100).toInt()}%',
                  style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
                ),
                const Spacer(),
                TextButton(
                  onPressed: () => provider.dismissAction(action.id),
                  child: const Text('Dismiss'),
                ),
                const SizedBox(width: 8),
                ElevatedButton(
                  onPressed: () => provider.completeAction(action.id),
                  child: const Text('Complete'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildContentTab(AIInsightsProvider provider) {
    if (provider.generatedContent.isEmpty) {
      return const EmptyState(
        icon: Icons.edit_note,
        title: 'No Content Generated',
        subtitle: 'Use AI to generate emails, posts, and more',
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: provider.generatedContent.length,
      itemBuilder: (context, index) {
        final content = provider.generatedContent[index];
        return _buildContentCard(content, provider);
      },
    );
  }

  Widget _buildContentCard(AIGeneratedContent content, AIInsightsProvider provider) {
    Color statusColor;
    switch (content.status) {
      case 'approved':
        statusColor = Colors.green;
        break;
      case 'rejected':
        statusColor = Colors.red;
        break;
      default:
        statusColor = Colors.orange;
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
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.purple.shade50,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Icon(
                    _getContentIcon(content.contentType),
                    color: Colors.purple.shade700,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        content.contentType.toUpperCase(),
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 14,
                        ),
                      ),
                      Text(
                        'Tone: ${content.tone} • ${content.length}',
                        style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
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
                    content.status.toUpperCase(),
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
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.grey.shade50,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.grey.shade200),
              ),
              child: Text(
                content.content,
                maxLines: 5,
                overflow: TextOverflow.ellipsis,
              ),
            ),
            const SizedBox(height: 12),
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                TextButton.icon(
                  onPressed: () => provider.regenerateContent(content.id),
                  icon: const Icon(Icons.refresh, size: 18),
                  label: const Text('Regenerate'),
                ),
                if (content.status == 'draft') ...[
                  const SizedBox(width: 8),
                  ElevatedButton.icon(
                    onPressed: () => provider.approveContent(content.id),
                    icon: const Icon(Icons.check, size: 18),
                    label: const Text('Approve'),
                  ),
                ],
              ],
            ),
          ],
        ),
      ),
    );
  }

  IconData _getActionIcon(String type) {
    switch (type.toLowerCase()) {
      case 'call':
        return Icons.phone;
      case 'email':
        return Icons.email;
      case 'meeting':
        return Icons.event;
      case 'follow_up':
        return Icons.follow_the_signs;
      default:
        return Icons.task_alt;
    }
  }

  IconData _getContentIcon(String type) {
    switch (type.toLowerCase()) {
      case 'email':
        return Icons.email;
      case 'social':
      case 'social_post':
        return Icons.share;
      case 'proposal':
        return Icons.description;
      default:
        return Icons.article;
    }
  }

  void _showGenerateContentDialog(BuildContext context, AIInsightsProvider provider) {
    String selectedType = 'email';
    String selectedTone = 'professional';
    String selectedLength = 'medium';
    final contextController = TextEditingController();

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => StatefulBuilder(
        builder: (context, setState) => Padding(
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
                  const Icon(Icons.auto_awesome, color: Colors.purple),
                  const SizedBox(width: 8),
                  const Text(
                    'Generate AI Content',
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
              const Text('Content Type'),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                children: ['email', 'social_post', 'proposal'].map((type) {
                  return ChoiceChip(
                    label: Text(type.replaceAll('_', ' ').toUpperCase()),
                    selected: selectedType == type,
                    onSelected: (_) => setState(() => selectedType = type),
                  );
                }).toList(),
              ),
              const SizedBox(height: 16),
              const Text('Tone'),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                children: ['professional', 'friendly', 'casual', 'formal'].map((tone) {
                  return ChoiceChip(
                    label: Text(tone.toUpperCase()),
                    selected: selectedTone == tone,
                    onSelected: (_) => setState(() => selectedTone = tone),
                  );
                }).toList(),
              ),
              const SizedBox(height: 16),
              const Text('Length'),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                children: ['short', 'medium', 'long'].map((length) {
                  return ChoiceChip(
                    label: Text(length.toUpperCase()),
                    selected: selectedLength == length,
                    onSelected: (_) => setState(() => selectedLength = length),
                  );
                }).toList(),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: contextController,
                decoration: const InputDecoration(
                  labelText: 'Context / Additional Info',
                  hintText: 'E.g., Product launch, follow-up after meeting...',
                  border: OutlineInputBorder(),
                ),
                maxLines: 2,
              ),
              const SizedBox(height: 16),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: () async {
                    Navigator.pop(context);
                    await provider.generateContent(
                      contentType: selectedType,
                      context: {
                        'description': contextController.text,
                      },
                      tone: selectedTone,
                      length: selectedLength,
                    );
                    _tabController.animateTo(2); // Switch to Content tab
                  },
                  icon: const Icon(Icons.auto_awesome),
                  label: const Text('Generate'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.purple,
                    padding: const EdgeInsets.symmetric(vertical: 12),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
