import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/utils/api_client.dart';
import '../../providers/enterprise_providers.dart';
import '../../models/enterprise_models.dart';
import '../../widgets/loading_indicator.dart';
import '../../widgets/empty_state.dart';

class LeadRoutingScreen extends StatefulWidget {
  const LeadRoutingScreen({super.key});

  @override
  State<LeadRoutingScreen> createState() => _LeadRoutingScreenState();
}

class _LeadRoutingScreenState extends State<LeadRoutingScreen>
    with SingleTickerProviderStateMixin {
  late LeadRoutingProvider _provider;
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _provider = LeadRoutingProvider(ApiClient());
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
          title: const Text('Lead Routing'),
          flexibleSpace: Container(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [Colors.cyan.shade700, Colors.blue.shade500],
              ),
            ),
          ),
          bottom: TabBar(
            controller: _tabController,
            indicatorColor: Colors.white,
            tabs: const [
              Tab(text: 'Dashboard', icon: Icon(Icons.dashboard)),
              Tab(text: 'Rules', icon: Icon(Icons.rule)),
              Tab(text: 'Assignments', icon: Icon(Icons.assignment_ind)),
            ],
          ),
        ),
        body: Consumer<LeadRoutingProvider>(
          builder: (context, provider, _) {
            return TabBarView(
              controller: _tabController,
              children: [
                _buildDashboardTab(provider),
                _buildRulesTab(provider),
                _buildAssignmentsTab(provider),
              ],
            );
          },
        ),
        floatingActionButton: FloatingActionButton.extended(
          onPressed: _showCreateRuleDialog,
          backgroundColor: Colors.cyan.shade700,
          icon: const Icon(Icons.add),
          label: const Text('New Rule'),
        ),
      ),
    );
  }

  Widget _buildDashboardTab(LeadRoutingProvider provider) {
    return RefreshIndicator(
      onRefresh: _loadData,
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildRoutingStats(provider),
            const SizedBox(height: 20),
            _buildPerformanceCard(provider),
            const SizedBox(height: 20),
            _buildRepDistribution(provider),
            const SizedBox(height: 20),
            _buildRecentAssignments(provider),
          ],
        ),
      ),
    );
  }

  Widget _buildRoutingStats(LeadRoutingProvider provider) {
    return Row(
      children: [
        Expanded(
          child: _buildStatCard(
            'Active Rules',
            provider.rules.where((r) => r.isActive).length.toString(),
            Icons.rule,
            Colors.cyan,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildStatCard(
            'Today\'s Assignments',
            provider.todayAssignments.toString(),
            Icons.assignment_turned_in,
            Colors.green,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildStatCard(
            'Avg Response',
            '${provider.avgResponseTime}m',
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

  Widget _buildPerformanceCard(LeadRoutingProvider provider) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Routing Performance',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 20),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildPerformanceMetric('Assignment Rate', '98%', Colors.green),
                _buildPerformanceMetric('Accept Rate', '85%', Colors.blue),
                _buildPerformanceMetric('SLA Compliance', '92%', Colors.purple),
              ],
            ),
            const SizedBox(height: 20),
            const Text(
              'Lead Distribution Today',
              style: TextStyle(fontWeight: FontWeight.w500),
            ),
            const SizedBox(height: 8),
            LinearProgressIndicator(
              value: 0.75,
              backgroundColor: Colors.cyan.shade100,
              valueColor: AlwaysStoppedAnimation(Colors.cyan.shade700),
            ),
            const SizedBox(height: 4),
            Text(
              '75 of 100 leads assigned',
              style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPerformanceMetric(String label, String value, Color color) {
    return Column(
      children: [
        Text(
          value,
          style: TextStyle(
            fontSize: 28,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
        Text(
          label,
          style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
        ),
      ],
    );
  }

  Widget _buildRepDistribution(LeadRoutingProvider provider) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Rep Workload Distribution',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const Divider(),
            _buildRepRow('John Smith', 28, 30, Colors.green),
            _buildRepRow('Sarah Johnson', 25, 30, Colors.green),
            _buildRepRow('Mike Wilson', 30, 30, Colors.orange),
            _buildRepRow('Emily Brown', 18, 30, Colors.blue),
            _buildRepRow('David Lee', 22, 30, Colors.blue),
          ],
        ),
      ),
    );
  }

  Widget _buildRepRow(String name, int current, int capacity, Color color) {
    final percentage = current / capacity;
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Column(
        children: [
          Row(
            children: [
              CircleAvatar(
                radius: 16,
                backgroundColor: color.withValues(alpha: 0.2),
                child: Text(
                  name.substring(0, 1),
                  style: TextStyle(color: color, fontWeight: FontWeight.bold),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(child: Text(name)),
              Text(
                '$current/$capacity',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  color: percentage >= 1 ? Colors.orange : Colors.grey.shade700,
                ),
              ),
            ],
          ),
          const SizedBox(height: 4),
          LinearProgressIndicator(
            value: percentage > 1 ? 1 : percentage,
            backgroundColor: color.withValues(alpha: 0.2),
            valueColor: AlwaysStoppedAnimation(color),
          ),
        ],
      ),
    );
  }

  Widget _buildRecentAssignments(LeadRoutingProvider provider) {
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
                  'Recent Assignments',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                TextButton(
                  onPressed: () => _tabController.animateTo(2),
                  child: const Text('View All'),
                ),
              ],
            ),
            const Divider(),
            if (provider.assignments.isEmpty)
              const Padding(
                padding: EdgeInsets.all(20),
                child: Center(child: Text('No recent assignments')),
              )
            else
              ...provider.assignments.take(5).map((a) => _buildAssignmentTile(a)),
          ],
        ),
      ),
    );
  }

  Widget _buildAssignmentTile(LeadAssignment assignment) {
    return ListTile(
      contentPadding: EdgeInsets.zero,
      leading: CircleAvatar(
        backgroundColor: Colors.cyan.shade50,
        child: Icon(Icons.person, color: Colors.cyan.shade700),
      ),
      title: Text(assignment.leadName),
      subtitle: Text('Assigned to ${assignment.assigneeName}'),
      trailing: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          Text(
            assignment.ruleName,
            style: TextStyle(fontSize: 11, color: Colors.grey.shade600),
          ),
          Text(
            _formatTimeAgo(assignment.assignedAt),
            style: TextStyle(fontSize: 11, color: Colors.grey.shade500),
          ),
        ],
      ),
    );
  }

  Widget _buildRulesTab(LeadRoutingProvider provider) {
    if (provider.isLoading) {
      return const LoadingIndicator(message: 'Loading rules...');
    }

    if (provider.rules.isEmpty) {
      return EmptyState(
        icon: Icons.rule_outlined,
        title: 'No Routing Rules',
        subtitle: 'Create rules to automatically assign leads',
        action: ElevatedButton.icon(
          onPressed: _showCreateRuleDialog,
          icon: const Icon(Icons.add),
          label: const Text('Create Rule'),
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: () => provider.loadRules(),
      child: ReorderableListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: provider.rules.length,
        onReorder: (oldIndex, newIndex) {
          provider.reorderRules(oldIndex, newIndex);
        },
        itemBuilder: (context, index) {
          return _buildRuleCard(
            provider.rules[index],
            provider,
            key: ValueKey(provider.rules[index].id),
          );
        },
      ),
    );
  }

  Widget _buildRuleCard(LeadRoutingRule rule, LeadRoutingProvider provider, {Key? key}) {
    return Card(
      key: key,
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.drag_handle, color: Colors.grey.shade400),
                const SizedBox(width: 8),
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: rule.isActive ? Colors.cyan.shade50 : Colors.grey.shade100,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Icon(
                    Icons.rule,
                    color: rule.isActive ? Colors.cyan.shade700 : Colors.grey,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        rule.name,
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
                      Text(
                        'Priority: ${rule.priority}',
                        style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
                      ),
                    ],
                  ),
                ),
                Switch(
                  value: rule.isActive,
                  onChanged: (value) {
                    provider.toggleRule(rule.id, value);
                  },
                  activeThumbColor: Colors.cyan.shade700,
                ),
              ],
            ),
            ...[
            const SizedBox(height: 8),
            Text(
              rule.description!,
              style: TextStyle(color: Colors.grey.shade600),
            ),
          ],
            const Divider(height: 24),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                _buildRuleChip('Type: ${rule.routingType}'),
                if (rule.conditions.containsKey('region'))
                  _buildRuleChip('Region: ${rule.conditions['region']}'),
                if (rule.conditions.containsKey('industry'))
                  _buildRuleChip('Industry: ${rule.conditions['industry']}'),
                if (rule.conditions.containsKey('lead_score'))
                  _buildRuleChip('Score ≥ ${rule.conditions['lead_score']}'),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                TextButton.icon(
                  onPressed: () => _showEditRuleDialog(rule),
                  icon: const Icon(Icons.edit, size: 18),
                  label: const Text('Edit'),
                ),
                TextButton.icon(
                  onPressed: () => _confirmDeleteRule(rule, provider),
                  icon: const Icon(Icons.delete, size: 18, color: Colors.red),
                  label: const Text('Delete', style: TextStyle(color: Colors.red)),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRuleChip(String label) {
    return Chip(
      label: Text(label, style: const TextStyle(fontSize: 11)),
      backgroundColor: Colors.cyan.shade50,
      padding: EdgeInsets.zero,
      materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
    );
  }

  Widget _buildAssignmentsTab(LeadRoutingProvider provider) {
    if (provider.isLoading) {
      return const LoadingIndicator(message: 'Loading assignments...');
    }

    if (provider.assignments.isEmpty) {
      return const EmptyState(
        icon: Icons.assignment_ind_outlined,
        title: 'No Assignments',
        subtitle: 'Lead assignments will appear here',
      );
    }

    return RefreshIndicator(
      onRefresh: () => provider.loadAssignments(),
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: provider.assignments.length,
        itemBuilder: (context, index) {
          return _buildAssignmentCard(provider.assignments[index], provider);
        },
      ),
    );
  }

  Widget _buildAssignmentCard(LeadAssignment assignment, LeadRoutingProvider provider) {
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
                  backgroundColor: _getStatusColor(assignment.status).withValues(alpha: 0.2),
                  child: Text(
                    assignment.leadName.substring(0, 1).toUpperCase(),
                    style: TextStyle(
                      color: _getStatusColor(assignment.status),
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
                        assignment.leadName,
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
                      Text(
                        assignment.leadCompany ?? 'No company',
                        style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
                      ),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: _getStatusColor(assignment.status).withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    assignment.status.toUpperCase(),
                    style: TextStyle(
                      color: _getStatusColor(assignment.status),
                      fontWeight: FontWeight.bold,
                      fontSize: 10,
                    ),
                  ),
                ),
              ],
            ),
            const Divider(height: 24),
            Row(
              children: [
                Icon(Icons.person_outline, size: 16, color: Colors.grey.shade600),
                const SizedBox(width: 4),
                Text(
                  assignment.assigneeName,
                  style: TextStyle(color: Colors.grey.shade700),
                ),
                const Spacer(),
                Icon(Icons.rule, size: 16, color: Colors.grey.shade600),
                const SizedBox(width: 4),
                Text(
                  assignment.ruleName,
                  style: TextStyle(color: Colors.grey.shade700, fontSize: 12),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Icon(Icons.schedule, size: 16, color: Colors.grey.shade600),
                const SizedBox(width: 4),
                Text(
                  _formatDate(assignment.assignedAt),
                  style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
                ),
                ...[
                const Spacer(),
                Icon(Icons.timer, size: 16, color: Colors.grey.shade600),
                const SizedBox(width: 4),
                Text(
                  'Response: ${assignment.responseTime}m',
                  style: TextStyle(
                    color: assignment.responseTime! <= 30 ? Colors.green : Colors.orange,
                    fontSize: 12,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
              ],
            ),
            if (assignment.status == 'pending') ...[
              const SizedBox(height: 12),
              Row(
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  OutlinedButton(
                    onPressed: () => provider.reassignLead(assignment.id),
                    child: const Text('Reassign'),
                  ),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }

  Color _getStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'accepted':
        return Colors.green;
      case 'pending':
        return Colors.orange;
      case 'rejected':
        return Colors.red;
      case 'reassigned':
        return Colors.blue;
      default:
        return Colors.grey;
    }
  }

  String _formatDate(DateTime date) {
    return '${date.day}/${date.month}/${date.year} ${date.hour}:${date.minute.toString().padLeft(2, '0')}';
  }

  String _formatTimeAgo(DateTime date) {
    final difference = DateTime.now().difference(date);
    if (difference.inDays > 0) {
      return '${difference.inDays}d ago';
    } else if (difference.inHours > 0) {
      return '${difference.inHours}h ago';
    } else {
      return '${difference.inMinutes}m ago';
    }
  }

  void _showCreateRuleDialog() {
    final nameController = TextEditingController();
    final descriptionController = TextEditingController();
    String routingType = 'round_robin';
    int priority = 1;

    showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          title: const Text('Create Routing Rule'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(
                  controller: nameController,
                  decoration: const InputDecoration(
                    labelText: 'Rule Name',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 16),
                TextField(
                  controller: descriptionController,
                  decoration: const InputDecoration(
                    labelText: 'Description (optional)',
                    border: OutlineInputBorder(),
                  ),
                  maxLines: 2,
                ),
                const SizedBox(height: 16),
                DropdownButtonFormField<String>(
                  initialValue: routingType,
                  decoration: const InputDecoration(
                    labelText: 'Routing Type',
                    border: OutlineInputBorder(),
                  ),
                  items: const [
                    DropdownMenuItem(value: 'round_robin', child: Text('Round Robin')),
                    DropdownMenuItem(value: 'weighted', child: Text('Weighted')),
                    DropdownMenuItem(value: 'geographic', child: Text('Geographic')),
                    DropdownMenuItem(value: 'skill_based', child: Text('Skill Based')),
                  ],
                  onChanged: (value) {
                    setDialogState(() {
                      routingType = value!;
                    });
                  },
                ),
                const SizedBox(height: 16),
                Row(
                  children: [
                    const Text('Priority: '),
                    IconButton(
                      onPressed: priority > 1 
                          ? () => setDialogState(() => priority--)
                          : null,
                      icon: const Icon(Icons.remove_circle),
                    ),
                    Text('$priority'),
                    IconButton(
                      onPressed: () => setDialogState(() => priority++),
                      icon: const Icon(Icons.add_circle),
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
                _provider.createRule(
                  {
                    'name': nameController.text,
                    'description': descriptionController.text,
                    'routing_type': routingType,
                    'priority': priority,
                  },
                );
                Navigator.pop(context);
              },
              style: ElevatedButton.styleFrom(backgroundColor: Colors.cyan.shade700),
              child: const Text('Create'),
            ),
          ],
        ),
      ),
    );
  }

  void _showEditRuleDialog(LeadRoutingRule rule) {
    // Similar to create dialog but pre-filled with rule data
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Edit rule dialog')),
    );
  }

  void _confirmDeleteRule(LeadRoutingRule rule, LeadRoutingProvider provider) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Rule'),
        content: Text('Are you sure you want to delete "${rule.name}"?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              provider.deleteRule(rule.id);
              Navigator.pop(context);
            },
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('Delete'),
          ),
        ],
      ),
    );
  }
}
