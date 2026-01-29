import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/utils/api_client.dart';
import '../../providers/enterprise_providers.dart';
import '../../models/enterprise_models.dart';
import '../../widgets/loading_indicator.dart';
import '../../widgets/empty_state.dart';

class EmailSequencesScreen extends StatefulWidget {
  const EmailSequencesScreen({super.key});

  @override
  State<EmailSequencesScreen> createState() => _EmailSequencesScreenState();
}

class _EmailSequencesScreenState extends State<EmailSequencesScreen>
    with SingleTickerProviderStateMixin {
  late EmailSequenceProvider _provider;
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _provider = EmailSequenceProvider(ApiClient());
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
          title: const Text('Email Sequences'),
          flexibleSpace: Container(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [Colors.deepPurple.shade600, Colors.purple.shade400],
              ),
            ),
          ),
          bottom: TabBar(
            controller: _tabController,
            indicatorColor: Colors.white,
            tabs: const [
              Tab(text: 'Sequences', icon: Icon(Icons.timeline)),
              Tab(text: 'Enrollments', icon: Icon(Icons.people)),
              Tab(text: 'Analytics', icon: Icon(Icons.analytics)),
            ],
          ),
        ),
        body: Consumer<EmailSequenceProvider>(
          builder: (context, provider, _) {
            return TabBarView(
              controller: _tabController,
              children: [
                _buildSequencesTab(provider),
                _buildEnrollmentsTab(provider),
                _buildAnalyticsTab(provider),
              ],
            );
          },
        ),
        floatingActionButton: FloatingActionButton.extended(
          onPressed: _showCreateSequenceDialog,
          backgroundColor: Colors.deepPurple,
          icon: const Icon(Icons.add),
          label: const Text('New Sequence'),
        ),
      ),
    );
  }

  Widget _buildSequencesTab(EmailSequenceProvider provider) {
    if (provider.isLoading) {
      return const LoadingIndicator(message: 'Loading sequences...');
    }

    if (provider.sequences.isEmpty) {
      return EmptyState(
        icon: Icons.email_outlined,
        title: 'No Email Sequences',
        subtitle: 'Create your first email automation sequence',
        action: ElevatedButton.icon(
          onPressed: _showCreateSequenceDialog,
          icon: const Icon(Icons.add),
          label: const Text('Create Sequence'),
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: () => provider.loadSequences(),
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: provider.sequences.length,
        itemBuilder: (context, index) {
          return _buildSequenceCard(provider.sequences[index], provider);
        },
      ),
    );
  }

  Widget _buildSequenceCard(EmailSequence sequence, EmailSequenceProvider provider) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: InkWell(
        onTap: () => _showSequenceDetails(sequence, provider),
        borderRadius: BorderRadius.circular(12),
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
                      color: sequence.isActive 
                          ? Colors.green.shade50 
                          : Colors.grey.shade100,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Icon(
                      Icons.email,
                      color: sequence.isActive ? Colors.green : Colors.grey,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          sequence.name,
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 16,
                          ),
                        ),
                        Text(
                          '${sequence.steps.length} steps • ${sequence.enrolledCount} enrolled',
                          style: TextStyle(
                            color: Colors.grey.shade600,
                            fontSize: 13,
                          ),
                        ),
                      ],
                    ),
                  ),
                  Switch(
                    value: sequence.isActive,
                    onChanged: (value) {
                      provider.toggleSequence(sequence.id, value);
                    },
                    activeThumbColor: Colors.green,
                  ),
                ],
              ),
              if (sequence.description != null) ...[
                const SizedBox(height: 12),
                Text(
                  sequence.description!,
                  style: TextStyle(color: Colors.grey.shade700),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
              const Divider(height: 24),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  _buildMetric('Sent', sequence.sentCount.toString(), Colors.blue),
                  _buildMetric('Opened', '${(sequence.openRate * 100).toStringAsFixed(1)}%', Colors.green),
                  _buildMetric('Clicked', '${(sequence.clickRate * 100).toStringAsFixed(1)}%', Colors.orange),
                  _buildMetric('Replied', '${(sequence.replyRate * 100).toStringAsFixed(1)}%', Colors.purple),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildMetric(String label, String value, Color color) {
    return Column(
      children: [
        Text(
          value,
          style: TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 16,
            color: color,
          ),
        ),
        Text(
          label,
          style: TextStyle(
            color: Colors.grey.shade600,
            fontSize: 12,
          ),
        ),
      ],
    );
  }

  Widget _buildEnrollmentsTab(EmailSequenceProvider provider) {
    if (provider.isLoading) {
      return const LoadingIndicator(message: 'Loading enrollments...');
    }

    if (provider.enrollments.isEmpty) {
      return const EmptyState(
        icon: Icons.person_add_outlined,
        title: 'No Enrollments',
        subtitle: 'Enroll contacts in sequences to see them here',
      );
    }

    return RefreshIndicator(
      onRefresh: () => provider.loadEnrollments(),
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: provider.enrollments.length,
        itemBuilder: (context, index) {
          return _buildEnrollmentCard(provider.enrollments[index], provider);
        },
      ),
    );
  }

  Widget _buildEnrollmentCard(SequenceEnrollment enrollment, EmailSequenceProvider provider) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: _getStatusColor(enrollment.status).withValues(alpha: 0.2),
          child: Text(
            enrollment.contactName.substring(0, 1).toUpperCase(),
            style: TextStyle(
              color: _getStatusColor(enrollment.status),
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        title: Text(enrollment.contactName),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Sequence: ${enrollment.sequenceName}'),
            Row(
              children: [
                Text(
                  'Step ${enrollment.currentStep}',
                  style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
                ),
                const SizedBox(width: 8),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                  decoration: BoxDecoration(
                    color: _getStatusColor(enrollment.status).withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Text(
                    enrollment.status.toUpperCase(),
                    style: TextStyle(
                      color: _getStatusColor(enrollment.status),
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
        trailing: enrollment.status == 'active'
            ? IconButton(
                icon: const Icon(Icons.pause_circle),
                onPressed: () => provider.pauseEnrollment(enrollment.id),
                color: Colors.orange,
              )
            : enrollment.status == 'paused'
                ? IconButton(
                    icon: const Icon(Icons.play_circle),
                    onPressed: () => provider.resumeEnrollment(enrollment.id),
                    color: Colors.green,
                  )
                : null,
        isThreeLine: true,
      ),
    );
  }

  Widget _buildAnalyticsTab(EmailSequenceProvider provider) {
    return RefreshIndicator(
      onRefresh: _loadData,
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildOverviewStats(provider),
            const SizedBox(height: 24),
            _buildPerformanceCard(provider),
            const SizedBox(height: 24),
            _buildTopSequences(provider),
          ],
        ),
      ),
    );
  }

  Widget _buildOverviewStats(EmailSequenceProvider provider) {
    final totalEnrolled = provider.sequences.fold<int>(
      0, (sum, s) => sum + (s.enrolledCount ?? 0),
    );
    final totalSent = provider.sequences.fold<int>(
      0, (sum, s) => sum + s.sentCount,
    );
    final avgOpenRate = provider.sequences.isEmpty
        ? 0.0
        : provider.sequences.map((s) => s.openRate).reduce((a, b) => a + b) /
            provider.sequences.length;

    return Row(
      children: [
        Expanded(child: _buildStatCard('Active Sequences', 
            provider.sequences.where((s) => s.isActive).length.toString(), 
            Icons.play_circle, Colors.green)),
        const SizedBox(width: 12),
        Expanded(child: _buildStatCard('Total Enrolled', 
            totalEnrolled.toString(), 
            Icons.people, Colors.blue)),
        const SizedBox(width: 12),
        Expanded(child: _buildStatCard('Emails Sent', 
            totalSent.toString(), 
            Icons.send, Colors.purple)),
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
                fontSize: 22,
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

  Widget _buildPerformanceCard(EmailSequenceProvider provider) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Overall Performance',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 20),
            _buildProgressRow('Open Rate', 0.42, Colors.green),
            _buildProgressRow('Click Rate', 0.18, Colors.blue),
            _buildProgressRow('Reply Rate', 0.08, Colors.purple),
            _buildProgressRow('Unsubscribe Rate', 0.02, Colors.red),
          ],
        ),
      ),
    );
  }

  Widget _buildProgressRow(String label, double value, Color color) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(label),
              Text(
                '${(value * 100).toStringAsFixed(1)}%',
                style: TextStyle(fontWeight: FontWeight.bold, color: color),
              ),
            ],
          ),
          const SizedBox(height: 4),
          LinearProgressIndicator(
            value: value,
            backgroundColor: color.withValues(alpha: 0.2),
            valueColor: AlwaysStoppedAnimation(color),
          ),
        ],
      ),
    );
  }

  Widget _buildTopSequences(EmailSequenceProvider provider) {
    final sorted = List<EmailSequence>.from(provider.sequences)
      ..sort((a, b) => b.openRate.compareTo(a.openRate));

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Top Performing Sequences',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const Divider(),
            if (sorted.isEmpty)
              const Padding(
                padding: EdgeInsets.all(20),
                child: Center(child: Text('No sequences yet')),
              )
            else
              ...sorted.take(5).map((seq) => ListTile(
                contentPadding: EdgeInsets.zero,
                leading: CircleAvatar(
                  backgroundColor: Colors.deepPurple.shade50,
                  child: const Icon(Icons.email, color: Colors.deepPurple),
                ),
                title: Text(seq.name),
                subtitle: Text('${seq.enrolledCount} enrolled'),
                trailing: Text(
                  '${(seq.openRate * 100).toStringAsFixed(1)}%',
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    color: Colors.green,
                  ),
                ),
              )),
          ],
        ),
      ),
    );
  }

  Color _getStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'active':
        return Colors.green;
      case 'paused':
        return Colors.orange;
      case 'completed':
        return Colors.blue;
      case 'unsubscribed':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  void _showSequenceDetails(EmailSequence sequence, EmailSequenceProvider provider) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.7,
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
            Row(
              children: [
                Expanded(
                  child: Text(
                    sequence.name,
                    style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
                  ),
                ),
                Switch(
                  value: sequence.isActive,
                  onChanged: (value) {
                    provider.toggleSequence(sequence.id, value);
                    Navigator.pop(context);
                  },
                  activeThumbColor: Colors.green,
                ),
              ],
            ),
            if (sequence.description != null) ...[
              const SizedBox(height: 8),
              Text(
                sequence.description!,
                style: TextStyle(color: Colors.grey.shade600),
              ),
            ],
            const SizedBox(height: 24),
            const Text(
              'Sequence Steps',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            ...sequence.steps.asMap().entries.map((entry) {
              final index = entry.key;
              final step = entry.value;
              return _buildStepCard(index + 1, step);
            }),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: () {
                Navigator.pop(context);
                _showAddStepDialog(sequence);
              },
              icon: const Icon(Icons.add),
              label: const Text('Add Step'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.deepPurple,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStepCard(int stepNumber, EmailSequenceStep step) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            CircleAvatar(
              backgroundColor: Colors.deepPurple,
              radius: 16,
              child: Text(
                stepNumber.toString(),
                style: const TextStyle(color: Colors.white, fontSize: 14),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    step.subject,
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  Row(
                    children: [
                      Icon(Icons.schedule, size: 14, color: Colors.grey.shade600),
                      const SizedBox(width: 4),
                      Text(
                        'Wait ${step.delayDays} day${step.delayDays > 1 ? 's' : ''}',
                        style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            IconButton(
              icon: const Icon(Icons.edit, size: 20),
              onPressed: () {},
              color: Colors.grey,
            ),
          ],
        ),
      ),
    );
  }

  void _showCreateSequenceDialog() {
    final nameController = TextEditingController();
    final descriptionController = TextEditingController();

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Create Email Sequence'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: nameController,
              decoration: const InputDecoration(
                labelText: 'Sequence Name',
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
              _provider.createSequence(
                name: nameController.text,
                description: descriptionController.text,
              );
              Navigator.pop(context);
            },
            style: ElevatedButton.styleFrom(backgroundColor: Colors.deepPurple),
            child: const Text('Create'),
          ),
        ],
      ),
    );
  }

  void _showAddStepDialog(EmailSequence sequence) {
    final subjectController = TextEditingController();
    final bodyController = TextEditingController();
    int delayDays = 1;

    showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          title: const Text('Add Sequence Step'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(
                  controller: subjectController,
                  decoration: const InputDecoration(
                    labelText: 'Email Subject',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 16),
                TextField(
                  controller: bodyController,
                  decoration: const InputDecoration(
                    labelText: 'Email Body',
                    border: OutlineInputBorder(),
                  ),
                  maxLines: 5,
                ),
                const SizedBox(height: 16),
                Row(
                  children: [
                    const Text('Delay: '),
                    IconButton(
                      onPressed: delayDays > 1 
                          ? () => setDialogState(() => delayDays--) 
                          : null,
                      icon: const Icon(Icons.remove_circle),
                    ),
                    Text('$delayDays day${delayDays > 1 ? 's' : ''}'),
                    IconButton(
                      onPressed: () => setDialogState(() => delayDays++),
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
                _provider.addStep(
                  sequence.id,
                  {
                    'subject': subjectController.text,
                    'body': bodyController.text,
                    'delay_days': delayDays,
                  },
                );
                Navigator.pop(context);
              },
              style: ElevatedButton.styleFrom(backgroundColor: Colors.deepPurple),
              child: const Text('Add Step'),
            ),
          ],
        ),
      ),
    );
  }
}
