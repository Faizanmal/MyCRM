import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/utils/api_client.dart';
import '../../providers/advanced_providers.dart';
import '../../models/advanced_models.dart';
import '../../widgets/loading_indicator.dart';
import '../../widgets/empty_state.dart';

class IntegrationHubScreen extends StatefulWidget {
  const IntegrationHubScreen({super.key});

  @override
  State<IntegrationHubScreen> createState() => _IntegrationHubScreenState();
}

class _IntegrationHubScreenState extends State<IntegrationHubScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  late IntegrationHubProvider _provider;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _provider = IntegrationHubProvider(ApiClient());
    _loadData();
  }

  Future<void> _loadData() async {
    await _provider.loadAll();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider.value(
      value: _provider,
      child: Scaffold(
        body: NestedScrollView(
          headerSliverBuilder: (context, innerBoxIsScrolled) => [
            SliverAppBar(
              expandedHeight: 180,
              floating: false,
              pinned: true,
              flexibleSpace: FlexibleSpaceBar(
                title: const Text('Integration Hub'),
                background: Container(
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                      colors: [
                        Colors.blue.shade700,
                        Colors.purple.shade600,
                      ],
                    ),
                  ),
                  child: SafeArea(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const SizedBox(height: 40),
                          Consumer<IntegrationHubProvider>(
                            builder: (context, provider, _) => Row(
                              children: [
                                _buildStatCard(
                                  'Active',
                                  '${provider.activeIntegrations.length}',
                                  Icons.check_circle,
                                ),
                                const SizedBox(width: 16),
                                _buildStatCard(
                                  'Available',
                                  '${provider.availableProviders.length}',
                                  Icons.add_circle_outline,
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
              bottom: TabBar(
                controller: _tabController,
                indicatorColor: Colors.white,
                tabs: const [
                  Tab(text: 'Active Integrations'),
                  Tab(text: 'Available'),
                ],
              ),
            ),
          ],
          body: Consumer<IntegrationHubProvider>(
            builder: (context, provider, _) {
              if (provider.isLoading) {
                return const LoadingIndicator(message: 'Loading integrations...');
              }

              return RefreshIndicator(
                onRefresh: _loadData,
                child: TabBarView(
                  controller: _tabController,
                  children: [
                    _buildActiveIntegrations(provider),
                    _buildAvailableProviders(provider),
                  ],
                ),
              );
            },
          ),
        ),
      ),
    );
  }

  Widget _buildStatCard(String label, String value, IconData icon) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.2),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Icon(icon, color: Colors.white, size: 20),
          const SizedBox(width: 8),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                value,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              Text(
                label,
                style: TextStyle(
                  color: Colors.white.withValues(alpha: 0.8),
                  fontSize: 12,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildActiveIntegrations(IntegrationHubProvider provider) {
    if (provider.activeIntegrations.isEmpty) {
      return const EmptyState(
        icon: Icons.extension_off,
        title: 'No Active Integrations',
        subtitle: 'Connect your first integration to get started',
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: provider.integrations.length,
      itemBuilder: (context, index) {
        final integration = provider.integrations[index];
        return _buildIntegrationCard(integration, provider);
      },
    );
  }

  Widget _buildIntegrationCard(Integration integration, IntegrationHubProvider provider) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.blue.shade50,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Icon(
                    _getProviderIcon(integration.provider?.slug ?? ''),
                    color: Colors.blue.shade700,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        integration.name,
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                      Text(
                        integration.provider?.name ?? 'Unknown Provider',
                        style: TextStyle(color: Colors.grey.shade600),
                      ),
                    ],
                  ),
                ),
                _buildStatusBadge(integration.status),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Icon(Icons.sync, size: 16, color: Colors.grey.shade600),
                const SizedBox(width: 4),
                Text(
                  integration.lastSyncAt != null
                      ? 'Last sync: ${_formatDate(integration.lastSyncAt!)}'
                      : 'Never synced',
                  style: TextStyle(
                    color: Colors.grey.shade600,
                    fontSize: 12,
                  ),
                ),
              ],
            ),
            if (integration.errorMessage != null) ...[
              const SizedBox(height: 8),
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.red.shade50,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    Icon(Icons.error_outline, color: Colors.red.shade700, size: 16),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        integration.errorMessage!,
                        style: TextStyle(color: Colors.red.shade700, fontSize: 12),
                      ),
                    ),
                  ],
                ),
              ),
            ],
            const Divider(height: 24),
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                TextButton.icon(
                  onPressed: () => provider.testConnection(integration.id),
                  icon: const Icon(Icons.check_circle_outline, size: 18),
                  label: const Text('Test'),
                ),
                TextButton.icon(
                  onPressed: () => provider.syncNow(integration.id),
                  icon: const Icon(Icons.sync, size: 18),
                  label: const Text('Sync Now'),
                ),
                TextButton.icon(
                  onPressed: () => _showDisconnectDialog(integration, provider),
                  icon: Icon(Icons.link_off, size: 18, color: Colors.red.shade400),
                  label: Text('Disconnect', style: TextStyle(color: Colors.red.shade400)),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAvailableProviders(IntegrationHubProvider provider) {
    if (provider.providers.isEmpty) {
      return const EmptyState(
        icon: Icons.extension,
        title: 'No Providers Available',
        subtitle: 'All integrations have been connected',
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: provider.providers.length,
      itemBuilder: (context, index) {
        final providerItem = provider.providers[index];
        return _buildProviderCard(providerItem, provider);
      },
    );
  }

  Widget _buildProviderCard(IntegrationProvider providerItem, IntegrationHubProvider provider) {
    final isConnected = provider.integrations.any((i) => i.provider?.id == providerItem.id);
    
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.purple.shade50,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Icon(
                    _getProviderIcon(providerItem.slug),
                    color: Colors.purple.shade700,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        providerItem.name,
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                      Text(
                        providerItem.description,
                        style: TextStyle(color: Colors.grey.shade600),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: providerItem.supportedFeatures.map((feature) {
                return Chip(
                  label: Text(
                    feature,
                    style: const TextStyle(fontSize: 12),
                  ),
                  backgroundColor: Colors.grey.shade100,
                  padding: EdgeInsets.zero,
                  visualDensity: VisualDensity.compact,
                );
              }).toList(),
            ),
            const SizedBox(height: 12),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: isConnected
                    ? null
                    : () => _connectProvider(providerItem, provider),
                icon: Icon(isConnected ? Icons.check : Icons.add),
                label: Text(isConnected ? 'Connected' : 'Connect'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: isConnected ? Colors.green : Colors.blue,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatusBadge(String status) {
    Color color;
    IconData icon;
    switch (status) {
      case 'connected':
        color = Colors.green;
        icon = Icons.check_circle;
        break;
      case 'error':
        color = Colors.red;
        icon = Icons.error;
        break;
      case 'pending':
        color = Colors.orange;
        icon = Icons.pending;
        break;
      default:
        color = Colors.grey;
        icon = Icons.help;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 14, color: color),
          const SizedBox(width: 4),
          Text(
            status.toUpperCase(),
            style: TextStyle(
              color: color,
              fontWeight: FontWeight.bold,
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }

  IconData _getProviderIcon(String slug) {
    switch (slug.toLowerCase()) {
      case 'slack':
        return Icons.chat;
      case 'google':
      case 'google-workspace':
        return Icons.g_mobiledata;
      case 'zapier':
        return Icons.bolt;
      case 'salesforce':
        return Icons.cloud;
      case 'hubspot':
        return Icons.hub;
      case 'mailchimp':
        return Icons.email;
      default:
        return Icons.extension;
    }
  }

  String _formatDate(DateTime date) {
    final now = DateTime.now();
    final diff = now.difference(date);
    
    if (diff.inMinutes < 60) {
      return '${diff.inMinutes}m ago';
    } else if (diff.inHours < 24) {
      return '${diff.inHours}h ago';
    } else {
      return '${diff.inDays}d ago';
    }
  }

  void _connectProvider(IntegrationProvider providerItem, IntegrationHubProvider provider) async {
    // Show connecting dialog
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => const AlertDialog(
        content: Row(
          children: [
            CircularProgressIndicator(),
            SizedBox(width: 16),
            Text('Connecting...'),
          ],
        ),
      ),
    );

    final authUrl = await provider.connectIntegration(
      providerItem.id,
      '${providerItem.name} Integration',
    );

    if (!context.mounted) return;
    Navigator.pop(context);

    if (authUrl != null) {
      if (!context.mounted) return;
      // Show dialog with auth URL or launch browser
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Please complete authentication at: $authUrl')),
      );
    } else {
      if (!context.mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Integration created successfully!')),
      );
    }
  }

  void _showDisconnectDialog(Integration integration, IntegrationHubProvider provider) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Disconnect Integration'),
        content: Text('Are you sure you want to disconnect ${integration.name}?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              provider.disconnectIntegration(integration.id);
              Navigator.pop(context);
            },
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('Disconnect'),
          ),
        ],
      ),
    );
  }
}
