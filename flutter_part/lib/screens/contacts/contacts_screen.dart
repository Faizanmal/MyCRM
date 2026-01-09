import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/constants/app_constants.dart';
import '../../models/crm_models.dart';
import '../../providers/contacts_provider.dart';
import 'contact_detail_screen.dart';
import 'add_contact_screen.dart';

class ContactsScreen extends StatefulWidget {
  const ContactsScreen({super.key});
  
  @override
  State<ContactsScreen> createState() => _ContactsScreenState();
}

class _ContactsScreenState extends State<ContactsScreen> {
  final ScrollController _scrollController = ScrollController();
  
  @override
  void initState() {
    super.initState();
    // Fetch contacts when screen loads
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<ContactsProvider>().fetchContacts(refresh: true);
    });

    // Add scroll listener for pagination
    _scrollController.addListener(_onScroll);
  }
  
  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  void _onScroll() {
    final provider = context.read<ContactsProvider>();
    if (_scrollController.position.pixels == _scrollController.position.maxScrollExtent) {
      if (provider.hasMore && !provider.isLoading) {
        provider.fetchContacts();
      }
    }
  }

  Future<void> _refreshContacts() async {
    await context.read<ContactsProvider>().fetchContacts(refresh: true);
  }
  
  void _navigateToAddContact() async {
    await Navigator.push<bool>(
      context,
      MaterialPageRoute(builder: (context) => const AddContactScreen()),
    );
  }
  
  void _navigateToContactDetail(Contact contact) async {
    await Navigator.push<bool>(
      context,
      MaterialPageRoute(
        builder: (context) => ContactDetailScreen(contact: contact),
      ),
    );
  }

  void _navigateToEditContact(Contact contact) async {
    await Navigator.push<bool>(
      context,
      MaterialPageRoute(
        builder: (context) => AddContactScreen(contact: contact),
      ),
    );
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Consumer<ContactsProvider>(
        builder: (context, provider, child) {
          if (provider.isLoading && provider.contacts.isEmpty) {
            return const Center(child: CircularProgressIndicator());
          }

          if (provider.error != null && provider.contacts.isEmpty) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.error_outline, size: 48, color: AppColors.error),
                  const SizedBox(height: AppSizes.paddingMd),
                  Text('Error: ${provider.error}'),
                  TextButton(
                    onPressed: _refreshContacts,
                    child: const Text('Retry'),
                  ),
                ],
              ),
            );
          }

          return RefreshIndicator(
            onRefresh: _refreshContacts,
            child: provider.contacts.isEmpty
                ? _buildEmptyState()
                : ListView.separated(
                    controller: _scrollController,
                    padding: const EdgeInsets.all(AppSizes.paddingMd),
                    itemCount: provider.contacts.length + (provider.hasMore ? 1 : 0),
                    separatorBuilder: (context, index) => const SizedBox(height: AppSizes.paddingSm),
                    itemBuilder: (context, index) {
                      if (index == provider.contacts.length) {
                        return const Center(
                          child: Padding(
                            padding: EdgeInsets.all(8.0),
                            child: CircularProgressIndicator(),
                          ),
                        );
                      }

                      final contact = provider.contacts[index];
                      return _buildContactCard(contact);
                    },
                  ),
          );
        },
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _navigateToAddContact,
        child: const Icon(Icons.add),
      ),
    );
  }
  
  Widget _buildContactCard(Contact contact) {
    return Card(
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: AppColors.primary,
          child: Text(
            contact.initials,
            style: const TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        title: Text(
          contact.fullName,
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (contact.company != null)
              Text('${contact.company} ${contact.position != null ? '• ${contact.position}' : ''}'),
            if (contact.email != null)
              Text(
                contact.email!,
                style: const TextStyle(fontSize: AppSizes.fontSm),
              ),
            if (contact.phone != null)
              Text(
                contact.phone!,
                style: const TextStyle(fontSize: AppSizes.fontSm),
              ),
          ],
        ),
        trailing: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              padding: const EdgeInsets.symmetric(
                horizontal: AppSizes.paddingSm,
                vertical: 4,
              ),
              decoration: BoxDecoration(
                color: contact.status == 'Active'
                    ? AppColors.success.withValues(alpha: 0.1)
                    : AppColors.warning.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(AppSizes.radiusSm),
              ),
              child: Text(
                contact.status ?? 'Unknown',
                style: TextStyle(
                  fontSize: AppSizes.fontXs,
                  fontWeight: FontWeight.w600,
                  color: contact.status == 'Active'
                      ? AppColors.success
                      : AppColors.warning,
                ),
              ),
            ),
            const SizedBox(width: 8),
            IconButton(
              icon: const Icon(Icons.edit, size: 20),
              color: AppColors.grey500,
              onPressed: () => _navigateToEditContact(contact),
              padding: EdgeInsets.zero,
              constraints: const BoxConstraints(),
            ),
          ],
        ),
        isThreeLine: true,
        onTap: () => _navigateToContactDetail(contact),
      ),
    );
  }
  
  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.people_outline,
            size: 80,
            color: AppColors.grey400,
          ),
          const SizedBox(height: AppSizes.paddingMd),
          const Text(
            'No contacts yet',
            style: TextStyle(
              fontSize: AppSizes.fontLg,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: AppSizes.paddingSm),
          Text(
            'Add your first contact to get started',
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
