import 'package:flutter/material.dart';
import '../../core/constants/app_constants.dart';
import '../../core/utils/date_formatter.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});
  
  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  bool _isLoading = true;
  Map<String, dynamic> _stats = {};
  
  @override
  void initState() {
    super.initState();
    _loadDashboardData();
  }
  
  Future<void> _loadDashboardData() async {
    setState(() => _isLoading = true);
    
    // Simulate API call
    await Future.delayed(const Duration(seconds: 1));
    
    setState(() {
      _stats = {
        'total_contacts': 248,
        'total_leads': 156,
        'total_opportunities': 89,
        'total_tasks': 45,
        'revenue': 1250000,
        'conversion_rate': 32.5,
        'active_deals': 23,
        'tasks_completed': 182,
      };
      _isLoading = false;
    });
  }
  
  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }
    
    return RefreshIndicator(
      onRefresh: _loadDashboardData,
      child: ListView(
        padding: const EdgeInsets.all(AppSizes.paddingMd),
        children: [
          // Welcome Header
          _buildWelcomeHeader(),
          const SizedBox(height: AppSizes.paddingLg),
          
          // Stats Cards
          _buildStatsGrid(),
          const SizedBox(height: AppSizes.paddingLg),
          
          // Charts Section
          _buildChartsSection(),
          const SizedBox(height: AppSizes.paddingLg),
          
          // Recent Activity
          _buildRecentActivity(),
        ],
      ),
    );
  }
  
  Widget _buildWelcomeHeader() {
    return Card(
      child: Container(
        padding: const EdgeInsets.all(AppSizes.paddingLg),
        decoration: BoxDecoration(
          gradient: AppColors.primaryGradient,
          borderRadius: BorderRadius.circular(AppSizes.radiusMd),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Row(
              children: [
                Icon(Icons.wb_sunny, color: Colors.white, size: 28),
                SizedBox(width: 12),
                Text(
                  'Good Morning!',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: AppSizes.font2xl,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              'Here\'s what\'s happening with your CRM today',
              style: TextStyle(
                color: Colors.white.withValues(alpha: 0.9),
                fontSize: AppSizes.fontMd,
              ),
            ),
            const SizedBox(height: 16),
            Text(
              DateFormatter.formatDate(DateTime.now()),
              style: TextStyle(
                color: Colors.white.withValues(alpha: 0.8),
                fontSize: AppSizes.fontSm,
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildStatsGrid() {
    return GridView.count(
      crossAxisCount: 2,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      mainAxisSpacing: AppSizes.paddingMd,
      crossAxisSpacing: AppSizes.paddingMd,
      childAspectRatio: 1.5,
      children: [
        _buildStatCard(
          'Total Contacts',
          _stats['total_contacts'].toString(),
          Icons.people,
          AppColors.primary,
        ),
        _buildStatCard(
          'Total Leads',
          _stats['total_leads'].toString(),
          Icons.person_add,
          AppColors.success,
        ),
        _buildStatCard(
          'Opportunities',
          _stats['total_opportunities'].toString(),
          Icons.trending_up,
          AppColors.warning,
        ),
        _buildStatCard(
          'Active Tasks',
          _stats['total_tasks'].toString(),
          Icons.task,
          AppColors.secondary,
        ),
      ],
    );
  }
  
  Widget _buildStatCard(String title, String value, IconData icon, Color color) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(AppSizes.paddingMd),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Text(
                    title,
                    style: TextStyle(
                      color: AppColors.grey600,
                      fontSize: AppSizes.fontSm,
                      fontWeight: FontWeight.w500,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: color.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(AppSizes.radiusSm),
                  ),
                  child: Icon(icon, color: color, size: 20),
                ),
              ],
            ),
            Text(
              value,
              style: const TextStyle(
                fontSize: AppSizes.font3xl,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildChartsSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Padding(
          padding: EdgeInsets.symmetric(horizontal: AppSizes.paddingSm),
          child: Text(
            'Performance Overview',
            style: TextStyle(
              fontSize: AppSizes.fontLg,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        const SizedBox(height: AppSizes.paddingMd),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(AppSizes.paddingLg),
            child: Column(
              children: [
                _buildMetricRow(
                  'Revenue',
                  DateFormatter.formatCurrency(_stats['revenue'].toDouble()),
                  AppColors.success,
                ),
                const SizedBox(height: AppSizes.paddingMd),
                _buildMetricRow(
                  'Conversion Rate',
                  '${_stats['conversion_rate']}%',
                  AppColors.primary,
                ),
                const SizedBox(height: AppSizes.paddingMd),
                _buildMetricRow(
                  'Active Deals',
                  _stats['active_deals'].toString(),
                  AppColors.warning,
                ),
                const SizedBox(height: AppSizes.paddingMd),
                _buildMetricRow(
                  'Tasks Completed',
                  _stats['tasks_completed'].toString(),
                  AppColors.secondary,
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
  
  Widget _buildMetricRow(String label, String value, Color color) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          label,
          style: const TextStyle(
            fontSize: AppSizes.fontMd,
            fontWeight: FontWeight.w500,
          ),
        ),
        Container(
          padding: const EdgeInsets.symmetric(
            horizontal: AppSizes.paddingMd,
            vertical: AppSizes.paddingSm,
          ),
          decoration: BoxDecoration(
            color: color.withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(AppSizes.radiusSm),
          ),
          child: Text(
            value,
            style: TextStyle(
              fontSize: AppSizes.fontMd,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
        ),
      ],
    );
  }
  
  Widget _buildRecentActivity() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Padding(
          padding: EdgeInsets.symmetric(horizontal: AppSizes.paddingSm),
          child: Text(
            'Recent Activity',
            style: TextStyle(
              fontSize: AppSizes.fontLg,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        const SizedBox(height: AppSizes.paddingMd),
        Card(
          child: Column(
            children: [
              _buildActivityItem(
                'New contact added',
                'John Doe was added to your contacts',
                Icons.person_add,
                AppColors.primary,
                DateTime.now().subtract(const Duration(hours: 2)),
              ),
              const Divider(height: 1),
              _buildActivityItem(
                'Task completed',
                'Follow up with ABC Corp',
                Icons.check_circle,
                AppColors.success,
                DateTime.now().subtract(const Duration(hours: 5)),
              ),
              const Divider(height: 1),
              _buildActivityItem(
                'Deal won',
                '\$50,000 deal closed successfully',
                Icons.celebration,
                AppColors.warning,
                DateTime.now().subtract(const Duration(days: 1)),
              ),
            ],
          ),
        ),
      ],
    );
  }
  
  Widget _buildActivityItem(
    String title,
    String subtitle,
    IconData icon,
    Color color,
    DateTime time,
  ) {
    return ListTile(
      leading: Container(
        padding: const EdgeInsets.all(8),
        decoration: BoxDecoration(
          color: color.withValues(alpha: 0.1),
          borderRadius: BorderRadius.circular(AppSizes.radiusSm),
        ),
        child: Icon(icon, color: color, size: 20),
      ),
      title: Text(
        title,
        style: const TextStyle(fontWeight: FontWeight.w600),
      ),
      subtitle: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(subtitle),
          const SizedBox(height: 4),
          Text(
            DateFormatter.timeAgo(time),
            style: TextStyle(
              fontSize: AppSizes.fontXs,
              color: AppColors.grey500,
            ),
          ),
        ],
      ),
      isThreeLine: true,
    );
  }
}
