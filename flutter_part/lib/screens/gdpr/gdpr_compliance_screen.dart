import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/utils/api_client.dart';
import '../../providers/enterprise_providers.dart';
import '../../models/enterprise_models.dart';
import '../../widgets/loading_indicator.dart';
import '../../widgets/empty_state.dart';

class GDPRComplianceScreen extends StatefulWidget {
  const GDPRComplianceScreen({super.key});

  @override
  State<GDPRComplianceScreen> createState() => _GDPRComplianceScreenState();
}

class _GDPRComplianceScreenState extends State<GDPRComplianceScreen>
    with SingleTickerProviderStateMixin {
  late GDPRProvider _provider;
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _provider = GDPRProvider(ApiClient());
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
          title: const Text('GDPR Compliance'),
          flexibleSpace: Container(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [Colors.teal.shade600, Colors.green.shade500],
              ),
            ),
          ),
          bottom: TabBar(
            controller: _tabController,
            indicatorColor: Colors.white,
            tabs: const [
              Tab(text: 'Dashboard', icon: Icon(Icons.dashboard)),
              Tab(text: 'Consents', icon: Icon(Icons.verified_user)),
              Tab(text: 'Requests', icon: Icon(Icons.request_page)),
            ],
          ),
        ),
        body: Consumer<GDPRProvider>(
          builder: (context, provider, _) {
            return TabBarView(
              controller: _tabController,
              children: [
                _buildDashboardTab(provider),
                _buildConsentsTab(provider),
                _buildRequestsTab(provider),
              ],
            );
          },
        ),
        floatingActionButton: FloatingActionButton.extended(
          onPressed: _showNewRequestDialog,
          backgroundColor: Colors.teal,
          icon: const Icon(Icons.add),
          label: const Text('New Request'),
        ),
      ),
    );
  }

  Widget _buildDashboardTab(GDPRProvider provider) {
    return RefreshIndicator(
      onRefresh: _loadData,
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildComplianceScore(),
            const SizedBox(height: 20),
            _buildStatsCards(provider),
            const SizedBox(height: 20),
            _buildRecentActivity(provider),
            const SizedBox(height: 20),
            _buildComplianceChecklist(),
          ],
        ),
      ),
    );
  }

  Widget _buildComplianceScore() {
    return Card(
      child: Container(
        padding: const EdgeInsets.all(24),
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: [Colors.teal.shade600, Colors.green.shade400],
          ),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Row(
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: const [
                  Text(
                    'Compliance Score',
                    style: TextStyle(
                      color: Colors.white70,
                      fontSize: 16,
                    ),
                  ),
                  SizedBox(height: 8),
                  Text(
                    '92%',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 48,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  Text(
                    'Excellent compliance status',
                    style: TextStyle(color: Colors.white70),
                  ),
                ],
              ),
            ),
            Container(
              width: 100,
              height: 100,
              child: Stack(
                fit: StackFit.expand,
                children: [
                  CircularProgressIndicator(
                    value: 0.92,
                    strokeWidth: 10,
                    backgroundColor: Colors.white24,
                    valueColor: const AlwaysStoppedAnimation(Colors.white),
                  ),
                  const Center(
                    child: Icon(
                      Icons.shield,
                      color: Colors.white,
                      size: 40,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatsCards(GDPRProvider provider) {
    return Row(
      children: [
        Expanded(
          child: _buildStatCard(
            'Active Consents',
            provider.consents.where((c) => c.isActive).length.toString(),
            Icons.check_circle,
            Colors.green,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildStatCard(
            'Pending Requests',
            provider.requests.where((r) => r.status == 'pending').length.toString(),
            Icons.pending_actions,
            Colors.orange,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildStatCard(
            'Completed',
            provider.requests.where((r) => r.status == 'completed').length.toString(),
            Icons.task_alt,
            Colors.blue,
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

  Widget _buildRecentActivity(GDPRProvider provider) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Recent Activity',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const Divider(),
            if (provider.requests.isEmpty)
              const Padding(
                padding: EdgeInsets.all(20),
                child: Center(child: Text('No recent activity')),
              )
            else
              ...provider.requests.take(5).map((request) => ListTile(
                leading: CircleAvatar(
                  backgroundColor: _getStatusColor(request.status).withOpacity(0.2),
                  child: Icon(
                    _getRequestIcon(request.requestType),
                    color: _getStatusColor(request.status),
                    size: 20,
                  ),
                ),
                title: Text(request.requestType.replaceAll('_', ' ').toUpperCase()),
                subtitle: Text('Status: ${request.status}'),
                trailing: Text(
                  _formatDate(request.createdAt),
                  style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
                ),
              )),
          ],
        ),
      ),
    );
  }

  Widget _buildComplianceChecklist() {
    final items = [
      {'title': 'Privacy Policy Updated', 'done': true},
      {'title': 'Cookie Consent Implemented', 'done': true},
      {'title': 'Data Processing Agreement', 'done': true},
      {'title': 'Breach Notification Process', 'done': true},
      {'title': 'Data Retention Policy', 'done': false},
      {'title': 'Employee Training', 'done': false},
    ];

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
                  'Compliance Checklist',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                Text(
                  '${items.where((i) => i['done'] == true).length}/${items.length}',
                  style: TextStyle(color: Colors.grey.shade600),
                ),
              ],
            ),
            const Divider(),
            ...items.map((item) => CheckboxListTile(
              value: item['done'] as bool,
              onChanged: (value) {},
              title: Text(item['title'] as String),
              controlAffinity: ListTileControlAffinity.leading,
              activeColor: Colors.teal,
            )),
          ],
        ),
      ),
    );
  }

  Widget _buildConsentsTab(GDPRProvider provider) {
    if (provider.isLoading) {
      return const LoadingIndicator(message: 'Loading consents...');
    }

    if (provider.consents.isEmpty) {
      return const EmptyState(
        icon: Icons.verified_user_outlined,
        title: 'No Consents',
        subtitle: 'Consent records will appear here',
      );
    }

    return RefreshIndicator(
      onRefresh: () => provider.loadConsents(),
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: provider.consents.length,
        itemBuilder: (context, index) {
          final consent = provider.consents[index];
          return _buildConsentCard(consent, provider);
        },
      ),
    );
  }

  Widget _buildConsentCard(GDPRConsent consent, GDPRProvider provider) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ExpansionTile(
        leading: CircleAvatar(
          backgroundColor: consent.isActive ? Colors.green.shade100 : Colors.grey.shade200,
          child: Icon(
            consent.isActive ? Icons.check : Icons.close,
            color: consent.isActive ? Colors.green : Colors.grey,
          ),
        ),
        title: Text(consent.consentType.replaceAll('_', ' ').toUpperCase()),
        subtitle: Text('Contact ID: ${consent.contactId}'),
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildDetailRow('Source', consent.source),
                _buildDetailRow('IP Address', consent.ipAddress ?? 'N/A'),
                _buildDetailRow('Granted At', _formatDate(consent.grantedAt)),
                if (consent.expiresAt != null)
                  _buildDetailRow('Expires At', _formatDate(consent.expiresAt!)),
                const SizedBox(height: 12),
                Row(
                  mainAxisAlignment: MainAxisAlignment.end,
                  children: [
                    TextButton.icon(
                      onPressed: () => provider.revokeConsent(consent.id),
                      icon: const Icon(Icons.cancel, color: Colors.red),
                      label: const Text('Revoke', style: TextStyle(color: Colors.red)),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRequestsTab(GDPRProvider provider) {
    if (provider.isLoading) {
      return const LoadingIndicator(message: 'Loading requests...');
    }

    if (provider.requests.isEmpty) {
      return EmptyState(
        icon: Icons.request_page_outlined,
        title: 'No Data Requests',
        subtitle: 'Data subject requests will appear here',
        action: ElevatedButton.icon(
          onPressed: _showNewRequestDialog,
          icon: const Icon(Icons.add),
          label: const Text('Create Request'),
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: () => provider.loadRequests(),
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: provider.requests.length,
        itemBuilder: (context, index) {
          final request = provider.requests[index];
          return _buildRequestCard(request, provider);
        },
      ),
    );
  }

  Widget _buildRequestCard(DataSubjectRequest request, GDPRProvider provider) {
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
                  backgroundColor: _getStatusColor(request.status).withOpacity(0.2),
                  child: Icon(
                    _getRequestIcon(request.requestType),
                    color: _getStatusColor(request.status),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        request.requestType.replaceAll('_', ' ').toUpperCase(),
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
                      Text(
                        'Contact ID: ${request.contactId}',
                        style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
                      ),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: _getStatusColor(request.status).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    request.status.toUpperCase(),
                    style: TextStyle(
                      color: _getStatusColor(request.status),
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                    ),
                  ),
                ),
              ],
            ),
            const Divider(height: 24),
            _buildDetailRow('Created', _formatDate(request.createdAt)),
            if (request.dueDate != null)
              _buildDetailRow('Due Date', _formatDate(request.dueDate!)),
            if (request.completedAt != null)
              _buildDetailRow('Completed', _formatDate(request.completedAt!)),
            if (request.status == 'pending') ...[
              const SizedBox(height: 12),
              Row(
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  OutlinedButton(
                    onPressed: () => provider.processRequest(request.id),
                    child: const Text('Process'),
                  ),
                  const SizedBox(width: 8),
                  ElevatedButton(
                    onPressed: () => provider.completeRequest(request.id),
                    style: ElevatedButton.styleFrom(backgroundColor: Colors.teal),
                    child: const Text('Complete'),
                  ),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildDetailRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: TextStyle(color: Colors.grey.shade600)),
          Text(value, style: const TextStyle(fontWeight: FontWeight.w500)),
        ],
      ),
    );
  }

  Color _getStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'completed':
        return Colors.green;
      case 'pending':
        return Colors.orange;
      case 'processing':
        return Colors.blue;
      case 'rejected':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  IconData _getRequestIcon(String type) {
    switch (type.toLowerCase()) {
      case 'access':
        return Icons.visibility;
      case 'erasure':
      case 'deletion':
        return Icons.delete_forever;
      case 'rectification':
        return Icons.edit;
      case 'portability':
        return Icons.download;
      case 'objection':
        return Icons.block;
      default:
        return Icons.request_page;
    }
  }

  String _formatDate(DateTime date) {
    return '${date.day}/${date.month}/${date.year}';
  }

  void _showNewRequestDialog() {
    String selectedType = 'access';
    final contactIdController = TextEditingController();

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('New Data Subject Request'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            DropdownButtonFormField<String>(
              value: selectedType,
              decoration: const InputDecoration(
                labelText: 'Request Type',
                border: OutlineInputBorder(),
              ),
              items: const [
                DropdownMenuItem(value: 'access', child: Text('Data Access')),
                DropdownMenuItem(value: 'erasure', child: Text('Data Erasure')),
                DropdownMenuItem(value: 'rectification', child: Text('Rectification')),
                DropdownMenuItem(value: 'portability', child: Text('Data Portability')),
                DropdownMenuItem(value: 'objection', child: Text('Objection')),
              ],
              onChanged: (value) {
                selectedType = value!;
              },
            ),
            const SizedBox(height: 16),
            TextField(
              controller: contactIdController,
              decoration: const InputDecoration(
                labelText: 'Contact ID or Email',
                border: OutlineInputBorder(),
              ),
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
              _provider.createRequest(
                requestType: selectedType,
                contactId: int.tryParse(contactIdController.text) ?? 0,
              );
              Navigator.pop(context);
            },
            style: ElevatedButton.styleFrom(backgroundColor: Colors.teal),
            child: const Text('Create'),
          ),
        ],
      ),
    );
  }
}
