import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/utils/api_client.dart';
import '../../providers/advanced_providers.dart';
import '../../models/advanced_models.dart';
import '../../widgets/loading_indicator.dart';
import '../../widgets/empty_state.dart';

class CampaignsScreen extends StatefulWidget {
  const CampaignsScreen({super.key});

  @override
  State<CampaignsScreen> createState() => _CampaignsScreenState();
}

class _CampaignsScreenState extends State<CampaignsScreen> {
  late CampaignProvider _provider;

  @override
  void initState() {
    super.initState();
    _provider = CampaignProvider(ApiClient());
    _loadData();
  }

  Future<void> _loadData() async {
    await _provider.loadCampaigns();
  }

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider.value(
      value: _provider,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Campaigns'),
          flexibleSpace: Container(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [Colors.teal.shade600, Colors.green.shade600],
              ),
            ),
          ),
          actions: [
            IconButton(
              icon: const Icon(Icons.filter_list),
              onPressed: () => _showFilterDialog(),
            ),
          ],
        ),
        body: Consumer<CampaignProvider>(
          builder: (context, provider, _) {
            if (provider.isLoading) {
              return const LoadingIndicator(message: 'Loading campaigns...');
            }

            if (provider.campaigns.isEmpty) {
              return EmptyState(
                icon: Icons.campaign_outlined,
                title: 'No Campaigns',
                subtitle: 'Create your first campaign to get started',
                action: ElevatedButton.icon(
                  onPressed: () => _showCreateCampaignDialog(),
                  icon: const Icon(Icons.add),
                  label: const Text('Create Campaign'),
                ),
              );
            }

            return RefreshIndicator(
              onRefresh: _loadData,
              child: ListView.builder(
                padding: const EdgeInsets.all(16),
                itemCount: provider.campaigns.length,
                itemBuilder: (context, index) {
                  return _buildCampaignCard(provider.campaigns[index]);
                },
              ),
            );
          },
        ),
        floatingActionButton: FloatingActionButton.extended(
          onPressed: () => _showCreateCampaignDialog(),
          icon: const Icon(Icons.add),
          label: const Text('New Campaign'),
          backgroundColor: Colors.teal,
        ),
      ),
    );
  }

  Widget _buildCampaignCard(Campaign campaign) {
    Color statusColor;
    IconData statusIcon;
    switch (campaign.status) {
      case 'sent':
        statusColor = Colors.green;
        statusIcon = Icons.check_circle;
        break;
      case 'scheduled':
        statusColor = Colors.blue;
        statusIcon = Icons.schedule;
        break;
      case 'sending':
        statusColor = Colors.orange;
        statusIcon = Icons.send;
        break;
      default:
        statusColor = Colors.grey;
        statusIcon = Icons.edit;
    }

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        onTap: () => _showCampaignDetails(campaign),
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
                      color: Colors.teal.shade50,
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Icon(
                      campaign.campaignType == 'email'
                          ? Icons.email
                          : Icons.sms,
                      color: Colors.teal,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          campaign.name,
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 16,
                          ),
                        ),
                        if (campaign.description.isNotEmpty)
                          Text(
                            campaign.description,
                            style: TextStyle(color: Colors.grey.shade600),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                      ],
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 10,
                      vertical: 6,
                    ),
                    decoration: BoxDecoration(
                      color: statusColor.withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(statusIcon, size: 14, color: statusColor),
                        const SizedBox(width: 4),
                        Text(
                          campaign.status.toUpperCase(),
                          style: TextStyle(
                            color: statusColor,
                            fontWeight: FontWeight.bold,
                            fontSize: 11,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              Row(
                children: [
                  _buildMetric(
                    Icons.people,
                    '${campaign.recipientCount}',
                    'Recipients',
                  ),
                  const SizedBox(width: 24),
                  _buildMetric(
                    Icons.visibility,
                    '${(campaign.openRate * 100).toStringAsFixed(1)}%',
                    'Open Rate',
                  ),
                  const SizedBox(width: 24),
                  _buildMetric(
                    Icons.touch_app,
                    '${(campaign.clickRate * 100).toStringAsFixed(1)}%',
                    'Click Rate',
                  ),
                ],
              ),
              if (campaign.status == 'draft') ...[
                const Divider(height: 24),
                Row(
                  mainAxisAlignment: MainAxisAlignment.end,
                  children: [
                    TextButton.icon(
                      onPressed: () => _scheduleCampaign(campaign),
                      icon: const Icon(Icons.schedule, size: 18),
                      label: const Text('Schedule'),
                    ),
                    const SizedBox(width: 8),
                    ElevatedButton.icon(
                      onPressed: () => _sendCampaign(campaign),
                      icon: const Icon(Icons.send, size: 18),
                      label: const Text('Send Now'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.teal,
                      ),
                    ),
                  ],
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildMetric(IconData icon, String value, String label) {
    return Row(
      children: [
        Icon(icon, size: 16, color: Colors.grey.shade600),
        const SizedBox(width: 4),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              value,
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
            Text(
              label,
              style: TextStyle(color: Colors.grey.shade600, fontSize: 11),
            ),
          ],
        ),
      ],
    );
  }

  void _showCreateCampaignDialog() {
    final nameController = TextEditingController();
    final descController = TextEditingController();
    String selectedType = 'email';

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => StatefulBuilder(
        builder: (context, setState) => Padding(
          padding: EdgeInsets.only(
            left: 16,
            right: 16,
            top: 16,
            bottom: MediaQuery.of(context).viewInsets.bottom + 16,
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  const Icon(Icons.campaign, color: Colors.teal),
                  const SizedBox(width: 8),
                  const Text(
                    'Create Campaign',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  const Spacer(),
                  IconButton(
                    onPressed: () => Navigator.pop(context),
                    icon: const Icon(Icons.close),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              TextField(
                controller: nameController,
                decoration: const InputDecoration(
                  labelText: 'Campaign Name',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: descController,
                decoration: const InputDecoration(
                  labelText: 'Description',
                  border: OutlineInputBorder(),
                ),
                maxLines: 2,
              ),
              const SizedBox(height: 12),
              const Text('Campaign Type'),
              const SizedBox(height: 8),
              Row(
                children: [
                  ChoiceChip(
                    label: const Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.email, size: 16),
                        SizedBox(width: 4),
                        Text('Email'),
                      ],
                    ),
                    selected: selectedType == 'email',
                    onSelected: (_) => setState(() => selectedType = 'email'),
                  ),
                  const SizedBox(width: 8),
                  ChoiceChip(
                    label: const Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.sms, size: 16),
                        SizedBox(width: 4),
                        Text('SMS'),
                      ],
                    ),
                    selected: selectedType == 'sms',
                    onSelected: (_) => setState(() => selectedType = 'sms'),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: () async {
                    if (nameController.text.isEmpty) return;
                    Navigator.pop(context);
                    await _provider.createCampaign({
                      'name': nameController.text,
                      'description': descController.text,
                      'campaign_type': selectedType,
                    });
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.teal,
                    padding: const EdgeInsets.symmetric(vertical: 12),
                  ),
                  child: const Text('Create'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showCampaignDetails(Campaign campaign) {
    _provider.loadCampaignAnalytics(campaign.id);
    
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
              const SizedBox(height: 16),
              Text(
                campaign.name,
                style: const TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
              ),
              if (campaign.description.isNotEmpty) ...[
                const SizedBox(height: 8),
                Text(
                  campaign.description,
                  style: TextStyle(color: Colors.grey.shade600),
                ),
              ],
              const SizedBox(height: 24),
              const Text(
                'Performance Metrics',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(child: _buildStatBox('Recipients', '${campaign.recipientCount}')),
                  const SizedBox(width: 12),
                  Expanded(child: _buildStatBox('Opens', '${campaign.openCount}')),
                  const SizedBox(width: 12),
                  Expanded(child: _buildStatBox('Clicks', '${campaign.clickCount}')),
                ],
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: _buildStatBox(
                      'Open Rate',
                      '${(campaign.openRate * 100).toStringAsFixed(1)}%',
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: _buildStatBox(
                      'Click Rate',
                      '${(campaign.clickRate * 100).toStringAsFixed(1)}%',
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 24),
              const Text(
                'Timeline',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 12),
              _buildTimelineItem(
                'Created',
                campaign.createdAt,
                Icons.create,
              ),
              if (campaign.scheduledAt != null)
                _buildTimelineItem(
                  'Scheduled',
                  campaign.scheduledAt!,
                  Icons.schedule,
                ),
              if (campaign.sentAt != null)
                _buildTimelineItem(
                  'Sent',
                  campaign.sentAt!,
                  Icons.send,
                ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStatBox(String label, String value) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey.shade100,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        children: [
          Text(
            value,
            style: const TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
            ),
          ),
          Text(
            label,
            style: TextStyle(color: Colors.grey.shade600),
          ),
        ],
      ),
    );
  }

  Widget _buildTimelineItem(String label, DateTime date, IconData icon) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: Colors.teal.shade50,
              shape: BoxShape.circle,
            ),
            child: Icon(icon, color: Colors.teal, size: 20),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(label, style: const TextStyle(fontWeight: FontWeight.bold)),
                Text(
                  _formatDateTime(date),
                  style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  String _formatDateTime(DateTime date) {
    return '${date.day}/${date.month}/${date.year} at ${date.hour}:${date.minute.toString().padLeft(2, '0')}';
  }

  void _scheduleCampaign(Campaign campaign) {
    DateTime selectedDate = DateTime.now().add(const Duration(hours: 1));

    showDatePicker(
      context: context,
      initialDate: selectedDate,
      firstDate: DateTime.now(),
      lastDate: DateTime.now().add(const Duration(days: 365)),
    ).then((date) {
      if (date != null) {
        if (!mounted) return;
        showTimePicker(
          context: context,
          initialTime: TimeOfDay.now(),
        ).then((time) {
          if (time != null) {
            if (!mounted) return;
            final scheduled = DateTime(
              date.year,
              date.month,
              date.day,
              time.hour,
              time.minute,
            );
            // Schedule campaign
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text('Campaign scheduled for ${_formatDateTime(scheduled)}'),
              ),
            );
          }
        });
      }
    });
  }

  void _sendCampaign(Campaign campaign) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Send Campaign'),
        content: Text('Are you sure you want to send "${campaign.name}" now?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              _provider.sendCampaign(campaign.id);
            },
            child: const Text('Send Now'),
          ),
        ],
      ),
    );
  }

  void _showFilterDialog() {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Filter Campaigns',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            Wrap(
              spacing: 8,
              children: ['All', 'Draft', 'Scheduled', 'Sent'].map((filter) {
                return FilterChip(
                  label: Text(filter),
                  selected: filter == 'All',
                  onSelected: (_) {
                    Navigator.pop(context);
                    // Apply filter
                  },
                );
              }).toList(),
            ),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }
}
