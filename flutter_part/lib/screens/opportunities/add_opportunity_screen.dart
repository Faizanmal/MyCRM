import 'package:flutter/material.dart';
import '../../core/constants/app_constants.dart';

class AddOpportunityScreen extends StatefulWidget {
  const AddOpportunityScreen({super.key});
  
  @override
  State<AddOpportunityScreen> createState() => _AddOpportunityScreenState();
}

class _AddOpportunityScreenState extends State<AddOpportunityScreen> {
  final _formKey = GlobalKey<FormState>();
  bool _isLoading = false;
  
  final _nameController = TextEditingController();
  final _amountController = TextEditingController();
  final _descriptionController = TextEditingController();
  
  DateTime _closeDate = DateTime.now().add(const Duration(days: 30));
  String _selectedStage = 'Prospecting';
  double _probability = 30;
  
  final List<String> _stageOptions = [
    'Prospecting',
    'Qualification',
    'Proposal',
    'Negotiation',
    'Closed Won',
    'Closed Lost',
  ];
  
  @override
  void dispose() {
    _nameController.dispose();
    _amountController.dispose();
    _descriptionController.dispose();
    super.dispose();
  }
  
  Future<void> _selectCloseDate() async {
    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: _closeDate,
      firstDate: DateTime.now(),
      lastDate: DateTime.now().add(const Duration(days: 365 * 2)),
    );
    
    if (picked != null) {
      setState(() => _closeDate = picked);
    }
  }
  
  void _updateProbabilityForStage(String stage) {
    setState(() {
      switch (stage) {
        case 'Prospecting':
          _probability = 10;
          break;
        case 'Qualification':
          _probability = 30;
          break;
        case 'Proposal':
          _probability = 50;
          break;
        case 'Negotiation':
          _probability = 75;
          break;
        case 'Closed Won':
          _probability = 100;
          break;
        case 'Closed Lost':
          _probability = 0;
          break;
      }
    });
  }
  
  Future<void> _saveOpportunity() async {
    if (!_formKey.currentState!.validate()) return;
    
    setState(() => _isLoading = true);
    
    await Future.delayed(const Duration(seconds: 1));
    
    if (mounted) {
      setState(() => _isLoading = false);
      
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Opportunity created successfully'),
          backgroundColor: AppColors.success,
        ),
      );
      
      Navigator.pop(context, true);
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Add Opportunity'),
        actions: [
          if (_isLoading)
            const Center(
              child: Padding(
                padding: EdgeInsets.all(AppSizes.paddingSm),
                child: SizedBox(
                  width: 24,
                  height: 24,
                  child: CircularProgressIndicator(strokeWidth: 2),
                ),
              ),
            )
          else
            TextButton(
              onPressed: _saveOpportunity,
              child: const Text(
                'Save',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
            ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(AppSizes.paddingMd),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Opportunity Info
              const Text(
                'Opportunity Information',
                style: TextStyle(
                  fontSize: AppSizes.fontMd,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: AppSizes.paddingSm),
              TextFormField(
                controller: _nameController,
                decoration: const InputDecoration(
                  labelText: 'Opportunity Name *',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.business_center),
                  hintText: 'e.g., Enterprise Software Deal',
                ),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Name is required';
                  }
                  return null;
                },
              ),
              const SizedBox(height: AppSizes.paddingSm),
              TextFormField(
                controller: _amountController,
                decoration: const InputDecoration(
                  labelText: 'Amount *',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.attach_money),
                  prefixText: '\$ ',
                ),
                keyboardType: TextInputType.number,
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Amount is required';
                  }
                  if (double.tryParse(value) == null) {
                    return 'Enter a valid amount';
                  }
                  return null;
                },
              ),
              const SizedBox(height: AppSizes.paddingLg),
              
              // Stage and Close Date
              const Text(
                'Pipeline Stage',
                style: TextStyle(
                  fontSize: AppSizes.fontMd,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: AppSizes.paddingSm),
              DropdownButtonFormField<String>(
                value: _selectedStage,
                decoration: const InputDecoration(
                  labelText: 'Stage',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.trending_up),
                ),
                items: _stageOptions.map((stage) {
                  return DropdownMenuItem(
                    value: stage,
                    child: Text(stage),
                  );
                }).toList(),
                onChanged: (value) {
                  setState(() => _selectedStage = value!);
                  _updateProbabilityForStage(value!);
                },
              ),
              const SizedBox(height: AppSizes.paddingSm),
              InkWell(
                onTap: _selectCloseDate,
                child: InputDecorator(
                  decoration: const InputDecoration(
                    labelText: 'Expected Close Date',
                    border: OutlineInputBorder(),
                    prefixIcon: Icon(Icons.calendar_today),
                  ),
                  child: Text(
                    '${_closeDate.day}/${_closeDate.month}/${_closeDate.year}',
                  ),
                ),
              ),
              const SizedBox(height: AppSizes.paddingLg),
              
              // Probability Slider
              const Text(
                'Win Probability',
                style: TextStyle(
                  fontSize: AppSizes.fontMd,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: AppSizes.paddingSm),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(AppSizes.paddingMd),
                  child: Column(
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text('Probability'),
                          Text(
                            '${_probability.toInt()}%',
                            style: TextStyle(
                              fontSize: AppSizes.fontLg,
                              fontWeight: FontWeight.bold,
                              color: _probability >= 70
                                  ? AppColors.success
                                  : _probability >= 40
                                      ? AppColors.warning
                                      : AppColors.error,
                            ),
                          ),
                        ],
                      ),
                      Slider(
                        value: _probability,
                        min: 0,
                        max: 100,
                        divisions: 20,
                        label: '${_probability.toInt()}%',
                        onChanged: (value) {
                          setState(() => _probability = value);
                        },
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: AppSizes.paddingLg),
              
              // Description
              const Text(
                'Description',
                style: TextStyle(
                  fontSize: AppSizes.fontMd,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: AppSizes.paddingSm),
              TextFormField(
                controller: _descriptionController,
                decoration: const InputDecoration(
                  labelText: 'Description',
                  border: OutlineInputBorder(),
                  alignLabelWithHint: true,
                ),
                maxLines: 4,
              ),
              const SizedBox(height: AppSizes.paddingXl),
              
              // Save button
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: _isLoading ? null : _saveOpportunity,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.primary,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: AppSizes.paddingMd),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(AppSizes.radiusMd),
                    ),
                  ),
                  child: _isLoading
                      ? const SizedBox(
                          width: 24,
                          height: 24,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                          ),
                        )
                      : const Text(
                          'Create Opportunity',
                          style: TextStyle(
                            fontSize: AppSizes.fontMd,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                ),
              ),
              const SizedBox(height: AppSizes.paddingLg),
            ],
          ),
        ),
      ),
    );
  }
}
