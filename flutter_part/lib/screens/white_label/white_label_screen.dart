import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/utils/api_client.dart';
import '../../providers/enterprise_providers.dart';
import '../../models/enterprise_models.dart';
import '../../widgets/loading_indicator.dart';
import '../../widgets/empty_state.dart';

class WhiteLabelScreen extends StatefulWidget {
  const WhiteLabelScreen({super.key});

  @override
  State<WhiteLabelScreen> createState() => _WhiteLabelScreenState();
}

class _WhiteLabelScreenState extends State<WhiteLabelScreen>
    with SingleTickerProviderStateMixin {
  late WhiteLabelProvider _provider;
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _provider = WhiteLabelProvider(ApiClient());
    _tabController = TabController(length: 3, vsync: this);
    _loadData();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _loadData() async {
    await _provider.loadAll();
  }

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider.value(
      value: _provider,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('White Label & Branding'),
          flexibleSpace: Container(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [Colors.indigo.shade700, Colors.blue.shade500],
              ),
            ),
          ),
          bottom: TabBar(
            controller: _tabController,
            indicatorColor: Colors.white,
            tabs: const [
              Tab(text: 'Branding', icon: Icon(Icons.palette)),
              Tab(text: 'Organizations', icon: Icon(Icons.business)),
              Tab(text: 'Plans', icon: Icon(Icons.subscriptions)),
            ],
          ),
        ),
        body: Consumer<WhiteLabelProvider>(
          builder: (context, provider, _) {
            return TabBarView(
              controller: _tabController,
              children: [
                _buildBrandingTab(provider),
                _buildOrganizationsTab(provider),
                _buildPlansTab(provider),
              ],
            );
          },
        ),
      ),
    );
  }

  Widget _buildBrandingTab(WhiteLabelProvider provider) {
    if (provider.isLoading) {
      return const LoadingIndicator(message: 'Loading branding...');
    }

    final config = provider.brandingConfig;

    return RefreshIndicator(
      onRefresh: _loadData,
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildBrandPreview(config),
            const SizedBox(height: 24),
            _buildColorSettings(config, provider),
            const SizedBox(height: 24),
            _buildLogoSettings(config, provider),
            const SizedBox(height: 24),
            _buildCustomCSSSettings(config, provider),
            const SizedBox(height: 24),
            _buildDomainSettings(config, provider),
          ],
        ),
      ),
    );
  }

  Widget _buildBrandPreview(BrandingConfig? config) {
    return Card(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: config != null 
                  ? Color(int.parse(config.primaryColor.replaceFirst('#', '0xFF')))
                  : Colors.indigo,
              borderRadius: const BorderRadius.vertical(top: Radius.circular(12)),
            ),
            child: Row(
              children: [
                if (config?.logoUrl != null)
                  Container(
                    width: 40,
                    height: 40,
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(8),
                      child: Image.network(
                        config!.logoUrl!,
                        fit: BoxFit.contain,
                        errorBuilder: (_, __, ___) => const Icon(Icons.business),
                      ),
                    ),
                  )
                else
                  Container(
                    width: 40,
                    height: 40,
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: const Icon(Icons.business),
                  ),
                const SizedBox(width: 12),
                Text(
                  config?.companyName ?? 'Your Company',
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Brand Preview',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 8),
                Text(
                  'This is how your branded interface will appear to users.',
                  style: TextStyle(color: Colors.grey.shade600),
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    ElevatedButton(
                      onPressed: () {},
                      style: ElevatedButton.styleFrom(
                        backgroundColor: config != null
                            ? Color(int.parse(config.primaryColor.replaceFirst('#', '0xFF')))
                            : Colors.indigo,
                      ),
                      child: const Text('Primary Button'),
                    ),
                    const SizedBox(width: 12),
                    OutlinedButton(
                      onPressed: () {},
                      style: OutlinedButton.styleFrom(
                        foregroundColor: config != null
                            ? Color(int.parse(config.secondaryColor.replaceFirst('#', '0xFF')))
                            : Colors.blue,
                      ),
                      child: const Text('Secondary Button'),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildColorSettings(BrandingConfig? config, WhiteLabelProvider provider) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.palette),
                const SizedBox(width: 8),
                const Text(
                  'Color Settings',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const Divider(),
            _buildColorRow('Primary Color', config?.primaryColor ?? '#3F51B5', (color) {
              provider.updateBranding(primaryColor: color);
            }),
            _buildColorRow('Secondary Color', config?.secondaryColor ?? '#2196F3', (color) {
              provider.updateBranding(secondaryColor: color);
            }),
            _buildColorRow('Accent Color', config?.accentColor ?? '#FF4081', (color) {
              provider.updateBranding(accentColor: color);
            }),
          ],
        ),
      ),
    );
  }

  Widget _buildColorRow(String label, String currentColor, Function(String) onChanged) {
    Color displayColor;
    try {
      displayColor = Color(int.parse(currentColor.replaceFirst('#', '0xFF')));
    } catch (e) {
      displayColor = Colors.grey;
    }

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Text(label),
          const Spacer(),
          InkWell(
            onTap: () => _showColorPicker(label, currentColor, onChanged),
            child: Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                color: displayColor,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.grey.shade300),
              ),
            ),
          ),
          const SizedBox(width: 8),
          Text(
            currentColor.toUpperCase(),
            style: TextStyle(color: Colors.grey.shade600, fontFamily: 'monospace'),
          ),
        ],
      ),
    );
  }

  void _showColorPicker(String label, String currentColor, Function(String) onChanged) {
    final colors = [
      '#F44336', '#E91E63', '#9C27B0', '#673AB7', '#3F51B5',
      '#2196F3', '#03A9F4', '#00BCD4', '#009688', '#4CAF50',
      '#8BC34A', '#CDDC39', '#FFEB3B', '#FFC107', '#FF9800',
      '#FF5722', '#795548', '#9E9E9E', '#607D8B', '#000000',
    ];

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Select $label'),
        content: SizedBox(
          width: 280,
          child: Wrap(
            spacing: 8,
            runSpacing: 8,
            children: colors.map((color) {
              final displayColor = Color(int.parse(color.replaceFirst('#', '0xFF')));
              return InkWell(
                onTap: () {
                  onChanged(color);
                  Navigator.pop(context);
                },
                child: Container(
                  width: 40,
                  height: 40,
                  decoration: BoxDecoration(
                    color: displayColor,
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(
                      color: color == currentColor ? Colors.black : Colors.grey.shade300,
                      width: color == currentColor ? 3 : 1,
                    ),
                  ),
                ),
              );
            }).toList(),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
        ],
      ),
    );
  }

  Widget _buildLogoSettings(BrandingConfig? config, WhiteLabelProvider provider) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.image),
                const SizedBox(width: 8),
                const Text(
                  'Logo Settings',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const Divider(),
            Row(
              children: [
                Container(
                  width: 80,
                  height: 80,
                  decoration: BoxDecoration(
                    color: Colors.grey.shade100,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: Colors.grey.shade300),
                  ),
                  child: config?.logoUrl != null
                      ? ClipRRect(
                          borderRadius: BorderRadius.circular(12),
                          child: Image.network(
                            config!.logoUrl!,
                            fit: BoxFit.contain,
                            errorBuilder: (_, __, ___) => const Icon(Icons.image, size: 40),
                          ),
                        )
                      : const Icon(Icons.image, size: 40, color: Colors.grey),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('Company Logo'),
                      Text(
                        'Recommended: 200x60 px, PNG format',
                        style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
                      ),
                      const SizedBox(height: 8),
                      ElevatedButton.icon(
                        onPressed: () {
                          // Upload logo
                        },
                        icon: const Icon(Icons.upload),
                        label: const Text('Upload Logo'),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Container(
                  width: 80,
                  height: 80,
                  decoration: BoxDecoration(
                    color: Colors.grey.shade100,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: Colors.grey.shade300),
                  ),
                  child: config?.faviconUrl != null
                      ? ClipRRect(
                          borderRadius: BorderRadius.circular(12),
                          child: Image.network(
                            config!.faviconUrl!,
                            fit: BoxFit.contain,
                            errorBuilder: (_, __, ___) => const Icon(Icons.web, size: 40),
                          ),
                        )
                      : const Icon(Icons.web, size: 40, color: Colors.grey),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('Favicon'),
                      Text(
                        'Recommended: 32x32 px, ICO/PNG format',
                        style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
                      ),
                      const SizedBox(height: 8),
                      ElevatedButton.icon(
                        onPressed: () {
                          // Upload favicon
                        },
                        icon: const Icon(Icons.upload),
                        label: const Text('Upload Favicon'),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCustomCSSSettings(BrandingConfig? config, WhiteLabelProvider provider) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.code),
                const SizedBox(width: 8),
                const Text(
                  'Custom CSS',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const Divider(),
            TextField(
              maxLines: 6,
              decoration: InputDecoration(
                hintText: '/* Add custom CSS here */\n.custom-class { ... }',
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
                filled: true,
                fillColor: Colors.grey.shade50,
              ),
              style: const TextStyle(fontFamily: 'monospace', fontSize: 12),
            ),
            const SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                TextButton(
                  onPressed: () {},
                  child: const Text('Preview'),
                ),
                const SizedBox(width: 8),
                ElevatedButton(
                  onPressed: () {},
                  child: const Text('Apply'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDomainSettings(BrandingConfig? config, WhiteLabelProvider provider) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.language),
                const SizedBox(width: 8),
                const Text(
                  'Custom Domain',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const Divider(),
            TextField(
              decoration: InputDecoration(
                labelText: 'Custom Domain',
                hintText: 'crm.yourcompany.com',
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
                prefixIcon: const Icon(Icons.dns),
              ),
            ),
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.blue.shade50,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                children: [
                  Icon(Icons.info_outline, color: Colors.blue.shade700),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Add a CNAME record pointing to: app.mycrm.com',
                      style: TextStyle(color: Colors.blue.shade700, fontSize: 12),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                OutlinedButton.icon(
                  onPressed: () {},
                  icon: const Icon(Icons.verified),
                  label: const Text('Verify Domain'),
                ),
                const SizedBox(width: 8),
                ElevatedButton.icon(
                  onPressed: () {},
                  icon: const Icon(Icons.save),
                  label: const Text('Save Settings'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildOrganizationsTab(WhiteLabelProvider provider) {
    if (provider.isLoading) {
      return const LoadingIndicator(message: 'Loading organizations...');
    }

    if (provider.organizations.isEmpty) {
      return EmptyState(
        icon: Icons.business_outlined,
        title: 'No Organizations',
        subtitle: 'Create your first organization',
        action: ElevatedButton.icon(
          onPressed: _showCreateOrgDialog,
          icon: const Icon(Icons.add),
          label: const Text('Create Organization'),
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: () => provider.loadOrganizations(),
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: provider.organizations.length,
        itemBuilder: (context, index) {
          return _buildOrganizationCard(provider.organizations[index]);
        },
      ),
    );
  }

  Widget _buildOrganizationCard(Organization org) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: Colors.indigo.shade50,
          child: Text(
            org.name.substring(0, 1).toUpperCase(),
            style: TextStyle(color: Colors.indigo.shade700, fontWeight: FontWeight.bold),
          ),
        ),
        title: Text(org.name),
        subtitle: Text('${org.userCount} users • ${org.plan}'),
        trailing: PopupMenuButton<String>(
          onSelected: (value) {
            // Handle action
          },
          itemBuilder: (context) => [
            const PopupMenuItem(value: 'edit', child: Text('Edit')),
            const PopupMenuItem(value: 'branding', child: Text('Branding')),
            const PopupMenuItem(value: 'delete', child: Text('Delete')),
          ],
        ),
        onTap: () {},
      ),
    );
  }

  Widget _buildPlansTab(WhiteLabelProvider provider) {
    if (provider.isLoading) {
      return const LoadingIndicator(message: 'Loading plans...');
    }

    return RefreshIndicator(
      onRefresh: () => provider.loadPlans(),
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _buildPlanCard(
            'Starter',
            '\$29/mo',
            ['Up to 100 contacts', '2 users', 'Basic features', 'Email support'],
            Colors.blue,
            false,
          ),
          _buildPlanCard(
            'Professional',
            '\$79/mo',
            ['Up to 5,000 contacts', '10 users', 'Advanced features', 'Priority support', 'Custom branding'],
            Colors.indigo,
            true,
          ),
          _buildPlanCard(
            'Enterprise',
            'Custom',
            ['Unlimited contacts', 'Unlimited users', 'All features', 'Dedicated support', 'Full white-label', 'Custom integrations'],
            Colors.purple,
            false,
          ),
        ],
      ),
    );
  }

  Widget _buildPlanCard(String name, String price, List<String> features, Color color, bool isPopular) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: Container(
        decoration: BoxDecoration(
          border: isPopular ? Border.all(color: color, width: 2) : null,
          borderRadius: BorderRadius.circular(12),
        ),
        child: Column(
          children: [
            if (isPopular)
              Container(
                width: double.infinity,
                padding: const EdgeInsets.symmetric(vertical: 8),
                decoration: BoxDecoration(
                  color: color,
                  borderRadius: const BorderRadius.vertical(top: Radius.circular(10)),
                ),
                child: const Text(
                  'MOST POPULAR',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                    fontSize: 12,
                  ),
                ),
              ),
            Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                children: [
                  Text(
                    name,
                    style: TextStyle(
                      fontSize: 22,
                      fontWeight: FontWeight.bold,
                      color: color,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    price,
                    style: const TextStyle(
                      fontSize: 32,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 20),
                  ...features.map((f) => Padding(
                    padding: const EdgeInsets.symmetric(vertical: 4),
                    child: Row(
                      children: [
                        Icon(Icons.check, color: color, size: 20),
                        const SizedBox(width: 8),
                        Text(f),
                      ],
                    ),
                  )),
                  const SizedBox(height: 20),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: () {},
                      style: ElevatedButton.styleFrom(
                        backgroundColor: color,
                        padding: const EdgeInsets.symmetric(vertical: 12),
                      ),
                      child: const Text('Select Plan'),
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

  void _showCreateOrgDialog() {
    final nameController = TextEditingController();

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Create Organization'),
        content: TextField(
          controller: nameController,
          decoration: const InputDecoration(
            labelText: 'Organization Name',
            border: OutlineInputBorder(),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              _provider.createOrganization(name: nameController.text);
              Navigator.pop(context);
            },
            child: const Text('Create'),
          ),
        ],
      ),
    );
  }
}
