import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../widgets/common/app_drawer.dart';

class ReportsScreen extends StatefulWidget {
  const ReportsScreen({super.key});

  @override
  State<ReportsScreen> createState() => _ReportsScreenState();
}

class _ReportsScreenState extends State<ReportsScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  String _selectedPeriod = 'This Month';

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Reports & Analytics'),
        flexibleSpace: Container(
          decoration: const BoxDecoration(
            gradient: LinearGradient(
              colors: [Color(0xFF1E3A8A), Color(0xFF3B82F6)],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
          ),
        ),
        actions: [
          PopupMenuButton<String>(
            icon: const Icon(Icons.calendar_today),
            onSelected: (value) {
              setState(() => _selectedPeriod = value);
            },
            itemBuilder: (context) => [
              const PopupMenuItem(value: 'Today', child: Text('Today')),
              const PopupMenuItem(value: 'This Week', child: Text('This Week')),
              const PopupMenuItem(value: 'This Month', child: Text('This Month')),
              const PopupMenuItem(value: 'This Quarter', child: Text('This Quarter')),
              const PopupMenuItem(value: 'This Year', child: Text('This Year')),
            ],
          ),
          IconButton(
            icon: const Icon(Icons.download),
            onPressed: _exportReport,
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: Colors.white,
          tabs: const [
            Tab(text: 'Sales', icon: Icon(Icons.trending_up)),
            Tab(text: 'Leads', icon: Icon(Icons.people)),
            Tab(text: 'Pipeline', icon: Icon(Icons.waterfall_chart)),
            Tab(text: 'Team', icon: Icon(Icons.groups)),
          ],
        ),
      ),
      drawer: const AppDrawer(),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildSalesReport(),
          _buildLeadsReport(),
          _buildPipelineReport(),
          _buildTeamReport(),
        ],
      ),
    );
  }

  Widget _buildSalesReport() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildPeriodHeader('Sales Performance - $_selectedPeriod'),
          const SizedBox(height: 16),
          _buildKPICards([
            {'title': 'Total Revenue', 'value': '\$125,430', 'change': '+12.5%', 'isPositive': true},
            {'title': 'Deals Closed', 'value': '28', 'change': '+8.3%', 'isPositive': true},
            {'title': 'Avg Deal Size', 'value': '\$4,480', 'change': '+3.2%', 'isPositive': true},
            {'title': 'Win Rate', 'value': '32%', 'change': '-2.1%', 'isPositive': false},
          ]),
          const SizedBox(height: 24),
          _buildSectionTitle('Revenue Trend'),
          const SizedBox(height: 8),
          _buildRevenueChart(),
          const SizedBox(height: 24),
          _buildSectionTitle('Top Deals'),
          const SizedBox(height: 8),
          _buildTopDealsList(),
        ],
      ),
    );
  }

  Widget _buildLeadsReport() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildPeriodHeader('Lead Analytics - $_selectedPeriod'),
          const SizedBox(height: 16),
          _buildKPICards([
            {'title': 'New Leads', 'value': '156', 'change': '+24.3%', 'isPositive': true},
            {'title': 'Qualified', 'value': '89', 'change': '+18.7%', 'isPositive': true},
            {'title': 'Conversion Rate', 'value': '28%', 'change': '+5.2%', 'isPositive': true},
            {'title': 'Avg Response Time', 'value': '2.4h', 'change': '-15%', 'isPositive': true},
          ]),
          const SizedBox(height: 24),
          _buildSectionTitle('Lead Sources'),
          const SizedBox(height: 8),
          _buildLeadSourcesChart(),
          const SizedBox(height: 24),
          _buildSectionTitle('Lead Status Distribution'),
          const SizedBox(height: 8),
          _buildLeadStatusChart(),
        ],
      ),
    );
  }

  Widget _buildPipelineReport() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildPeriodHeader('Pipeline Analysis - $_selectedPeriod'),
          const SizedBox(height: 16),
          _buildKPICards([
            {'title': 'Pipeline Value', 'value': '\$892,500', 'change': '+15.8%', 'isPositive': true},
            {'title': 'Active Deals', 'value': '67', 'change': '+12.1%', 'isPositive': true},
            {'title': 'Expected Revenue', 'value': '\$285,600', 'change': '+8.4%', 'isPositive': true},
            {'title': 'Avg Sales Cycle', 'value': '32 days', 'change': '-3 days', 'isPositive': true},
          ]),
          const SizedBox(height: 24),
          _buildSectionTitle('Pipeline by Stage'),
          const SizedBox(height: 8),
          _buildPipelineStagesChart(),
          const SizedBox(height: 24),
          _buildSectionTitle('Forecast'),
          const SizedBox(height: 8),
          _buildForecastList(),
        ],
      ),
    );
  }

  Widget _buildTeamReport() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildPeriodHeader('Team Performance - $_selectedPeriod'),
          const SizedBox(height: 16),
          _buildKPICards([
            {'title': 'Team Revenue', 'value': '\$425,600', 'change': '+18.2%', 'isPositive': true},
            {'title': 'Activities', 'value': '1,234', 'change': '+22.5%', 'isPositive': true},
            {'title': 'Quota Attainment', 'value': '87%', 'change': '+5.3%', 'isPositive': true},
            {'title': 'Avg Productivity', 'value': '94%', 'change': '+2.1%', 'isPositive': true},
          ]),
          const SizedBox(height: 24),
          _buildSectionTitle('Leaderboard'),
          const SizedBox(height: 8),
          _buildTeamLeaderboard(),
          const SizedBox(height: 24),
          _buildSectionTitle('Activity Breakdown'),
          const SizedBox(height: 8),
          _buildActivityBreakdown(),
        ],
      ),
    );
  }

  Widget _buildPeriodHeader(String title) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          title,
          style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
        ),
        Chip(
          label: Text(_selectedPeriod),
          backgroundColor: Theme.of(context).primaryColor.withValues(alpha: 0.1),
        ),
      ],
    );
  }

  Widget _buildKPICards(List<Map<String, dynamic>> kpis) {
    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        crossAxisSpacing: 12,
        mainAxisSpacing: 12,
        childAspectRatio: 1.5,
      ),
      itemCount: kpis.length,
      itemBuilder: (context, index) {
        final kpi = kpis[index];
        final isPositive = kpi['isPositive'] as bool;
        return Card(
          elevation: 2,
          child: Padding(
            padding: const EdgeInsets.all(12),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  kpi['title'],
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(color: Colors.grey[600]),
                ),
                const SizedBox(height: 4),
                Text(
                  kpi['value'],
                  style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 4),
                Row(
                  children: [
                    Icon(
                      isPositive ? Icons.arrow_upward : Icons.arrow_downward,
                      size: 14,
                      color: isPositive ? Colors.green : Colors.red,
                    ),
                    Text(
                      kpi['change'],
                      style: TextStyle(
                        color: isPositive ? Colors.green : Colors.red,
                        fontSize: 12,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildSectionTitle(String title) {
    return Text(
      title,
      style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w600),
    );
  }

  Widget _buildRevenueChart() {
    return Container(
      height: 200,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [BoxShadow(color: Colors.black.withValues(alpha: 0.05), blurRadius: 10)],
      ),
      child: LineChart(
        LineChartData(
          gridData: FlGridData(show: true, drawVerticalLine: false),
          titlesData: FlTitlesData(
            leftTitles: AxisTitles(sideTitles: SideTitles(showTitles: true, reservedSize: 40)),
            bottomTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                getTitlesWidget: (value, meta) {
                  const labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
                  if (value.toInt() < labels.length) {
                    return Text(labels[value.toInt()], style: const TextStyle(fontSize: 10));
                  }
                  return const Text('');
                },
              ),
            ),
            rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
            topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
          ),
          borderData: FlBorderData(show: false),
          lineBarsData: [
            LineChartBarData(
              spots: const [
                FlSpot(0, 15),
                FlSpot(1, 22),
                FlSpot(2, 18),
                FlSpot(3, 32),
                FlSpot(4, 28),
                FlSpot(5, 42),
              ],
              isCurved: true,
              color: const Color(0xFF3B82F6),
              barWidth: 3,
              belowBarData: BarAreaData(
                show: true,
                color: const Color(0xFF3B82F6).withValues(alpha: 0.1),
              ),
              dotData: const FlDotData(show: false),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTopDealsList() {
    final deals = [
      {'name': 'Acme Corp Enterprise', 'value': '\$45,000', 'stage': 'Negotiation', 'probability': '80%'},
      {'name': 'TechStart Pro Plan', 'value': '\$28,500', 'stage': 'Proposal', 'probability': '65%'},
      {'name': 'Global Industries', 'value': '\$22,000', 'stage': 'Qualification', 'probability': '45%'},
    ];

    return Card(
      child: ListView.separated(
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        itemCount: deals.length,
        separatorBuilder: (_, _) => const Divider(height: 1),
        itemBuilder: (context, index) {
          final deal = deals[index];
          return ListTile(
            title: Text(deal['name']!, style: const TextStyle(fontWeight: FontWeight.w500)),
            subtitle: Text(deal['stage']!),
            trailing: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(deal['value']!, style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.green)),
                Text(deal['probability']!, style: TextStyle(fontSize: 12, color: Colors.grey[600])),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildLeadSourcesChart() {
    return Container(
      height: 200,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [BoxShadow(color: Colors.black.withValues(alpha: 0.05), blurRadius: 10)],
      ),
      child: PieChart(
        PieChartData(
          sections: [
            PieChartSectionData(value: 35, title: 'Website', color: const Color(0xFF3B82F6), radius: 60),
            PieChartSectionData(value: 25, title: 'Referral', color: const Color(0xFF10B981), radius: 60),
            PieChartSectionData(value: 20, title: 'Social', color: const Color(0xFFF59E0B), radius: 60),
            PieChartSectionData(value: 15, title: 'Email', color: const Color(0xFFEF4444), radius: 60),
            PieChartSectionData(value: 5, title: 'Other', color: const Color(0xFF8B5CF6), radius: 60),
          ],
          centerSpaceRadius: 0,
          sectionsSpace: 2,
        ),
      ),
    );
  }

  Widget _buildLeadStatusChart() {
    return Container(
      height: 200,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [BoxShadow(color: Colors.black.withValues(alpha: 0.05), blurRadius: 10)],
      ),
      child: BarChart(
        BarChartData(
          alignment: BarChartAlignment.spaceAround,
          maxY: 50,
          barGroups: [
            BarChartGroupData(x: 0, barRods: [BarChartRodData(toY: 45, color: const Color(0xFF3B82F6), width: 20)]),
            BarChartGroupData(x: 1, barRods: [BarChartRodData(toY: 32, color: const Color(0xFF10B981), width: 20)]),
            BarChartGroupData(x: 2, barRods: [BarChartRodData(toY: 28, color: const Color(0xFFF59E0B), width: 20)]),
            BarChartGroupData(x: 3, barRods: [BarChartRodData(toY: 18, color: const Color(0xFFEF4444), width: 20)]),
          ],
          titlesData: FlTitlesData(
            bottomTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                getTitlesWidget: (value, meta) {
                  const labels = ['New', 'Qualified', 'Contacted', 'Converted'];
                  if (value.toInt() < labels.length) {
                    return Text(labels[value.toInt()], style: const TextStyle(fontSize: 10));
                  }
                  return const Text('');
                },
              ),
            ),
            leftTitles: AxisTitles(sideTitles: SideTitles(showTitles: true, reservedSize: 30)),
            rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
            topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
          ),
          borderData: FlBorderData(show: false),
          gridData: const FlGridData(show: false),
        ),
      ),
    );
  }

  Widget _buildPipelineStagesChart() {
    final stages = [
      {'name': 'Prospecting', 'value': 245000, 'deals': 23, 'color': const Color(0xFF3B82F6)},
      {'name': 'Qualification', 'value': 180000, 'deals': 15, 'color': const Color(0xFF10B981)},
      {'name': 'Proposal', 'value': 320000, 'deals': 12, 'color': const Color(0xFFF59E0B)},
      {'name': 'Negotiation', 'value': 147500, 'deals': 8, 'color': const Color(0xFFEF4444)},
    ];

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: stages.map((stage) {
            final percentage = (stage['value'] as int) / 320000;
            return Padding(
              padding: const EdgeInsets.symmetric(vertical: 8),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(stage['name'] as String, style: const TextStyle(fontWeight: FontWeight.w500)),
                      Text('\$${((stage['value'] as int) / 1000).toStringAsFixed(0)}K (${stage['deals']} deals)'),
                    ],
                  ),
                  const SizedBox(height: 4),
                  LinearProgressIndicator(
                    value: percentage,
                    backgroundColor: Colors.grey[200],
                    valueColor: AlwaysStoppedAnimation(stage['color'] as Color),
                    minHeight: 8,
                    borderRadius: BorderRadius.circular(4),
                  ),
                ],
              ),
            );
          }).toList(),
        ),
      ),
    );
  }

  Widget _buildForecastList() {
    final forecasts = [
      {'period': 'This Month', 'expected': '\$85,200', 'best': '\$102,400', 'worst': '\$62,800'},
      {'period': 'Next Month', 'expected': '\$92,500', 'best': '\$118,200', 'worst': '\$71,300'},
      {'period': 'Q4 Total', 'expected': '\$285,600', 'best': '\$342,000', 'worst': '\$215,400'},
    ];

    return Card(
      child: ListView.separated(
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        itemCount: forecasts.length,
        separatorBuilder: (_, _) => const Divider(height: 1),
        itemBuilder: (context, index) {
          final forecast = forecasts[index];
          return ListTile(
            title: Text(forecast['period']!, style: const TextStyle(fontWeight: FontWeight.w500)),
            subtitle: Text('Expected: ${forecast['expected']}'),
            trailing: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text('Best: ${forecast['best']}', style: const TextStyle(color: Colors.green, fontSize: 12)),
                Text('Worst: ${forecast['worst']}', style: const TextStyle(color: Colors.red, fontSize: 12)),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildTeamLeaderboard() {
    final team = [
      {'rank': 1, 'name': 'Sarah Johnson', 'revenue': '\$48,200', 'deals': 12, 'quota': 115},
      {'rank': 2, 'name': 'Mike Chen', 'revenue': '\$42,800', 'deals': 10, 'quota': 102},
      {'rank': 3, 'name': 'Emily Davis', 'revenue': '\$38,500', 'deals': 9, 'quota': 92},
      {'rank': 4, 'name': 'David Wilson', 'revenue': '\$31,200', 'deals': 7, 'quota': 74},
    ];

    return Card(
      child: ListView.separated(
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        itemCount: team.length,
        separatorBuilder: (_, _) => const Divider(height: 1),
        itemBuilder: (context, index) {
          final member = team[index];
          Color rankColor;
          switch (member['rank']) {
            case 1:
              rankColor = Colors.amber;
              break;
            case 2:
              rankColor = Colors.grey;
              break;
            case 3:
              rankColor = Colors.brown;
              break;
            default:
              rankColor = Colors.blueGrey;
          }
          return ListTile(
            leading: CircleAvatar(
              backgroundColor: rankColor,
              child: Text('${member['rank']}', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
            ),
            title: Text(member['name'] as String, style: const TextStyle(fontWeight: FontWeight.w500)),
            subtitle: Text('${member['deals']} deals closed'),
            trailing: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(member['revenue'] as String, style: const TextStyle(fontWeight: FontWeight.bold)),
                Text('${member['quota']}% quota', 
                  style: TextStyle(fontSize: 12, color: (member['quota'] as int) >= 100 ? Colors.green : Colors.orange)),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildActivityBreakdown() {
    final activities = [
      {'type': 'Calls Made', 'count': 342, 'icon': Icons.phone, 'color': Colors.blue},
      {'type': 'Emails Sent', 'count': 528, 'icon': Icons.email, 'color': Colors.green},
      {'type': 'Meetings Held', 'count': 87, 'icon': Icons.calendar_today, 'color': Colors.orange},
      {'type': 'Proposals Sent', 'count': 45, 'icon': Icons.description, 'color': Colors.purple},
    ];

    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        crossAxisSpacing: 12,
        mainAxisSpacing: 12,
        childAspectRatio: 2,
      ),
      itemCount: activities.length,
      itemBuilder: (context, index) {
        final activity = activities[index];
        return Card(
          child: Padding(
            padding: const EdgeInsets.all(12),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: (activity['color'] as Color).withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Icon(activity['icon'] as IconData, color: activity['color'] as Color),
                ),
                const SizedBox(width: 12),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text('${activity['count']}', style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                    Text(activity['type'] as String, style: TextStyle(fontSize: 12, color: Colors.grey[600])),
                  ],
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  void _exportReport() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Exporting report...')),
    );
  }
}
