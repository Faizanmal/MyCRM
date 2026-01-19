import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/utils/api_client.dart';
import '../../providers/enterprise_providers.dart';
import '../../models/enterprise_models.dart';
import '../../widgets/loading_indicator.dart';
import '../../widgets/empty_state.dart';

class DataEnrichmentScreen extends StatefulWidget {
  const DataEnrichmentScreen({super.key});

  @override
  State<DataEnrichmentScreen> createState() => _DataEnrichmentScreenState();
}

class _DataEnrichmentScreenState extends State<DataEnrichmentScreen>
    with SingleTickerProviderStateMixin {
  late DataEnrichmentProvider _provider;
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _provider = DataEnrichmentProvider(ApiClient());
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
          title: const Text('Data Enrichment'),
          flexibleSpace: Container(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [Colors.amber.shade700, Colors.orange.shade500],
              ),
            ),
          ),
          bottom: TabBar(
            controller: _tabController,
            indicatorColor: Colors.white,
            tabs: const [
              Tab(text: 'Dashboard', icon: Icon(Icons.dashboard)),
              Tab(text: 'Jobs', icon: Icon(Icons.work)),
              Tab(text: 'Results', icon: Icon(Icons.analytics)),
            ],
          ),
        ),
        body: Consumer<DataEnrichmentProvider>(
          builder: (context, provider, _) {
            return TabBarView(
              controller: _tabController,
              children: [
                _buildDashboardTab(provider),
                _buildJobsTab(provider),
                _buildResultsTab(provider),
              ],
            );
          },
        ),
        floatingActionButton: FloatingActionButton.extended(
          onPressed: _showEnrichmentDialog,
          backgroundColor: Colors.amber.shade700,
          icon: const Icon(Icons.auto_fix_high),
          label: const Text('Enrich Data'),
        ),
      ),
    );
  }

  Widget _buildDashboardTab(DataEnrichmentProvider provider) {
    return RefreshIndicator(
      onRefresh: _loadData,
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildEnrichmentStats(provider),
            const SizedBox(height: 20),
            _buildDataQualityCard(provider),
            const SizedBox(height: 20),
            _buildEnrichmentSources(),
            const SizedBox(height: 20),
            _buildRecentEnrichments(provider),
          ],
        ),
      ),
    );
  }

  Widget _buildEnrichmentStats(DataEnrichmentProvider provider) {
    return Row(
      children: [
        Expanded(
          child: _buildStatCard(
            'Enriched Records',
            provider.results.length.toString(),
            Icons.check_circle,
            Colors.green,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildStatCard(
            'Pending Jobs',
            provider.jobs.where((j) => j.status == 'pending').length.toString(),
            Icons.pending,
            Colors.orange,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildStatCard(
            'Match Rate',
            '${(provider.matchRate * 100).toStringAsFixed(0)}%',
            Icons.percent,
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

  Widget _buildDataQualityCard(DataEnrichmentProvider provider) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.insights, color: Colors.amber.shade700),
                const SizedBox(width: 8),
                const Text(
                  'Data Quality Score',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const SizedBox(height: 20),
            Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      _buildQualityRow('Email Validity', 0.94, Colors.green),
                      _buildQualityRow('Phone Numbers', 0.78, Colors.amber),
                      _buildQualityRow('Company Data', 0.85, Colors.green),
                      _buildQualityRow('Social Profiles', 0.62, Colors.orange),
                      _buildQualityRow('Job Titles', 0.88, Colors.green),
                    ],
                  ),
                ),
                const SizedBox(width: 20),
                Container(
                  width: 100,
                  height: 100,
                  child: Stack(
                    fit: StackFit.expand,
                    children: [
                      CircularProgressIndicator(
                        value: 0.81,
                        strokeWidth: 10,
                        backgroundColor: Colors.grey.shade200,
                        valueColor: AlwaysStoppedAnimation(Colors.amber.shade700),
                      ),
                      const Center(
                        child: Text(
                          '81%',
                          style: TextStyle(
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
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

  Widget _buildQualityRow(String label, double value, Color color) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Expanded(child: Text(label, style: const TextStyle(fontSize: 13))),
          const SizedBox(width: 8),
          SizedBox(
            width: 80,
            child: LinearProgressIndicator(
              value: value,
              backgroundColor: color.withOpacity(0.2),
              valueColor: AlwaysStoppedAnimation(color),
            ),
          ),
          const SizedBox(width: 8),
          Text(
            '${(value * 100).toInt()}%',
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

  Widget _buildEnrichmentSources() {
    final sources = [
      {'name': 'LinkedIn', 'icon': Icons.work, 'color': Color(0xFF0077B5), 'connected': true},
      {'name': 'Clearbit', 'icon': Icons.business, 'color': Colors.blue, 'connected': true},
      {'name': 'ZoomInfo', 'icon': Icons.person_search, 'color': Colors.purple, 'connected': false},
      {'name': 'Hunter.io', 'icon': Icons.email, 'color': Colors.orange, 'connected': true},
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
                  'Data Sources',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                TextButton.icon(
                  onPressed: () {},
                  icon: const Icon(Icons.add, size: 18),
                  label: const Text('Add'),
                ),
              ],
            ),
            const Divider(),
            ...sources.map((source) => ListTile(
              contentPadding: EdgeInsets.zero,
              leading: CircleAvatar(
                backgroundColor: (source['color'] as Color).withOpacity(0.2),
                child: Icon(source['icon'] as IconData, color: source['color'] as Color),
              ),
              title: Text(source['name'] as String),
              trailing: source['connected'] as bool
                  ? Chip(
                      label: const Text('Connected', style: TextStyle(fontSize: 11)),
                      backgroundColor: Colors.green.shade100,
                      labelStyle: const TextStyle(color: Colors.green),
                    )
                  : OutlinedButton(
                      onPressed: () {},
                      child: const Text('Connect'),
                    ),
            )),
          ],
        ),
      ),
    );
  }

  Widget _buildRecentEnrichments(DataEnrichmentProvider provider) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Recent Enrichments',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const Divider(),
            if (provider.results.isEmpty)
              const Padding(
                padding: EdgeInsets.all(20),
                child: Center(child: Text('No recent enrichments')),
              )
            else
              ...provider.results.take(5).map((result) => _buildEnrichmentResultTile(result)),
          ],
        ),
      ),
    );
  }

  Widget _buildEnrichmentResultTile(EnrichmentResult result) {
    return ListTile(
      contentPadding: EdgeInsets.zero,
      leading: CircleAvatar(
        backgroundColor: Colors.amber.shade50,
        child: Icon(Icons.person, color: Colors.amber.shade700),
      ),
      title: Text(result.entityName),
      subtitle: Text('${result.fieldsEnriched} fields enriched'),
      trailing: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          Text(
            '${result.confidence}%',
            style: TextStyle(
              fontWeight: FontWeight.bold,
              color: result.confidence >= 80 ? Colors.green : Colors.orange,
            ),
          ),
          Text(
            _formatTimeAgo(result.enrichedAt),
            style: TextStyle(fontSize: 11, color: Colors.grey.shade600),
          ),
        ],
      ),
    );
  }

  Widget _buildJobsTab(DataEnrichmentProvider provider) {
    if (provider.isLoading) {
      return const LoadingIndicator(message: 'Loading jobs...');
    }

    if (provider.jobs.isEmpty) {
      return EmptyState(
        icon: Icons.work_outline,
        title: 'No Enrichment Jobs',
        subtitle: 'Start an enrichment job to see it here',
        action: ElevatedButton.icon(
          onPressed: _showEnrichmentDialog,
          icon: const Icon(Icons.add),
          label: const Text('Create Job'),
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: () => provider.loadJobs(),
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: provider.jobs.length,
        itemBuilder: (context, index) {
          return _buildJobCard(provider.jobs[index], provider);
        },
      ),
    );
  }

  Widget _buildJobCard(EnrichmentJob job, DataEnrichmentProvider provider) {
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
                    color: _getStatusColor(job.status).withOpacity(0.2),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Icon(
                    _getStatusIcon(job.status),
                    color: _getStatusColor(job.status),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        job.name,
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
                      Text(
                        '${job.processedRecords}/${job.totalRecords} records',
                        style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
                      ),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: _getStatusColor(job.status).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    job.status.toUpperCase(),
                    style: TextStyle(
                      color: _getStatusColor(job.status),
                      fontWeight: FontWeight.bold,
                      fontSize: 11,
                    ),
                  ),
                ),
              ],
            ),
            if (job.status == 'running') ...[
              const SizedBox(height: 16),
              LinearProgressIndicator(
                value: job.totalRecords > 0 
                    ? job.processedRecords / job.totalRecords 
                    : 0,
                backgroundColor: Colors.amber.shade100,
                valueColor: AlwaysStoppedAnimation(Colors.amber.shade700),
              ),
              const SizedBox(height: 8),
              Text(
                '${((job.processedRecords / job.totalRecords) * 100).toStringAsFixed(0)}% complete',
                style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
              ),
            ],
            const Divider(height: 24),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Created: ${_formatDate(job.createdAt)}',
                  style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
                ),
                if (job.status == 'pending')
                  Row(
                    children: [
                      TextButton(
                        onPressed: () => provider.cancelJob(job.id),
                        child: const Text('Cancel', style: TextStyle(color: Colors.red)),
                      ),
                      ElevatedButton(
                        onPressed: () => provider.startJob(job.id),
                        style: ElevatedButton.styleFrom(backgroundColor: Colors.amber.shade700),
                        child: const Text('Start'),
                      ),
                    ],
                  ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildResultsTab(DataEnrichmentProvider provider) {
    if (provider.isLoading) {
      return const LoadingIndicator(message: 'Loading results...');
    }

    if (provider.results.isEmpty) {
      return const EmptyState(
        icon: Icons.analytics_outlined,
        title: 'No Results Yet',
        subtitle: 'Enrichment results will appear here after processing',
      );
    }

    return RefreshIndicator(
      onRefresh: () => provider.loadResults(),
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: provider.results.length,
        itemBuilder: (context, index) {
          return _buildResultCard(provider.results[index]);
        },
      ),
    );
  }

  Widget _buildResultCard(EnrichmentResult result) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ExpansionTile(
        leading: CircleAvatar(
          backgroundColor: Colors.amber.shade50,
          child: Text(
            result.entityName.substring(0, 1).toUpperCase(),
            style: TextStyle(color: Colors.amber.shade700, fontWeight: FontWeight.bold),
          ),
        ),
        title: Text(result.entityName),
        subtitle: Text(
          '${result.fieldsEnriched} fields • ${result.confidence}% confidence',
        ),
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Enriched Data',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 12),
                ...result.enrichedData.entries.map((entry) => Padding(
                  padding: const EdgeInsets.symmetric(vertical: 4),
                  child: Row(
                    children: [
                      Icon(Icons.check, color: Colors.green, size: 16),
                      const SizedBox(width: 8),
                      Text(
                        entry.key.replaceAll('_', ' ').toUpperCase(),
                        style: TextStyle(
                          color: Colors.grey.shade600,
                          fontSize: 12,
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          entry.value.toString(),
                          style: const TextStyle(fontWeight: FontWeight.w500),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ],
                  ),
                )),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Color _getStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'completed':
        return Colors.green;
      case 'running':
        return Colors.blue;
      case 'pending':
        return Colors.orange;
      case 'failed':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  IconData _getStatusIcon(String status) {
    switch (status.toLowerCase()) {
      case 'completed':
        return Icons.check_circle;
      case 'running':
        return Icons.sync;
      case 'pending':
        return Icons.pending;
      case 'failed':
        return Icons.error;
      default:
        return Icons.help;
    }
  }

  String _formatDate(DateTime date) {
    return '${date.day}/${date.month}/${date.year}';
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

  void _showEnrichmentDialog() {
    String selectedType = 'contacts';
    bool includeLinkedIn = true;
    bool includeEmail = true;
    bool includeCompany = true;

    showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          title: const Text('Enrich Data'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                DropdownButtonFormField<String>(
                  value: selectedType,
                  decoration: const InputDecoration(
                    labelText: 'Data Type',
                    border: OutlineInputBorder(),
                  ),
                  items: const [
                    DropdownMenuItem(value: 'contacts', child: Text('Contacts')),
                    DropdownMenuItem(value: 'leads', child: Text('Leads')),
                    DropdownMenuItem(value: 'companies', child: Text('Companies')),
                  ],
                  onChanged: (value) {
                    setDialogState(() {
                      selectedType = value!;
                    });
                  },
                ),
                const SizedBox(height: 20),
                const Text(
                  'Data Sources',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 8),
                CheckboxListTile(
                  value: includeLinkedIn,
                  onChanged: (v) => setDialogState(() => includeLinkedIn = v!),
                  title: const Text('LinkedIn'),
                  subtitle: const Text('Company & professional data'),
                  controlAffinity: ListTileControlAffinity.leading,
                  contentPadding: EdgeInsets.zero,
                ),
                CheckboxListTile(
                  value: includeEmail,
                  onChanged: (v) => setDialogState(() => includeEmail = v!),
                  title: const Text('Email Finder'),
                  subtitle: const Text('Verify & find emails'),
                  controlAffinity: ListTileControlAffinity.leading,
                  contentPadding: EdgeInsets.zero,
                ),
                CheckboxListTile(
                  value: includeCompany,
                  onChanged: (v) => setDialogState(() => includeCompany = v!),
                  title: const Text('Company Data'),
                  subtitle: const Text('Firmographics & technographics'),
                  controlAffinity: ListTileControlAffinity.leading,
                  contentPadding: EdgeInsets.zero,
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancel'),
            ),
            ElevatedButton.icon(
              onPressed: () {
                _provider.createJob(
                  entityType: selectedType,
                  sources: [
                    if (includeLinkedIn) 'linkedin',
                    if (includeEmail) 'email',
                    if (includeCompany) 'company',
                  ],
                );
                Navigator.pop(context);
              },
              icon: const Icon(Icons.auto_fix_high),
              label: const Text('Start Enrichment'),
              style: ElevatedButton.styleFrom(backgroundColor: Colors.amber.shade700),
            ),
          ],
        ),
      ),
    );
  }
}
