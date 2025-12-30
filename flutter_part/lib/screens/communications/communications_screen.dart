import 'package:flutter/material.dart';
import '../../widgets/loading_indicator.dart';
import '../../widgets/empty_state.dart';

class CommunicationsScreen extends StatefulWidget {
  const CommunicationsScreen({super.key});

  @override
  State<CommunicationsScreen> createState() => _CommunicationsScreenState();
}

class _CommunicationsScreenState extends State<CommunicationsScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final bool _isLoading = false;

  // Mock data
  final List<Map<String, dynamic>> _communications = [
    {
      'type': 'email',
      'subject': 'Follow-up on our meeting',
      'contact': 'John Smith',
      'date': DateTime.now().subtract(const Duration(hours: 2)),
      'direction': 'outgoing',
    },
    {
      'type': 'call',
      'subject': 'Discovery call',
      'contact': 'Sarah Johnson',
      'date': DateTime.now().subtract(const Duration(hours: 5)),
      'direction': 'incoming',
      'duration': '15:32',
    },
    {
      'type': 'meeting',
      'subject': 'Product demo',
      'contact': 'TechCorp Team',
      'date': DateTime.now().subtract(const Duration(days: 1)),
      'direction': 'outgoing',
      'duration': '45:00',
    },
    {
      'type': 'note',
      'subject': 'Customer feedback notes',
      'contact': 'Mike Brown',
      'date': DateTime.now().subtract(const Duration(days: 2)),
      'direction': 'outgoing',
    },
  ];

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
        title: const Text('Communications'),
        flexibleSpace: Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [Colors.deepPurple.shade600, Colors.purple.shade500],
            ),
          ),
        ),
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: Colors.white,
          tabs: const [
            Tab(text: 'All'),
            Tab(text: 'Emails'),
            Tab(text: 'Calls'),
            Tab(text: 'Notes'),
          ],
        ),
      ),
      body: _isLoading
          ? const LoadingIndicator(message: 'Loading communications...')
          : TabBarView(
              controller: _tabController,
              children: [
                _buildList(null),
                _buildList('email'),
                _buildList('call'),
                _buildList('note'),
              ],
            ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _showAddCommunicationSheet(),
        backgroundColor: Colors.deepPurple,
        child: const Icon(Icons.add),
      ),
    );
  }

  Widget _buildList(String? typeFilter) {
    final filtered = typeFilter == null
        ? _communications
        : _communications.where((c) => c['type'] == typeFilter).toList();

    if (filtered.isEmpty) {
      return EmptyState(
        icon: _getIconForType(typeFilter ?? 'all'),
        title: 'No ${typeFilter ?? 'communications'} yet',
        subtitle: 'Start communicating with your contacts',
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: filtered.length,
      itemBuilder: (context, index) {
        final comm = filtered[index];
        return _buildCommunicationCard(comm);
      },
    );
  }

  Widget _buildCommunicationCard(Map<String, dynamic> comm) {
    final type = comm['type'] as String;
    final isOutgoing = comm['direction'] == 'outgoing';

    Color typeColor;
    IconData typeIcon;
    switch (type) {
      case 'email':
        typeColor = Colors.blue;
        typeIcon = Icons.email;
        break;
      case 'call':
        typeColor = Colors.green;
        typeIcon = isOutgoing ? Icons.call_made : Icons.call_received;
        break;
      case 'meeting':
        typeColor = Colors.orange;
        typeIcon = Icons.videocam;
        break;
      case 'note':
        typeColor = Colors.purple;
        typeIcon = Icons.note;
        break;
      default:
        typeColor = Colors.grey;
        typeIcon = Icons.message;
    }

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        onTap: () => _showCommunicationDetails(comm),
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: typeColor.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(typeIcon, color: typeColor),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      comm['subject'],
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 15,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Row(
                      children: [
                        Icon(Icons.person, size: 14, color: Colors.grey.shade600),
                        const SizedBox(width: 4),
                        Text(
                          comm['contact'],
                          style: TextStyle(color: Colors.grey.shade600),
                        ),
                      ],
                    ),
                    if (comm['duration'] != null) ...[
                      const SizedBox(height: 4),
                      Row(
                        children: [
                          Icon(Icons.timer, size: 14, color: Colors.grey.shade600),
                          const SizedBox(width: 4),
                          Text(
                            comm['duration'],
                            style: TextStyle(color: Colors.grey.shade600),
                          ),
                        ],
                      ),
                    ],
                  ],
                ),
              ),
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text(
                    _formatDate(comm['date']),
                    style: TextStyle(
                      color: Colors.grey.shade600,
                      fontSize: 12,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: typeColor.withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      type.toUpperCase(),
                      style: TextStyle(
                        color: typeColor,
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
      ),
    );
  }

  IconData _getIconForType(String type) {
    switch (type) {
      case 'email':
        return Icons.email_outlined;
      case 'call':
        return Icons.phone_outlined;
      case 'note':
        return Icons.note_outlined;
      default:
        return Icons.message_outlined;
    }
  }

  String _formatDate(DateTime date) {
    final now = DateTime.now();
    final diff = now.difference(date);

    if (diff.inMinutes < 60) {
      return '${diff.inMinutes}m ago';
    } else if (diff.inHours < 24) {
      return '${diff.inHours}h ago';
    } else if (diff.inDays < 7) {
      return '${diff.inDays}d ago';
    } else {
      return '${date.day}/${date.month}';
    }
  }

  void _showCommunicationDetails(Map<String, dynamic> comm) {
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
        builder: (context, scrollController) => SingleChildScrollView(
          controller: scrollController,
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
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
              const SizedBox(height: 24),
              Text(
                comm['subject'],
                style: const TextStyle(
                  fontSize: 22,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 12),
              _buildDetailRow(Icons.person, comm['contact']),
              _buildDetailRow(Icons.access_time, _formatDate(comm['date'])),
              _buildDetailRow(Icons.arrow_forward, 
                comm['direction'] == 'outgoing' ? 'Outgoing' : 'Incoming'),
              if (comm['duration'] != null)
                _buildDetailRow(Icons.timer, comm['duration']),
              const SizedBox(height: 24),
              const Text(
                'Notes',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.grey.shade100,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Text(
                  'No additional notes for this communication.',
                  style: TextStyle(color: Colors.grey),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDetailRow(IconData icon, String text) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        children: [
          Icon(icon, size: 18, color: Colors.grey.shade600),
          const SizedBox(width: 12),
          Text(text),
        ],
      ),
    );
  }

  void _showAddCommunicationSheet() {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Log Communication',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 24),
            Row(
              children: [
                _buildTypeButton(Icons.email, 'Email', Colors.blue),
                const SizedBox(width: 16),
                _buildTypeButton(Icons.phone, 'Call', Colors.green),
                const SizedBox(width: 16),
                _buildTypeButton(Icons.videocam, 'Meeting', Colors.orange),
                const SizedBox(width: 16),
                _buildTypeButton(Icons.note, 'Note', Colors.purple),
              ],
            ),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }

  Widget _buildTypeButton(IconData icon, String label, Color color) {
    return Expanded(
      child: InkWell(
        onTap: () {
          Navigator.pop(context);
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Log $label')),
          );
        },
        borderRadius: BorderRadius.circular(12),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 16),
          decoration: BoxDecoration(
            color: color.withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: color.withValues(alpha: 0.3)),
          ),
          child: Column(
            children: [
              Icon(icon, color: color),
              const SizedBox(height: 8),
              Text(
                label,
                style: TextStyle(
                  color: color,
                  fontWeight: FontWeight.bold,
                  fontSize: 12,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
