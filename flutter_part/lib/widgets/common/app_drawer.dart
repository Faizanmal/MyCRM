import 'package:flutter/material.dart';
import '../../screens/dashboard/dashboard_screen.dart';
import '../../screens/contacts/contacts_screen.dart';
import '../../screens/leads/leads_screen.dart';
import '../../screens/opportunities/opportunities_screen.dart';
import '../../screens/tasks/tasks_screen.dart';
import '../../screens/communications/communications_screen.dart';
import '../../screens/campaigns/campaigns_screen.dart';
import '../../screens/reports/reports_screen.dart';
import '../../screens/documents/documents_screen.dart';
import '../../screens/esign/esign_screen.dart';
import '../../screens/conversation_ai/conversation_intelligence_screen.dart';
import '../../screens/integration_hub/integration_hub_screen.dart';
import '../../screens/ai_insights/ai_insights_screen.dart';
import '../../screens/gamification/gamification_screen.dart';
import '../../screens/revenue/revenue_intelligence_screen.dart';
import '../../screens/email_tracking/email_tracking_screen.dart';
import '../../screens/scheduling/scheduling_screen.dart';

class AppDrawer extends StatelessWidget {
  const AppDrawer({super.key});

  @override
  Widget build(BuildContext context) {
    return Drawer(
      child: Column(
        children: [
          _buildHeader(context),
          Expanded(
            child: ListView(
              padding: EdgeInsets.zero,
              children: [
                _buildSection('Main'),
                _buildNavItem(context, Icons.dashboard, 'Dashboard', const DashboardScreen()),
                _buildNavItem(context, Icons.people, 'Contacts', const ContactsScreen()),
                _buildNavItem(context, Icons.trending_up, 'Leads', const LeadsScreen()),
                _buildNavItem(context, Icons.business_center, 'Opportunities', const OpportunitiesScreen()),
                _buildNavItem(context, Icons.task_alt, 'Tasks', const TasksScreen()),
                _buildNavItem(context, Icons.message, 'Communications', const CommunicationsScreen()),
                
                const Divider(),
                _buildSection('Sales & Marketing'),
                _buildNavItem(context, Icons.campaign, 'Campaigns', const CampaignsScreen()),
                _buildNavItem(context, Icons.attach_money, 'Revenue', const RevenueIntelligenceScreen()),
                _buildNavItem(context, Icons.mail, 'Email Tracking', const EmailTrackingScreen()),
                _buildNavItem(context, Icons.schedule, 'Scheduling', const SchedulingScreen()),
                
                const Divider(),
                _buildSection('Tools'),
                _buildNavItem(context, Icons.analytics, 'Reports', const ReportsScreen()),
                _buildNavItem(context, Icons.folder, 'Documents', const DocumentsScreen()),
                _buildNavItem(context, Icons.draw, 'E-Signatures', const EsignScreen()),
                _buildNavItem(context, Icons.mic, 'Conversation AI', const ConversationIntelligenceScreen()),
                
                const Divider(),
                _buildSection('Advanced'),
                _buildNavItem(context, Icons.hub, 'Integrations', const IntegrationHubScreen()),
                _buildNavItem(context, Icons.psychology, 'AI Insights', const AIInsightsScreen()),
                _buildNavItem(context, Icons.emoji_events, 'Gamification', const GamificationScreen()),
                
                const Divider(),
                _buildSection('Account'),
                _buildNavItem(context, Icons.settings, 'Settings', null, onTap: () => _showSettings(context)),
                _buildNavItem(context, Icons.help, 'Help & Support', null, onTap: () => _showHelp(context)),
                _buildNavItem(context, Icons.logout, 'Logout', null, onTap: () => _logout(context), isDestructive: true),
              ],
            ),
          ),
          _buildFooter(context),
        ],
      ),
    );
  }

  Widget _buildHeader(BuildContext context) {
    return Container(
      padding: EdgeInsets.only(top: MediaQuery.of(context).padding.top + 16, left: 16, right: 16, bottom: 16),
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          colors: [Color(0xFF1E3A8A), Color(0xFF3B82F6)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(2),
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              border: Border.all(color: Colors.white, width: 2),
            ),
            child: const CircleAvatar(
              radius: 28,
              backgroundColor: Colors.white24,
              child: Text('JD', style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('John Doe', style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.w600)),
                const SizedBox(height: 2),
                Text('Sales Manager', style: TextStyle(color: Colors.white.withValues(alpha: 0.8), fontSize: 12)),
                const SizedBox(height: 4),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                  decoration: BoxDecoration(
                    color: Colors.green.withValues(alpha: 0.3),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.circle, size: 8, color: Colors.greenAccent),
                      SizedBox(width: 4),
                      Text('Online', style: TextStyle(color: Colors.white, fontSize: 10)),
                    ],
                  ),
                ),
              ],
            ),
          ),
          IconButton(
            icon: const Icon(Icons.notifications_outlined, color: Colors.white),
            onPressed: () => _showNotifications(context),
          ),
        ],
      ),
    );
  }

  Widget _buildSection(String title) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
      child: Text(
        title.toUpperCase(),
        style: TextStyle(
          fontSize: 11,
          fontWeight: FontWeight.w600,
          color: Colors.grey[500],
          letterSpacing: 1.2,
        ),
      ),
    );
  }

  Widget _buildNavItem(
    BuildContext context, 
    IconData icon, 
    String title, 
    Widget? destination, {
    VoidCallback? onTap,
    bool isDestructive = false,
  }) {
    final color = isDestructive ? Colors.red : null;
    
    return ListTile(
      leading: Icon(icon, color: color, size: 22),
      title: Text(title, style: TextStyle(color: color, fontSize: 14)),
      dense: true,
      onTap: () {
        Navigator.pop(context); // Close drawer
        if (onTap != null) {
          onTap();
        } else if (destination != null) {
          Navigator.pushReplacement(
            context,
            MaterialPageRoute(builder: (_) => destination),
          );
        }
      },
    );
  }

  Widget _buildFooter(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        border: Border(top: BorderSide(color: Colors.grey[200]!)),
      ),
      child: Row(
        children: [
          const Icon(Icons.cloud_sync, size: 16, color: Colors.green),
          const SizedBox(width: 8),
          Text('Synced just now', style: TextStyle(fontSize: 12, color: Colors.grey[600])),
          const Spacer(),
          Text('v2.1.0', style: TextStyle(fontSize: 12, color: Colors.grey[400])),
        ],
      ),
    );
  }

  void _showSettings(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(16))),
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
              Center(child: Container(width: 40, height: 4, decoration: BoxDecoration(color: Colors.grey[300], borderRadius: BorderRadius.circular(2)))),
              const SizedBox(height: 16),
              const Text('Settings', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
              const SizedBox(height: 24),
              _buildSettingsSection('Account', [
                _buildSettingItem(Icons.person, 'Profile', 'Edit your profile information'),
                _buildSettingItem(Icons.security, 'Security', 'Password, 2FA settings'),
                _buildSettingItem(Icons.notifications, 'Notifications', 'Configure alerts'),
              ]),
              _buildSettingsSection('Preferences', [
                _buildSettingItem(Icons.dark_mode, 'Appearance', 'Dark mode, themes'),
                _buildSettingItem(Icons.language, 'Language', 'English (US)'),
                _buildSettingItem(Icons.access_time, 'Timezone', 'UTC-8 (Pacific)'),
              ]),
              _buildSettingsSection('Data', [
                _buildSettingItem(Icons.sync, 'Sync Settings', 'Offline sync preferences'),
                _buildSettingItem(Icons.download, 'Export Data', 'Download your data'),
                _buildSettingItem(Icons.delete_outline, 'Clear Cache', 'Free up storage'),
              ]),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSettingsSection(String title, List<Widget> items) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(title, style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600, color: Colors.grey[600])),
        const SizedBox(height: 8),
        ...items,
        const SizedBox(height: 16),
      ],
    );
  }

  Widget _buildSettingItem(IconData icon, String title, String subtitle) {
    return ListTile(
      leading: Container(
        padding: const EdgeInsets.all(8),
        decoration: BoxDecoration(
          color: Colors.grey[100],
          borderRadius: BorderRadius.circular(8),
        ),
        child: Icon(icon, size: 20),
      ),
      title: Text(title),
      subtitle: Text(subtitle, style: TextStyle(fontSize: 12, color: Colors.grey[600])),
      trailing: const Icon(Icons.chevron_right),
      onTap: () {},
    );
  }

  void _showHelp(BuildContext context) {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(16))),
      builder: (context) => Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text('Help & Support', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
            const SizedBox(height: 24),
            ListTile(
              leading: const Icon(Icons.book, color: Colors.blue),
              title: const Text('Documentation'),
              subtitle: const Text('View guides and tutorials'),
              onTap: () {},
            ),
            ListTile(
              leading: const Icon(Icons.chat, color: Colors.green),
              title: const Text('Live Chat'),
              subtitle: const Text('Chat with support team'),
              onTap: () {},
            ),
            ListTile(
              leading: const Icon(Icons.email, color: Colors.orange),
              title: const Text('Email Support'),
              subtitle: const Text('support@mycrm.com'),
              onTap: () {},
            ),
            ListTile(
              leading: const Icon(Icons.bug_report, color: Colors.red),
              title: const Text('Report a Bug'),
              subtitle: const Text('Help us improve'),
              onTap: () {},
            ),
          ],
        ),
      ),
    );
  }

  void _showNotifications(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(16))),
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.6,
        minChildSize: 0.4,
        maxChildSize: 0.9,
        expand: false,
        builder: (context, scrollController) => Column(
          children: [
            Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  const Text('Notifications', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
                  const Spacer(),
                  TextButton(onPressed: () {}, child: const Text('Mark all read')),
                ],
              ),
            ),
            Expanded(
              child: ListView(
                controller: scrollController,
                children: [
                  _buildNotification('New lead assigned', 'Acme Corp - John Smith', '5m ago', Icons.person_add, Colors.blue),
                  _buildNotification('Deal closed', 'TechStart Pro Plan - \$28,500', '1h ago', Icons.celebration, Colors.green),
                  _buildNotification('Task due soon', 'Follow up call with Mike', '2h ago', Icons.alarm, Colors.orange),
                  _buildNotification('New comment', 'Sarah commented on your deal', '3h ago', Icons.comment, Colors.purple),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildNotification(String title, String subtitle, String time, IconData icon, Color color) {
    return ListTile(
      leading: Container(
        padding: const EdgeInsets.all(10),
        decoration: BoxDecoration(
          color: color.withValues(alpha: 0.1),
          shape: BoxShape.circle,
        ),
        child: Icon(icon, color: color, size: 20),
      ),
      title: Text(title, style: const TextStyle(fontWeight: FontWeight.w500)),
      subtitle: Text(subtitle),
      trailing: Text(time, style: TextStyle(fontSize: 12, color: Colors.grey[500])),
    );
  }

  void _logout(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Logout'),
        content: const Text('Are you sure you want to logout?'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              // Perform logout
            },
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('Logout'),
          ),
        ],
      ),
    );
  }
}
