import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/constants/app_constants.dart';
import '../../models/crm_models.dart';
import '../../providers/leads_provider.dart';
import 'lead_detail_screen.dart';
import 'add_lead_screen.dart';

class LeadsScreen extends StatefulWidget {
  const LeadsScreen({super.key});
  
  @override
  State<LeadsScreen> createState() => _LeadsScreenState();
}

class _LeadsScreenState extends State<LeadsScreen> {
  final ScrollController _scrollController = ScrollController();
  
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<LeadsProvider>().fetchLeads(refresh: true);
    });

    _scrollController.addListener(_onScroll);
  }
  
  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  void _onScroll() {
    final provider = context.read<LeadsProvider>();
    if (_scrollController.position.pixels == _scrollController.position.maxScrollExtent) {
      if (provider.hasMore && !provider.isLoading) {
        provider.fetchLeads();
      }
    }
  }

  Future<void> _refreshLeads() async {
    await context.read<LeadsProvider>().fetchLeads(refresh: true);
  }
  
  void _navigateToAddLead() async {
    await Navigator.push<bool>(
      context,
      MaterialPageRoute(builder: (context) => const AddLeadScreen()),
    );
  }
  
  void _navigateToLeadDetail(Lead lead) async {
    await Navigator.push<bool>(
      context,
      MaterialPageRoute(
        builder: (context) => LeadDetailScreen(lead: lead),
      ),
    );
  }

  void _navigateToEditLead(Lead lead) async {
    await Navigator.push<bool>(
      context,
      MaterialPageRoute(
        builder: (context) => AddLeadScreen(lead: lead),
      ),
    );
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Consumer<LeadsProvider>(
        builder: (context, provider, child) {
          if (provider.isLoading && provider.leads.isEmpty) {
            return const Center(child: CircularProgressIndicator());
          }

          if (provider.error != null && provider.leads.isEmpty) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.error_outline, size: 48, color: AppColors.error),
                  const SizedBox(height: AppSizes.paddingMd),
                  Text('Error: ${provider.error}'),
                  TextButton(
                    onPressed: _refreshLeads,
                    child: const Text('Retry'),
                  ),
                ],
              ),
            );
          }

          return RefreshIndicator(
            onRefresh: _refreshLeads,
            child: provider.leads.isEmpty
                ? _buildEmptyState()
                : ListView.separated(
                    controller: _scrollController,
                    padding: const EdgeInsets.all(AppSizes.paddingMd),
                    itemCount: provider.leads.length + (provider.hasMore ? 1 : 0),
                    separatorBuilder: (context, index) => const SizedBox(height: AppSizes.paddingSm),
                    itemBuilder: (context, index) {
                      if (index == provider.leads.length) {
                        return const Center(
                          child: Padding(
                            padding: EdgeInsets.all(8.0),
                            child: CircularProgressIndicator(),
                          ),
                        );
                      }

                      final lead = provider.leads[index];
                      return _buildLeadCard(lead);
                    },
                  ),
          );
        },
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _navigateToAddLead,
        child: const Icon(Icons.add),
      ),
    );
  }
  
  Widget _buildLeadCard(Lead lead) {
    Color statusColor = _getStatusColor(lead.status ?? 'New');
    Color scoreColor = _getScoreColor(lead.score ?? 0);
    
    return Card(
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: scoreColor,
          child: Text(
            lead.initials,
            style: const TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        title: Row(
          children: [
            Expanded(
              child: Text(
                lead.fullName,
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
            ),
            if (lead.score != null)
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 8,
                  vertical: 4,
                ),
                decoration: BoxDecoration(
                  color: scoreColor.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(AppSizes.radiusSm),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(Icons.star, size: 14, color: scoreColor),
                    const SizedBox(width: 4),
                    Text(
                      '${lead.score}',
                      style: TextStyle(
                        fontSize: AppSizes.fontXs,
                        fontWeight: FontWeight.bold,
                        color: scoreColor,
                      ),
                    ),
                  ],
                ),
              ),
          ],
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (lead.company != null) Text(lead.company!),
            if (lead.email != null)
              Text(
                lead.email!,
                style: const TextStyle(fontSize: AppSizes.fontSm),
              ),
            const SizedBox(height: 4),
            Row(
              children: [
                if (lead.source != null)
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 6,
                      vertical: 2,
                    ),
                    decoration: BoxDecoration(
                      color: AppColors.grey200,
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Text(
                      lead.source!,
                      style: const TextStyle(
                        fontSize: 10,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),
                const SizedBox(width: 8),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 6,
                    vertical: 2,
                  ),
                  decoration: BoxDecoration(
                    color: statusColor.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    lead.status ?? 'Unknown',
                    style: TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.w600,
                      color: statusColor,
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
        trailing: IconButton(
          icon: const Icon(Icons.edit, size: 20),
          color: AppColors.grey500,
          onPressed: () => _navigateToEditLead(lead),
          padding: EdgeInsets.zero,
          constraints: const BoxConstraints(),
        ),
        isThreeLine: true,
        onTap: () => _navigateToLeadDetail(lead),
      ),
    );
  }
  
  Color _getStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'new':
        return AppColors.primary;
      case 'contacted':
        return AppColors.info;
      case 'qualified':
        return AppColors.success;
      case 'unqualified':
        return AppColors.error;
      case 'converted':
        return AppColors.secondary;
      default:
        return AppColors.grey500;
    }
  }
  
  Color _getScoreColor(int score) {
    if (score >= 80) return AppColors.success;
    if (score >= 60) return AppColors.warning;
    return AppColors.error;
  }
  
  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.person_add_outlined,
            size: 80,
            color: AppColors.grey400,
          ),
          const SizedBox(height: AppSizes.paddingMd),
          const Text(
            'No leads yet',
            style: TextStyle(
              fontSize: AppSizes.fontLg,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: AppSizes.paddingSm),
          Text(
            'Add your first lead to start nurturing',
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
