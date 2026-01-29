import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/utils/api_client.dart';
import '../../providers/enterprise_providers.dart';
import '../../models/enterprise_models.dart';

class ESGReportingScreen extends StatefulWidget {
  const ESGReportingScreen({super.key});

  @override
  State<ESGReportingScreen> createState() => _ESGReportingScreenState();
}

class _ESGReportingScreenState extends State<ESGReportingScreen>
    with SingleTickerProviderStateMixin {
  late ESGProvider _provider;
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _provider = ESGProvider(ApiClient());
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
          title: const Text('ESG Reporting'),
          flexibleSpace: Container(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [Colors.green.shade700, Colors.teal.shade500],
              ),
            ),
          ),
          bottom: TabBar(
            controller: _tabController,
            indicatorColor: Colors.white,
            isScrollable: true,
            tabs: const [
              Tab(text: 'Overview', icon: Icon(Icons.dashboard)),
              Tab(text: 'Environmental', icon: Icon(Icons.eco)),
              Tab(text: 'Social', icon: Icon(Icons.people)),
              Tab(text: 'Governance', icon: Icon(Icons.gavel)),
            ],
          ),
        ),
        body: Consumer<ESGProvider>(
          builder: (context, provider, _) {
            return TabBarView(
              controller: _tabController,
              children: [
                _buildOverviewTab(provider),
                _buildEnvironmentalTab(provider),
                _buildSocialTab(provider),
                _buildGovernanceTab(provider),
              ],
            );
          },
        ),
        floatingActionButton: FloatingActionButton.extended(
          onPressed: _showAddMetricDialog,
          backgroundColor: Colors.green.shade700,
          icon: const Icon(Icons.add),
          label: const Text('Add Metric'),
        ),
      ),
    );
  }

  Widget _buildOverviewTab(ESGProvider provider) {
    return RefreshIndicator(
      onRefresh: _loadData,
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildESGScoreCard(provider),
            const SizedBox(height: 20),
            _buildCategoryCards(provider),
            const SizedBox(height: 20),
            _buildRecentMetrics(provider),
            const SizedBox(height: 20),
            _buildComplianceStatus(),
          ],
        ),
      ),
    );
  }

  Widget _buildESGScoreCard(ESGProvider provider) {
    final envScore = _calculateCategoryScore(provider, 'environmental');
    final socScore = _calculateCategoryScore(provider, 'social');
    final govScore = _calculateCategoryScore(provider, 'governance');
    final overallScore = (envScore + socScore + govScore) / 3;

    return Card(
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.all(24),
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: [Colors.green.shade700, Colors.teal.shade500],
          ),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Column(
          children: [
            const Text(
              'Overall ESG Score',
              style: TextStyle(color: Colors.white70, fontSize: 16),
            ),
            const SizedBox(height: 16),
            Stack(
              alignment: Alignment.center,
              children: [
                SizedBox(
                  width: 140,
                  height: 140,
                  child: CircularProgressIndicator(
                    value: overallScore / 100,
                    strokeWidth: 12,
                    backgroundColor: Colors.white24,
                    valueColor: const AlwaysStoppedAnimation(Colors.white),
                  ),
                ),
                Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      overallScore.toStringAsFixed(0),
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 48,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const Text(
                      'out of 100',
                      style: TextStyle(color: Colors.white70),
                    ),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 20),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildMiniScore('E', envScore, Colors.green.shade200),
                _buildMiniScore('S', socScore, Colors.blue.shade200),
                _buildMiniScore('G', govScore, Colors.purple.shade200),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMiniScore(String label, double score, Color color) {
    return Column(
      children: [
        CircleAvatar(
          backgroundColor: color,
          radius: 24,
          child: Text(
            score.toStringAsFixed(0),
            style: const TextStyle(
              color: Colors.black87,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        const SizedBox(height: 4),
        Text(label, style: const TextStyle(color: Colors.white70)),
      ],
    );
  }

  double _calculateCategoryScore(ESGProvider provider, String category) {
    final metrics = provider.metrics.where((m) => m.category == category).toList();
    if (metrics.isEmpty) return 75.0; // Default score
    return metrics.map((m) => m.score).reduce((a, b) => a + b) / metrics.length;
  }

  Widget _buildCategoryCards(ESGProvider provider) {
    return Row(
      children: [
        Expanded(
          child: _buildCategoryCard(
            'Environmental',
            Icons.eco,
            Colors.green,
            provider.metrics.where((m) => m.category == 'environmental').length,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildCategoryCard(
            'Social',
            Icons.people,
            Colors.blue,
            provider.metrics.where((m) => m.category == 'social').length,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildCategoryCard(
            'Governance',
            Icons.gavel,
            Colors.purple,
            provider.metrics.where((m) => m.category == 'governance').length,
          ),
        ),
      ],
    );
  }

  Widget _buildCategoryCard(String title, IconData icon, Color color, int count) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Icon(icon, color: color, size: 32),
            const SizedBox(height: 8),
            Text(
              count.toString(),
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
            Text(
              'Metrics',
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey.shade600,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRecentMetrics(ESGProvider provider) {
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
                  'Recent Metrics',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                TextButton(
                  onPressed: () {},
                  child: const Text('View All'),
                ),
              ],
            ),
            const Divider(),
            if (provider.metrics.isEmpty)
              const Padding(
                padding: EdgeInsets.all(20),
                child: Center(child: Text('No metrics recorded yet')),
              )
            else
              ...provider.metrics.take(5).map((metric) => _buildMetricTile(metric)),
          ],
        ),
      ),
    );
  }

  Widget _buildMetricTile(ESGMetric metric) {
    final color = _getCategoryColor(metric.category);
    
    return ListTile(
      contentPadding: EdgeInsets.zero,
      leading: CircleAvatar(
        backgroundColor: color.withValues(alpha: 0.2),
        child: Icon(_getCategoryIcon(metric.category), color: color, size: 20),
      ),
      title: Text(metric.name),
      subtitle: Text(metric.category.toUpperCase()),
      trailing: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          Text(
            '${metric.value} ${metric.unit}',
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
          Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                metric.trend > 0 ? Icons.trending_up : 
                metric.trend < 0 ? Icons.trending_down : Icons.trending_flat,
                size: 16,
                color: metric.trendIsPositive ? Colors.green : Colors.red,
              ),
              Text(
                '${metric.trend.abs().toStringAsFixed(1)}%',
                style: TextStyle(
                  fontSize: 12,
                  color: metric.trendIsPositive ? Colors.green : Colors.red,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildComplianceStatus() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Compliance Status',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const Divider(),
            _buildComplianceItem('UN SDG Alignment', true, '14/17 goals aligned'),
            _buildComplianceItem('GRI Standards', true, 'Fully compliant'),
            _buildComplianceItem('SASB Framework', true, 'Industry metrics tracked'),
            _buildComplianceItem('TCFD Recommendations', false, '3 items pending'),
            _buildComplianceItem('EU Taxonomy', false, 'In progress'),
          ],
        ),
      ),
    );
  }

  Widget _buildComplianceItem(String framework, bool compliant, String detail) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Icon(
            compliant ? Icons.check_circle : Icons.pending,
            color: compliant ? Colors.green : Colors.orange,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(framework, style: const TextStyle(fontWeight: FontWeight.w500)),
                Text(detail, style: TextStyle(color: Colors.grey.shade600, fontSize: 12)),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEnvironmentalTab(ESGProvider provider) {
    final envMetrics = provider.metrics.where((m) => m.category == 'environmental').toList();

    return RefreshIndicator(
      onRefresh: _loadData,
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildCarbonFootprint(),
            const SizedBox(height: 20),
            _buildEnvironmentalMetrics(envMetrics),
            const SizedBox(height: 20),
            _buildEmissionsBreakdown(),
          ],
        ),
      ),
    );
  }

  Widget _buildCarbonFootprint() {
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
                    color: Colors.green.shade50,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Icon(Icons.co2, color: Colors.green.shade700, size: 32),
                ),
                const SizedBox(width: 16),
                const Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Carbon Footprint',
                        style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                      ),
                      Text('Annual CO2 equivalent emissions'),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),
            Row(
              children: [
                Expanded(child: _buildEmissionCard('Scope 1', '245 tCO2e', Colors.red)),
                const SizedBox(width: 12),
                Expanded(child: _buildEmissionCard('Scope 2', '1,230 tCO2e', Colors.orange)),
                const SizedBox(width: 12),
                Expanded(child: _buildEmissionCard('Scope 3', '4,560 tCO2e', Colors.amber)),
              ],
            ),
            const SizedBox(height: 20),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text('Net Zero Target Progress'),
                Text(
                  '42%',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: Colors.green.shade700,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            LinearProgressIndicator(
              value: 0.42,
              backgroundColor: Colors.green.shade100,
              valueColor: AlwaysStoppedAnimation(Colors.green.shade700),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEmissionCard(String scope, String value, Color color) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withValues(alpha: 0.3)),
      ),
      child: Column(
        children: [
          Text(scope, style: TextStyle(color: color, fontSize: 12)),
          const SizedBox(height: 4),
          Text(
            value,
            style: TextStyle(
              fontWeight: FontWeight.bold,
              color: color,
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEnvironmentalMetrics(List<ESGMetric> metrics) {
    if (metrics.isEmpty) {
      return Card(
        child: Padding(
          padding: const EdgeInsets.all(40),
          child: Center(
            child: Column(
              children: [
                Icon(Icons.eco_outlined, size: 48, color: Colors.grey.shade400),
                const SizedBox(height: 16),
                const Text('No environmental metrics recorded'),
              ],
            ),
          ),
        ),
      );
    }

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Environmental Metrics',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const Divider(),
            ...metrics.map((m) => _buildMetricTile(m)),
          ],
        ),
      ),
    );
  }

  Widget _buildEmissionsBreakdown() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Emissions by Source',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const Divider(),
            _buildEmissionSource('Electricity', 0.35, '2,110 tCO2e'),
            _buildEmissionSource('Business Travel', 0.25, '1,508 tCO2e'),
            _buildEmissionSource('Supply Chain', 0.22, '1,326 tCO2e'),
            _buildEmissionSource('Fleet', 0.12, '724 tCO2e'),
            _buildEmissionSource('Other', 0.06, '362 tCO2e'),
          ],
        ),
      ),
    );
  }

  Widget _buildEmissionSource(String source, double percentage, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(source),
              Text(value, style: const TextStyle(fontWeight: FontWeight.w500)),
            ],
          ),
          const SizedBox(height: 4),
          LinearProgressIndicator(
            value: percentage,
            backgroundColor: Colors.grey.shade200,
            valueColor: AlwaysStoppedAnimation(Colors.green.shade600),
          ),
        ],
      ),
    );
  }

  Widget _buildSocialTab(ESGProvider provider) {
    final socialMetrics = provider.metrics.where((m) => m.category == 'social').toList();

    return RefreshIndicator(
      onRefresh: _loadData,
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildDiversityCard(),
            const SizedBox(height: 20),
            _buildWorkforceMetrics(),
            const SizedBox(height: 20),
            _buildSocialMetricsList(socialMetrics),
          ],
        ),
      ),
    );
  }

  Widget _buildDiversityCard() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Diversity & Inclusion',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 20),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildDiversityStat('Women in Leadership', '38%', Icons.woman),
                _buildDiversityStat('Diverse Workforce', '42%', Icons.diversity_3),
                _buildDiversityStat('Pay Equity Ratio', '0.97', Icons.balance),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDiversityStat(String label, String value, IconData icon) {
    return Column(
      children: [
        CircleAvatar(
          backgroundColor: Colors.blue.shade50,
          radius: 28,
          child: Icon(icon, color: Colors.blue),
        ),
        const SizedBox(height: 8),
        Text(
          value,
          style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        Text(
          label,
          style: TextStyle(fontSize: 11, color: Colors.grey.shade600),
          textAlign: TextAlign.center,
        ),
      ],
    );
  }

  Widget _buildWorkforceMetrics() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Workforce Metrics',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const Divider(),
            _buildWorkforceRow('Employee Satisfaction', '4.2/5.0', Icons.sentiment_satisfied),
            _buildWorkforceRow('Training Hours per Employee', '42 hrs', Icons.school),
            _buildWorkforceRow('Voluntary Turnover Rate', '8.5%', Icons.exit_to_app),
            _buildWorkforceRow('Health & Safety Incidents', '2', Icons.health_and_safety),
            _buildWorkforceRow('Community Investment', '\$1.2M', Icons.volunteer_activism),
          ],
        ),
      ),
    );
  }

  Widget _buildWorkforceRow(String label, String value, IconData icon) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Icon(icon, color: Colors.blue, size: 24),
          const SizedBox(width: 12),
          Expanded(child: Text(label)),
          Text(value, style: const TextStyle(fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }

  Widget _buildSocialMetricsList(List<ESGMetric> metrics) {
    if (metrics.isEmpty) {
      return Card(
        child: Padding(
          padding: const EdgeInsets.all(40),
          child: Center(
            child: Column(
              children: [
                Icon(Icons.people_outline, size: 48, color: Colors.grey.shade400),
                const SizedBox(height: 16),
                const Text('No social metrics recorded'),
              ],
            ),
          ),
        ),
      );
    }

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Social Metrics',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const Divider(),
            ...metrics.map((m) => _buildMetricTile(m)),
          ],
        ),
      ),
    );
  }

  Widget _buildGovernanceTab(ESGProvider provider) {
    final govMetrics = provider.metrics.where((m) => m.category == 'governance').toList();

    return RefreshIndicator(
      onRefresh: _loadData,
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildBoardComposition(),
            const SizedBox(height: 20),
            _buildEthicsCompliance(),
            const SizedBox(height: 20),
            _buildGovernanceMetricsList(govMetrics),
          ],
        ),
      ),
    );
  }

  Widget _buildBoardComposition() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Board Composition',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 20),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildBoardStat('Board Size', '9', Icons.groups),
                _buildBoardStat('Independent', '67%', Icons.verified_user),
                _buildBoardStat('Women', '33%', Icons.woman),
                _buildBoardStat('Avg Tenure', '5.2 yrs', Icons.schedule),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBoardStat(String label, String value, IconData icon) {
    return Column(
      children: [
        Icon(icon, color: Colors.purple, size: 28),
        const SizedBox(height: 8),
        Text(
          value,
          style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
        ),
        Text(
          label,
          style: TextStyle(fontSize: 11, color: Colors.grey.shade600),
          textAlign: TextAlign.center,
        ),
      ],
    );
  }

  Widget _buildEthicsCompliance() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Ethics & Compliance',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const Divider(),
            _buildComplianceRow('Code of Conduct', true),
            _buildComplianceRow('Anti-Corruption Policy', true),
            _buildComplianceRow('Whistleblower Protection', true),
            _buildComplianceRow('Data Privacy Policy', true),
            _buildComplianceRow('Supply Chain Due Diligence', true),
            _buildComplianceRow('Political Contribution Policy', false),
          ],
        ),
      ),
    );
  }

  Widget _buildComplianceRow(String item, bool implemented) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        children: [
          Icon(
            implemented ? Icons.check_circle : Icons.radio_button_unchecked,
            color: implemented ? Colors.green : Colors.grey,
            size: 20,
          ),
          const SizedBox(width: 12),
          Text(item),
        ],
      ),
    );
  }

  Widget _buildGovernanceMetricsList(List<ESGMetric> metrics) {
    if (metrics.isEmpty) {
      return Card(
        child: Padding(
          padding: const EdgeInsets.all(40),
          child: Center(
            child: Column(
              children: [
                Icon(Icons.gavel_outlined, size: 48, color: Colors.grey.shade400),
                const SizedBox(height: 16),
                const Text('No governance metrics recorded'),
              ],
            ),
          ),
        ),
      );
    }

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Governance Metrics',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const Divider(),
            ...metrics.map((m) => _buildMetricTile(m)),
          ],
        ),
      ),
    );
  }

  Color _getCategoryColor(String category) {
    switch (category) {
      case 'environmental':
        return Colors.green;
      case 'social':
        return Colors.blue;
      case 'governance':
        return Colors.purple;
      default:
        return Colors.grey;
    }
  }

  IconData _getCategoryIcon(String category) {
    switch (category) {
      case 'environmental':
        return Icons.eco;
      case 'social':
        return Icons.people;
      case 'governance':
        return Icons.gavel;
      default:
        return Icons.category;
    }
  }

  void _showAddMetricDialog() {
    final nameController = TextEditingController();
    final valueController = TextEditingController();
    final unitController = TextEditingController();
    String selectedCategory = 'environmental';

    showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          title: const Text('Add ESG Metric'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                DropdownButtonFormField<String>(
                  initialValue: selectedCategory,
                  decoration: const InputDecoration(
                    labelText: 'Category',
                    border: OutlineInputBorder(),
                  ),
                  items: const [
                    DropdownMenuItem(value: 'environmental', child: Text('Environmental')),
                    DropdownMenuItem(value: 'social', child: Text('Social')),
                    DropdownMenuItem(value: 'governance', child: Text('Governance')),
                  ],
                  onChanged: (value) {
                    setDialogState(() {
                      selectedCategory = value!;
                    });
                  },
                ),
                const SizedBox(height: 16),
                TextField(
                  controller: nameController,
                  decoration: const InputDecoration(
                    labelText: 'Metric Name',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 16),
                Row(
                  children: [
                    Expanded(
                      flex: 2,
                      child: TextField(
                        controller: valueController,
                        decoration: const InputDecoration(
                          labelText: 'Value',
                          border: OutlineInputBorder(),
                        ),
                        keyboardType: TextInputType.number,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: TextField(
                        controller: unitController,
                        decoration: const InputDecoration(
                          labelText: 'Unit',
                          border: OutlineInputBorder(),
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: () {
                _provider.addMetric(
                  category: selectedCategory,
                  name: nameController.text,
                  value: double.tryParse(valueController.text) ?? 0,
                  unit: unitController.text,
                );
                Navigator.pop(context);
              },
              style: ElevatedButton.styleFrom(backgroundColor: Colors.green.shade700),
              child: const Text('Add Metric'),
            ),
          ],
        ),
      ),
    );
  }
}
