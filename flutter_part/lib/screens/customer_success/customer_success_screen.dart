import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/utils/api_client.dart';
import '../../providers/enterprise_providers.dart';
import '../../models/enterprise_models.dart';
import '../../widgets/loading_indicator.dart';
import '../../widgets/empty_state.dart';

class CustomerSuccessScreen extends StatefulWidget {
  const CustomerSuccessScreen({super.key});

  @override
  State<CustomerSuccessScreen> createState() => _CustomerSuccessScreenState();
}

class _CustomerSuccessScreenState extends State<CustomerSuccessScreen>
    with SingleTickerProviderStateMixin {
  late CustomerSuccessProvider _provider;
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _provider = CustomerSuccessProvider(ApiClient());
    _tabController = TabController(length: 4, vsync: this);
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
          title: const Text('Customer Success'),
          flexibleSpace: Container(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [Colors.teal.shade700, Colors.green.shade600],
              ),
            ),
          ),
          bottom: TabBar(
            controller: _tabController,
            indicatorColor: Colors.white,
            tabs: const [
              Tab(text: 'Dashboard', icon: Icon(Icons.dashboard)),
              Tab(text: 'Accounts', icon: Icon(Icons.business)),
              Tab(text: 'Renewals', icon: Icon(Icons.autorenew)),
              Tab(text: 'Health', icon: Icon(Icons.health_and_safety)),
            ],
          ),
        ),
        body: Consumer<CustomerSuccessProvider>(
          builder: (context, provider, _) {
            if (provider.isLoading) {
              return const LoadingIndicator(message: 'Loading customer success data...');
            }

            return TabBarView(
              controller: _tabController,
              children: [
                _buildDashboardTab(provider),
                _buildAccountsTab(provider),
                _buildRenewalsTab(provider),
                _buildHealthTab(provider),
              ],
            );
          },
        ),
      ),
    );
  }

  Widget _buildDashboardTab(CustomerSuccessProvider provider) {
    final dashboard = provider.dashboard ?? {};
    
    return RefreshIndicator(
      onRefresh: () => provider.loadDashboard(),
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildMetricsRow(dashboard),
            const SizedBox(height: 24),
            _buildChurnRisksSection(provider),
            const SizedBox(height: 24),
            _buildUpcomingRenewalsSection(provider),
          ],
        ),
      ),
    );
  }

  Widget _buildMetricsRow(Map<String, dynamic> dashboard) {
    return GridView.count(
      crossAxisCount: 2,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisSpacing: 12,
      mainAxisSpacing: 12,
      childAspectRatio: 1.5,
      children: [
        _buildMetricCard(
          'Total Accounts',
          '${dashboard['total_accounts'] ?? 0}',
          Icons.business,
          Colors.blue,
        ),
        _buildMetricCard(
          'Avg Health Score',
          '${dashboard['avg_health_score'] ?? 0}%',
          Icons.health_and_safety,
          Colors.green,
        ),
        _buildMetricCard(
          'At-Risk Accounts',
          '${dashboard['at_risk_count'] ?? 0}',
          Icons.warning,
          Colors.orange,
        ),
        _buildMetricCard(
          'NPS Score',
          '${dashboard['nps_score'] ?? 0}',
          Icons.thumb_up,
          Colors.purple,
        ),
      ],
    );
  }

  Widget _buildMetricCard(String title, String value, IconData icon, Color color) {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
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
              title,
              style: TextStyle(
                color: Colors.grey.shade600,
                fontSize: 12,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildChurnRisksSection(CustomerSuccessProvider provider) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Text(
              'Churn Risks',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            TextButton(
              onPressed: () => _tabController.animateTo(3),
              child: const Text('View All'),
            ),
          ],
        ),
        const SizedBox(height: 12),
        if (provider.churnRisks.isEmpty)
          _buildEmptyCard('No churn risks detected', Icons.check_circle)
        else
          ...provider.churnRisks.take(3).map((risk) => _buildChurnRiskCard(risk)),
      ],
    );
  }

  Widget _buildChurnRiskCard(ChurnRisk risk) {
    Color riskColor;
    switch (risk.riskLevel) {
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
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: riskColor.withValues(alpha: 0.2),
          child: Icon(Icons.warning, color: riskColor),
        ),
        title: Text(risk.accountName),
        subtitle: Text('Risk Score: ${(risk.riskScore * 100).toStringAsFixed(0)}%'),
        trailing: Chip(
          label: Text(
            risk.riskLevel.toUpperCase(),
            style: const TextStyle(color: Colors.white, fontSize: 10),
          ),
          backgroundColor: riskColor,
        ),
        onTap: () => _showRiskDetails(risk),
      ),
    );
  }

  Widget _buildUpcomingRenewalsSection(CustomerSuccessProvider provider) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Text(
              'Upcoming Renewals',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            TextButton(
              onPressed: () => _tabController.animateTo(2),
              child: const Text('View All'),
            ),
          ],
        ),
        const SizedBox(height: 12),
        if (provider.upcomingRenewals.isEmpty)
          _buildEmptyCard('No upcoming renewals', Icons.event)
        else
          ...provider.upcomingRenewals.take(3).map((renewal) => _buildRenewalCard(renewal)),
      ],
    );
  }

  Widget _buildRenewalCard(Renewal renewal) {
    final daysUntil = renewal.renewalDate.difference(DateTime.now()).inDays;
    Color urgencyColor = daysUntil <= 7
        ? Colors.red
        : daysUntil <= 30
            ? Colors.orange
            : Colors.green;

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: urgencyColor.withValues(alpha: 0.2),
          child: Icon(Icons.autorenew, color: urgencyColor),
        ),
        title: Text(renewal.accountName),
        subtitle: Text('\$${renewal.amount.toStringAsFixed(0)} • In $daysUntil days'),
        trailing: Text(
          '${(renewal.probability * 100).toStringAsFixed(0)}%',
          style: TextStyle(
            fontWeight: FontWeight.bold,
            color: Colors.green.shade700,
          ),
        ),
      ),
    );
  }

  Widget _buildEmptyCard(String message, IconData icon) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, color: Colors.grey),
            const SizedBox(width: 12),
            Text(message, style: TextStyle(color: Colors.grey.shade600)),
          ],
        ),
      ),
    );
  }

  Widget _buildAccountsTab(CustomerSuccessProvider provider) {
    if (provider.accounts.isEmpty) {
      return const EmptyState(
        icon: Icons.business_outlined,
        title: 'No Accounts',
        subtitle: 'Customer accounts will appear here',
      );
    }

    return RefreshIndicator(
      onRefresh: () => provider.loadAccounts(),
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: provider.accounts.length,
        itemBuilder: (context, index) {
          final account = provider.accounts[index];
          return _buildAccountCard(account);
        },
      ),
    );
  }

  Widget _buildAccountCard(CustomerAccount account) {
    Color healthColor;
    switch (account.healthColor) {
      case 'green':
        healthColor = Colors.green;
        break;
      case 'yellow':
        healthColor = Colors.yellow.shade700;
        break;
      case 'orange':
        healthColor = Colors.orange;
        break;
      default:
        healthColor = Colors.red;
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
                  child: Text(
                    account.name,
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                    ),
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: healthColor.withValues(alpha: 0.2),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.favorite, size: 14, color: healthColor),
                      const SizedBox(width: 4),
                      Text(
                        '${account.healthScore}%',
                        style: TextStyle(
                          color: healthColor,
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
                _buildAccountInfo(Icons.attach_money, '\$${account.annualValue.toStringAsFixed(0)}'),
                const SizedBox(width: 24),
                _buildAccountInfo(Icons.workspace_premium, account.tier.toUpperCase()),
                const SizedBox(width: 24),
                _buildAccountInfo(Icons.circle, account.status.toUpperCase()),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAccountInfo(IconData icon, String text) {
    return Row(
      children: [
        Icon(icon, size: 16, color: Colors.grey),
        const SizedBox(width: 4),
        Text(
          text,
          style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
        ),
      ],
    );
  }

  Widget _buildRenewalsTab(CustomerSuccessProvider provider) {
    if (provider.renewals.isEmpty && provider.upcomingRenewals.isEmpty) {
      return const EmptyState(
        icon: Icons.autorenew,
        title: 'No Renewals',
        subtitle: 'Renewal information will appear here',
      );
    }

    final allRenewals = [...provider.upcomingRenewals, ...provider.renewals]
        .toSet()
        .toList();

    return RefreshIndicator(
      onRefresh: () => Future.wait([
        provider.loadRenewals(),
        provider.loadUpcomingRenewals(),
      ]),
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: allRenewals.length,
        itemBuilder: (context, index) {
          return _buildRenewalCard(allRenewals[index]);
        },
      ),
    );
  }

  Widget _buildHealthTab(CustomerSuccessProvider provider) {
    return RefreshIndicator(
      onRefresh: () => Future.wait([
        provider.loadHealthScores(),
        provider.loadChurnRisks(),
      ]),
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Health Overview',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            _buildHealthDistribution(provider),
            const SizedBox(height: 24),
            const Text(
              'At-Risk Accounts',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            if (provider.churnRisks.isEmpty)
              _buildEmptyCard('All accounts are healthy!', Icons.check_circle)
            else
              ...provider.churnRisks.map((risk) => _buildChurnRiskCard(risk)),
          ],
        ),
      ),
    );
  }

  Widget _buildHealthDistribution(CustomerSuccessProvider provider) {
    final accounts = provider.accounts;
    final healthy = accounts.where((a) => a.healthScore >= 80).length;
    final warning = accounts.where((a) => a.healthScore >= 60 && a.healthScore < 80).length;
    final atRisk = accounts.where((a) => a.healthScore >= 40 && a.healthScore < 60).length;
    final critical = accounts.where((a) => a.healthScore < 40).length;

    return Row(
      children: [
        Expanded(child: _buildHealthStat('Healthy', healthy, Colors.green)),
        Expanded(child: _buildHealthStat('Warning', warning, Colors.yellow.shade700)),
        Expanded(child: _buildHealthStat('At Risk', atRisk, Colors.orange)),
        Expanded(child: _buildHealthStat('Critical', critical, Colors.red)),
      ],
    );
  }

  Widget _buildHealthStat(String label, int count, Color color) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                color: color.withValues(alpha: 0.2),
                shape: BoxShape.circle,
              ),
              child: Center(
                child: Text(
                  '$count',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: color,
                  ),
                ),
              ),
            ),
            const SizedBox(height: 8),
            Text(
              label,
              style: TextStyle(
                fontSize: 11,
                color: Colors.grey.shade600,
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _showRiskDetails(ChurnRisk risk) {
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
            Text(
              risk.accountName,
              style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text(
              'Risk Score: ${(risk.riskScore * 100).toStringAsFixed(0)}%',
              style: TextStyle(color: Colors.grey.shade600),
            ),
            const SizedBox(height: 24),
            const Text(
              'Risk Factors',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            ...risk.riskFactors.map((factor) => Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Row(
                children: [
                  const Icon(Icons.warning_amber, color: Colors.orange, size: 20),
                  const SizedBox(width: 12),
                  Expanded(child: Text(factor)),
                ],
              ),
            )),
            const SizedBox(height: 24),
            const Text(
              'Recommended Actions',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            ...risk.recommendedActions.map((action) => Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Row(
                children: [
                  const Icon(Icons.lightbulb_outline, color: Colors.green, size: 20),
                  const SizedBox(width: 12),
                  Expanded(child: Text(action)),
                ],
              ),
            )),
          ],
        ),
      ),
    );
  }
}
