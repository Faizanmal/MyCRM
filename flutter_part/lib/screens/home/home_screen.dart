import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../core/constants/app_constants.dart';
import '../../services/notifications/notification_service.dart';
import '../dashboard/dashboard_screen.dart';
import '../contacts/contacts_screen.dart';
import '../leads/leads_screen.dart';
import '../opportunities/opportunities_screen.dart';
import '../tasks/tasks_screen.dart';
import '../auth/login_screen.dart';
import '../integration_hub/integration_hub_screen.dart';
import '../ai_insights/ai_insights_screen.dart';
import '../gamification/gamification_screen.dart';
import '../campaigns/campaigns_screen.dart';
import '../revenue/revenue_intelligence_screen.dart';
import '../ai_assistant/ai_assistant_screen.dart';
import '../social_selling/social_selling_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});
  
  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _selectedIndex = 0;

  @override
  void initState() {
    super.initState();
    // Initialize notifications when home screen loads
    WidgetsBinding.instance.addPostFrameCallback((_) {
      NotificationService().init();
    });
  }
  
  final List<Widget> _screens = [
    const DashboardScreen(),
    const ContactsScreen(),
    const LeadsScreen(),
    const OpportunitiesScreen(),
    const TasksScreen(),
  ];
  
  final List<NavigationDestination> _destinations = const [
    NavigationDestination(
      icon: Icon(Icons.dashboard_outlined),
      selectedIcon: Icon(Icons.dashboard, color: AppColors.primary),
      label: 'Dashboard',
    ),
    NavigationDestination(
      icon: Icon(Icons.people_outline),
      selectedIcon: Icon(Icons.people, color: AppColors.primary),
      label: 'Contacts',
    ),
    NavigationDestination(
      icon: Icon(Icons.person_add_outlined),
      selectedIcon: Icon(Icons.person_add, color: AppColors.primary),
      label: 'Leads',
    ),
    NavigationDestination(
      icon: Icon(Icons.trending_up_outlined),
      selectedIcon: Icon(Icons.trending_up, color: AppColors.primary),
      label: 'Deals',
    ),
    NavigationDestination(
      icon: Icon(Icons.task_outlined),
      selectedIcon: Icon(Icons.task, color: AppColors.primary),
      label: 'Tasks',
    ),
  ];
  
  @override
  Widget build(BuildContext context) {
    final authProvider = Provider.of<AuthProvider>(context);
    final user = authProvider.user;
    
    return Scaffold(
      appBar: AppBar(
        title: Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
          decoration: BoxDecoration(
            gradient: AppColors.primaryGradient,
            borderRadius: BorderRadius.circular(AppSizes.radiusMd),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.auto_awesome, color: Colors.white, size: 20),
              const SizedBox(width: 8),
              Text(
                AppConstants.appName,
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: AppSizes.fontLg,
                ),
              ),
            ],
          ),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.notifications_outlined),
            onPressed: () => _showNotificationsSheet(),
          ),
          IconButton(
            icon: const Icon(Icons.search),
            onPressed: () => _showSearchDialog(),
          ),
          const SizedBox(width: 8),
        ],
      ),
      drawer: _buildDrawer(authProvider, user),
      body: _screens[_selectedIndex],
      bottomNavigationBar: NavigationBar(
        selectedIndex: _selectedIndex,
        onDestinationSelected: (index) {
          setState(() => _selectedIndex = index);
        },
        destinations: _destinations,
      ),
    );
  }

  Widget _buildDrawer(AuthProvider authProvider, dynamic user) {
    return Drawer(
      child: ListView(
        padding: EdgeInsets.zero,
        children: [
          UserAccountsDrawerHeader(
            decoration: const BoxDecoration(
              gradient: AppColors.primaryGradient,
            ),
            accountName: Text(
              user?.fullName ?? 'User',
              style: const TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: AppSizes.fontLg,
              ),
            ),
            accountEmail: Text(user?.email ?? ''),
            currentAccountPicture: CircleAvatar(
              backgroundColor: Colors.white,
              child: Text(
                user?.initials ?? 'U',
                style: const TextStyle(
                  fontSize: AppSizes.font2xl,
                  fontWeight: FontWeight.bold,
                  color: AppColors.primary,
                ),
              ),
            ),
          ),
          
          // Main Navigation
          _buildSectionHeader('Main'),
          _buildDrawerItem(Icons.dashboard, 'Dashboard', 0),
          _buildDrawerItem(Icons.people, 'Contacts', 1),
          _buildDrawerItem(Icons.person_add, 'Leads', 2),
          _buildDrawerItem(Icons.trending_up, 'Opportunities', 3),
          _buildDrawerItem(Icons.task, 'Tasks', 4),
          
          const Divider(),
          
          // Advanced Features
          _buildSectionHeader('✨ Advanced'),
          _buildNavigationItem(
            Icons.extension,
            'Integration Hub',
            () => _navigateTo(const IntegrationHubScreen()),
          ),
          _buildNavigationItem(
            Icons.psychology,
            'AI Insights',
            () => _navigateTo(const AIInsightsScreen()),
          ),
          _buildNavigationItem(
            Icons.emoji_events,
            'Gamification',
            () => _navigateTo(const GamificationScreen()),
          ),
          
          const Divider(),
          
          // Sales & Marketing
          _buildSectionHeader('📊 Sales & Marketing'),
          _buildNavigationItem(
            Icons.campaign,
            'Campaigns',
            () => _navigateTo(const CampaignsScreen()),
          ),
          _buildNavigationItem(
            Icons.attach_money,
            'Revenue Intelligence',
            () => _navigateTo(const RevenueIntelligenceScreen()),
          ),
          _buildNavigationItem(
            Icons.email,
            'Email Tracking',
            () => _showComingSoon('Email Tracking'),
          ),
          _buildNavigationItem(
            Icons.calendar_today,
            'Scheduling',
            () => _showComingSoon('Smart Scheduling'),
          ),
          _buildNavigationItem(
            Icons.auto_awesome,
            'AI Sales Assistant',
            () => _navigateTo(const AISalesAssistantScreen()),
          ),
          _buildNavigationItem(
            Icons.share,
            'Social Selling',
            () => _navigateTo(const SocialSellingScreen()),
          ),
          
          const Divider(),
          
          // Tools
          _buildSectionHeader('⚙️ Tools'),
          _buildNavigationItem(
            Icons.description,
            'Documents',
            () => _showComingSoon('Documents'),
          ),
          _buildNavigationItem(
            Icons.draw,
            'E-Sign',
            () => _showComingSoon('Document E-Sign'),
          ),
          _buildNavigationItem(
            Icons.analytics,
            'Reports',
            () => _showComingSoon('Advanced Reports'),
          ),
          _buildNavigationItem(
            Icons.headset_mic,
            'Conversation AI',
            () => _showComingSoon('Conversation Intelligence'),
          ),
          
          const Divider(),
          
          // Settings
          _buildSectionHeader('Settings'),
          _buildNavigationItem(
            Icons.settings,
            'Settings',
            () => _showComingSoon('Settings'),
          ),
          _buildNavigationItem(
            Icons.security,
            'Security',
            () => _showComingSoon('Security Settings'),
          ),
          _buildNavigationItem(
            Icons.help_outline,
            'Help & Support',
            () => _showComingSoon('Help & Support'),
          ),
          
          const Divider(),
          
          ListTile(
            leading: const Icon(Icons.logout, color: AppColors.error),
            title: const Text(
              'Logout',
              style: TextStyle(color: AppColors.error),
            ),
            onTap: () async {
              Navigator.pop(context);
              _showLogoutConfirmation(authProvider);
            },
          ),
          
          const SizedBox(height: 16),
        ],
      ),
    );
  }

  Widget _buildSectionHeader(String title) {
    return Padding(
      padding: const EdgeInsets.only(left: 16, top: 16, bottom: 8),
      child: Text(
        title,
        style: TextStyle(
          fontSize: 12,
          fontWeight: FontWeight.bold,
          color: Colors.grey.shade600,
          letterSpacing: 0.5,
        ),
      ),
    );
  }

  Widget _buildDrawerItem(IconData icon, String title, int index) {
    final isSelected = _selectedIndex == index;
    return ListTile(
      leading: Icon(
        icon,
        color: isSelected ? AppColors.primary : null,
      ),
      title: Text(
        title,
        style: TextStyle(
          color: isSelected ? AppColors.primary : null,
          fontWeight: isSelected ? FontWeight.bold : null,
        ),
      ),
      selected: isSelected,
      selectedTileColor: AppColors.primary.withValues(alpha: 0.1),
      onTap: () {
        setState(() => _selectedIndex = index);
        Navigator.pop(context);
      },
    );
  }

  Widget _buildNavigationItem(IconData icon, String title, VoidCallback onTap) {
    return ListTile(
      leading: Icon(icon),
      title: Text(title),
      trailing: const Icon(Icons.chevron_right, size: 20),
      onTap: () {
        Navigator.pop(context);
        onTap();
      },
    );
  }

  void _navigateTo(Widget screen) {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => screen),
    );
  }

  void _showComingSoon(String feature) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            const Icon(Icons.info_outline, color: Colors.white),
            const SizedBox(width: 12),
            Expanded(child: Text('$feature coming soon!')),
          ],
        ),
        behavior: SnackBarBehavior.floating,
        action: SnackBarAction(
          label: 'OK',
          textColor: Colors.white,
          onPressed: () {},
        ),
      ),
    );
  }

  void _showNotificationsSheet() {
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
        builder: (context, scrollController) => Column(
          children: [
            Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    'Notifications',
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  TextButton(
                    onPressed: () {},
                    child: const Text('Mark all read'),
                  ),
                ],
              ),
            ),
            const Divider(height: 1),
            Expanded(
              child: ListView.builder(
                controller: scrollController,
                itemCount: 5,
                itemBuilder: (context, index) {
                  return ListTile(
                    leading: CircleAvatar(
                      backgroundColor: Colors.blue.shade100,
                      child: Icon(
                        _getNotificationIcon(index),
                        color: Colors.blue,
                        size: 20,
                      ),
                    ),
                    title: Text(_getNotificationTitle(index)),
                    subtitle: Text(_getNotificationSubtitle(index)),
                    trailing: Text(
                      '${index + 1}h ago',
                      style: TextStyle(
                        color: Colors.grey.shade600,
                        fontSize: 12,
                      ),
                    ),
                    onTap: () {
                      Navigator.pop(context);
                    },
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }

  IconData _getNotificationIcon(int index) {
    final icons = [
      Icons.person_add,
      Icons.attach_money,
      Icons.email,
      Icons.event,
      Icons.emoji_events,
    ];
    return icons[index % icons.length];
  }

  String _getNotificationTitle(int index) {
    final titles = [
      'New lead added',
      'Deal closed successfully',
      'Email opened by client',
      'Meeting reminder',
      'Achievement unlocked!',
    ];
    return titles[index % titles.length];
  }

  String _getNotificationSubtitle(int index) {
    final subtitles = [
      'John Smith was added as a new lead',
      'Acme Corp deal worth \$50,000 closed',
      'Sarah viewed your proposal email',
      'Call with TechCorp in 30 minutes',
      'You earned the "Deal Closer" badge',
    ];
    return subtitles[index % subtitles.length];
  }

  void _showSearchDialog() {
    showSearch(
      context: context,
      delegate: CRMSearchDelegate(),
    );
  }

  void _showLogoutConfirmation(AuthProvider authProvider) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Logout'),
        content: const Text('Are you sure you want to logout?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () async {
              Navigator.pop(context);
              await authProvider.logout();
              if (!context.mounted) return;
              Navigator.of(context).pushReplacement(
                MaterialPageRoute(builder: (_) => const LoginScreen()),
              );
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.error,
            ),
            child: const Text('Logout'),
          ),
        ],
      ),
    );
  }
}

class CRMSearchDelegate extends SearchDelegate {
  @override
  List<Widget> buildActions(BuildContext context) {
    return [
      IconButton(
        icon: const Icon(Icons.clear),
        onPressed: () {
          query = '';
        },
      ),
    ];
  }

  @override
  Widget buildLeading(BuildContext context) {
    return IconButton(
      icon: const Icon(Icons.arrow_back),
      onPressed: () {
        close(context, null);
      },
    );
  }

  @override
  Widget buildResults(BuildContext context) {
    return _buildSearchResults();
  }

  @override
  Widget buildSuggestions(BuildContext context) {
    if (query.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.search, size: 64, color: Colors.grey.shade400),
            const SizedBox(height: 16),
            Text(
              'Search contacts, leads, deals...',
              style: TextStyle(color: Colors.grey.shade600),
            ),
          ],
        ),
      );
    }
    return _buildSearchResults();
  }

  Widget _buildSearchResults() {
    // Mock search results
    final results = [
      {'type': 'contact', 'name': 'John Smith', 'email': 'john@example.com'},
      {'type': 'lead', 'name': 'Sarah Johnson', 'company': 'TechCorp'},
      {'type': 'deal', 'name': 'Enterprise Deal', 'value': '\$50,000'},
      {'type': 'task', 'name': 'Follow up call', 'due': 'Today'},
    ].where((item) => 
      item['name']!.toLowerCase().contains(query.toLowerCase())
    ).toList();

    if (results.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.search_off, size: 64, color: Colors.grey.shade400),
            const SizedBox(height: 16),
            Text(
              'No results found for "$query"',
              style: TextStyle(color: Colors.grey.shade600),
            ),
          ],
        ),
      );
    }

    return ListView.builder(
      itemCount: results.length,
      itemBuilder: (context, index) {
        final result = results[index];
        IconData icon;
        Color color;
        
        switch (result['type']) {
          case 'contact':
            icon = Icons.person;
            color = Colors.blue;
            break;
          case 'lead':
            icon = Icons.person_add;
            color = Colors.green;
            break;
          case 'deal':
            icon = Icons.attach_money;
            color = Colors.amber;
            break;
          case 'task':
            icon = Icons.task;
            color = Colors.purple;
            break;
          default:
            icon = Icons.circle;
            color = Colors.grey;
        }

        return ListTile(
          leading: CircleAvatar(
            backgroundColor: color.withValues(alpha: 0.2),
            child: Icon(icon, color: color),
          ),
          title: Text(result['name']!),
          subtitle: Text(
            result.entries
              .where((e) => e.key != 'type' && e.key != 'name')
              .map((e) => e.value)
              .join(' • '),
          ),
          trailing: Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: color.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Text(
              result['type']!.toUpperCase(),
              style: TextStyle(
                color: color,
                fontSize: 10,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          onTap: () {
            close(context, result);
          },
        );
      },
    );
  }
}
