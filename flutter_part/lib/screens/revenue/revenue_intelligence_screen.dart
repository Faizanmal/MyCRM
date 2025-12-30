import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/utils/api_client.dart';
import '../../providers/advanced_providers.dart';
import '../../models/advanced_models.dart';
import '../../widgets/loading_indicator.dart';
import '../../widgets/empty_state.dart';

class RevenueIntelligenceScreen extends StatefulWidget {
  const RevenueIntelligenceScreen({super.key});

  @override
  State<RevenueIntelligenceScreen> createState() => _RevenueIntelligenceScreenState();
}

class _RevenueIntelligenceScreenState extends State<RevenueIntelligenceScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  late RevenueIntelligenceProvider _provider;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _provider = RevenueIntelligenceProvider(ApiClient());
    _loadData();
  }

  Future<void> _loadData() async {
    await _provider.loadAll();
    await _provider.loadWinLossAnalysis();
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
              expandedHeight: 200,
              floating: false,
              pinned: true,
              flexibleSpace: FlexibleSpaceBar(
                title: const Text('Revenue Intelligence'),
                background: Container(
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                      colors: [
                        Colors.green.shade700,
                        Colors.teal.shade600,
                      ],
                    ),
                  ),
                  child: SafeArea(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Consumer<RevenueIntelligenceProvider>(
                        builder: (context, provider, _) {
                          return Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const SizedBox(height: 40),
                              _buildOverviewStats(provider),
                            ],
                          );
                        },
                      ),
                    ),
                  ),
                ),
              ),
              bottom: TabBar(
                controller: _tabController,
                indicatorColor: Colors.white,
                tabs: const [
                  Tab(text: 'Targets'),
                  Tab(text: 'Deal Scores'),
                  Tab(text: 'Risk Alerts'),
                ],
              ),
            ),
          ],
          body: Consumer<RevenueIntelligenceProvider>(
            builder: (context, provider, _) {
              if (provider.isLoading) {
                return const LoadingIndicator(message: 'Loading revenue data...');
              }

              return RefreshIndicator(
                onRefresh: _loadData,
                child: TabBarView(
                  controller: _tabController,
                  children: [
                    _buildTargetsTab(provider),
                    _buildDealScoresTab(provider),
                    _buildRiskAlertsTab(provider),
                  ],
                ),
              );
            },
          ),
        ),
        floatingActionButton: FloatingActionButton.extended(
          onPressed: () => _provider.bulkScoreDeals(),
          icon: const Icon(Icons.refresh),
          label: const Text('Score Deals'),
          backgroundColor: Colors.green,
        ),
      ),
    );
  }

  Widget _buildOverviewStats(RevenueIntelligenceProvider provider) {
    final totalTarget = provider.targets.fold<double>(
      0,
      (sum, t) => sum + t.targetAmount,
    );
    final totalCurrent = provider.targets.fold<double>(
      0,
      (sum, t) => sum + t.currentAmount,
    );
    final overallProgress = totalTarget > 0 ? totalCurrent / totalTarget : 0.0;

    return Column(
      children: [
        Row(
          children: [
            Expanded(
              child: _buildStatCard(
                '\$${_formatNumber(totalCurrent)}',
                'Revenue',
                Icons.attach_money,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildStatCard(
                '\$${_formatNumber(totalTarget)}',
                'Target',
                Icons.flag,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildStatCard(
                '${provider.activeAlerts.length}',
                'Alerts',
                Icons.warning,
                color: provider.activeAlerts.isNotEmpty ? Colors.orange : null,
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              child: LinearProgressIndicator(
                value: overallProgress,
                backgroundColor: Colors.white.withValues(alpha: 0.3),
                valueColor: const AlwaysStoppedAnimation<Color>(Colors.white),
                borderRadius: BorderRadius.circular(4),
                minHeight: 8,
              ),
            ),
            const SizedBox(width: 12),
            Text(
              '${(overallProgress * 100).toStringAsFixed(0)}%',
              style: const TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildStatCard(String value, String label, IconData icon, {Color? color}) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.2),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        children: [
          Icon(icon, color: color ?? Colors.white, size: 20),
          const SizedBox(height: 4),
          Text(
            value,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 14,
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
    );
  }

  Widget _buildTargetsTab(RevenueIntelligenceProvider provider) {
    if (provider.targets.isEmpty) {
      return const EmptyState(
        icon: Icons.flag_outlined,
        title: 'No Revenue Targets',
        subtitle: 'Set targets to track your progress',
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: provider.targets.length,
      itemBuilder: (context, index) {
        return _buildTargetCard(provider.targets[index]);
      },
    );
  }

  Widget _buildTargetCard(RevenueTarget target) {
    Color statusColor;
    switch (target.status) {
      case 'achieved':
        statusColor = Colors.green;
        break;
      case 'at_risk':
        statusColor = Colors.orange;
        break;
      case 'behind':
        statusColor = Colors.red;
        break;
      default:
        statusColor = Colors.blue;
    }

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
                  target.period.toUpperCase(),
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: statusColor.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    target.status.replaceAll('_', ' ').toUpperCase(),
                    style: TextStyle(
                      color: statusColor,
                      fontWeight: FontWeight.bold,
                      fontSize: 11,
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
                      Text(
                        '\$${_formatNumber(target.currentAmount)}',
                        style: const TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(
                        'of \$${_formatNumber(target.targetAmount)}',
                        style: TextStyle(color: Colors.grey.shade600),
                      ),
                    ],
                  ),
                ),
                SizedBox(
                  width: 80,
                  height: 80,
                  child: Stack(
                    children: [
                      Center(
                        child: SizedBox(
                          width: 70,
                          height: 70,
                          child: CircularProgressIndicator(
                            value: target.progressPercent,
                            strokeWidth: 8,
                            backgroundColor: Colors.grey.shade200,
                            valueColor: AlwaysStoppedAnimation<Color>(statusColor),
                          ),
                        ),
                      ),
                      Center(
                        child: Text(
                          '${(target.progressPercent * 100).toStringAsFixed(0)}%',
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 16,
                          ),
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

  Widget _buildDealScoresTab(RevenueIntelligenceProvider provider) {
    if (provider.dealScores.isEmpty) {
      return EmptyState(
        icon: Icons.analytics_outlined,
        title: 'No Deal Scores',
        subtitle: 'Score your deals to get insights',
        action: ElevatedButton.icon(
          onPressed: () => provider.bulkScoreDeals(),
          icon: const Icon(Icons.refresh),
          label: const Text('Score All Deals'),
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: provider.dealScores.length,
      itemBuilder: (context, index) {
        return _buildDealScoreCard(provider.dealScores[index]);
      },
    );
  }

  Widget _buildDealScoreCard(DealScore dealScore) {
    Color riskColor;
    switch (dealScore.riskLevel) {
      case 'low':
        riskColor = Colors.green;
        break;
      case 'medium':
        riskColor = Colors.orange;
        break;
      case 'high':
        riskColor = Colors.red;
        break;
      default:
        riskColor = Colors.grey;
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
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        dealScore.opportunityName,
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 8,
                              vertical: 2,
                            ),
                            decoration: BoxDecoration(
                              color: riskColor.withValues(alpha: 0.1),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Text(
                              '${dealScore.riskLevel.toUpperCase()} RISK',
                              style: TextStyle(
                                color: riskColor,
                                fontSize: 10,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
                Container(
                  width: 60,
                  height: 60,
                  decoration: BoxDecoration(
                    color: _getScoreColor(dealScore.score).withValues(alpha: 0.1),
                    shape: BoxShape.circle,
                  ),
                  child: Center(
                    child: Text(
                      '${dealScore.score}',
                      style: TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                        color: _getScoreColor(dealScore.score),
                      ),
                    ),
                  ),
                ),
              ],
            ),
            if (dealScore.recommendations.isNotEmpty) ...[
              const Divider(height: 24),
              const Text(
                'Recommendations',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              ...dealScore.recommendations.take(3).map((rec) => Padding(
                padding: const EdgeInsets.only(bottom: 4),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Icon(Icons.lightbulb, size: 16, color: Colors.amber.shade700),
                    const SizedBox(width: 8),
                    Expanded(child: Text(rec, style: const TextStyle(fontSize: 13))),
                  ],
                ),
              )),
            ],
          ],
        ),
      ),
    );
  }

  Color _getScoreColor(int score) {
    if (score >= 80) return Colors.green;
    if (score >= 60) return Colors.blue;
    if (score >= 40) return Colors.orange;
    return Colors.red;
  }

  Widget _buildRiskAlertsTab(RevenueIntelligenceProvider provider) {
    if (provider.riskAlerts.isEmpty) {
      return const EmptyState(
        icon: Icons.check_circle_outline,
        title: 'No Risk Alerts',
        subtitle: 'Your deals are healthy!',
      );
    }

    final activeAlerts = provider.activeAlerts;
    final resolvedAlerts = provider.riskAlerts.where((a) => a.isResolved).toList();

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        if (activeAlerts.isNotEmpty) ...[
          _buildSectionHeader('Active Alerts', Icons.warning, Colors.orange),
          ...activeAlerts.map((alert) => _buildAlertCard(alert, provider)),
        ],
        if (resolvedAlerts.isNotEmpty) ...[
          _buildSectionHeader('Resolved', Icons.check_circle, Colors.green),
          ...resolvedAlerts.map((alert) => _buildAlertCard(alert, provider)),
        ],
      ],
    );
  }

  Widget _buildSectionHeader(String title, IconData icon, Color color) {
    return Padding(
      padding: const EdgeInsets.only(top: 8, bottom: 12),
      child: Row(
        children: [
          Icon(icon, color: color, size: 20),
          const SizedBox(width: 8),
          Text(
            title,
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAlertCard(DealRiskAlert alert, RevenueIntelligenceProvider provider) {
    Color severityColor;
    switch (alert.severity) {
      case 'high':
        severityColor = Colors.red;
        break;
      case 'medium':
        severityColor = Colors.orange;
        break;
      default:
        severityColor = Colors.yellow.shade700;
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
                    color: severityColor.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Icon(
                    Icons.warning_amber,
                    color: severityColor,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        alert.alertType.replaceAll('_', ' ').toUpperCase(),
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(
                        alert.message,
                        style: TextStyle(color: Colors.grey.shade600),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: severityColor.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    alert.severity.toUpperCase(),
                    style: TextStyle(
                      color: severityColor,
                      fontWeight: FontWeight.bold,
                      fontSize: 10,
                    ),
                  ),
                ),
              ],
            ),
            if (!alert.isResolved) ...[
              const Divider(height: 24),
              Row(
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  if (!alert.isAcknowledged)
                    TextButton(
                      onPressed: () => provider.acknowledgeAlert(alert.id),
                      child: const Text('Acknowledge'),
                    ),
                  const SizedBox(width: 8),
                  ElevatedButton(
                    onPressed: () => _showResolveDialog(alert, provider),
                    child: const Text('Resolve'),
                  ),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }

  void _showResolveDialog(DealRiskAlert alert, RevenueIntelligenceProvider provider) {
    final notesController = TextEditingController();

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Resolve Alert'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text('Add resolution notes:'),
            const SizedBox(height: 12),
            TextField(
              controller: notesController,
              decoration: const InputDecoration(
                border: OutlineInputBorder(),
                hintText: 'What did you do to resolve this?',
              ),
              maxLines: 3,
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              // Resolve alert with notes
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Alert resolved')),
              );
            },
            child: const Text('Resolve'),
          ),
        ],
      ),
    );
  }

  String _formatNumber(double number) {
    if (number >= 1000000) {
      return '${(number / 1000000).toStringAsFixed(1)}M';
    } else if (number >= 1000) {
      return '${(number / 1000).toStringAsFixed(1)}K';
    }
    return number.toStringAsFixed(0);
  }
}
