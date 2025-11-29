import 'package:flutter/material.dart';
import '../../core/constants/app_constants.dart';
import '../../models/crm_models.dart';

class LeadsScreen extends StatefulWidget {
  const LeadsScreen({super.key});
  
  @override
  State<LeadsScreen> createState() => _LeadsScreenState();
}

class _LeadsScreenState extends State<LeadsScreen> {
  List<Lead> _leads = [];
  bool _isLoading = true;
  
  @override
  void initState() {
    super.initState();
    _loadLeads();
  }
  
  Future<void> _loadLeads() async {
    setState(() => _isLoading = true);
    
    await Future.delayed(const Duration(milliseconds: 800));
    
    setState(() {
      _leads = [
        Lead(
          id: 1,
          firstName: 'Alice',
          lastName: 'Williams',
          email: 'alice.w@example.com',
          phone: '+1234567893',
          company: 'StartupXYZ',
          source: 'Website',
          status: 'New',
          score: 85,
        ),
        Lead(
          id: 2,
          firstName: 'Charlie',
          lastName: 'Brown',
          email: 'charlie.b@example.com',
          phone: '+1234567894',
          company: 'Enterprise Co',
          source: 'Referral',
          status: 'Contacted',
          score: 72,
        ),
        Lead(
          id: 3,
          firstName: 'Diana',
          lastName: 'Prince',
          email: 'diana.p@example.com',
          phone: '+1234567895',
          company: 'Innovation Labs',
          source: 'Social Media',
          status: 'Qualified',
          score: 95,
        ),
      ];
      _isLoading = false;
    });
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _loadLeads,
              child: _leads.isEmpty
                  ? _buildEmptyState()
                  : ListView.separated(
                      padding: const EdgeInsets.all(AppSizes.paddingMd),
                      itemCount: _leads.length,
                      separatorBuilder: (context, index) => const SizedBox(height: AppSizes.paddingSm),
                      itemBuilder: (context, index) {
                        final lead = _leads[index];
                        return _buildLeadCard(lead);
                      },
                    ),
            ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          // TODO: Navigate to add lead screen
        },
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
        isThreeLine: true,
        onTap: () {
          // TODO: Navigate to lead detail screen
        },
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
