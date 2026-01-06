import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/utils/api_client.dart';
import '../../providers/advanced_providers.dart';
import '../../widgets/loading_indicator.dart';
import 'email_drafts_tab.dart';
import 'coaching_tab.dart';
import 'objection_tab.dart';
import 'call_scripts_tab.dart';

class AISalesAssistantScreen extends StatefulWidget {
  const AISalesAssistantScreen({super.key});

  @override
  State<AISalesAssistantScreen> createState() => _AISalesAssistantScreenState();
}

class _AISalesAssistantScreenState extends State<AISalesAssistantScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  late AISalesAssistantProvider _provider;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
    // Use the existing ApiClient instance which handles auth tokens
    _provider = AISalesAssistantProvider(ApiClient());
    _loadData();
  }

  Future<void> _loadData() async {
    await _provider.loadAll();
  }

  @override
  void dispose() {
    _tabController.dispose();
    _provider.dispose();
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
              expandedHeight: 120,
              floating: false,
              pinned: true,
              flexibleSpace: FlexibleSpaceBar(
                title: const Text('AI Sales Assistant'),
                background: Container(
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                      colors: [
                        Colors.deepPurple.shade700,
                        Colors.purple.shade600,
                      ],
                    ),
                  ),
                ),
              ),
              bottom: TabBar(
                controller: _tabController,
                indicatorColor: Colors.white,
                isScrollable: true,
                tabs: const [
                  Tab(text: 'Email Drafts'),
                  Tab(text: 'Coaching'),
                  Tab(text: 'Objections'),
                  Tab(text: 'Scripts'),
                ],
              ),
            ),
          ],
          body: Consumer<AISalesAssistantProvider>(
            builder: (context, provider, _) {
              if (provider.isLoading && provider.emailDrafts.isEmpty) {
                return const LoadingIndicator(message: 'Loading AI Assistant...');
              }

              return TabBarView(
                controller: _tabController,
                children: [
                  EmailDraftsTab(provider: provider),
                  CoachingTab(provider: provider),
                  ObjectionTab(provider: provider),
                  CallScriptsTab(provider: provider),
                ],
              );
            },
          ),
        ),
      ),
    );
  }
}
