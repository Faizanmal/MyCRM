import 'package:flutter/material.dart';
import '../../core/constants/app_constants.dart';
import '../../core/utils/date_formatter.dart';
import '../../models/crm_models.dart';

class OpportunityDetailScreen extends StatefulWidget {
  final Opportunity opportunity;
  
  const OpportunityDetailScreen({super.key, required this.opportunity});
  
  @override
  State<OpportunityDetailScreen> createState() => _OpportunityDetailScreenState();
}

class _OpportunityDetailScreenState extends State<OpportunityDetailScreen> {
  late Opportunity _opportunity;
  bool _isEditing = false;
  
  late TextEditingController _nameController;
  late TextEditingController _amountController;
  late TextEditingController _descriptionController;
  
  @override
  void initState() {
    super.initState();
    _opportunity = widget.opportunity;
    _initControllers();
  }
  
  void _initControllers() {
    _nameController = TextEditingController(text: _opportunity.name);
    _amountController = TextEditingController(
      text: _opportunity.amount?.toString() ?? '',
    );
    _descriptionController = TextEditingController(
      text: _opportunity.description ?? '',
    );
  }
  
  @override
  void dispose() {
    _nameController.dispose();
    _amountController.dispose();
    _descriptionController.dispose();
    super.dispose();
  }
  
  Color _getStageColor(String? stage) {
    switch (stage?.toLowerCase()) {
      case 'prospecting':
        return AppColors.info;
      case 'qualification':
        return AppColors.primary;
      case 'proposal':
        return AppColors.warning;
      case 'negotiation':
        return AppColors.secondary;
      case 'closed won':
        return AppColors.success;
      case 'closed lost':
        return AppColors.error;
      default:
        return AppColors.grey500;
    }
  }
  
  Color _getProbabilityColor(double? probability) {
    if (probability == null) return AppColors.grey500;
    if (probability >= 70) return AppColors.success;
    if (probability >= 40) return AppColors.warning;
    return AppColors.error;
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_isEditing ? 'Edit Opportunity' : 'Opportunity Details'),
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
            // Header Card
            _buildHeaderCard(),
            const SizedBox(height: AppSizes.paddingLg),
            
            // Metrics Card
            _buildMetricsCard(),
            const SizedBox(height: AppSizes.paddingLg),
            
            // Details Card
            _buildDetailsCard(),
            const SizedBox(height: AppSizes.paddingLg),
            
            // Pipeline Stage
            if (!_isEditing) _buildPipelineStages(),
            
            if (_isEditing) ...[
              const SizedBox(height: AppSizes.paddingLg),
              _buildSaveButton(),
            ],
          ],
        ),
      ),
    );
  }
  
  Widget _buildHeaderCard() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(AppSizes.paddingMd),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (_isEditing)
              TextField(
                controller: _nameController,
                decoration: const InputDecoration(
                  labelText: 'Opportunity Name',
                  border: OutlineInputBorder(),
                ),
                style: const TextStyle(
                  fontSize: AppSizes.fontLg,
                  fontWeight: FontWeight.bold,
                ),
              )
            else ...[
              Text(
                _opportunity.name,
                style: const TextStyle(
                  fontSize: AppSizes.fontXl,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: AppSizes.paddingSm),
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: AppSizes.paddingSm,
                  vertical: 4,
                ),
                decoration: BoxDecoration(
                  color: _getStageColor(_opportunity.stage).withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(AppSizes.radiusSm),
                ),
                child: Text(
                  _opportunity.stage ?? 'Unknown Stage',
                  style: TextStyle(
                    fontSize: AppSizes.fontSm,
                    fontWeight: FontWeight.bold,
                    color: _getStageColor(_opportunity.stage),
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
  
  Widget _buildMetricsCard() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(AppSizes.paddingMd),
        child: Row(
          children: [
            Expanded(
              child: Column(
                children: [
                  const Text(
                    'Amount',
                    style: TextStyle(fontSize: AppSizes.fontSm, color: Colors.grey),
                  ),
                  const SizedBox(height: 8),
                  if (_isEditing)
                    TextField(
                      controller: _amountController,
                      decoration: const InputDecoration(
                        prefixText: '\$ ',
                        border: OutlineInputBorder(),
                      ),
                      keyboardType: TextInputType.number,
                    )
                  else
                    Text(
                      _opportunity.amount != null
                          ? DateFormatter.formatCurrency(_opportunity.amount!)
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
            if (!_isEditing) ...[
              Container(
                width: 1,
                height: 50,
                color: AppColors.grey200,
              ),
              Expanded(
                child: Column(
                  children: [
                    const Text(
                      'Probability',
                      style: TextStyle(fontSize: AppSizes.fontSm, color: Colors.grey),
                    ),
                    const SizedBox(height: 8),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(
                          '${_opportunity.probability?.toInt() ?? 0}%',
                          style: TextStyle(
                            fontSize: AppSizes.fontLg,
                            fontWeight: FontWeight.bold,
                            color: _getProbabilityColor(_opportunity.probability),
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
                      'Close Date',
                      style: TextStyle(fontSize: AppSizes.fontSm, color: Colors.grey),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      _opportunity.closeDate != null
                          ? DateFormatter.formatDate(_opportunity.closeDate!)
                          : 'N/A',
                      style: const TextStyle(
                        fontSize: AppSizes.fontMd,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
  
  Widget _buildDetailsCard() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(AppSizes.paddingMd),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Details',
              style: TextStyle(
                fontSize: AppSizes.fontLg,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: AppSizes.paddingMd),
            
            if (_isEditing)
              TextField(
                controller: _descriptionController,
                decoration: const InputDecoration(
                  labelText: 'Description',
                  border: OutlineInputBorder(),
                  alignLabelWithHint: true,
                ),
                maxLines: 4,
              )
            else ...[
              _buildInfoRow(
                Icons.person,
                'Contact',
                _opportunity.contactName ?? 'Not assigned',
              ),
              if (_opportunity.description != null)
                _buildInfoRow(
                  Icons.description,
                  'Description',
                  _opportunity.description!,
                ),
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
        crossAxisAlignment: CrossAxisAlignment.start,
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
  
  Widget _buildPipelineStages() {
    final stages = [
      'Prospecting',
      'Qualification',
      'Proposal',
      'Negotiation',
      'Closed Won',
    ];
    
    final currentIndex = stages.indexWhere(
      (s) => s.toLowerCase() == _opportunity.stage?.toLowerCase(),
    );
    
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(AppSizes.paddingMd),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Pipeline Progress',
              style: TextStyle(
                fontSize: AppSizes.fontLg,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: AppSizes.paddingMd),
            Row(
              children: stages.asMap().entries.map((entry) {
                final index = entry.key;
                final stage = entry.value;
                final isActive = index <= currentIndex;
                final isCurrent = index == currentIndex;
                
                return Expanded(
                  child: Column(
                    children: [
                      Container(
                        width: 24,
                        height: 24,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: isActive ? AppColors.primary : AppColors.grey200,
                          border: isCurrent
                              ? Border.all(color: AppColors.primary, width: 3)
                              : null,
                        ),
                        child: isActive
                            ? Icon(
                                Icons.check,
                                size: 14,
                                color: Colors.white,
                              )
                            : null,
                      ),
                      const SizedBox(height: 4),
                      Text(
                        stage.split(' ').first,
                        style: TextStyle(
                          fontSize: 8,
                          color: isActive ? AppColors.primary : AppColors.grey500,
                          fontWeight: isCurrent ? FontWeight.bold : FontWeight.normal,
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ],
                  ),
                );
              }).toList(),
            ),
          ],
        ),
      ),
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
              content: Text('Opportunity updated successfully'),
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
