import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/constants/app_constants.dart';
import '../../models/crm_models.dart';
import '../../providers/leads_provider.dart';
import 'add_lead_screen.dart';

class LeadDetailScreen extends StatefulWidget {
  final Lead lead;
  
  const LeadDetailScreen({super.key, required this.lead});
  
  @override
  State<LeadDetailScreen> createState() => _LeadDetailScreenState();
}

class _LeadDetailScreenState extends State<LeadDetailScreen> {
  late Lead _lead;
  
  @override
  void initState() {
    super.initState();
    _lead = widget.lead;
  }
  
  void _editLead() async {
    await Navigator.push<bool>(
      context,
      MaterialPageRoute(
        builder: (context) => AddLeadScreen(lead: _lead),
      ),
    );

    if (mounted) {
      final updatedLead = context.read<LeadsProvider>()
          .leads.firstWhere((l) => l.id == _lead.id, orElse: () => _lead);
      setState(() {
        _lead = updatedLead;
      });
    }
  }
  
  Future<void> _deleteLead() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Lead'),
        content: Text('Are you sure you want to delete ${_lead.fullName}?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            style: TextButton.styleFrom(foregroundColor: AppColors.error),
            child: const Text('Delete'),
          ),
        ],
      ),
    );

    if (confirmed == true && mounted) {
      final success = await context.read<LeadsProvider>().deleteLead(_lead.id!);

      if (mounted) {
        if (success) {
          Navigator.pop(context, true);
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Lead deleted'),
              backgroundColor: AppColors.error,
            ),
          );
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Failed to delete lead'),
              backgroundColor: AppColors.error,
            ),
          );
        }
      }
    }
  }
  
  Future<void> _convertToOpportunity() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Convert to Opportunity'),
        content: Text('Convert "${_lead.title ?? 'Unknown Lead'}" to an opportunity?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Convert'),
          ),
        ],
      ),
    );
    
    if (confirmed == true && mounted) {
      final contact = await context.read<LeadsProvider>().convertLead(_lead.id!);

      if (mounted) {
        if (contact != null) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Lead converted to opportunity'),
              backgroundColor: AppColors.success,
            ),
          );
          Navigator.pop(context, true);
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Failed to convert lead'),
              backgroundColor: AppColors.error,
            ),
          );
        }
      }
    }
  }
  
  Color _getStatusColor(String? status) {
    switch (status?.toLowerCase()) {
      case 'new':
        return AppColors.info;
      case 'contacted':
        return AppColors.primary;
      case 'qualified':
        return AppColors.success;
      case 'unqualified':
        return AppColors.grey500;
      default:
        return AppColors.warning;
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Lead Details'),
        actions: [
          IconButton(
            icon: const Icon(Icons.edit),
            onPressed: _editLead,
          ),
          PopupMenuButton<String>(
            onSelected: (value) {
              if (value == 'delete') {
                _deleteLead();
              }
            },
            itemBuilder: (context) => [
              const PopupMenuItem(
                value: 'delete',
                child: Row(
                  children: [
                    Icon(Icons.delete, color: AppColors.error),
                    SizedBox(width: 8),
                    Text('Delete', style: TextStyle(color: AppColors.error)),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(AppSizes.paddingMd),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            _buildHeader(),
            const SizedBox(height: AppSizes.paddingLg),
            
            // Status and Score
            _buildStatusSection(),
            const SizedBox(height: AppSizes.paddingLg),
            
            // Lead Info
            _buildInfoSection(),
            const SizedBox(height: AppSizes.paddingLg),
            
            // Actions
            _buildActionsSection(),
          ],
        ),
      ),
    );
  }
  
  Widget _buildHeader() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(AppSizes.paddingMd),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              _lead.title ?? 'No Title',
              style: const TextStyle(
                fontSize: AppSizes.fontXl,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: AppSizes.paddingSm),
            Row(
              children: [
                Icon(Icons.business, size: 16, color: AppColors.grey500),
                const SizedBox(width: 4),
                Text(
                  _lead.company ?? 'No company',
                  style: TextStyle(color: AppColors.grey600),
                ),
                const SizedBox(width: AppSizes.paddingMd),
                Icon(Icons.source, size: 16, color: AppColors.grey500),
                const SizedBox(width: 4),
                Text(
                  _lead.source ?? 'Unknown source',
                  style: TextStyle(color: AppColors.grey600),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildStatusSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(AppSizes.paddingMd),
        child: Row(
          children: [
            Expanded(
              child: Column(
                children: [
                  const Text(
                    'Status',
                    style: TextStyle(
                      fontSize: AppSizes.fontSm,
                      color: Colors.grey,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: AppSizes.paddingSm,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      color: _getStatusColor(_lead.status).withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(AppSizes.radiusSm),
                    ),
                    child: Text(
                      _lead.status ?? 'New',
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        color: _getStatusColor(_lead.status),
                      ),
                    ),
                  ),
                ],
              ),
            ),
            Container(
              width: 1,
              height: 50,
              color: AppColors.grey200,
            ),
            Expanded(
              child: Column(
                children: [
                  const Text(
                    'Score',
                    style: TextStyle(
                      fontSize: AppSizes.fontSm,
                      color: Colors.grey,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.star, color: AppColors.warning, size: 20),
                      const SizedBox(width: 4),
                      Text(
                        '${_lead.score ?? 0}',
                        style: const TextStyle(
                          fontSize: AppSizes.fontLg,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            Container(
              width: 1,
              height: 50,
              color: AppColors.grey200,
            ),
            Expanded(
              child: Column(
                children: [
                  const Text(
                    'Value',
                    style: TextStyle(
                      fontSize: AppSizes.fontSm,
                      color: Colors.grey,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    _lead.estimatedValue != null
                        ? '\$${_lead.estimatedValue!.toStringAsFixed(0)}'
                        : 'N/A',
                    style: TextStyle(
                      fontSize: AppSizes.fontLg,
                      fontWeight: FontWeight.bold,
                      color: AppColors.success,
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
  
  Widget _buildInfoSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(AppSizes.paddingMd),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Contact Information',
              style: TextStyle(
                fontSize: AppSizes.fontLg,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: AppSizes.paddingMd),
            
            _buildInfoRow(Icons.email, 'Email', _lead.email ?? 'Not set'),
            _buildInfoRow(Icons.phone, 'Phone', _lead.phone ?? 'Not set'),
            _buildInfoRow(Icons.business, 'Company', _lead.company ?? 'Not set'),
            if (_lead.description != null)
              _buildInfoRow(Icons.description, 'Description', _lead.description!),
          ],
        ),
      ),
    );
  }
  
  Widget _buildInfoRow(IconData icon, String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: AppSizes.paddingSm),
      child: Row(
        children: [
          Icon(icon, color: AppColors.grey500, size: 20),
          const SizedBox(width: AppSizes.paddingSm),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  label,
                  style: TextStyle(
                    fontSize: AppSizes.fontSm,
                    color: AppColors.grey500,
                  ),
                ),
                Text(
                  value,
                  style: const TextStyle(fontSize: AppSizes.fontMd),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildActionsSection() {
    return Column(
      children: [
        SizedBox(
          width: double.infinity,
          child: ElevatedButton.icon(
            onPressed: _convertToOpportunity,
            icon: const Icon(Icons.trending_up),
            label: const Text('Convert to Opportunity'),
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.success,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: AppSizes.paddingMd),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(AppSizes.radiusMd),
              ),
            ),
          ),
        ),
        const SizedBox(height: AppSizes.paddingSm),
        SizedBox(
          width: double.infinity,
          child: OutlinedButton.icon(
            onPressed: () {
              // Add task for this lead
            },
            icon: const Icon(Icons.add_task),
            label: const Text('Add Task'),
            style: OutlinedButton.styleFrom(
              padding: const EdgeInsets.symmetric(vertical: AppSizes.paddingMd),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(AppSizes.radiusMd),
              ),
            ),
          ),
        ),
      ],
    );
  }
}
