import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/utils/api_client.dart';
import '../../providers/enterprise_providers.dart';
import '../../models/enterprise_models.dart';
import '../../widgets/loading_indicator.dart';
import '../../widgets/empty_state.dart';

class MarketplaceScreen extends StatefulWidget {
  const MarketplaceScreen({super.key});

  @override
  State<MarketplaceScreen> createState() => _MarketplaceScreenState();
}

class _MarketplaceScreenState extends State<MarketplaceScreen>
    with SingleTickerProviderStateMixin {
  late MarketplaceProvider _provider;
  late TabController _tabController;
  String? _selectedCategory;
  final TextEditingController _searchController = TextEditingController();

  final List<String> _categories = [
    'All',
    'Sales',
    'Marketing',
    'Analytics',
    'Communication',
    'Productivity',
    'Integration',
  ];

  @override
  void initState() {
    super.initState();
    _provider = MarketplaceProvider(ApiClient());
    _tabController = TabController(length: 2, vsync: this);
    _loadData();
  }

  @override
  void dispose() {
    _tabController.dispose();
    _searchController.dispose();
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
          title: const Text('App Marketplace'),
          flexibleSpace: Container(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [Colors.indigo.shade600, Colors.blue.shade500],
              ),
            ),
          ),
          bottom: TabBar(
            controller: _tabController,
            indicatorColor: Colors.white,
            tabs: const [
              Tab(text: 'Browse', icon: Icon(Icons.apps)),
              Tab(text: 'Installed', icon: Icon(Icons.check_circle)),
            ],
          ),
        ),
        body: Consumer<MarketplaceProvider>(
          builder: (context, provider, _) {
            return TabBarView(
              controller: _tabController,
              children: [
                _buildBrowseTab(provider),
                _buildInstalledTab(provider),
              ],
            );
          },
        ),
      ),
    );
  }

  Widget _buildBrowseTab(MarketplaceProvider provider) {
    return Column(
      children: [
        _buildSearchBar(),
        _buildCategoryChips(),
        Expanded(
          child: provider.isLoading
              ? const LoadingIndicator(message: 'Loading apps...')
              : provider.apps.isEmpty
                  ? const EmptyState(
                      icon: Icons.apps_outlined,
                      title: 'No Apps Found',
                      subtitle: 'Try a different search or category',
                    )
                  : RefreshIndicator(
                      onRefresh: _loadData,
                      child: GridView.builder(
                        padding: const EdgeInsets.all(16),
                        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                          crossAxisCount: 2,
                          childAspectRatio: 0.75,
                          crossAxisSpacing: 12,
                          mainAxisSpacing: 12,
                        ),
                        itemCount: provider.apps.length,
                        itemBuilder: (context, index) {
                          return _buildAppCard(provider.apps[index], provider);
                        },
                      ),
                    ),
        ),
      ],
    );
  }

  Widget _buildSearchBar() {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: TextField(
        controller: _searchController,
        decoration: InputDecoration(
          hintText: 'Search apps...',
          prefixIcon: const Icon(Icons.search),
          suffixIcon: _searchController.text.isNotEmpty
              ? IconButton(
                  icon: const Icon(Icons.clear),
                  onPressed: () {
                    _searchController.clear();
                    _provider.loadApps();
                  },
                )
              : null,
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide: BorderSide.none,
          ),
          filled: true,
          fillColor: Colors.grey.shade100,
        ),
        onSubmitted: (value) {
          _provider.loadApps(search: value, category: _selectedCategory);
        },
      ),
    );
  }

  Widget _buildCategoryChips() {
    return SizedBox(
      height: 50,
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 12),
        itemCount: _categories.length,
        itemBuilder: (context, index) {
          final category = _categories[index];
          final isSelected = (_selectedCategory ?? 'All') == category;
          
          return Padding(
            padding: const EdgeInsets.symmetric(horizontal: 4),
            child: FilterChip(
              label: Text(category),
              selected: isSelected,
              onSelected: (selected) {
                setState(() {
                  _selectedCategory = selected ? category : null;
                });
                _provider.loadApps(
                  category: category == 'All' ? null : category.toLowerCase(),
                  search: _searchController.text.isNotEmpty ? _searchController.text : null,
                );
              },
              selectedColor: Colors.indigo.shade100,
              checkmarkColor: Colors.indigo,
            ),
          );
        },
      ),
    );
  }

  Widget _buildAppCard(MarketplaceApp app, MarketplaceProvider provider) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: InkWell(
        onTap: () => _showAppDetails(app, provider),
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    width: 48,
                    height: 48,
                    decoration: BoxDecoration(
                      color: Colors.indigo.shade50,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: app.iconUrl != null
                        ? ClipRRect(
                            borderRadius: BorderRadius.circular(12),
                            child: Image.network(
                              app.iconUrl!,
                              fit: BoxFit.cover,
                              errorBuilder: (_, __, ___) => Icon(
                                Icons.extension,
                                color: Colors.indigo.shade400,
                              ),
                            ),
                          )
                        : Icon(
                            Icons.extension,
                            color: Colors.indigo.shade400,
                          ),
                  ),
                  const Spacer(),
                  if (app.isInstalled)
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: Colors.green.shade100,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: const Text(
                        'Installed',
                        style: TextStyle(
                          color: Colors.green,
                          fontSize: 10,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                ],
              ),
              const SizedBox(height: 12),
              Text(
                app.name,
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 14,
                ),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 4),
              Text(
                app.description,
                style: TextStyle(
                  color: Colors.grey.shade600,
                  fontSize: 12,
                ),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
              const Spacer(),
              Row(
                children: [
                  Icon(Icons.star, color: Colors.amber, size: 16),
                  const SizedBox(width: 4),
                  Text(
                    app.rating.toStringAsFixed(1),
                    style: TextStyle(
                      color: Colors.grey.shade700,
                      fontSize: 12,
                    ),
                  ),
                  const Spacer(),
                  Text(
                    app.isFree ? 'Free' : '\$${app.price?.toStringAsFixed(0)}/mo',
                    style: TextStyle(
                      color: app.isFree ? Colors.green : Colors.indigo,
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildInstalledTab(MarketplaceProvider provider) {
    if (provider.isLoading) {
      return const LoadingIndicator(message: 'Loading installed apps...');
    }

    if (provider.installedApps.isEmpty) {
      return EmptyState(
        icon: Icons.extension_off_outlined,
        title: 'No Apps Installed',
        subtitle: 'Browse the marketplace to find useful apps',
        action: ElevatedButton.icon(
          onPressed: () => _tabController.animateTo(0),
          icon: const Icon(Icons.apps),
          label: const Text('Browse Apps'),
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: () => provider.loadInstalledApps(),
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: provider.installedApps.length,
        itemBuilder: (context, index) {
          return _buildInstalledAppCard(provider.installedApps[index], provider);
        },
      ),
    );
  }

  Widget _buildInstalledAppCard(InstalledApp app, MarketplaceProvider provider) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        leading: Container(
          width: 48,
          height: 48,
          decoration: BoxDecoration(
            color: Colors.indigo.shade50,
            borderRadius: BorderRadius.circular(12),
          ),
          child: Icon(Icons.extension, color: Colors.indigo.shade400),
        ),
        title: Text(app.appName),
        subtitle: Text(
          app.isActive ? 'Active' : 'Disabled',
          style: TextStyle(
            color: app.isActive ? Colors.green : Colors.grey,
          ),
        ),
        trailing: PopupMenuButton<String>(
          onSelected: (value) {
            if (value == 'uninstall') {
              _confirmUninstall(app, provider);
            } else if (value == 'settings') {
              _showAppSettings(app);
            }
          },
          itemBuilder: (context) => [
            const PopupMenuItem(
              value: 'settings',
              child: Row(
                children: [
                  Icon(Icons.settings),
                  SizedBox(width: 12),
                  Text('Settings'),
                ],
              ),
            ),
            const PopupMenuItem(
              value: 'uninstall',
              child: Row(
                children: [
                  Icon(Icons.delete, color: Colors.red),
                  SizedBox(width: 12),
                  Text('Uninstall', style: TextStyle(color: Colors.red)),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _showAppDetails(MarketplaceApp app, MarketplaceProvider provider) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.7,
        minChildSize: 0.5,
        maxChildSize: 0.95,
        expand: false,
        builder: (context, scrollController) => ListView(
          controller: scrollController,
          padding: const EdgeInsets.all(20),
          children: [
            Center(
              child: Container(
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                  color: Colors.grey.shade300,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),
            const SizedBox(height: 20),
            Row(
              children: [
                Container(
                  width: 64,
                  height: 64,
                  decoration: BoxDecoration(
                    color: Colors.indigo.shade50,
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Icon(
                    Icons.extension,
                    size: 32,
                    color: Colors.indigo.shade400,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        app.name,
                        style: const TextStyle(
                          fontSize: 22,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(
                        'by ${app.developer}',
                        style: TextStyle(color: Colors.grey.shade600),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),
            Row(
              children: [
                Icon(Icons.star, color: Colors.amber),
                const SizedBox(width: 4),
                Text(
                  '${app.rating} • ${app.installCount} installs',
                  style: TextStyle(color: Colors.grey.shade700),
                ),
                const Spacer(),
                Text(
                  app.isFree ? 'Free' : '\$${app.price?.toStringAsFixed(2)}/month',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: app.isFree ? Colors.green : Colors.indigo,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: app.isInstalled
                    ? () {
                        provider.uninstallApp(app.id);
                        Navigator.pop(context);
                      }
                    : () {
                        provider.installApp(app.id);
                        Navigator.pop(context);
                      },
                style: ElevatedButton.styleFrom(
                  backgroundColor: app.isInstalled ? Colors.red : Colors.indigo,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: Text(
                  app.isInstalled ? 'Uninstall' : 'Install',
                  style: const TextStyle(fontSize: 16),
                ),
              ),
            ),
            const SizedBox(height: 24),
            const Text(
              'Description',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text(
              app.description,
              style: TextStyle(color: Colors.grey.shade700, height: 1.5),
            ),
            const SizedBox(height: 24),
            const Text(
              'Features',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            ...app.features.map((feature) => Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Row(
                children: [
                  const Icon(Icons.check_circle, color: Colors.green, size: 20),
                  const SizedBox(width: 12),
                  Expanded(child: Text(feature)),
                ],
              ),
            )),
          ],
        ),
      ),
    );
  }

  void _confirmUninstall(InstalledApp app, MarketplaceProvider provider) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Uninstall App'),
        content: Text('Are you sure you want to uninstall ${app.appName}?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              provider.uninstallApp(app.appId);
              Navigator.pop(context);
            },
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('Uninstall'),
          ),
        ],
      ),
    );
  }

  void _showAppSettings(InstalledApp app) {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '${app.appName} Settings',
              style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 20),
            SwitchListTile(
              title: const Text('Enable App'),
              value: app.isActive,
              onChanged: (value) {
                // Toggle app status
                Navigator.pop(context);
              },
            ),
            const Divider(),
            ListTile(
              leading: const Icon(Icons.info_outline),
              title: const Text('App Information'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () {},
            ),
            ListTile(
              leading: const Icon(Icons.sync),
              title: const Text('Sync Settings'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () {},
            ),
            const SizedBox(height: 20),
          ],
        ),
      ),
    );
  }
}
