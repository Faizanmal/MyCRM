import 'package:flutter/material.dart';
import '../../core/constants/app_constants.dart';
import '../../models/crm_models.dart';

class LeadDetailScreen extends StatefulWidget {
  final Lead lead;
  
  const LeadDetailScreen({super.key, required this.lead});
  
  @override
  State<LeadDetailScreen> createState() => _LeadDetailScreenState();
}

class _LeadDetailScreenState extends State<LeadDetailScreen> {
  late Lead _lead;
  bool _isEditing = false;
  
  late TextEditingController _titleController;
  late TextEditingController _companyController;
  late TextEditingController _emailController;
  late TextEditingController _phoneController;
  late TextEditingController _descriptionController;
  
  @override
  void initState() {
    super.initState();
    _lead = widget.lead;
    _initControllers();
  }
  
  void _initControllers() {
    _titleController = TextEditingController(text: _lead.title);
    _companyController = TextEditingController(text: _lead.company ?? '');
    _emailController = TextEditingController(text: _lead.email ?? '');
    _phoneController = TextEditingController(text: _lead.phone ?? '');
    _descriptionController = TextEditingController(text: _lead.description ?? '');
  }
  
  @override
  void dispose() {
    _titleController.dispose();
    _companyController.dispose();
    _emailController.dispose();
    _phoneController.dispose();
    _descriptionController.dispose();
    super.dispose();
  }
  
  Future<void> _convertToOpportunity() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Convert to Opportunity'),
        content: Text('Convert "${_lead.title}" to an opportunity?'),
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
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Lead converted to opportunity'),
          backgroundColor: AppColors.success,
        ),
      );
      Navigator.pop(context, true);
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
        title: Text(_isEditing ? 'Edit Lead' : 'Lead Details'),
        actions: [
          if (!_isEditing)
            IconButton(
              icon: const Icon(Icons.edit),
              onPressed: () => setState(() => _isEditing = true),
            ),
          if (_isEditing)
            IconButton(
              icon: const Icon(Icons.close),
              onPressed: () {
                setState(() => _isEditing = false);
                _initControllers();
              },
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
            if (!_isEditing) _buildActionsSection(),
            
            if (_isEditing) ...[
              const SizedBox(height: AppSizes.paddingLg),
              _buildSaveButton(),
            ],
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
            if (_isEditing)
              TextFormField(
                controller: _titleController,
                decoration: const InputDecoration(
                  labelText: 'Lead Title',
                  border: OutlineInputBorder(),
                ),
                style: const TextStyle(
                  fontSize: AppSizes.fontLg,
                  fontWeight: FontWeight.bold,
                ),
              )
            else
              Text(
                _lead.title,
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
            
            if (_isEditing) ...[
              TextField(
                controller: _emailController,
                decoration: const InputDecoration(
                  labelText: 'Email',
                  prefixIcon: Icon(Icons.email),
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: AppSizes.paddingSm),
              TextField(
                controller: _phoneController,
                decoration: const InputDecoration(
                  labelText: 'Phone',
                  prefixIcon: Icon(Icons.phone),
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: AppSizes.paddingSm),
              TextField(
                controller: _companyController,
                decoration: const InputDecoration(
                  labelText: 'Company',
                  prefixIcon: Icon(Icons.business),
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: AppSizes.paddingSm),
              TextField(
                controller: _descriptionController,
                decoration: const InputDecoration(
                  labelText: 'Description',
                  prefixIcon: Icon(Icons.description),
                  border: OutlineInputBorder(),
                ),
                maxLines: 3,
              ),
            ] else ...[
              _buildInfoRow(Icons.email, 'Email', _lead.email ?? 'Not set'),
              _buildInfoRow(Icons.phone, 'Phone', _lead.phone ?? 'Not set'),
              _buildInfoRow(Icons.business, 'Company', _lead.company ?? 'Not set'),
              if (_lead.description != null)
                _buildInfoRow(Icons.description, 'Description', _lead.description!),
            ],
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
  
  Widget _buildSaveButton() {
    return SizedBox(
      width: double.infinity,
      child: ElevatedButton(
        onPressed: () {
          setState(() => _isEditing = false);
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Lead updated successfully'),
              backgroundColor: AppColors.success,
            ),
          );
        },
        style: ElevatedButton.styleFrom(
          backgroundColor: AppColors.primary,
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(vertical: AppSizes.paddingMd),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(AppSizes.radiusMd),
          ),
        ),
        child: const Text(
          'Save Changes',
          style: TextStyle(
            fontSize: AppSizes.fontMd,
            fontWeight: FontWeight.bold,
          ),
        ),
      ),
    );
  }
}
