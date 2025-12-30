import 'package:flutter/material.dart';
import '../../core/constants/app_constants.dart';
import '../../core/utils/date_formatter.dart';
import '../../models/crm_models.dart';
import 'opportunity_detail_screen.dart';
import 'add_opportunity_screen.dart';

class OpportunitiesScreen extends StatefulWidget {
  const OpportunitiesScreen({super.key});
  
  @override
  State<OpportunitiesScreen> createState() => _OpportunitiesScreenState();
}

class _OpportunitiesScreenState extends State<OpportunitiesScreen> {
  List<Opportunity> _opportunities = [];
  bool _isLoading = true;
  
  @override
  void initState() {
    super.initState();
    _loadOpportunities();
  }
  
  Future<void> _loadOpportunities() async {
    setState(() => _isLoading = true);
    
    await Future.delayed(const Duration(milliseconds: 800));
    
    setState(() {
      _opportunities = [
        Opportunity(
          id: 1,
          name: 'Enterprise Software Deal',
          amount: 150000,
          stage: 'Proposal',
          probability: 75,
          closeDate: DateTime.now().add(const Duration(days: 30)),
          contactName: 'John Doe',
        ),
        Opportunity(
          id: 2,
          name: 'Marketing Campaign',
          amount: 50000,
          stage: 'Negotiation',
          probability: 60,
          closeDate: DateTime.now().add(const Duration(days: 15)),
          contactName: 'Jane Smith',
        ),
        Opportunity(
          id: 3,
          name: 'Cloud Migration Project',
          amount: 250000,
          stage: 'Qualification',
          probability: 40,
          closeDate: DateTime.now().add(const Duration(days: 60)),
          contactName: 'Bob Johnson',
        ),
      ];
      _isLoading = false;
    });
  }
  
  void _navigateToAddOpportunity() async {
    final result = await Navigator.push<bool>(
      context,
      MaterialPageRoute(builder: (context) => const AddOpportunityScreen()),
    );
    
    if (result == true) {
      _loadOpportunities();
    }
  }
  
  void _navigateToOpportunityDetail(Opportunity opportunity) async {
    final result = await Navigator.push<bool>(
      context,
      MaterialPageRoute(
        builder: (context) => OpportunityDetailScreen(opportunity: opportunity),
      ),
    );
    
    if (result == true) {
      _loadOpportunities();
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _loadOpportunities,
              child: _opportunities.isEmpty
                  ? _buildEmptyState()
                  : ListView.separated(
                      padding: const EdgeInsets.all(AppSizes.paddingMd),
                      itemCount: _opportunities.length,
                      separatorBuilder: (context, index) => const SizedBox(height: AppSizes.paddingSm),
                      itemBuilder: (context, index) {
                        final opportunity = _opportunities[index];
                        return _buildOpportunityCard(opportunity);
                      },
                    ),
            ),
      floatingActionButton: FloatingActionButton(
        onPressed: _navigateToAddOpportunity,
        child: const Icon(Icons.add),
      ),
    );
  }
  
  Widget _buildOpportunityCard(Opportunity opportunity) {
    Color stageColor = _getStageColor(opportunity.stage ?? '');
    
    return Card(
      child: InkWell(
        onTap: () => _navigateToOpportunityDetail(opportunity),
        borderRadius: BorderRadius.circular(AppSizes.radiusMd),
        child: Padding(
          padding: const EdgeInsets.all(AppSizes.paddingMd),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Text(
                      opportunity.name,
                      style: const TextStyle(
                        fontSize: AppSizes.fontLg,
                        fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: AppSizes.paddingSm,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    color: stageColor.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(AppSizes.radiusSm),
                  ),
                  child: Text(
                    opportunity.stage ?? 'Unknown',
                    style: TextStyle(
                      fontSize: AppSizes.fontXs,
                      fontWeight: FontWeight.w600,
                      color: stageColor,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: AppSizes.paddingSm),
            
            // Amount
            if (opportunity.amount != null)
              Row(
                children: [
                  const Icon(Icons.attach_money, size: 18, color: AppColors.success),
                  const SizedBox(width: 4),
                  Text(
                    DateFormatter.formatCurrency(opportunity.amount!),
                    style: const TextStyle(
                      fontSize: AppSizes.fontLg,
                      fontWeight: FontWeight.bold,
                      color: AppColors.success,
                    ),
                  ),
                ],
              ),
            const SizedBox(height: AppSizes.paddingSm),
            
            // Probability
            if (opportunity.probability != null)
              Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Probability',
                          style: TextStyle(
                            fontSize: AppSizes.fontSm,
                            color: AppColors.grey600,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Row(
                          children: [
                            Expanded(
                              child: ClipRRect(
                                borderRadius: BorderRadius.circular(4),
                                child: LinearProgressIndicator(
                                  value: opportunity.probability! / 100,
                                  minHeight: 8,
                                  backgroundColor: AppColors.grey200,
                                  valueColor: AlwaysStoppedAnimation<Color>(
                                    _getProbabilityColor(opportunity.probability!),
                                  ),
                                ),
                              ),
                            ),
                            const SizedBox(width: 8),
                            Text(
                              '${opportunity.probability}%',
                              style: const TextStyle(
                                fontWeight: FontWeight.w600,
                                fontSize: AppSizes.fontSm,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            const SizedBox(height: AppSizes.paddingSm),
            
            const Divider(height: 1),
            const SizedBox(height: AppSizes.paddingSm),
            
            // Footer
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                if (opportunity.contactName != null)
                  Row(
                    children: [
                      const Icon(Icons.person, size: 16, color: AppColors.grey600),
                      const SizedBox(width: 4),
                      Text(
                        opportunity.contactName!,
                        style: TextStyle(
                          fontSize: AppSizes.fontSm,
                          color: AppColors.grey600,
                        ),
                      ),
                    ],
                  ),
                if (opportunity.closeDate != null)
                  Row(
                    children: [
                      const Icon(Icons.calendar_today, size: 16, color: AppColors.grey600),
                      const SizedBox(width: 4),
                      Text(
                        DateFormatter.formatDate(opportunity.closeDate!),
                        style: TextStyle(
                          fontSize: AppSizes.fontSm,
                          color: AppColors.grey600,
                        ),
                      ),
                    ],
                  ),
              ],
            ),
          ],
        ),
        ),
      ),
    );
  }
  
  Color _getStageColor(String stage) {
    switch (stage.toLowerCase()) {
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
  
  Color _getProbabilityColor(double probability) {
    if (probability >= 70) return AppColors.success;
    if (probability >= 40) return AppColors.warning;
    return AppColors.error;
  }
  
  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.trending_up_outlined,
            size: 80,
            color: AppColors.grey400,
          ),
          const SizedBox(height: AppSizes.paddingMd),
          const Text(
            'No opportunities yet',
            style: TextStyle(
              fontSize: AppSizes.fontLg,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: AppSizes.paddingSm),
          Text(
            'Create opportunities to track your deals',
            style: TextStyle(
              fontSize: AppSizes.fontMd,
              color: AppColors.grey600,
            ),
          ),
        ],
      ),
    );
  }
}
